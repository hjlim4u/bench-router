---
title: >-
    ACE
category: entities
tags: [benchmark, hf-official, general]
sources: ["url:https://huggingface.co/datasets/mercor/ACE", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Evaluation criteria in four consumer domains: DIY, food, shopping, gaming
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# ACE

Evaluation criteria in four consumer domains: DIY, food, shopping, gaming.

From the dataset card (`mercor/ACE`):

> ACE Dataset This dataset contains evaluation criteria across four domains: DIY, Food, Shopping, and Gaming. Configurations diy: DIY and home improvement criteria food: Food and recipe criteria shopping: Shopping and product criteria gaming: Gaming design criteria Usage from datasets import load_dataset Load a specific domain diy_data = load_dataset("mercor/ACE", "diy") food_data = load_dataset("mercor/ACE", "food") …

## Index

```toml
[[unit]]
id = "hf:mercor/ACE"
desc = "Evaluation criteria in four consumer domains: DIY, food, shopping, gaming"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "Leaderboard API (2026-10-18) returned no rows; no model scores are published yet. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: general

## Related benchmarks

- [[entities/benchmarks/artificial-analysis]] — Artificial Analysis indexes
- [[entities/benchmarks/hf/evasionbench]] — EvasionBench
- [[entities/benchmarks/hf/mmlu-pro]] — MMLU-Pro
- [[entities/benchmarks/hf/typed-decisions]] — Typed Decisions
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)

## Sources

- <https://huggingface.co/datasets/mercor/ACE>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
