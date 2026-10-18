---
title: >-
    LEXam
category: entities
tags: [benchmark, hf-official, legal]
sources: ["url:https://huggingface.co/datasets/LEXam-Benchmark/LEXam", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Legal reasoning on 340 Swiss, EU, and international law exams (English and German)
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LEXam

Legal reasoning on 340 Swiss, EU, and international law exams (English and German).

From the dataset card (`LEXam-Benchmark/LEXam`):

> LEXam: Benchmarking Legal Reasoning on 340 Law Exams A diverse, rigorous evaluation suite for legal AI from Swiss, EU, and international law examinations.

## Index

```toml
[[unit]]
id = "hf:LEXam-Benchmark/LEXam"
desc = "Legal reasoning on 340 Swiss, EU, and international law exams (English and German)"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["legal"], domain = ["legal_government"] }
reason = "Leaderboard API (2026-10-18): 10 rows, 10 models, 0 verified, 9 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/domain|domain]]: legal_government
- [[concepts/facets/task|task]]: legal

## Related benchmarks

- [[entities/benchmarks/hf/lexam-hard]] — LEXam-hard
- [[entities/benchmarks/hf/redlinebench]] — RedlineBench

## Sources

- <https://huggingface.co/datasets/LEXam-Benchmark/LEXam>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
