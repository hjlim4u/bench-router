---
title: >-
  Model and effort selection as separate decisions
category: concepts
tags: [agentic, reasoning]
sources:
  - "url:https://developers.openai.com/api/docs/guides/model-selection"
  - "url:https://platform.claude.com/docs/en/about-claude/models/choosing-a-model"
  - "url:https://platform.claude.com/docs/en/build-with-claude/effort"
  - "url:https://ai.google.dev/gemini-api/docs/thinking"
  - "conversation:2026-10-22"
created: 2026-10-19T01:52:29Z
updated: 2026-10-22T07:20:11Z
as_of: 2026-10-22
summary: >-
  Model choice, reasoning effort, feasibility constraints, and measured workflow quality are distinct inputs to agent selection.
provenance:
  extracted: 0.3
  inferred: 0.7
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-openai-model-selection|2026-10-19-openai-model-selection]]"
  - "[[_raw/_archived/2026-10-19-anthropic-model-selection|2026-10-19-anthropic-model-selection]]"
  - "[[_raw/_archived/2026-10-19-anthropic-effort|2026-10-19-anthropic-effort]]"
  - "[[_raw/_archived/2026-10-19-google-gemini-thinking|2026-10-19-google-gemini-thinking]]"
---

# Model and effort selection as separate decisions

A model/effort configuration is a candidate execution setting, not a universal amount of intelligence or a measured probability of task success. ^[inferred]

## How the decisions differ

| Decision | Question to answer |
|---|---|
| Feasibility | Can this configured agent satisfy required tools, input types, context, locality, availability, and budget? |
| Model | Which model is a plausible fit for the requested work? |
| Effort | Which supported setting fits this workload on that model and version? |
| Evaluation | Does the complete workflow meet the required quality, latency, and cost limits? |

This separation is a synthesis for routing design, not a shared vendor API contract. ^[inferred]

## Applying the concept

Use [[references/sources/openai-model-selection|OpenAI's combinations]], [[references/sources/anthropic-effort|Anthropic's model-specific advice]], and [[references/sources/google-gemini-thinking|Google's supported thinking settings]] as dated priors. The meaning and available values of effort depend on the model and product. Equal labels do not establish equal token budgets or capabilities. ^[inferred]

Record workload attributes such as clarity, ambiguity, reasoning demands, tool-use duration, expected polish, deadline, and spending limit. These attributes describe the request; assigning them numeric weights requires separate evidence. ^[inferred]

## Pattern and role assignments

In a multi-agent workflow, model and effort choices also interact with the collaboration pattern. Propose patterns from task structure, then compare role-specific configurations and aggregation using workflow evidence before finalizing the plan. The best generator need not be the best checker, and a small gap between individual scores does not establish an ensemble gain. This is a project design inference, developed in [[projects/bench-router/synthesis/multi-agent-pattern-selection]]. ^[inferred]

## Limits

A benchmark's difficulty label is not automatically a vendor's effort recommendation. For example, the Arena `hard_prompts` facet has its own tagging criteria in [[concepts/facets/difficulty]]. A configured reasoning level can differ from the level used to measure a benchmark; that mismatch belongs in the evidence record. ^[inferred]

## Related

- [[concepts/facets/difficulty]]
- [[concepts/facets/agent_signal]]
- [[synthesis/vendor-guided-model-selection]]
- [[projects/bench-router/synthesis/routing-selection-audit]]
- [[projects/bench-router/synthesis/multi-agent-pattern-selection]]

## Sources

- [[_raw/_archived/2026-10-19-openai-model-selection]]
- [[_raw/_archived/2026-10-19-anthropic-model-selection]]
- [[_raw/_archived/2026-10-19-anthropic-effort]]
- [[_raw/_archived/2026-10-19-google-gemini-thinking]]

The archived records are bounded excerpts with canonical links. The separation above is an interpretation of the inspected guides.
