---
title: >-
    MMLU-Pro
category: entities
tags: [benchmark, hf-official, general]
sources: ["url:https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    12K complex multiple-choice questions across disciplines for multi-task understanding
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# MMLU-Pro

12K complex multiple-choice questions across disciplines for multi-task understanding.

From the dataset card (`TIGER-Lab/MMLU-Pro`):

> MMLU-Pro Dataset MMLU-Pro dataset is a more robust and challenging massive multi-task understanding dataset tailored to more rigorously benchmark large language models' capabilities. This dataset contains 12K complex questions across various disciplines.

## Index

```toml
[[unit]]
id = "hf:TIGER-Lab/MMLU-Pro"
desc = "12K complex multiple-choice questions across disciplines for multi-task understanding"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "Leaderboard API (2026-10-18): 142 rows, 142 models, 0 verified, 110 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: general

## Related benchmarks

- [[entities/benchmarks/artificial-analysis]] — Artificial Analysis indexes
- [[entities/benchmarks/hf/ace]] — ACE
- [[entities/benchmarks/hf/evasionbench]] — EvasionBench
- [[entities/benchmarks/hf/typed-decisions]] — Typed Decisions
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)

## Sources

- <https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
