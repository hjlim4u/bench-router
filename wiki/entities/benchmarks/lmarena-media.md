---
title: >-
    LMArena generative media
category: entities
tags: [benchmark, lmarena, out-of-scope]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"]
summary: >-
    Pairwise votes on image and video generation and editing. This router delegates text and code work to CLI agents, so these are not assignment targets.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LMArena generative media

Pairwise votes on image and video generation and editing. This router delegates text and code work to CLI agents, so these are not assignment targets.

## Index

```toml
[[unit]]
id = "arena:text_to_image/overall"
desc = "Text-to-image generation"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Not a CLI-agent delegation target"

[[unit]]
id = "arena:image_edit/overall"
desc = "Image editing"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Not a CLI-agent delegation target"

[[unit]]
id = "arena:text_to_video/overall"
desc = "Text-to-video generation"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Not a CLI-agent delegation target"

[[unit]]
id = "arena:image_to_video/overall"
desc = "Image-to-video generation"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Not a CLI-agent delegation target"

[[unit]]
id = "arena:video_edit/overall"
desc = "Video editing"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "Not a CLI-agent delegation target"
```

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/lmarena-document]] — LMArena Document (style control)
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-search]] — LMArena Search (style control)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)
- [[entities/benchmarks/lmarena-webdev]] — LMArena WebDev (Code Arena)

## Other out-of-scope benchmarks

- [[entities/benchmarks/hf/arguana]] — ArguAna (MTEB)
- [[entities/benchmarks/hf/nanofold-public]] — NanoFold Public
- [[entities/benchmarks/hf/open-asr-leaderboard]] — Open ASR Leaderboard
- [[entities/benchmarks/hf/pbench]] — PBench
- [[entities/benchmarks/hf/vaani-benchmark-v1-0]] — Vaani Benchmark
- [[entities/benchmarks/hf/video-mme-v2]] — Video-MME-v2
- [[entities/benchmarks/hf/vlabench-primitive-ft-lerobot-video]] — VLABench
- [[entities/benchmarks/hf/wbench]] — WBench
- [[entities/benchmarks/hf/bright]] — BRIGHT

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
