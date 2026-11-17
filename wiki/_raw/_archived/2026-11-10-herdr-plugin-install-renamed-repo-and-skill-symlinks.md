---
title: "Installing herdr-projects after the Shepherdr rename, herdr-app, and npx skills symlinks"
category: skills
tags:
  - topic/herdr
  - herdr-projects
  - shepherdr
  - bench-router
summary: "How to reinstall the herdr-projects TUI plugin from the renamed Shepherdr repo, install herdr-app safely, and keep symlinked skill files that npx skills now skips."
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
  extracted: 0.9
  inferred: 0.1
sources:
  - "bench-router session (2026-11-09)"
---

## `herdr plugin install eliasstravik/herdr-projects` fails with ENOENT

**Problem:** The install prints only `No such file or directory (os error 2)`, even with `--yes` and debug logging.

**Root cause:** The GitHub repo was renamed to `eliasstravik/shepherdr` (HTTP 301), and its HEAD no longer has a `herdr-plugin.toml`; Shepherdr 3.x is a herdr-app add-on, not a TUI plugin.

**Fix:**
```bash
# ❌ before
herdr plugin install eliasstravik/herdr-projects --yes
# ✅ after: the last tag still named "Projects" (1.x board contract)
herdr plugin install eliasstravik/shepherdr --ref v1.2.27 --yes
herdr-projects install   # rewrites the launcher ~/.herdr-projects/data/bin/herdr-projects
herdr-projects doctor
```

**Confirmed by:** `herdr-projects version` → 1.2.27; `doctor` checks pass for the program, launcher and plugin.

**Notes:** `v2.x` keeps plugin id `herdr-projects` but is named Shepherdr (transitional). After a reinstall, the old launcher keeps pointing at the deleted checkout until `herdr-projects install` runs.

## Installing herdr-app next to an existing herdr-core

**Behavior:** `https://releases.herdr.dev/app/install.sh` installs the app into `~/.local/share/herdr-app`, links `~/.local/bin/herdr-app`, verifies the tarball sha256, and installs herdr-core only when no `herdr-core` exists.

**Workaround / Pattern:** Download and read the script, then run the saved copy. An existing `~/.local/bin/herdr-core` (and its `hc` link) is left alone. Shepherdr needs herdr-app ≥ 0.1.12 and hc ≥ 0.1.17; Shepherdr also runs web-only on herdr-core without the app.

## `npx skills add` drops symlinks that leave the skill folder

**Behavior:** Reinstalling the bench-router skill warns `Skipping symlink that points outside the skill directory` and the installed `references/agents/{antigravity.md,claude.md,codex.toml}` disappear (they are symlinks to the repo's `.agents/`, `.claude/`, `.codex/` bench-decider definitions).

**Fix:** Copy them resolved after the install, in `mise.toml` `install-skill`:
```bash
npx -y skills add "$PWD" -g -a claude-code codex antigravity -y
cp -L skills/bench-router/references/agents/* ~/.agents/skills/bench-router/references/agents/
```

**Confirmed by:** Rerunning `mise run install-skill` keeps all three files (commit be67d43).
