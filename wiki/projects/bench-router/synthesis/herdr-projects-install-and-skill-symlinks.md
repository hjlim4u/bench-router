---
title: >-
  Installing herdr-projects post-rename, herdr-app coexistence, and npx skills symlinks
category: projects
tags: [herdr, herdr-projects, shepherdr, skills, symlinks, mise]
summary: >-
  How to reinstall herdr-projects 1.2.27 from renamed Shepherdr repo, install herdr-app alongside herdr-core, and resolve npx skills symlink drops.
project: bench-router
base_confidence: 0.85
provenance:
  extracted: 0.9
  inferred: 0.1
lifecycle: draft
lifecycle_changed: 2026-11-10
created: 2026-11-10T00:00:00Z
updated: 2026-11-10T00:30:00Z
sources:
  - "bench-router session (2026-11-09)"
snapshots:
  - "[[_raw/_archived/2026-11-10-herdr-plugin-install-renamed-repo-and-skill-symlinks|2026-11-10-herdr-plugin-install-renamed-repo-and-skill-symlinks]]"
---

# Installing herdr-projects post-rename, herdr-app coexistence, and npx skills symlinks

## 1. Reinstalling herdr-projects TUI Plugin

Due to the repository rename to `eliasstravik/shepherdr` and removal of `herdr-plugin.toml` from HEAD:
```bash
herdr plugin install eliasstravik/shepherdr --ref v1.2.27 --yes
herdr-projects install
herdr-projects doctor
```

## 2. Installing herdr-app with Existing herdr-core

- Download and inspect `https://releases.herdr.dev/app/install.sh`.
- Installs the app into `~/.local/share/herdr-app` and links `~/.local/bin/herdr-app`.
- Existing `~/.local/bin/herdr-core` (`hc`) is preserved.

## 3. Resolving `npx skills add` Symlink Drops

- `npx -y skills add "$PWD" -g -a claude-code codex antigravity -y` skips out-of-tree symlinks (`references/agents/{antigravity.md,claude.md,codex.toml}`).
- **Fix:** In `mise.toml` `install-skill`, copy them resolved immediately after installation:
  ```bash
  cp -L skills/bench-router/references/agents/* ~/.agents/skills/bench-router/references/agents/
  ```

## Sources

- [[_raw/_archived/2026-11-10-herdr-plugin-install-renamed-repo-and-skill-symlinks]]
