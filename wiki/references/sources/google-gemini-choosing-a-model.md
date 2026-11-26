---
title: >-
  Google AI Studio: Choosing a Gemini model
category: references
tags: [source, google, gemini-4, model-selection, effort]
sources:
  - "url:https://aistudio.google.com/docs/choosing-a-model.md"
  - "url:https://aistudio.google.com/docs/models/gemini-4-neon.md"
source_url: "https://aistudio.google.com/docs/choosing-a-model.md"
created: 2026-11-19T08:02:38Z
updated: 2026-11-26T00:32:19Z
as_of: 2026-11-26
summary: >-
  Official Google AI Studio model selection guide comparing Gemini 4 Carbon, Neon, Hydrogen, and 3.5 Flash-Lite, thinking levels, and multi-step model pairing.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.67
lifecycle: draft
lifecycle_changed: 2026-11-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-11-19-google-gemini-choosing-a-model|2026-11-19-google-gemini-choosing-a-model]]"
  - "[[_raw/_archived/2026-11-19-google-gemini-4-neon-model-page|2026-11-19-google-gemini-4-neon-model-page]]"
  - "[[_raw/_archived/2026-11-26-google-gemini-choosing-a-model|2026-11-26-google-gemini-choosing-a-model]]"
---

# Google AI Studio: Choosing a Gemini model

Google's official selection guide (`aistudio.google.com/docs/choosing-a-model.md`, checked 2026-11-19) recommends matching reasoning depth, response speed, and token price across four general-purpose models. ^[extracted]

## Model Comparison Table

| Model | Speed | Thinking levels | Price per 1M tokens (input / output) | Tier & Role |
|---|---|---|---|---|
| `gemini-4-carbon` | Deliberate | `low`, `medium` (default), `high` | $2.00 / $10.00 (intro thru Nov 30, 2026; $4.00 / $20.00 from Dec 1, 2026) | Hardest architecture, multi-file debugging, science, security audits; paid tier only |
| `gemini-4-neon` | Moderate | `low`, `medium`, `high` (default), `xhigh` | $3.00 / $15.00 | Complex high-frequency engineering, knowledge work, science; paid tier only |
| `gemini-4-hydrogen` | Fast | `low`, `medium`, `high` (default), `xhigh` | $1.50 / $7.50 | Default for everyday coding, interactive apps, parallel workers; free & paid tiers |
| `gemini-3.5-flash-lite` | Fastest | `minimal` (default), `low`, `medium`, `high` | $0.30 / $2.50 | High-volume extraction, translation, summarization, sub-second targets; free & paid tiers |

## Selection Guidance

- **Default to `gemini-4-hydrogen`**: Cuts fabricated claims by >5x vs Gemini 3.8 Flash by flagging missing context instead of guessing, and batches read/search tool calls in parallel. ^[extracted]
- **Escalate to `gemini-4-neon`**: Sits between Hydrogen and Carbon. Finishes faster with fewer output tokens than Carbon while handling harder reasoning than Hydrogen. Choose when Hydrogen is not enough and Carbon's extra verification is not required. ^[extracted]
- **Escalate to `gemini-4-carbon`**: Spends more thinking tokens per turn to test hypotheses, isolate root causes across repositories, and check fixes against tests. ^[extracted]
- **Pair models via Interactions API**: Because Carbon, Neon, and Hydrogen share the same request schema, 1M unified context window, and tools, workflows can pass `previous_interaction_id` from a planner (`gemini-4-carbon` or `gemini-4-neon`) to an executor (`gemini-4-hydrogen`). ^[extracted]
- **Specialized models**: `gemini-decision-1` for zero-output-token classification/routing/scoring, Nano Banana for images, Gemini Omni for video, and Gemini 3.8 Live for real-time voice. ^[extracted]

## Limits

Vendor selection guidance reflects Google's recommended defaults and pricing tiers as of 2026-11-26 (updated from 2026-11-19: Carbon's $2/$10 rate through 2026-11-30 is labeled promotional pricing, and Google AI Studio plan access is clarified — Hydrogen and Flash-Lite are free on all plans, Neon on AI Pro/Ultra, Carbon on AI Ultra, while Carbon and Neon require the paid API tier). It does not establish cross-provider rankings or local CLI quota availability.

## Sources

- [[_raw/_archived/2026-11-19-google-gemini-choosing-a-model]]
- [[_raw/_archived/2026-11-26-google-gemini-choosing-a-model]]

## Related

- [[references/google-gemini-4-neon]]
- [[references/sources/google-gemini-4-neon-release]]
- [[references/sources/google-gemini-models]]
- [[concepts/model-effort-selection]]
- [[synthesis/vendor-guided-model-selection]]
- [[synthesis/Research: Google Gemini 4 Neon]]
