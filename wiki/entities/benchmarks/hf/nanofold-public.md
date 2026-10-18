---
title: >-
    NanoFold Public
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/ChrisHayduk/nanofold-public", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Protein structure prediction training and validation data
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# NanoFold Public

Protein structure prediction training and validation data.

From the dataset card (`ChrisHayduk/nanofold-public`):

> NanoFold Public NanoFold Public is the public train/validation portion of the nanoFold protein-folding benchmark. It packages a compact, fixed, auditable subset of OpenProteinSet/OpenFold-derived protein structure training data for fast iteration on data-efficient folding models. The dataset has 10000 train chains and 1000 public validation chains. Each row is one protein chain.

## Index

```toml
[[unit]]
id = "hf:ChrisHayduk/nanofold-public"
desc = "Protein structure prediction training and validation data"
metric = "index"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Speech, video, robotics, protein, or embedding evaluation; not a CLI-agent delegation target"
evidence = "dataset"
```

## Other out-of-scope benchmarks

- [[entities/benchmarks/hf/arguana]] — ArguAna (MTEB)
- [[entities/benchmarks/hf/open-asr-leaderboard]] — Open ASR Leaderboard
- [[entities/benchmarks/hf/pbench]] — PBench
- [[entities/benchmarks/hf/vaani-benchmark-v1-0]] — Vaani Benchmark
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- <https://huggingface.co/datasets/ChrisHayduk/nanofold-public>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
