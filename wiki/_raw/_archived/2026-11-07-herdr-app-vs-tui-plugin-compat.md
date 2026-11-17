---
title: >-
  Herdr desktop app (herdr-app) does not run herdr-plugin.toml plugins: TUI plugin compatibility
tags: [herdr, herdr-app, plugin, compatibility]
summary: >-
  herdr-app (hc/herdr-core runtime, layouts+JS mods) is separate from the herdr 0.9.5 TUI plugin system; of Ovis, reviewr, herdr-projects only Ovis has app support.
project: bench-router
base_confidence: 0.65
provenance:
  extracted: 0.7
  inferred: 0.3
lifecycle_changed: 2026-11-07
sources:
  - "bench-router session (2026-11-07)"
---

## Gotcha: "herdr native app" is herdr-app, not the TUI

**Behavior:** herdr.dev docs (llms.txt, stable 0.9.5) describe only the TUI and say nothing about a desktop app, so a docs-only search wrongly concludes no app exists. The desktop app is a separate repo, `herdrdev/herdr-app` (default branch `master`, README 0.1.12+ per shepherdr), running on herdr-core (`hc`), not the TUI server.

**Explanation:** herdr-app is extended by *layouts* and *mods* (JavaScript, docs/mods.md, trusted code), not by `herdr-plugin.toml` (`herdr plugin install`). So TUI plugins are not app-native. Wrong first answer in this session came from reading only herdr.dev docs.

**Per installed plugin (README-level check, nothing executed):**
- `devswha.ovis` 0.4.13: ships its own desktop app and can show Herdr app terminals via `hc` (`OVIS_RUNTIME=herdr-core`; checked with hc 0.1.14/0.1.17). Client support, not a mod.
- `persiyanov.reviewr` 0.48.0: README has no herdr-core/app mention; treat as TUI-only. ^[inferred]
- `herdr-projects` 1.2.26: TUI plugin (linux/macos). Successor shepherdr 3.x is the herdr-app layout. See [[2026-11-07-shepherdr-rename-herdr-projects]].

**Confirmed by:** README/docs reading only; not run against herdr-app.
