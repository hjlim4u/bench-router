---
title: >-
    GSM8K
category: entities
tags: [benchmark, hf-official, math]
sources: ["url:https://huggingface.co/datasets/openai/gsm8k", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    8.5K grade school math word problems needing 2 to 8 steps
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# GSM8K

8.5K grade school math word problems needing 2 to 8 steps.

From the dataset card (`openai/gsm8k`):

> Dataset Card for GSM8K Dataset Summary GSM8K (Grade School Math 8K) is a dataset of 8.5K high quality linguistically diverse grade school math word problems. The dataset was created to support the task of question answering on basic mathematical problems that require multi-step reasoning. These problems take between 2 and 8 steps to solve.

## Index

```toml
[[unit]]
id = "hf:openai/gsm8k"
desc = "8.5K grade school math word problems needing 2 to 8 steps"
metric = "pass_pct"
status = "saturated"
adoption = "archive"
facets = { task = ["math"] }
reason = "Saturated (grade school math; no longer separates top models)"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: math

## Related benchmarks

- [[entities/benchmarks/hf/aime-2026]] — AIME 2026 (MathArena)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)
- [[entities/benchmarks/mg/hmmt-feb-2026]] — HMMT Feb 2026

## Sources

- <https://huggingface.co/datasets/openai/gsm8k>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
