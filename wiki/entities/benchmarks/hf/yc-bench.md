---
title: >-
    YC-Bench
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/collinear-ai/yc-bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    The model runs an AI startup as CEO for one simulated year through CLI tools (hundreds of turns)
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# YC-Bench

The model runs an AI startup as CEO for one simulated year through CLI tools (hundreds of turns).

From the dataset card (`collinear-ai/yc-bench`):

> YC-Bench Long-horizon agent benchmark. The LLM plays CEO of an AI startup for 1 simulated year via CLI tool use against a deterministic discrete-event simulation. Tests: employee allocation, prestige specialization, cash flow, deadline risk, adversarial client detection — sustained over hundreds of turns.

## Index

```toml
[[unit]]
id = "hf:collinear-ai/yc-bench"
desc = "The model runs an AI startup as CEO for one simulated year through CLI tools (hundreds of turns)"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"], shape = ["long_horizon"] }
reason = "Leaderboard API (2026-10-18): 10 rows, 10 models, 0 verified, 9 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/shape|shape]]: long_horizon
- [[concepts/facets/task|task]]: multi_tool

## Related benchmarks

- [[entities/benchmarks/hf/claw-eval]] — Claw-Eval
- [[entities/benchmarks/hf/skillsbench]] — SkillsBench
- [[entities/benchmarks/hf/wildclawbench]] — WildClawBench
- [[entities/benchmarks/mg/toolathlon-verified]] — Toolathlon-Verified

## Sources

- <https://huggingface.co/datasets/collinear-ai/yc-bench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
