---
title: >-
    VLABench
category: entities
tags: [benchmark, hf-official, out-of-scope]
sources: ["url:https://huggingface.co/datasets/VLABench/vlabench_primitive_ft_lerobot_video", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Robot manipulation primitive tasks for VLA models
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# VLABench

Robot manipulation primitive tasks for VLA models.

From the dataset card (`VLABench/vlabench_primitive_ft_lerobot_video`):

> VLABench Primitive Tasks Dataset - LeRobot v3.0 Dataset Description This dataset is organized in the LeRobot v3.0 format and is used for integrating VLABench into the LeRobot framework officially. Compared with the v2.0 version and the RLDS version of the dataset, this release stores visual observations in a video-compressed format rather than as individual image files.

## Index

```toml
[[unit]]
id = "hf:VLABench/vlabench_primitive_ft_lerobot_video"
desc = "Robot manipulation primitive tasks for VLA models"
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
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- <https://huggingface.co/datasets/VLABench/vlabench_primitive_ft_lerobot_video>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
