---
title: >-
  CodexBar (steipete) — usage limits and local cost CLI
category: references
tags: [source, quota, cost-tracking]
sources:
  - "url:https://github.com/steipete/codexbar"
  - "url:https://github.com/steipete/codexbar/blob/main/docs/cli.md"
  - "url:https://github.com/steipete/codexbar/blob/main/docs/antigravity.md"
  - "url:https://github.com/steipete/codexbar/blob/main/docs/claude.md"
  - "url:https://github.com/steipete/codexbar/blob/main/Integrations/Linux/README.md"
source_url: "https://github.com/steipete/codexbar"
created: 2026-11-08T15:19:13Z
updated: 2026-11-08T15:19:13Z
as_of: 2026-11-08
summary: >-
  macOS menu bar app plus Linux CLI. `codexbar usage --format json` gives quota windows including model-specific rows; `codexbar cost --format json` gives local token cost per day, model, and project.
provenance:
  extracted: 0.8
  inferred: 0.15
  ambiguous: 0.05
base_confidence: 0.57
lifecycle: draft
lifecycle_changed: 2026-11-08
---

# CodexBar

Repo: https://github.com/steipete/codexbar (docs via ctx7 `/steipete/codexbar`, 2026-11-08). Not installed or run on this machine.

## Key claims

- **Platforms.** macOS menu bar app, plus a Linux CLI and desktop client from GitHub release tarballs (checksum-verified installer to `~/.local/lib/codexbar-cli`), Homebrew, and AUR `codexbar-cli`. Browser cookie import is macOS-only. Linux uses OAuth, CLI, or manual cookies. ^[extracted]
- **`codexbar usage --format json|toon`** covers many providers (up to 3 fetched at once). It returns `rateWindowLabels`, `resetCredits`, and a provider-specific `usage.details` array. `--source auto|web|cli|oauth|api` selects the fetch path. ^[extracted]
- **Claude.** The OAuth path reads `~/.claude/.credentials.json` on Linux and calls `GET api.anthropic.com/api/oauth/usage?cedar_ember=1` (with fallback retry). In `ClaudeUsageSnapshot`, it maps `five_hour` → `primary` (session), `seven_day` → `secondary` (weekly), `seven_day_sonnet` / `seven_day_opus` → model-specific weekly windows, `limits[].weekly_scoped` → `extraRateWindows` (e.g., Fable 5 limits), and `extra_usage` → `providerCost` (`used`, `limit`, `currency`, `balance` in USD for monthly Extra Usage / Usage Credits). It needs the `user:profile` scope. ^[extracted]
- **Antigravity.** Source order in `auto`: Antigravity app → `agy` CLI (`agy -p /usage --output-format json` or CLI HTTPS) → IDE language-server probe (`GetUserStatus`, `GetAvailableModels`, `GetCascadeModelConfigData`) → Google OAuth remote fallback (`cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary` and `retrieveUserQuota`). The IDE fallback has session bars but no weekly grouping. ^[extracted]
- **Codex.** Uses the local Codex RPC/PTY (CLI) or OAuth (`snapshot.primary` 300m, `snapshot.secondary` 10080m, `snapshot.extraRateWindows` for model-specific limits), plus an optional OpenAI web dashboard for credits. ^[extracted]
- **`codexbar cost --format json`** scans local Claude and Codex logs and supported local Antigravity, Cursor, Pi, and Muse Code history. It supports `--provider <id|all>`, `--group-by project|session`, `--days <N>`, `--breakdown`, and `--refresh`. ^[extracted]
- **`codexbar serve`** runs a loopback HTTP server with usage/cost JSON and a web UI (default port 8080). A dashboard snapshot needs a token. ^[extracted]

## Fit against CodeBurn

It covers `quota` (with model-scoped rows), `models`-like discovery (partly), `export`-like cost JSON, and `web`. Project breakdown is Codex-only, so Claude per-project overview is weaker than `codeburn overview --project`. ^[inferred]

## Limitations

- It reads credential files, Keychain items, and cookies. Review it before granting access. ^[inferred]
- Linux provider coverage is narrower than macOS and was not tested here. ^[ambiguous]

## Related

- [[references/sources/antigravity-cli-usage]]
- [[references/sources/claude-code-usage-reporting]]
- [[references/sources/local-token-cost-trackers]]
- [[concepts/quota-scopes]]
- [[synthesis/research-per-model-quota-codeburn-replacement]]
