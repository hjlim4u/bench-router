---
title: >-
    facet lang
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/arena-category/"]
summary: >-
    Prompt language. LMArena tags each prompt with a language using Polyglot.
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# facet lang

Prompt language. LMArena tags each prompt with a language using Polyglot.

`detect`: `rule:*` is decided by the router deterministically (zero tokens); `self` is tagged by the Orchestrator in the task JSON `facets`. `evidence`: official (primary source text) | dataset (dataset card) | name_only (only the name is known).

## Index

```toml
[[facet]]
id = "ko"
desc = "Korean prompts"
detect = "rule:script(hangul)"
arena_rule = "Polyglot language tag"
evidence = "official"

[[facet]]
id = "ja"
desc = "Japanese prompts"
detect = "rule:script(kana)"
arena_rule = "Polyglot language tag"
evidence = "official"

[[facet]]
id = "zh"
desc = "Chinese prompts"
detect = "rule:script(han_only)"
arena_rule = "Polyglot language tag"
evidence = "official"

[[facet]]
id = "ru"
desc = "Russian prompts"
detect = "rule:script(cyrillic)"
arena_rule = "Polyglot language tag"
evidence = "official"

[[facet]]
id = "en"
desc = "English prompts"
detect = "self"
arena_rule = "Polyglot language tag"
evidence = "official"

[[facet]]
id = "es"
desc = "Spanish prompts"
detect = "self"
arena_rule = "Polyglot language tag"
evidence = "official"

[[facet]]
id = "fr"
desc = "French prompts"
detect = "self"
arena_rule = "Polyglot language tag"
evidence = "official"

[[facet]]
id = "de"
desc = "German prompts"
detect = "self"
arena_rule = "Polyglot language tag"
evidence = "official"

[[facet]]
id = "pl"
desc = "Polish prompts"
detect = "self"
arena_rule = "Polyglot language tag"
evidence = "official"
```

## Other axes

- [[concepts/facets/agent_signal|agent_signal]]
- [[concepts/facets/difficulty|difficulty]]
- [[concepts/facets/domain|domain]]
- [[concepts/facets/shape|shape]]
- [[concepts/facets/task|task]]

## Sources

- [[references/sources/arena-category]] — <https://arena.ai/blog/arena-category/>
