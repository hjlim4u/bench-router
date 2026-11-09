---
title: >-
  herdr-projects renamed to shepherdr: same concept, new platform (herdr-app layout) and CLI (herdr-task)
tags: [herdr, herdr-projects, shepherdr, plugin]
summary: >-
  shepherdr 3.x keeps the same board+worktree+review concept but ships as a herdr-app layout (install.sh), not a herdr plugin; bench-router's herdr-projects runner assumptions may break on reinstall.
project: bench-router
base_confidence: 0.6
provenance:
  extracted: 0.7
  inferred: 0.3
lifecycle_changed: 2026-11-07
sources:
  - "bench-router session (2026-11-07)"
---

## Finding
- github.com/eliasstravik/herdr-projects now serves the shepherdr repo (same page content; redirect not confirmed).
- shepherdr 3.x (3.1.14, 2026-11-06): layout for the Herdr desktop app, installed via `git clone` + `./install.sh`; CHANGELOG 3.0.0 says herdr-plugin.toml "is gone from main", so `herdr plugin install eliasstravik/herdr-projects` likely no longer works for new installs/updates (not run to verify).
- CLIs documented: `shepherdr` (install|update|uninstall|doctor|web|stop), `herdr-task` (ready/fix/resume/autopilot). No documented `herdr-projects`, `models KIND`, `details`, `worker.access`. Data dir is `~/.herdr/`, 2.x data not migrated.
- Local install stays functional: herdr-projects 1.2.26 pinned at a6787e1 (`herdr plugin list`).
- bench-router couplings: `PROJECTS_BIN`/version regex in bench_router/herdr.py, install lines in README.md and docs/projects.md, fake versions in test_p2/test_coordination.
- Marketplace (GitHub topic `herdr-plugin`, 2066 repos; herdr.dev/plugins is JS-rendered) candidates: smarzban/tsk (task board, CLI for agents), nelsonPires5/herdr-board, aemrebarut/herdr-dagr, nidhi-singh02/agent-router. Unverified against bench-router's needed API.
- Gotcha: `gh` not installed on this machine; antigravity delegation via bench-router needs the multi-stage vendor decision flow before `route`.
