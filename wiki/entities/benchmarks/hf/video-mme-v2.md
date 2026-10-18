---
title: >-
    Video-MME-v2
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/MME-Benchmarks/Video-MME-v2", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Video understanding
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Video-MME-v2

Video understanding.

From the dataset card (`MME-Benchmarks/Video-MME-v2`):

> 🔥 News 2026.06.11 Videos re-encoded to H265, maintaining consistent evaluation scores. Fixed 2 incorrect MP4s & 3 mismatched URLs. Original data preserved in the original branch. 2026.05.22 Task types are now available for Q1-Q3 in coherence (logic) groups. 🤗 About This Repo This repository contains annotation data for "Video-MME-v2: Towards the Next Stage in Benchmarks for Comprehensive Video Understanding".

## Index

```toml
[[unit]]
id = "hf:MME-Benchmarks/Video-MME-v2"
desc = "Video understanding"
metric = "pass_pct"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Speech, video, robotics, protein, or embedding evaluation; not a CLI-agent delegation target"
evidence = "dataset"
```

## Other out-of-scope benchmarks

- [[entities/benchmarks/hf/arguana]] — ArguAna (MTEB)
- [[entities/benchmarks/hf/nanofold-public]] — NanoFold Public
- [[entities/benchmarks/hf/open-asr-leaderboard]] — Open ASR Leaderboard
- [[entities/benchmarks/hf/pbench]] — PBench
- [[entities/benchmarks/hf/vaani-benchmark-v1-0]] — Vaani Benchmark
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- <https://huggingface.co/datasets/MME-Benchmarks/Video-MME-v2>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
