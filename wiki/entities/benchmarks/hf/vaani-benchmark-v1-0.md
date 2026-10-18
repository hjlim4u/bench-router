---
title: >-
    Vaani Benchmark
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/ARTPARK-IISc/Vaani-Benchmark-V1.0", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Hindi speech recognition
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Vaani Benchmark

Hindi speech recognition.

From the dataset card (`ARTPARK-IISc/Vaani-Benchmark-V1.0`):

> Vaani-Benchmark-V1.0 A curated Hindi ASR evaluation set collected as part of the Vaani project at IISc Bengaluru. This is a separate, held-out collection — distinct from the publicly released Vaani dataset — built specifically for benchmarking. This benchmark contains 5,050 audio segments from 1,103 speakers across 104 Indian districts, each with three independent human transcriptions.

## Index

```toml
[[unit]]
id = "hf:ARTPARK-IISc/Vaani-Benchmark-V1.0"
desc = "Hindi speech recognition"
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
- [[entities/benchmarks/hf/open-asr-leaderboard]] — Open ASR Leaderboard
- [[entities/benchmarks/hf/pbench]] — PBench
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- <https://huggingface.co/datasets/ARTPARK-IISc/Vaani-Benchmark-V1.0>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
