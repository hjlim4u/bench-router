---
title: >-
  herdr-projects renamed to shepherdr: platform transition to herdr-app layout and herdr-task CLI
category: projects
tags: [herdr, herdr-projects, shepherdr, plugin, migration]
summary: >-
  shepherdr 3.x keeps the board+worktree+review concept but ships as a herdr-app layout (install.sh), not a herdr plugin; bench-router maintains 1.2.x pinning.
project: bench-router
base_confidence: 0.6
provenance:
  extracted: 0.7
  inferred: 0.3
lifecycle: draft
lifecycle_changed: 2026-11-07
created: 2026-11-07T00:00:00Z
updated: 2026-11-10T00:30:00Z
sources:
  - "bench-router session (2026-11-07)"
snapshots:
  - "[[_raw/_archived/2026-11-07-shepherdr-rename-herdr-projects|2026-11-07-shepherdr-rename-herdr-projects]]"
---

# herdr-projects renamed to shepherdr: platform transition

## Overview

The `eliasstravik/herdr-projects` repository was renamed to `eliasstravik/shepherdr`. With Shepherdr 3.x, the software transitioned from a TUI plugin (`herdr-plugin.toml`) to a native layout for the Herdr desktop app (`herdr-app`).

## Impact on bench-router

1. **Repository & Manifest Changes:**
   - Shepherdr 3.x dropped `herdr-plugin.toml` from its `main` branch. A naive `herdr plugin install eliasstravik/herdr-projects` fails with `os error 2`.
   - The CLI surface changed from `herdr-projects` to `herdr-task` and `shepherdr`.
2. **Compatibility Strategy:**
   - `bench-router` pins to the 1.x / 1.2.27 branch where the TUI plugin contract and `herdr-projects` binary remain intact.
   - Reinstallation requires pinning `--ref v1.2.27` (`herdr plugin install eliasstravik/shepherdr --ref v1.2.27`).

## Sources

- [[_raw/_archived/2026-11-07-shepherdr-rename-herdr-projects]]
