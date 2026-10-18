---
title: >-
    LMArena Factuality (Text and Search)
category: entities
tags: [benchmark, lmarena, general, search]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/factuality-in-arena"]
summary: >-
    Battles are sampled for a factuality audit; atomic web-verifiable claims are checked by search agents for calibrated truth probabilities; the response with higher average claim truthfulness wins. T...
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LMArena Factuality (Text and Search)

Battles are sampled for a factuality audit; atomic web-verifiable claims are checked by search agents for calibrated truth probabilities; the response with higher average claim truthfulness wins. These factuality battles feed a composite Bradley-Terry model with human preference; default factuality weight 25%.

Score columns: `rating`, `rating_lower`, `rating_upper` (composite Bradley-Terry).

## Index

```toml
[[unit]]
id = "arena:text_factuality/overall"
desc = "Composite of 75% human preference and 25% claim factuality (Text)"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["general"] }
reason = "Verified 2026-10-18 (185 models): all 3 profile models present (Claude Opus 5.5 (High), gpt-6.1-sol-max, Gemini 4 Argon (High)); collected via arena_spec(index) and desc notes the 75%/25% composite"

[[unit]]
id = "arena:search_factuality/overall"
desc = "Composite of 75% human preference and 25% claim factuality (Search)"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["search"] }
reason = "Verified 2026-10-18 (40 models): 2 profile models present (claude-opus-5.5-medium, gpt-6.1-sol-max); collected via arena_spec(index) and desc notes the 75%/25% composite"
```

## Open Questions

- Checked 2026-10-18: the HF dataset has `text_factuality` (3,932 rows across 29 categories; `overall` has 185 models including all 3 profile models) and `search_factuality` (`overall` has 40 models including `claude-opus-5.5-medium` and `gpt-6.1-sol-max`). Both are collected automatically via `arena_spec(index)` in `bench_router/data.py`.
- Note for interpretation: the factuality ranking is a 75%/25% composite with human preference (`text_style_control/overall` / `search_style_control/overall`); `evidence.py` displays units side by side without summing them.

## Facets

- [[concepts/facets/task|task]]: general, search

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/artificial-analysis]] — Artificial Analysis indexes
- [[entities/benchmarks/hf/ace]] — ACE
- [[entities/benchmarks/hf/evasionbench]] — EvasionBench
- [[entities/benchmarks/hf/mmlu-pro]] — MMLU-Pro
- [[entities/benchmarks/hf/typed-decisions]] — Typed Decisions
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/lmarena-document]] — LMArena Document (style control)
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/lmarena-search]] — LMArena Search (style control)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)
- [[entities/benchmarks/lmarena-webdev]] — LMArena WebDev (Code Arena)

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-factuality]] — <https://arena.ai/blog/factuality-in-arena>
