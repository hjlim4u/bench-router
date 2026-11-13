---
title: >-
  Google Gemini thinking by workload
category: references
tags: [source, reasoning, agentic]
sources: ["url:https://ai.google.dev/gemini-api/docs/thinking"]
created: 2026-10-19T01:52:29Z
updated: 2026-11-13T03:08:44Z
as_of: 2026-11-13
summary: >-
  Model-specific thinking defaults and levels, Hydrogen high starting guidance, conditional xhigh and output-budget constraints.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-google-gemini-thinking|2026-10-19-google-gemini-thinking]]"
  - "[[_raw/_archived/2026-11-13-google-gemini-thinking|2026-11-13-google-gemini-thinking]]"
---

# Google Gemini thinking by workload

The official guide describes dynamic thinking that adjusts reasoning to request complexity, with a configurable `thinking_level`.

## Documented workload guidance

| Workload | Starting advice, paraphrased |
|---|---|
| Fact lookup or classification | Use `minimal` or `low`, where supported |
| Concept comparison or ordinary creative reasoning | Use the model's default |
| Advanced coding, mathematics, or multistep planning | Use the highest supported thinking level |

## Dated configuration examples

| Model | Default | Supported levels |
|---|---|---|
| Gemini 4 Argon | `medium` | `low`, `medium`, `high` |
| Gemini 3.8 Flash | `medium` | `low`, `medium`, `high` |
| Gemini 3.5 Flash-Lite | `minimal` | `minimal`, `low`, `medium`, `high` |
| Gemini 3.1 Pro preview | `high` | `low`, `medium`, `high` |

## Limits

These values were checked on 2026-10-19. Maximum thinking means the selected model's supported maximum, not a universal `max` parameter. Thinking uses billable tokens; output limits include both thinking and response tokens. Dynamic thinking adjusts within a model; it does not itself select another provider or model.

## Related

- [[references/sources/google-gemini-models]]
- [[concepts/model-effort-selection]]
- [[concepts/facets/difficulty]]

## Current guidance — checked 2026-11-13

Carbon and Argon default to medium and support low, medium and high. Hydrogen defaults to high and supports low, medium, high and xhigh. For complex work, start at high. Reserve Hydrogen xhigh for hard multistep coding and agentic problems where high falls short and additional latency and tokens are acceptable. Do not map advanced work unconditionally to the maximum supported level. Evaluate all four Hydrogen levels with enough output budget and keep the lowest meeting the quality bar. Minimal is not supported by Gemini 4 or 3.8 Flash. Output budgets include thinking; an exhausted budget can produce truncated or empty output. Long decode beyond 65,536 requires background execution or continuation under the documented API conditions. Earlier supported-model rows remain valid dated records, not a complete current catalog.

Related: [[concepts/model-effort-selection]], [[synthesis/vendor-guided-model-selection]].

## Sources

- [[_raw/_archived/2026-10-19-google-gemini-thinking]] — bounded original excerpt and canonical origin; page update date differs from access date.

- [[_raw/_archived/2026-11-13-google-gemini-thinking]] — 2026-11-13 capture; extraction limitations are recorded in its frontmatter.
