---
title: >-
  OpenAI model and reasoning-effort selection
category: references
tags: [source, agentic, reasoning]
sources: ["url:https://developers.openai.com/api/docs/guides/model-selection"]
created: 2026-10-19T01:52:29Z
updated: 2026-10-19T01:52:29Z
as_of: 2026-10-19
summary: >-
  OpenAI's documented workload-to-model/effort examples and its recommendation to compare settings on the same inputs.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-openai-model-selection|2026-10-19-openai-model-selection]]"
---

# OpenAI model and reasoning-effort selection

OpenAI's Model selection guide, inspected on 2026-10-19, provides examples pairing workloads with models and reasoning effort.

## Documented starting points

| Workload, paraphrased | Model | Effort shown in the guide |
|---|---|---|
| Small edits, bounded problems, extraction | Luna | Low |
| Gathering context from apps, prioritization, constrained problems | Luna | Extra high |
| Technical projects with expected revisions | GPT-6.1 Sol | Medium |
| Finished deliverables and conflicting evidence | GPT-6.1 Sol | Extra high |
| Brief writing that retains nuance | Astra | Low |
| Broad projects requiring dependable interactions | Astra | Medium |
| Demanding analysis with strict requirements | Astra | Extra high |

## Evaluation principle

Compare configurations on identical inputs and retain one that meets the required quality with less resource use. Frequency, turnaround time, intended audience, and quality requirements affect the choice.

## Limits

These are dated starting points. The page distinguishes product/version availability and does not establish a common score for competing vendors. Display labels above are not verified CLI flags or configured bench-router profile IDs.

## Related

- [[concepts/model-effort-selection]]
- [[synthesis/vendor-guided-model-selection]]
- [[concepts/facets/task]]

## Sources

- [[_raw/_archived/2026-10-19-openai-model-selection]] — bounded original excerpt; canonical link and capture scope are recorded there.
