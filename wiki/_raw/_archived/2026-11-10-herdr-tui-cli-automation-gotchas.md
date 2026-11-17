---
title: "herdr 0.9.5 TUI CLI automation: confirmed behaviors and gotchas"
category: skills
tags:
  - topic/herdr
  - herdr
  - bench-router
  - agent-automation
summary: "Live-confirmed herdr 0.9.5 CLI behaviors for driving panes and agents from a script: output shapes, error codes, process lifetime, server scoping and agent turn detection."
tier: supporting
related: []
extends: null
contradicts: null
superseded_by: null
capture_source: claude-session
project: "bench-router"
base_confidence: 0.85
lifecycle: draft
lifecycle_changed: 2026-11-10
provenance:
  extracted: 0.85
  inferred: 0.15
sources:
  - "bench-router session (2026-11-09)"
---

## `herdr pane run` prints nothing on success

**Behavior:** `herdr pane run <pane> "<command>"` exits 0 with empty stdout. Parsing its output as JSON fails, and a run that really started gets recorded as an unconfirmed delivery.

**Workaround / Pattern:** Read `pane run` output raw (no JSON parse). Other commands (`workspace create`, `workspace close`, `pane get`, `agent start|prompt|get|wait`) print JSON.

**Confirmed by:** Live smoke test against herdr 0.9.5; the bug was caught live, then the fake in `test_p2.py` was made to return empty stdout so the test catches it.

## Shapes and error codes

**Behavior:**
- `herdr workspace create --cwd D --label L --no-focus` → `.result.workspace.workspace_id` and `.result.root_pane.pane_id` (plus `.result.tab`).
- Errors are JSON on **stderr**, exit status 1: `{"error":{"code":"pane_not_found",...}}`, `workspace_not_found`, `agent_not_found`, `agent_not_ready`, `agent_blocked`. Invalid CLI syntax exits 2.
- `herdr agent read` prints plain text, not JSON.

**Workaround / Pattern:** Match on the error `code` string in stderr. Treat `workspace_not_found` on close as "already closed", otherwise a cleanup retry loops forever.

## `workspace close` ends what runs inside it

**Behavior:** Closing a workspace hangs up (SIGHUP) the processes in its panes, including a running one-shot CLI and an interactive agent.

**Explanation:** The pane terminal closes, so its foreground process group gets SIGHUP. ^[inferred]

**Workaround / Pattern:** One workspace per run makes `workspace close` a safe stop that touches nothing else. When a script publishes completion via a file written after a `| tee log` pipeline, publish it after `tee` ends (`… | tee log; mv exit_code.tmp exit_code`); otherwise closing on the file can cut the log tail.

**Notes:** When checking whether a process survived, `pgrep -f "sleep 30"` also matches the checking shell's own command line; check the recorded PIDs with `kill -0`.

## IDs are scoped to one herdr server

**Behavior:** Workspace, pane and agent IDs (`wD:p1`) and agent names are only unique within one server (official docs say the same). A script run from another herdr session can address an unrelated workspace with the same ID.

**Workaround / Pattern:** Record `herdr status server`'s `socket:` line at start and refuse other servers before any close or settle. `herdr status server` has no JSON form; it prints the same socket with or without `HERDR_SOCKET_PATH` set.

## Starting an agent and detecting the end of its turn

**Behavior:**
- `herdr agent start NAME --kind claude --pane P -- <native args>` returns only once the agent is ready. In a folder Claude has never trusted, the folder-trust question blocks startup and the command returns `agent_not_ready` ("blocked during startup"). Folders under an already trusted repo (e.g. `<repo>/.bench-router/worktrees/...`) do not ask.
- `herdr agent prompt NAME TEXT --wait --until working --until blocked --timeout MS` returns as soon as the turn is seen working (≈0.5 s), confirming the prompt landed; multi-line text works.
- After a turn, status is `done` (idle but not yet seen) or `idle`; `agent get` then carries `completion_seq`, which startup readiness never sets.
- Right after a prompt without `--wait`, status can still read `idle` for up to ~5 s (docs: herdr waits up to five seconds to observe working). ^[inferred]

**Workaround / Pattern:** Do not infer "idle after prompt = turn finished". Send every prompt (including follow-up `tell` messages) with `--wait --until working`, and count a turn as finished only when `completion_seq` is present. Agent names must match `[a-z][a-z0-9_-]{0,31}`.

**Confirmed by:** Live probes with claude haiku in herdr 0.9.5; a real interactive bench-router run completed end to end. `agent get` returns `completion_seq` after a real turn (live: 15 after turn 1). A live run of finish → `tell` (with `--wait --until working`) → immediate `collect` reported `timed_out`, then `completed` with both turns' files. The idle lag without `--wait` itself comes from the docs.
