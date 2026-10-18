---
title: >-
    LMArena WebDev (Code Arena)
category: entities
tags: [benchmark, lmarena, web-frontend]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/leaderboard-changelog"]
summary: >-
    Pairwise votes on generated web apps. Split into HTML and React on 2026-02-26; Image-to-WebDev added 2026-04-15.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LMArena WebDev (Code Arena)

Pairwise votes on generated web apps. Split into HTML and React on 2026-02-26; Image-to-WebDev added 2026-04-15.

Score columns: `rating`, `rating_lower`, `rating_upper` (Bradley-Terry).

## Index

```toml
[[unit]]
id = "arena:webdev/overall"
desc = "User preference on all web development generation"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["webdev_html", "webdev_react"] }

[[unit]]
id = "arena:webdev/webdev-html"
desc = "Standalone HTML/CSS/JS generation within a single document scope"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["webdev_html"] }

[[unit]]
id = "arena:webdev/webdev-react"
desc = "Multi-file React application generation"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["webdev_react"] }

[[unit]]
id = "arena:webdev/image_to_webdev"
desc = "Web page built from an input image"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["image_to_webdev"] }
```

## Facets

- [[concepts/facets/task|task]]: image_to_webdev, webdev_html, webdev_react

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/lmarena-document]] — LMArena Document (style control)
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/lmarena-search]] — LMArena Search (style control)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
