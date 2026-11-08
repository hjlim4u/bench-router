---
title: >-
  What herdr-projects uniquely does for bench-router, and why Herdr-API/other plugins don't replace it yet
tags: [herdr, herdr-projects, adapter, bench-router]
summary: >-
  Source-verified herdr-projects 1.2.26 features used by the board runner (turn-end hooks, finish line, WORK_SETTINGS) and A/B/inline research on alternatives.
project: bench-router
base_confidence: 0.75
provenance:
  extracted: 0.8
  inferred: 0.2
lifecycle_changed: 2026-11-07
sources:
  - "bench-router session (2026-11-07)"
---

## Findings
- Read from local checkout (~/.config/herdr/plugins/github-installations/herdr-projects-*/*/checkout, a6787e1; ~42k lines Rust in crates/{core,flow,board,web}) and docs/how-work-gets-done.md.
- Biggest unique layer: turn-end detection. Plugin launches each agent itself with a hook (Claude `--settings <file>`, Codex `-c notify=[..]`, pi `-e`) and own session id, then reads the agent's saved conversation (last message, API/login errors, tokens). Without a hook, Herdr "idle" alone never finishes a task (needs finished message/error in conversation or closing-note.md; else held as "Stopped without a summary"). Herdr `done` = unseen idle, not completion.
- Also: waiting-for-you (question/permission/login) is not "finished"; per-task worktree via `herdr worktree create` with branch work/<n>-<slug> and git-config-lock retry; access default is full (`claude --dangerously-skip-permissions`, `codex --dangerously-bypass-approvals-and-sandbox`), `worker.access ask|auto` removes flags; plugin marks repo trusted in ~/.claude.json and ~/.codex/config.toml; finish line = commit, catch up with main, run repo `check` (3 retries), push+draft PR, adversarial review, approval; board.agents cap 4.
- bench_router/herdr.py WORK_SETTINGS (fixed per task): workspace.from here, workspace.cleanup false, review.when never, review.rounds 0, merge.by you, merge.pr false, attempts.by 1, plan.approve none, --no-research. worker.access is NOT fixed (follows board; default full). So review/PR/merge/attempts/plan/coordinator/UI are unused.
- Alternatives (README/manifest-level only, none executed): herdr-board (nelsonPires5) best JSON CLI/model/effort/permission/stop/resume, but worktree mode removed (isolation is agent's job, per docs/protocol.md), no tell; tsk lacks stop/per-task model/effort and opens PRs; agent-router picks agent via TypeSafe (conflicts with bench-router routing); htasks auto-merges PRs; dagr/herdr-plus are not executors. Headless Antigravity-3.8-flash (A) and Codex-sol (B) runs plus inline research agreed: Herdr-native "thin adapter" ranks first on paper, but A/B marked key parts (state machine, permission mapping, turn-end) as inferred; cost likely underestimated.
- Decision as of 2026-11-07: no code change; installed 1.2.26 works. Only risk is fresh `herdr plugin install eliasstravik/herdr-projects` / update after the shepherdr rename (herdr-plugin.toml removed from main in 3.0; not verified by running). Candidate low-cost action: doc warning in README.md and docs/projects.md.

## Operational gotchas
- Dispatch hits `conflict` when 4 admission records are active; stale `timed_out` records need `coordination release --key K --confirmed-stopped --note ...` after inspection, and an unsettled prior run in the same cwd must be `collect`ed first.
- Concurrent routes on the same cwd conflict (overlapping-workspace guard); give the second a separate `git worktree add --detach` as cwd.
- `bench-router route --profile P --runner local` pins a profile without the vendor decision flow (warns, no selection record); `--wait-ms 0` returns run ids; `collect --run CWD ID --run ... --until all` waits.
- gh CLI is not installed on this machine.
