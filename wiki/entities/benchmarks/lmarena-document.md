---
title: >-
    LMArena Document (style control)
category: entities
tags: [benchmark, lmarena, documents]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/leaderboard-changelog"]
summary: >-
    Side-by-side evaluations of real-world document reasoning across user-uploaded PDF files (launched 2026-03-03).
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LMArena Document (style control)

Side-by-side evaluations of real-world document reasoning across user-uploaded PDF files (launched 2026-03-03).

Score columns: `rating`, `rating_lower`, `rating_upper` (Bradley-Terry).

## Index

```toml
[[unit]]
id = "arena:document_style_control/overall"
desc = "User preference on PDF document reasoning"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["document"] }
```

## Facets

- [[concepts/facets/task|task]]: document

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/lmarena-search]] — LMArena Search (style control)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)
- [[entities/benchmarks/lmarena-webdev]] — LMArena WebDev (Code Arena)

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
