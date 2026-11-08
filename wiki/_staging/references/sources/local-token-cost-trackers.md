---
title: >-
  Local token-cost and quota trackers: CodeBurn, Tokscale, ccusage, and antigravity-usage
category: references
tags: [source, quota, cost-tracking]
sources:
  - "url:https://ccusage.com/guide"
  - "url:https://github.com/junhoyeo/tokscale"
  - "url:https://github.com/getagentseal/codeburn"
  - "url:https://github.com/skainguyen1412/antigravity-usage"
source_url: "https://ccusage.com/guide"
created: 2026-11-08T15:19:13Z
updated: 2026-11-08T15:20:39Z
as_of: 2026-11-08
summary: >-
  Comparison of CodeBurn (0.9.27), Tokscale (4.21.0), ccusage (20.0.48), and antigravity-usage across per-model quota visibility, usage credits, and local token-cost tracking.
provenance:
  extracted: 0.85
  inferred: 0.1
  ambiguous: 0.05
base_confidence: 0.67
lifecycle: draft
lifecycle_changed: 2026-11-08
---

# Local token-cost and quota trackers: CodeBurn, Tokscale, ccusage, and antigravity-usage

Docs via ctx7 (`/websites/ccusage_guide`, `/ccusage/ccusage`, `/junhoyeo/tokscale`, `/websites/deepwiki_getagentseal_codeburn`), 2026-11-08, plus local source inspection of CodeBurn 0.9.27 (`dist/main.js.map`).

## CodeBurn (`getagentseal/codeburn`)

- **Why Antigravity reports `available: false` in headless CLI use:** In `src/quota/antigravity.ts`, CodeBurn discovers only already-running `language_server` or `agy` processes via `ps -ax` and `lsof -nP -iTCP -sTCP:LISTEN` and posts Connect-RPC JSON to `127.0.0.1:<port>` (`RetrieveUserQuotaSummary` and `GetUserStatus`). It neither invokes `agy -p /usage --output-format json` nor implements a Google OAuth fallback (`// No Google OAuth fallback in v1`). When no local server process is listening at poll time, it returns `disconnected` (`available: false`).
- **Why Claude Pro Fable usage credits are missing:** In `src/quota/claude.ts` (`decodeClaudeUsage`), CodeBurn queries `https://api.anthropic.com/api/oauth/usage` and maps `five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet`, and `limits[]` (`kind === 'weekly_scoped'`, labeling rows `Weekly · <display_name>`), but omits `data.extra_usage` (`is_enabled`, `monthly_limit`, `used_credits`, `utilization`).

## Tokscale (`junhoyeo/tokscale`)

- **Local token & cost tracking:** Rust + OpenTUI CLI parsing 40+ coding agents' local session logs (`~/.claude/`, `~/.codex/`, Cursor, OpenCode, Gemini CLI, Hermes, OpenClaw). Supports `--client a,b`, `--week`, and `--json`.
- **Live subscription quota (`tokscale usage`):** Documented in `/junhoyeo/tokscale` (`README.md`): `tokscale usage`, `tokscale usage --json`, `tokscale usage --light`, and `tokscale codex status --json` fetch real-time subscription quotas and reset dates directly from vendor quota endpoints.
- **Antigravity sync:** `tokscale antigravity status` and `tokscale antigravity sync` discover running local Antigravity language servers over RPC and cache normalized JSONL artifacts; like CodeBurn, it requires a running editor/language server rather than invoking headless `agy -p /usage`.

## ccusage (`ccusage/ccusage`)

- **Local token & cost tracking:** Subcommands per agent (`ccusage daily|monthly|session|blocks`, `ccusage codex …`, `ccusage gemini …`, `ccusage pi …`, `ccusage openclaw …`), each supporting `--json`.
- **Project breakdown:** `--instances` groups by project and `--project <name>` filters to a single project, matching `codeburn overview --project`.
- **Quota & Antigravity limitations:** In `rust/crates/ccusage/src/blocks.rs`, `--token-limit max` computes the historical maximum tokens of past local blocks rather than querying provider quota APIs (`statusline` only reads local/session state). Furthermore, ccusage documents that "Antigravity CLI, Grok CLI, and Devin CLI are currently not supported."

## antigravity-usage (`skainguyen1412/antigravity-usage`)

- **Dedicated Antigravity per-model quota CLI:** Supports `antigravity-usage quota --json` and `--all-models`.
- **Dual connection modes:** `--method local` probes the local IDE/CLI language server (`GetUserStatus` / `RetrieveUserQuotaSummary`), while `--method google` (default fallback) authenticates via Google OAuth to fetch per-model/group quota when no local server is running. ^[extracted]

## Related

- [[references/sources/codexbar]]
- [[concepts/quota-scopes]]
- [[synthesis/research-per-model-quota-codeburn-replacement]]
