---
title: >-
    Typed Decisions
category: entities
tags: [benchmark, hf-official, general]
sources: ["url:https://huggingface.co/datasets/LocalLLaMA/typed-decisions", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Five typed questions about one unstructured state, each answered as a probability distribution
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Typed Decisions

Five typed questions about one unstructured state, each answered as a probability distribution.

From the dataset card (`LocalLLaMA/typed-decisions`):

> Typed Decisions A benchmark for typed probabilistic decisions. A model gets one piece of unstructured state and answers five typed questions about it at once, and every answer is a probability distribution, not a single label. The schema follows the System One primitives (noul, choice, score) used by TypeSafe AI, so a row replays against any API with that shape.

## Index

```toml
[[unit]]
id = "hf:LocalLLaMA/typed-decisions"
desc = "Five typed questions about one unstructured state, each answered as a probability distribution"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "Leaderboard API (2026-10-18): 7 rows, 7 models, 0 verified, 5 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: general

## Related benchmarks

- [[entities/benchmarks/artificial-analysis]] — Artificial Analysis indexes
- [[entities/benchmarks/hf/ace]] — ACE
- [[entities/benchmarks/hf/evasionbench]] — EvasionBench
- [[entities/benchmarks/hf/mmlu-pro]] — MMLU-Pro
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)

## Sources

- <https://huggingface.co/datasets/LocalLLaMA/typed-decisions>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
