---
title: >-
    facet shape
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/arena-category/", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Request shape.
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# facet shape

Request shape.

`detect`: `rule:*` is decided by the router deterministically (zero tokens); `self` is tagged by the Orchestrator in the task JSON `facets`. `evidence`: official (primary source text) | dataset (dataset card) | name_only (only the name is known).

## Index

```toml
[[facet]]
id = "longer_query"
desc = "Queries longer than 500 tokens (approximately 10% of all prompts)"
detect = "rule:prompt_tokens>500"
evidence = "official"

[[facet]]
id = "multi_turn"
desc = "Conversations with multiple turns"
detect = "rule:round>1"
evidence = "official"

[[facet]]
id = "long_horizon"
desc = "Agent work sustained over hundreds of steps or hours"
detect = "self"
evidence = "dataset"
```

## Other axes

- [[concepts/facets/agent_signal|agent_signal]]
- [[concepts/facets/difficulty|difficulty]]
- [[concepts/facets/domain|domain]]
- [[concepts/facets/lang|lang]]
- [[concepts/facets/task|task]]

## Sources

- [[references/sources/arena-category]] — <https://arena.ai/blog/arena-category/>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
