---
title: >-
  Herdr desktop app (herdr-app) and TUI plugin compatibility
category: projects
tags: [herdr, herdr-app, plugin, compatibility, bench-router]
summary: >-
  herdr-app (hc/herdr-core runtime, layouts+JS mods) is separate from the herdr 0.9.5 TUI plugin system; of Ovis, reviewr, herdr-projects only Ovis has app support.
project: bench-router
base_confidence: 0.65
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
  - "[[_raw/_archived/2026-11-07-herdr-app-vs-tui-plugin-compat|2026-11-07-herdr-app-vs-tui-plugin-compat]]"
---

# Herdr desktop app (herdr-app) and TUI plugin compatibility

## Gotcha: "herdr native app" is herdr-app, not the TUI

- **Behavior:** `herdr.dev` documentation (stable 0.9.5) describes only the TUI and says nothing about a desktop app, which led early investigations to wrongly conclude no native app exists. The desktop app is in a separate repository (`herdrdev/herdr-app`, running on `herdr-core` / `hc`), distinct from the TUI server.
- **Architectural Separation:** `herdr-app` is extended through **layouts** and **mods** (JavaScript, trusted code), whereas the TUI uses `herdr-plugin.toml` (`herdr plugin install`). Consequently, TUI plugins are not app-native.
- **Per-Plugin Compatibility Status:**
  - `devswha.ovis` 0.4.13: Ships its own desktop app and connects to Herdr app terminals via `hc` (`OVIS_RUNTIME=herdr-core`).
  - `persiyanov.reviewr` 0.48.0: TUI-only; no `herdr-core` support. ^[inferred]
  - `herdr-projects` 1.2.26: TUI plugin (Linux/macOS). Successor `shepherdr` 3.x is a `herdr-app` layout.

## Sources

- [[_raw/_archived/2026-11-07-herdr-app-vs-tui-plugin-compat]]
