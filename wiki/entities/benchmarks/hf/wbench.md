---
title: >-
    WBench
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/meituan-longcat/WBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Multi-turn evaluation of interactive video world models
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# WBench

Multi-turn evaluation of interactive video world models.

From the dataset card (`meituan-longcat/WBench`):

> WBench Dataset A Comprehensive Multi-turn Benchmark for Interactive Video World Model Evaluation TL;DR — WBench evaluates 20 video world models across 5 dimensions and 22 metrics. Overview WBench is a comprehensive multi-turn benchmark for interactive video world model evaluation.

## Index

```toml
[[unit]]
id = "hf:meituan-longcat/WBench"
desc = "Multi-turn evaluation of interactive video world models"
metric = "index"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Video generation model evaluation; not a CLI-agent delegation target"
evidence = "dataset"
```

## Other out-of-scope benchmarks

- [[entities/benchmarks/hf/arguana]] — ArguAna (MTEB)
- [[entities/benchmarks/hf/nanofold-public]] — NanoFold Public
- [[entities/benchmarks/hf/open-asr-leaderboard]] — Open ASR Leaderboard
- [[entities/benchmarks/hf/pbench]] — PBench
- [[entities/benchmarks/hf/vaani-benchmark-v1-0]] — Vaani Benchmark
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- <https://huggingface.co/datasets/meituan-longcat/WBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
