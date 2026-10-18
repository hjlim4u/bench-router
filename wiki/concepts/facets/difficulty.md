---
title: >-
    facet difficulty
category: concepts
tags: [facet, index]
sources: ["url:https://lmsys.org/blog/2024-05-17-category-hard", "url:https://arena.ai/blog/arena-expert"]
summary: >-
    Prompt difficulty.
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# facet difficulty

Prompt difficulty.

`detect`: `rule:*` is decided by the router deterministically (zero tokens); `self` is tagged by the Orchestrator in the task JSON `facets`. `evidence`: official (primary source text) | dataset (dataset card) | name_only (only the name is known).

## Index

```toml
[[facet]]
id = "hard_prompts"
desc = "Meets at least 6 of 7 criteria: specificity, domain knowledge, complexity, problem-solving, creativity, technical accuracy, real-world application"
detect = "self"
arena_rule = "LLM judges each criterion; hardness score >= 6"
evidence = "official"

[[facet]]
id = "expert"
desc = "Prompts characteristic of people at the top of their field (about 5.5% of prompts)"
detect = "self"
arena_rule = "Zero-shot DeepSeek-v3 with a tuned system prompt; prompt only"
evidence = "official"
```

## Other axes

- [[concepts/facets/agent_signal|agent_signal]]
- [[concepts/facets/domain|domain]]
- [[concepts/facets/lang|lang]]
- [[concepts/facets/shape|shape]]
- [[concepts/facets/task|task]]

## Sources

- [[references/sources/arena-hard-prompts]] — <https://lmsys.org/blog/2024-05-17-category-hard>
- [[references/sources/arena-expert]] — <https://arena.ai/blog/arena-expert>
