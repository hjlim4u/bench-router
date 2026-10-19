---
title: >-
  Anthropic model-selection strategies
category: references
tags: [source, agentic, coding]
sources: ["url:https://platform.claude.com/docs/en/about-claude/models/choosing-a-model"]
created: 2026-10-19T01:52:29Z
updated: 2026-10-19T01:52:29Z
as_of: 2026-10-19
summary: >-
  Anthropic's efficiency-first and capability-first starting strategies, model roles, and workload-specific evaluation requirements.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-anthropic-model-selection|2026-10-19-anthropic-model-selection]]"
---

# Anthropic model-selection strategies

The official guide considers required capabilities, response speed, budget, and effort.

## Documented starting strategies

Efficiency-first starts with Haiku and upgrades when evaluation exposes a capability gap. Capability-first establishes quality with a stronger model, then lowers effort or changes models when evaluations support the change.

| Dated model-matrix examples | Intended role, paraphrased |
|---|---|
| Haiku 5.5 | Budget-sensitive, high-volume processing and subagent work |
| Sonnet 5.5 | Everyday coding, analysis, and tool-based workflows |
| Opus 5.5 | Complex engineering and extended autonomous sessions |
| Fable 5.1 | The most demanding long-running research and agent tasks |

## Evaluation principle

Use actual prompts and data to compare correctness, output quality, edge cases, and cost. The guide also describes combining inexpensive workers with stronger advisors or orchestrators.

## Limits

The matrix is a starting recommendation dated 2026-10-19. Account access, model identifiers, supported effort, and task performance require separate checks. No cross-vendor ranking follows from these roles.

## Related

- [[references/sources/anthropic-effort]]
- [[synthesis/vendor-guided-model-selection]]
- [[concepts/facets/agent_signal]]

## Sources

- [[_raw/_archived/2026-10-19-anthropic-model-selection]] — bounded original excerpt and canonical origin.
