---
title: >-
  OpenAI model and reasoning-effort selection
category: references
tags: [source, agentic, reasoning]
sources: ["url:https://developers.openai.com/api/docs/guides/model-selection"]
created: 2026-10-19T01:52:29Z
updated: 2026-10-27T13:28:00Z
as_of: 2026-10-27
summary: >-
  OpenAI's documented model/effort starting points, quoted verbatim, and its advice to keep the lightest setting that meets the quality bar. Includes GPT-6.1 Terra consideration guidance.
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
  - "[[_raw/_archived/2026-10-24-openai-model-selection|2026-10-24-openai-model-selection]]"
  - "[[_raw/_archived/2026-10-27-openai-model-selection|2026-10-27-openai-model-selection]]"
---

# OpenAI model and reasoning-effort selection

OpenAI's Model selection guide, checked on 2026-10-24, pairs workloads with a model and a reasoning effort. Quotations below are verbatim.

> If cost and latency aren’t a concern, you can default to Astra. To reduce costs or latency, use the guidance below to choose a model and reasoning effort for your needs.

## When to consider GPT-6.1 Terra

> Try GPT-6.1 Terra for concise writing based on supplied material, computer-use tasks with a defined outcome, and scoped code fixes. Provide clear inputs, requirements, and a way to verify the result, such as checking saved records or running regression tests.

> Compare it with GPT-6.1 Sol on the same inputs and reasoning effort. For writing, judge audience fit, voice, and useful detail as well as accuracy and length. For computer use, check the saved result and the accuracy of the completion report.

## Documented starting points

| Model | Effort shown in the guide | Workload, verbatim |
|---|---|---|
| Luna | Low | Fine-grained edits, well-scoped problem-solving, and simple data extraction. |
| Luna | Extra high | Finding current context across multiple apps, prioritizing work, and solving problems with clear constraints. |
| GPT-6.1 Sol | Medium | Complex technical work and coordinated deliverables you expect to revise. |
| GPT-6.1 Sol | Extra high | Polished deliverables, connected visual systems, and decisions built from conflicting evidence. |
| Astra | Low | Concise writing and content adaptation that preserve facts and nuance. |
| Astra | Medium | Ambitious projects that need broad context, reliable interactions, and complete results. |
| Astra | Extra high | Demanding analysis and complex deliverables with exacting requirements. |

The page presents Extra high as a starting point for these workloads; it does not advise against it.

## Evaluation principle

> If you can, experiment using the same inputs to compare results and keep the lightest setting that meets your quality bar.

> A task you’re waiting on may need a faster setting than one that runs overnight.

## Limits

These are dated starting points. The page distinguishes product/version availability and does not establish a common score for competing vendors. Display labels above are not verified CLI flags or configured bench-router profile IDs. The page names no default reasoning effort.

## Related

- [[concepts/model-effort-selection]]
- [[synthesis/vendor-guided-model-selection]]
- [[concepts/facets/task]]

## Sources

- [[_raw/_archived/2026-10-27-openai-model-selection]] — defuddle markdown capture of updated guide including GPT-6.1 Terra.
- [[_raw/_archived/2026-10-24-openai-model-selection]] — verbatim excerpts of every quoted row and sentence.
- [[_raw/_archived/2026-10-19-openai-model-selection]] — earlier bounded excerpt; canonical link and capture scope are recorded there.
