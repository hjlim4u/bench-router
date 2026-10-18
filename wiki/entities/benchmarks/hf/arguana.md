---
title: >-
    ArguAna (MTEB)
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/mteb/arguana", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Counterargument retrieval for embedding models
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# ArguAna (MTEB)

Counterargument retrieval for embedding models.

From the dataset card (`mteb/arguana`):

> ArguAna An MTEB dataset Massive Text Embedding Benchmark ArguAna: Retrieval of the Best Counterargument without Prior Topic Knowledge Task category Retrieval (text-to-text) Domains Social, Web, Written Reference ACL Source datasets: mteb/arguana How to evaluate on this task You can evaluate an embedding model on this dataset using the following code: import mteb task = mteb.get_task("ArguAna") evaluator = …

## Index

```toml
[[unit]]
id = "hf:mteb/arguana"
desc = "Counterargument retrieval for embedding models"
metric = "index"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Speech, video, robotics, protein, or embedding evaluation; not a CLI-agent delegation target"
evidence = "dataset"
```

## Other out-of-scope benchmarks

- [[entities/benchmarks/hf/nanofold-public]] — NanoFold Public
- [[entities/benchmarks/hf/open-asr-leaderboard]] — Open ASR Leaderboard
- [[entities/benchmarks/hf/pbench]] — PBench
- [[entities/benchmarks/hf/vaani-benchmark-v1-0]] — Vaani Benchmark
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- <https://huggingface.co/datasets/mteb/arguana>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
