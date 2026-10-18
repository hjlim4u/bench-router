---
title: >-
    MMMU-Pro
category: entities
tags: [benchmark, hf-official, reasoning, vision]
sources: ["url:https://huggingface.co/datasets/MMMU/MMMU_Pro", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Multi-discipline multimodal understanding (image plus question, augmented options, vision-only setting)
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# MMMU-Pro

Multi-discipline multimodal understanding (image plus question, augmented options, vision-only setting).

From the dataset card (`MMMU/MMMU_Pro`):

> MMMU-Pro (A More Robust Multi-discipline Multimodal Understanding Benchmark) 🌐 Homepage | 🏆 Leaderboard | 🤗 Dataset | 🤗 Paper | 📖 arXiv | GitHub 🔔News 🛠️[2026-10-04] Fixed the option augmentation issue in Vision and Standard (10 options) settings. (test_Chemistry_240) 🛠️[2026-10-04] Added the missing condition to an under-specified question.

## Index

```toml
[[unit]]
id = "hf:MMMU/MMMU_Pro"
desc = "Multi-discipline multimodal understanding (image plus question, augmented options, vision-only setting)"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["vision", "science_reasoning"] }
reason = "Leaderboard API (2026-10-18): 10 rows, 10 models, 0 verified, 1 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: science_reasoning, vision

## Related benchmarks

- [[entities/benchmarks/hf/researchclawbench]] — ResearchClawBench
- [[entities/benchmarks/hf/swe-bench-multimodal]] — SWE-bench Multimodal
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)
- [[entities/benchmarks/mg/gpqa-diamond]] — GPQA Diamond
- [[entities/benchmarks/mg/hle]] — Humanity's Last Exam

## Sources

- <https://huggingface.co/datasets/MMMU/MMMU_Pro>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
