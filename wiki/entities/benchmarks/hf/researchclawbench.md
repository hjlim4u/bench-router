---
title: >-
    ResearchClawBench
category: entities
tags: [benchmark, hf-official, data-analysis, reasoning]
sources: ["url:https://huggingface.co/datasets/InternScience/ResearchClawBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Autonomous scientific research from raw data to publication-quality reports, compared with real papers
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# ResearchClawBench

Autonomous scientific research from raw data to publication-quality reports, compared with real papers.

From the dataset card (`InternScience/ResearchClawBench`):

> ResearchClawBench &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Evaluating AI Agents for Automated Research from Re-Discovery to New-Discovery Quick Start | Submit Tasks | How It Works | Domains | Leaderboard | Add Your Agent ResearchClawBench is a benchmark that measures whether AI coding agents can independently conduct scientific research — from reading raw data to producing publication-quality reports — and then rigorously …

## Index

```toml
[[unit]]
id = "hf:InternScience/ResearchClawBench"
desc = "Autonomous scientific research from raw data to publication-quality reports, compared with real papers"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["science_reasoning", "data_analysis"], shape = ["long_horizon"] }
reason = "Leaderboard API (2026-10-18): 7 rows, 7 models, 0 verified, 0 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/shape|shape]]: long_horizon
- [[concepts/facets/task|task]]: data_analysis, science_reasoning

## Related benchmarks

- [[entities/benchmarks/hf/mmmu-pro]] — MMMU-Pro
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/mg/aa-analyst-agent]] — AA-AnalystAgent
- [[entities/benchmarks/mg/gpqa-diamond]] — GPQA Diamond
- [[entities/benchmarks/mg/hle]] — Humanity's Last Exam

## Sources

- <https://huggingface.co/datasets/InternScience/ResearchClawBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
