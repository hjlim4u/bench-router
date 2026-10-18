---
title: >-
    RedlineBench
category: entities
tags: [benchmark, hf-official, legal]
sources: ["url:https://huggingface.co/datasets/crosbylegal/RedlineBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Contract negotiation as a sequence of judgment calls in multi-turn SaaS redlining, scored on five dimensions
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# RedlineBench

Contract negotiation as a sequence of judgment calls in multi-turn SaaS redlining, scored on five dimensions.

From the dataset card (`crosbylegal/RedlineBench`):

> Abstract Crosby–micro1 RedlineBench measures contract negotiation as a sequence of judgment calls rather than a collection of isolated clause edits. It captures multi-turn redlining workflows through simulations grounded in realistic SaaS transactions and attorney-generated explanations of key redline decisions, and evaluates models across five dimensions: legal correctness, commercial alignment, negotiation …

## Index

```toml
[[unit]]
id = "hf:crosbylegal/RedlineBench"
desc = "Contract negotiation as a sequence of judgment calls in multi-turn SaaS redlining, scored on five dimensions"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["legal"], domain = ["legal_government"], shape = ["multi_turn"] }
reason = "Leaderboard API (2026-10-18): 14 rows, 14 models, 0 verified, 12 external-source rows; 12 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active. Only HF leaderboard with proprietary-model rows, but the rows are published by the benchmark owner under its own namespace, not independently verified"
evidence = "dataset"
```

## Facets

- [[concepts/facets/domain|domain]]: legal_government
- [[concepts/facets/shape|shape]]: multi_turn
- [[concepts/facets/task|task]]: legal

## Related benchmarks

- [[entities/benchmarks/hf/lexam-hard]] — LEXam-hard
- [[entities/benchmarks/hf/lexam]] — LEXam

## Sources

- <https://huggingface.co/datasets/crosbylegal/RedlineBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
