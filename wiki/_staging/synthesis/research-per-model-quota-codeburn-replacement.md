---
title: >-
  Research: Per-model quota visibility and CodeBurn replacement
category: synthesis
tags: [quota, cost-tracking, claude, codex, antigravity, research]
sources:
  - "[[references/sources/antigravity-cli-usage]]"
  - "[[references/sources/claude-code-usage-reporting]]"
  - "[[references/sources/codex-app-server-rate-limits]]"
  - "[[references/sources/codexbar]]"
  - "[[references/sources/local-token-cost-trackers]]"
created: 2026-11-08T15:19:13Z
updated: 2026-11-08T15:19:13Z
summary: >-
  Synthesis of 3-round research on per-model quota tools. All three vendor CLIs expose model-level quota as JSON; CodexBar is the closest single-tool CodeBurn replacement.
provenance:
  extracted: 0.6
  inferred: 0.35
  ambiguous: 0.05
base_confidence: 0.79
lifecycle: draft
lifecycle_changed: 2026-11-08
---

# Research: Per-model quota visibility and CodeBurn replacement

## Overview

bench-router uses CodeBurn 0.9.27 for `quota --format json` (availability preflight), `models --format json` (profile discovery), and status/overview/export/web/antigravity-hook (`eval/codeburn.py`). Source inspection of CodeBurn 0.9.27 (`src/quota/antigravity.ts`, `src/quota/claude.ts`) shows two concrete gaps:
1. For Antigravity, CodeBurn only probes already-running local language-server TCP ports (`ps` + `lsof`) and has no `agy -p /usage` or Google OAuth fallback, so headless runs report `available: false`.
2. For Claude, CodeBurn parses `five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet`, and `limits[]` (`weekly_scoped`) from `GET api.anthropic.com/api/oauth/usage`, but drops `data.extra_usage` (`is_enabled`, `monthly_limit`, `used_credits`, `utilization`), which governs Fable on Claude Pro.

Each vendor's own CLI exposes the narrower scopes headlessly, as JSON, at zero tokens. Among third-party tools, **CodexBar** (`steipete/codexbar`) and **Tokscale** (`junhoyeo/tokscale`) combine multi-agent token-cost tracking with live quota commands (`codexbar usage --format json` / `codexbar cost --format json`, `tokscale usage --json`), while **ccusage** (`ccusage/ccusage`) covers per-project token cost and **`antigravity-usage`** (`skainguyen1412/antigravity-usage`) covers standalone Antigravity local/OAuth per-model quotas.

## Key Findings

- **Antigravity:** `agy -p /usage --output-format json` returns per-model-group buckets (weekly, 5h) with `remaining_fraction` (`Gemini Models`, `Claude and GPT models`, and a separate `Gemini 4 Argon` weekly pool on Pro). Verified on agy 1.5.3. Local language servers also expose per-model `clientModelConfigs[].quotaInfo.remainingFraction` via `GetUserStatus`. [[references/sources/antigravity-cli-usage]]
- **Claude:** `claude -p /usage --output-format stream-json --verbose < /dev/null` returns `usage_report.rate_limits` with `session`, `weekly_all`, and model-scoped `weekly_scoped` rows, plus `extra_usage` (usage credits: `is_enabled`, `monthly_limit`, `used_credits`, `utilization`). Fable on Pro requires `extra_usage.is_enabled` and remaining credit headroom. Verified on 2.1.319, where it showed `is_enabled: false`. [[references/sources/claude-code-usage-reporting]]
- **Codex:** `codex app-server` → `account/rateLimits/read` returns windows, `rateLimitsByLimitId` (with `normalModelSlug`), credits, reset credits, and `ordinaryUsageAllowed`. Verified on 0.167.0. [[references/sources/codex-app-server-rate-limits]]
- **CodexBar (`steipete/codexbar`):** Provides a Linux/macOS CLI (`codexbar`) with `codexbar usage --format json|toon` (mapping Claude `five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet`, `limits[].weekly_scoped` → `extraRateWindows`, and `extra_usage` → `providerCost`; Antigravity via local app → `agy` CLI → IDE probe → Google OAuth `cloudcode-pa.googleapis.com`), `codexbar cost --format json` (`--provider`, `--group-by project|session`, `--days`, `--breakdown`), and `codexbar serve`. It is the closest single-tool replacement for CodeBurn. [[references/sources/codexbar]]
- **Tokscale (`junhoyeo/tokscale`), ccusage (`ccusage/ccusage`), and `antigravity-usage`:** Tokscale (Rust CLI/TUI) parses 40+ agents' local logs (`tokscale --json`) and also fetches live provider quotas (`tokscale usage --json`, `tokscale codex status --json`), though its `tokscale antigravity sync` requires a running editor language server. `ccusage` (`npx ccusage@latest`) provides `--json --instances --project <name>` cost reports for Claude Code, Codex, Gemini CLI, Pi, and OpenClaw, but does not query live quota APIs and does not support Antigravity CLI. `skainguyen1412/antigravity-usage` (`antigravity-usage --json --all-models`) provides standalone Antigravity per-model quota checks with both `--method local` and `--method google` OAuth fallback. [[references/sources/local-token-cost-trackers]]

## Replacement map

| CodeBurn feature (bench-router use) | Per-model replacement | Notes |
|---|---|---|
| `quota --format json` (`probe_profiles`) | **Option A (Zero-dep native CLIs):** `agy -p /usage --output-format json`, `claude -p /usage --output-format stream-json --verbose`, `codex app-server` (`account/rateLimits/read`) | Official CLIs already installed; exposes Antigravity model groups (`Gemini Models`, `Claude and GPT models`, `Gemini 4 Argon`), Claude `weekly_scoped` + `extra_usage` (Fable on Pro), and Codex `rateLimitsByLimitId`. |
| `quota --format json` (Single unified CLI) | **Option B (`codexbar`):** `codexbar usage --format json` (or `tokscale usage --json` + `agy -p /usage`) | `codexbar` normalizes Claude (`extraRateWindows` + `providerCost` for `extra_usage`), Codex, and Antigravity (including `agy` CLI and OAuth fallback) into one JSON contract. |
| `models --format json` (`discover_profiles`) | `agy models`, Codex `~/.codex/models_cache.json`, Claude vendor guidelines (plus `codexbar cost` / `tokscale --json` for observed models) | `herdr.py` already implements `agy models`, `codex_models()`, and `claude_models` fallback. |
| `status` / `overview --project` / `export -f json` (`eval/codeburn.py`) | `codexbar cost --format json --group-by project`, `tokscale --json --client claude,codex`, or `ccusage daily/monthly --json --instances --project <name>` | `codexbar cost` covers Claude, Codex, Antigravity, Cursor, and Pi; `ccusage` has strong `--project` filtering for Claude/Codex; `tokscale` covers 40+ agents. |
| `web` / `doctor` / `antigravity-hook` | `codexbar serve` (web), `tokscale antigravity status/sync` or `antigravity-usage doctor` | `codexbar cost` reads local Antigravity logs directly without a CLI wrapper hook. |

## Recommendation

1. **For live routing preflight (`bench_router/herdr.py` `probe_profiles`):** Query the **native vendor CLIs** (`agy -p /usage --output-format json`, `claude -p /usage --output-format stream-json --verbose`, `codex app-server`) directly, or adopt **`codexbar usage --format json`**. Native CLIs require zero extra dependencies and directly expose Antigravity model-group buckets and Claude Pro's `extra_usage.is_enabled` / `utilization` for Fable.
2. **For full CodeBurn replacement (quota + local token/cost analytics in `eval/`):** **`CodexBar` (`steipete/codexbar`)** is the strongest single-binary replacement on Linux and macOS (`codexbar usage --format json` + `codexbar cost --format json --group-by project`), optionally paired with **`Tokscale` (`junhoyeo/tokscale`)** or **`ccusage`** for multi-agent historical token analytics. ^[inferred]

## Core Concepts

- [[concepts/quota-scopes]]: provider window vs model group vs model-scoped row vs credit-billed model.

## Entities & Tools

The vault keeps `entities/` for benchmarks only, so tools are documented on source pages: [[references/sources/codexbar]], [[references/sources/local-token-cost-trackers]] (CodeBurn, Tokscale, ccusage, `antigravity-usage`). Other tools surfaced during research: `Maciek-roboblog/Claude-Code-Usage-Monitor` (Claude-only Rich TUI), `tanaikech/antigravity-cli-check-usage-plugin` (Antigravity CLI hook), `tungcorn/antigravity-usage-checker` (Go CLI for local Antigravity API), and `gundamkid/anti-gravity-quota`.

## Contradictions & Open Questions

- A community Antigravity skill describes separate Gemini Pro and Flash pools. The live `agy /usage` report groups them together (`Gemini Models`), while separating `Gemini 4 Argon` on Pro. The live report is authoritative.
- CodeBurn 0.9.27 includes `src/quota/antigravity.ts` and `src/quota/claude.ts`, but its Antigravity adapter only probes active local language-server ports via `lsof` (returning `available: false` when no server is running) and its Claude adapter drops `extra_usage` from `api/oauth/usage`.
- The `weekly_scoped` and `rateLimitsByLimitId` model shapes are confirmed from docs, CodeBurn/CodexBar source mappings, or a single observation. No scoped row appeared on these accounts.
- Whether `claude -p /usage` uses plan quota is undocumented. The observed run reported 0 tokens.

## Sources Consulted

- [[references/sources/antigravity-cli-usage]]
- [[references/sources/claude-code-usage-reporting]]
- [[references/sources/codex-app-server-rate-limits]]
- [[references/sources/codexbar]]
- [[references/sources/local-token-cost-trackers]]
