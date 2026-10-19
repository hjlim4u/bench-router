---
title: >-
  Vendor-guided model selection — research map
category: synthesis
tags: [agentic, reasoning, coding]
sources:
  - "url:https://developers.openai.com/api/docs/guides/model-selection"
  - "url:https://platform.claude.com/docs/en/about-claude/models/choosing-a-model"
  - "url:https://platform.claude.com/docs/en/build-with-claude/effort"
  - "url:https://ai.google.dev/gemini-api/docs/models"
  - "url:https://ai.google.dev/gemini-api/docs/thinking"
  - "conversation:2026-10-19"
created: 2026-10-19T01:52:29Z
updated: 2026-10-19T01:52:29Z
as_of: 2026-10-19
summary: >-
  Entry point for official vendor guidance, the current bench-router policy audit, and a proposed approach to selecting model/effort configurations.
provenance:
  extracted: 0.6
  inferred: 0.4
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: core
snapshots:
  - "[[_raw/_archived/2026-10-19-openai-model-selection|2026-10-19-openai-model-selection]]"
  - "[[_raw/_archived/2026-10-19-anthropic-model-selection|2026-10-19-anthropic-model-selection]]"
  - "[[_raw/_archived/2026-10-19-anthropic-effort|2026-10-19-anthropic-effort]]"
  - "[[_raw/_archived/2026-10-19-google-gemini-models|2026-10-19-google-gemini-models]]"
  - "[[_raw/_archived/2026-10-19-google-gemini-thinking|2026-10-19-google-gemini-thinking]]"
  - "[[_raw/_archived/2026-10-19-routing-research-context|2026-10-19-routing-research-context]]"
---

# Vendor-guided model selection — research map

Official guidance supplies starting recommendations. Bench-router's existing numeric policy and a proposed replacement have different evidence and status.

## Read by question

| Question | Owner page |
|---|---|
| Which official OpenAI model/effort combinations were found? | [[references/sources/openai-model-selection]] |
| How does Anthropic choose a starting model? | [[references/sources/anthropic-model-selection]] |
| How does Claude effort depend on the model? | [[references/sources/anthropic-effort]] |
| How does Google position Gemini models? | [[references/sources/google-gemini-models]] |
| Which thinking level fits a Gemini workload? | [[references/sources/google-gemini-thinking]] |
| Why separate model and effort decisions? | [[concepts/model-effort-selection]] |
| What does bench-router currently calculate? | [[projects/bench-router/synthesis/routing-selection-audit]] |
| How could the findings inform routing? | [[projects/bench-router/synthesis/vendor-guided-routing-proposal]] |

## Findings

The inspected OpenAI guide offers workload/configuration examples. Anthropic separates model choice from model-specific effort tuning. Google documents model roles and workload-based thinking guidance. None of these inspected pages supplies a calibrated formula for comparing all three providers.

Vendor recommendations can narrow plausible configurations; workflow evidence is still needed to establish that a candidate meets a project's requirements. Treating recommendations as priors preserves their usefulness without presenting them as measured cross-vendor superiority. ^[inferred]

## Evidence boundaries

| Evidence | Supported conclusion | Unsupported shortcut |
|---|---|---|
| Official recommendation | A vendor recommends a configuration for a workload | It must beat another provider |
| Public benchmark | Performance under recorded evaluation conditions | Success probability for this repository task |
| Code inspection | The current policy uses particular inputs and constants | The constants are empirically optimal |
| Proposed routing procedure | A reviewable design derived from these findings | The procedure is already implemented or validated |

These boundaries are research interpretations. ^[inferred]

## Open questions

- Which model/effort combinations are actually available in each configured CLI?
- What quality criterion and representative workload should guide selection?
- How should unresolved candidates be compared when task-specific measurements are missing?
- Who will maintain source dates and review changed vendor recommendations?

## Related

- [[projects/bench-router/bench-router]]
- [[concepts/facets/task]]
- [[concepts/facets/difficulty]]
- [[concepts/facets/agent_signal]]

## Sources

- [[_raw/_archived/2026-10-19-openai-model-selection]]
- [[_raw/_archived/2026-10-19-anthropic-model-selection]]
- [[_raw/_archived/2026-10-19-anthropic-effort]]
- [[_raw/_archived/2026-10-19-google-gemini-models]]
- [[_raw/_archived/2026-10-19-google-gemini-thinking]]
- [[_raw/_archived/2026-10-19-routing-research-context]]

Source captures contain bounded excerpts and origin links, not complete copies of the official documents.
