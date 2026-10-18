---
title: >-
    facet domain
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/arena-expert"]
summary: >-
    Occupational field. The 8 of 23 BLS-SOC-based fields that have LMArena leaderboards. Gemini 2.5 Flash assigns zero or more per prompt.
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# facet domain

Occupational field. The 8 of 23 BLS-SOC-based fields that have LMArena leaderboards. Gemini 2.5 Flash assigns zero or more per prompt.

`detect`: `rule:*` is decided by the router deterministically (zero tokens); `self` is tagged by the Orchestrator in the task JSON `facets`. `evidence`: official (primary source text) | dataset (dataset card) | name_only (only the name is known).

## Index

```toml
[[facet]]
id = "software_it"
desc = "Software and IT Services"
detect = "self"
arena_rule = "Gemini 2.5 Flash multi-label, zero or more of 23 categories per prompt"
evidence = "official"

[[facet]]
id = "writing_language"
desc = "Writing, Literature, and Language"
detect = "self"
arena_rule = "Gemini 2.5 Flash multi-label, zero or more of 23 categories per prompt"
evidence = "official"

[[facet]]
id = "science"
desc = "Life, Physical, and Social Science"
detect = "self"
arena_rule = "Gemini 2.5 Flash multi-label, zero or more of 23 categories per prompt"
evidence = "official"

[[facet]]
id = "entertainment_media"
desc = "Entertainment, Sports, and Media"
detect = "self"
arena_rule = "Gemini 2.5 Flash multi-label, zero or more of 23 categories per prompt"
evidence = "official"

[[facet]]
id = "business_finance"
desc = "Business, Management, and Financial Operations"
detect = "self"
arena_rule = "Gemini 2.5 Flash multi-label, zero or more of 23 categories per prompt"
evidence = "official"

[[facet]]
id = "mathematical"
desc = "Mathematical"
detect = "self"
arena_rule = "Gemini 2.5 Flash multi-label, zero or more of 23 categories per prompt"
evidence = "official"

[[facet]]
id = "legal_government"
desc = "Legal and Government"
detect = "self"
arena_rule = "Gemini 2.5 Flash multi-label, zero or more of 23 categories per prompt"
evidence = "official"

[[facet]]
id = "medicine_healthcare"
desc = "Medicine and Healthcare"
detect = "self"
arena_rule = "Gemini 2.5 Flash multi-label, zero or more of 23 categories per prompt"
evidence = "official"
```

## Other axes

- [[concepts/facets/agent_signal|agent_signal]]
- [[concepts/facets/difficulty|difficulty]]
- [[concepts/facets/lang|lang]]
- [[concepts/facets/shape|shape]]
- [[concepts/facets/task|task]]

## Sources

- [[references/sources/arena-expert]] — <https://arena.ai/blog/arena-expert>
