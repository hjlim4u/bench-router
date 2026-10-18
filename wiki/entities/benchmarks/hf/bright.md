---
title: >-
    BRIGHT
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/mteb/BRIGHT", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Text retrieval that requires intensive reasoning (nDCG@10)
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# BRIGHT

Text retrieval that requires intensive reasoning (nDCG@10).

From the dataset card (`mteb/BRIGHT`):

> BRIGHT benchmark BRIGHT is the first text retrieval benchmark that requires intensive reasoning to retrieve relevant documents. The queries are collected from diverse domains (StackExchange, LeetCode, and math competitions), all sourced from realistic human data. Experiments show that existing retrieval models perform poorly on BRIGHT, where the highest score is only 22.1 measured by nDCG@10.

## Index

```toml
[[unit]]
id = "hf:mteb/BRIGHT"
desc = "Text retrieval that requires intensive reasoning (nDCG@10)"
metric = "index"
status = "current"
adoption = "excluded"
facets = { task = ["retrieval"] }
reason = "Leaderboard (2026-10-18) has one row, mteb/baseline-bm25s, a BM25 retrieval baseline. BRIGHT ranks retrieval systems, not CLI agents; excluded like ArguAna"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: retrieval

## Other out-of-scope benchmarks

- [[entities/benchmarks/hf/arguana]] — ArguAna (MTEB)
- [[entities/benchmarks/hf/nanofold-public]] — NanoFold Public
- [[entities/benchmarks/hf/open-asr-leaderboard]] — Open ASR Leaderboard
- [[entities/benchmarks/hf/pbench]] — PBench
- [[entities/benchmarks/hf/vaani-benchmark-v1-0]] — Vaani Benchmark
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media

## Sources

- <https://huggingface.co/datasets/mteb/BRIGHT>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
