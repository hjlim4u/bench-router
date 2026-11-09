---
title: >-
  Quota scopes: provider window, model group, model-scoped row, credit-billed model
category: concepts
tags: [quota, agentic]
sources:
  - "[[references/sources/antigravity-cli-usage]]"
  - "[[references/sources/claude-code-usage-reporting]]"
  - "[[references/sources/codex-app-server-rate-limits]]"
created: 2026-11-08T15:19:13Z
updated: 2026-11-08T15:19:13Z
summary: >-
  Subscription quota is reported at four scopes. Availability for a profile must be judged at the narrowest scope that covers its model.
provenance:
  extracted: 0.6
  inferred: 0.35
  ambiguous: 0.05
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-11-08
---

# Quota scopes

Subscription coding agents report remaining capacity at different scopes. The scope decides which profiles a given meter can exclude.

| Scope | Example | Where reported |
|---|---|---|
| Provider window | Claude `session` / `weekly_all`; Codex primary 300 min / secondary 10080 min | All three vendor CLIs; CodeBurn `quota` |
| Model group | Antigravity `Gemini Models`, `Claude and GPT models`, `Gemini 4 Argon` | `agy -p /usage` ([[references/sources/antigravity-cli-usage]]) |
| Model-scoped row | Claude `weekly_scoped` with `scope.model`; Codex `rateLimitsByLimitId[*].normalModelSlug` | [[references/sources/claude-code-usage-reporting]], [[references/sources/codex-app-server-rate-limits]] |
| Credit-billed model | Fable on Claude Pro bills to usage credits (`extra_usage.is_enabled`, utilization) | [[references/sources/claude-code-usage-reporting]] |

## Rules

- A profile is exhausted when **any** meter that covers its model is exhausted: the provider window, its group, or its scoped row. A credit-billed model depends on credit state instead of plan windows. ^[inferred]
- Do not mark a profile exhausted from another model's meter. CodeBurn exposes no model mapping, so bench-router's probe excludes a profile only when *all* windows are at 100% (see the all-window comment in `bench_router/herdr.py` `probe_profiles`). ^[extracted]
- Directions differ. Antigravity reports `remaining_fraction`, while Claude and Codex report used percent. ^[extracted]

## Related

- [[concepts/model-effort-selection]] (feasibility constraints are separate from quality)
- [[synthesis/research-per-model-quota-codeburn-replacement]]
