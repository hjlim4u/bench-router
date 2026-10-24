---
title: >-
  Anthropic model-selection strategies
category: references
tags: [source, agentic, coding]
sources: ["url:https://platform.claude.com/docs/en/about-claude/models/choosing-a-model"]
created: 2026-10-19T01:52:29Z
updated: 2026-10-24T12:45:00Z
as_of: 2026-10-24
summary: >-
  Anthropic's model matrix (most workloads start with Opus 5.5), efficiency-first and capability-first strategies, and effort defaults, quoted verbatim.
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
  - "[[_raw/_archived/2026-10-24-anthropic-model-selection|2026-10-24-anthropic-model-selection]]"
---

# Anthropic model-selection strategies

The official guide, checked on 2026-10-24, weighs capabilities, speed, cost, and effort. Quotations below are verbatim.

> Tuning effort is often a better lever than switching models. On Claude Fable 5.1, Claude Opus 5, and Claude Sonnet 5.5, start with the default (`high`) and adjust up or down based on your evals. On Claude Opus 5.5 and Claude Haiku 5.5 the default is `medium`; start there and adjust the same way.

## Model selection matrix

> Most workloads start with Claude Opus 5.5.

| When you need... | Consider starting with... | Example use cases |
|---|---|---|
| The highest available capability | Claude Fable 5.1 | Agent sessions that run for hours, multistep deep research, analysis carried through to a finished document, spreadsheet, or deck |
| Complex agentic coding and enterprise work | Claude Opus 5.5 | Multihour autonomous coding agents, large-scale refactoring, complex systems engineering, vision-heavy workflows, computer use |
| Speed and capability for everyday coding, agent, and enterprise workloads | Claude Sonnet 5.5 | Code generation, data analysis, content creation, visual understanding, agentic tool use |
| The lowest latency and price | Claude Haiku 5.5 | Real-time applications, high-volume intelligent processing, cost-sensitive deployments needing strong reasoning, subagent tasks |

## Documented starting strategies

**Efficiency-first.**

> For many applications, starting with a faster, more cost-effective model such as Claude Haiku 5.5 can be the optimal approach

> Upgrade only if necessary for specific capability gaps.

Best for: Initial prototyping and development; Applications with tight latency requirements; Cost-sensitive implementations; High-volume, straightforward tasks.

**Capability-first.**

> For complex tasks where intelligence and advanced capabilities are paramount, you might want to start capability-first: implement with the strongest starting point for your task, then optimize to more efficient models later

> Implement with Claude Opus 5.5.

> If your evals at `xhigh` or `max` effort still fall short on demanding reasoning or long-horizon agentic work, move to Claude Fable 5.1.

Best for: Complex reasoning tasks; Scientific or mathematical applications; Tasks requiring nuanced understanding; Applications where accuracy outweighs cost considerations; Advanced coding and high-autonomy agentic work.

## Evaluation principle

Use actual prompts and data to compare correctness, output quality, edge cases, and cost. The guide also describes combining inexpensive workers with stronger advisors or orchestrators.

## Limits

The matrix is a starting recommendation dated 2026-10-24. Account access, model identifiers, supported effort, and task performance require separate checks. No cross-vendor ranking follows from these roles.

## Related

- [[references/sources/anthropic-effort]]
- [[synthesis/vendor-guided-model-selection]]
- [[concepts/facets/agent_signal]]

## Sources

- [[_raw/_archived/2026-10-24-anthropic-model-selection]] — verbatim excerpts of the matrix, strategies and effort criterion.
- [[_raw/_archived/2026-10-19-anthropic-model-selection]] — earlier bounded excerpt and canonical origin.
