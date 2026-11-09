---
title: >-
  Claude Code usage reporting: /usage, SDKUsageReport, status line rate_limits, Fable usage credits
category: references
tags: [source, quota, claude]
sources:
  - "url:https://code.claude.com/docs/en/costs"
  - "url:https://code.claude.com/docs/en/model-config"
  - "url:https://code.claude.com/docs/en/statusline"
  - "url:https://code.claude.com/docs/en/agent-sdk/typescript"
source_url: "https://code.claude.com/docs/en/agent-sdk/typescript"
created: 2026-11-08T15:19:13Z
updated: 2026-11-08T15:19:13Z
as_of: 2026-11-08
summary: >-
  Claude Code exposes plan limit rows (session, weekly_all, weekly_scoped per model) and usage-credit state (extra_usage) through `/usage`. Fable on Pro bills to usage credits.
provenance:
  extracted: 0.85
  inferred: 0.1
  ambiguous: 0.05
base_confidence: 0.67
lifecycle: draft
lifecycle_changed: 2026-11-08
---

# Claude Code usage reporting

Docs: https://code.claude.com/docs/en/costs, /model-config, /statusline, /agent-sdk/typescript (fetched with ctx7, 2026-11-08).

## Key claims

- **Fable and usage credits.** "Depending on your plan and seat tier, Fable usage can bill to usage credits instead of drawing on your plan's included limits." The `/model` picker then shows "Requires usage credits". A one-time consent prompt is shown before Claude Code continues on Fable. ^[extracted]
- "Extra usage" was renamed "usage credits" (`/extra-usage` → `/usage-credits`, 2026-W21). It needs claude.ai subscription login, not an API key. ^[extracted]
- `/usage` shows a usage-credits row while credits are on. On Pro and Max it shows the month's spend against the monthly spend limit, or `Unlimited` when no limit is set. ^[extracted]
- **SDKUsageReport** (Agent SDK v0.3.273+, experimental) is the structured `/usage` result, carried as `usage_report` on the assistant message. ^[extracted]
  - `rate_limits.limits[]`: `kind` (`session`, `weekly_all`, `weekly_scoped`), `group`, `percent` (used, 0–100), `resets_at`, `scope.model.display_name` for model-scoped rows, `severity`, `is_active`. The docs say: "Classify a row on this [`kind`], never on a label." ^[extracted]
  - `rate_limits.extra_usage`: `is_enabled`, `monthly_limit` and `used_credits` (minor units, cents), `utilization`, `currency`. `is_enabled: false` means "usage credits can't pay for requests". ^[extracted]
  - `rate_limits` is `null` when the OAuth token lacks the `user:profile` scope. ^[extracted]
  - `session.model_usage` gives per-model tokens and a locally computed cost estimate. ^[extracted]
- **Headless retrieval works.** `claude -p /usage --output-format stream-json --verbose < /dev/null` returned the `usage_report` with 0 tokens and `local_command: usage` (Claude Code 2.1.319, Pro account, 2026-11-08). The observed rows were `session` 7% and `weekly_all` 50%. `extra_usage` came back with `is_enabled: false`, `monthly_limit: 2000`, `currency: USD`. ^[extracted]
- **Status line JSON** has `rate_limits.five_hour` and `rate_limits.seven_day` (`used_percentage`, `resets_at` epoch seconds) and `spend_limit` behind a gateway. It has no model-scoped rows and no usage-credit state. ^[extracted]

## Implication for bench-router

A Fable profile on Pro is runnable only when `extra_usage.is_enabled` is true and utilization is below the limit. The plan's 5h and weekly windows do not decide it. `weekly_scoped` rows cover the other model-specific limits. This is the "model-specific paid-credit eligibility" that `docs/reference.md` says CodeBurn checks cannot establish. ^[inferred]

## Limitations

- The type is marked experimental, so its shape may change. ^[extracted]
- The docs do not say whether `/usage` costs plan quota. The observed run reported 0 tokens and 0 cost. ^[inferred]
- No `weekly_scoped` row appeared on this account, so the `scope.model` shape is checked against the docs only. ^[ambiguous]

## Related

- [[concepts/quota-scopes]]
- [[synthesis/research-per-model-quota-codeburn-replacement]]
- [[references/sources/codexbar]] (its Claude OAuth path maps `weekly_scoped`, `seven_day_opus`, `seven_day_sonnet`)
