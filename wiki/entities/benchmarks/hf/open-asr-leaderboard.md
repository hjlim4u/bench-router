---
title: >-
    Open ASR Leaderboard
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/hf-audio/open-asr-leaderboard", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Speech recognition test sets
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Open ASR Leaderboard

Speech recognition test sets.

From the dataset card (`hf-audio/open-asr-leaderboard`):

> ESB Test Sets: Parquet & Sorted This dataset takes the open-asr-leaderboard/datasets-test-only data and sorts each split by audio length. The format is also changed, from custom loading script (un-safe remote code) to parquet (safe).

## Index

```toml
[[unit]]
id = "hf:hf-audio/open-asr-leaderboard"
desc = "Speech recognition test sets"
metric = "index"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Speech, video, robotics, protein, or embedding evaluation; not a CLI-agent delegation target"
evidence = "dataset"
```

## Other out-of-scope benchmarks

- [[entities/benchmarks/hf/arguana]] — ArguAna (MTEB)
- [[entities/benchmarks/hf/nanofold-public]] — NanoFold Public
- [[entities/benchmarks/hf/pbench]] — PBench
- [[entities/benchmarks/hf/vaani-benchmark-v1-0]] — Vaani Benchmark
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- <https://huggingface.co/datasets/hf-audio/open-asr-leaderboard>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
