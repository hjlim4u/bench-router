---
title: >-
    PBench
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/tiiuae/PBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Referring expression segmentation: segment the object a language expression names
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# PBench

Referring expression segmentation: segment the object a language expression names.

From the dataset card (`tiiuae/PBench`):

> PBench: A Perception Benchmark for Referring Expression Segmentation Referring expression segmentation is increasingly becoming a core building block for real products and real workflows.

## Index

```toml
[[unit]]
id = "hf:tiiuae/PBench"
desc = "Referring expression segmentation: segment the object a language expression names"
metric = "index"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Image segmentation model evaluation; not a CLI-agent delegation target"
evidence = "dataset"
```

## Other out-of-scope benchmarks

- [[entities/benchmarks/hf/arguana]] — ArguAna (MTEB)
- [[entities/benchmarks/hf/nanofold-public]] — NanoFold Public
- [[entities/benchmarks/hf/open-asr-leaderboard]] — Open ASR Leaderboard
- [[entities/benchmarks/hf/vaani-benchmark-v1-0]] — Vaani Benchmark
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- <https://huggingface.co/datasets/tiiuae/PBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
