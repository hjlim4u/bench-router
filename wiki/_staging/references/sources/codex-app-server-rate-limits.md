---
title: >-
  Codex app-server account/rateLimits/read
category: references
tags: [source, quota, codex]
sources:
  - "url:https://github.com/openai/codex/pull/5302"
  - "url:https://github.com/openai/codex/tree/main/codex-rs/app-server"
source_url: "https://github.com/openai/codex/tree/main/codex-rs/app-server"
created: 2026-11-08T15:19:13Z
updated: 2026-11-08T15:19:13Z
as_of: 2026-11-08
summary: >-
  `codex app-server` JSON-RPC `account/rateLimits/read` returns 5h/weekly windows, per-limit-id snapshots with an optional model slug, credits, and reset credits.
provenance:
  extracted: 0.75
  inferred: 0.15
  ambiguous: 0.1
base_confidence: 0.57
lifecycle: draft
lifecycle_changed: 2026-11-08
---

# Codex app-server account/rateLimits/read

Source: openai/codex app-server (rate-limit read API added in PR #5302). The schema below comes from a live call, not from the README.

## Key claims

- Send `initialize`, then `initialized`, then `{"method":"account/rateLimits/read"}` over stdio to `codex app-server`. Sources report empty replies when the read goes out before the handshake settles. A 1 s wait worked. ^[extracted]
- Live result (codex-cli 0.167.0, Plus, 2026-11-08): `rateLimits.primary` (`usedPercent`, `windowDurationMins: 300`, `resetsAt` epoch s), `secondary` (10080 min), `credits` (`hasCredits`, `unlimited`, `balance`), `planType`, `spendControlReached`, `rateLimitReachedType`. ^[extracted]
- `rateLimitsByLimitId` maps each limit id to the same snapshot shape plus `limitName` and `normalModelSlug`. Only `codex` appeared on this account. A model-specific limit (for example a separate pool for a fast model) is expected to show up as another key with a model slug set. ^[inferred]
- `rateLimitResetCredits.availableCount` and `credits[]` list banked full resets ("Full reset (Weekly + 5 hr)"). CodeBurn reports these as notes ("2 available · 0 usable now"). ^[extracted]
- `ordinaryUsageAllowed` is a direct boolean for whether ordinary use is allowed now. ^[extracted]
- An `account/rateLimits/updated` notification pushes changes without polling. ^[extracted]

## Limitations

- The reply carries `accountId`. Do not log or commit the raw reply. ^[inferred]
- No public schema doc for `rateLimitsByLimitId` was found. The field names come from one observation. ^[ambiguous]

## Related

- [[concepts/quota-scopes]]
- [[synthesis/research-per-model-quota-codeburn-replacement]]
