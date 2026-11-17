---
title: >-
  herdr 0.9.5 TUI CLI automation: confirmed behaviors and gotchas
category: projects
tags: [herdr, bench-router, agent-automation, cli]
summary: >-
  Live-confirmed herdr 0.9.5 CLI behaviors for driving panes and agents from scripts: empty pane run stdout, JSON errors on stderr, server scoping, and agent turn detection.
project: bench-router
base_confidence: 0.85
provenance:
  extracted: 0.85
  inferred: 0.15
lifecycle: draft
lifecycle_changed: 2026-11-10
created: 2026-11-10T00:00:00Z
updated: 2026-11-10T00:30:00Z
sources:
  - "bench-router session (2026-11-09)"
snapshots:
  - "[[_raw/_archived/2026-11-10-herdr-tui-cli-automation-gotchas|2026-11-10-herdr-tui-cli-automation-gotchas]]"
---

# herdr 0.9.5 TUI CLI automation: confirmed behaviors and gotchas

Live-confirmed behaviors and edge cases when automating `herdr 0.9.5` TUI from scripts:

## 1. `herdr pane run` Prints Nothing on Success
- `herdr pane run <pane> "<command>"` exits 0 with completely empty stdout.
- Calling code must not attempt to parse stdout as JSON. Other commands (`workspace create`, `agent start|prompt|get|wait`) emit structured JSON.

## 2. Command Shapes and Error Handling
- `herdr workspace create --cwd D --label L --no-focus` returns JSON on stdout with `.result.workspace.workspace_id` and `.result.root_pane.pane_id`.
- Errors are returned as JSON on **stderr** with exit status 1 (`{"error":{"code":"pane_not_found",...}}`, `workspace_not_found`, `agent_blocked`).
- `herdr agent read` outputs raw text, not JSON.

## 3. Server Scoping & Process Lifetime
- Scoped to `HERDR_SERVER_DIR` (or defaults to `~/.local/share/herdr/servers/default`).
- Background processes survive pane exit unless killed explicitly.

## Sources

- [[_raw/_archived/2026-11-10-herdr-tui-cli-automation-gotchas]]
