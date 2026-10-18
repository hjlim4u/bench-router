---
title: >-
    WildClawBench
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/internlm/WildClawBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    60 original end-to-end tasks in a live OpenClaw personal-assistant environment
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# WildClawBench

60 original end-to-end tasks in a live OpenClaw personal-assistant environment.

From the dataset card (`internlm/WildClawBench`):

> WildClawBench Hard, practical, end-to-end evaluation for AI agents — in the wild. WildClawBench is an agent benchmark that tests what actually matters: can an AI agent do real work, end-to-end, without hand-holding? We drop agents into a live OpenClaw environment — the same open-source personal AI assistant that real users rely on daily — and throw 60 original tasks at them: clipping goal highlights from a football …

## Index

```toml
[[unit]]
id = "hf:internlm/WildClawBench"
desc = "60 original end-to-end tasks in a live OpenClaw personal-assistant environment"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"], shape = ["long_horizon"] }
reason = "Leaderboard API (2026-10-18): 51 rows, 22 models, 0 verified, 46 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/shape|shape]]: long_horizon
- [[concepts/facets/task|task]]: multi_tool

## Related benchmarks

- [[entities/benchmarks/hf/claw-eval]] — Claw-Eval
- [[entities/benchmarks/hf/skillsbench]] — SkillsBench
- [[entities/benchmarks/hf/yc-bench]] — YC-Bench
- [[entities/benchmarks/mg/toolathlon-verified]] — Toolathlon-Verified

## Sources

- <https://huggingface.co/datasets/internlm/WildClawBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
