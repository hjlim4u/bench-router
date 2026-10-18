---
title: >-
    IFStruct v1.0
category: entities
tags: [benchmark, hf-official, general]
sources: ["url:https://huggingface.co/datasets/LiquidAI/ifstruct-v1.0", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Structured-output compliance: valid JSON/YAML following a requested schema, without constrained decoding
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# IFStruct v1.0

Structured-output compliance: valid JSON/YAML following a requested schema, without constrained decoding.

From the dataset card (`LiquidAI/ifstruct-v1.0`):

> IFStruct v1.0 [!Note] 📝 Blog post: https://www.liquid.ai/blog/ifstruct-v1.0 💻 GitHub: https://github.com/Liquid4All/ifstruct IFStruct is a benchmark for structured-output compliance: can a model produce valid JSON/YAML that follows a requested schema, when the requirements are phrased the many different ways real users phrase them? It is scored without constrained decoding, and only the structure is judged (not …

## Index

```toml
[[unit]]
id = "hf:LiquidAI/ifstruct-v1.0"
desc = "Structured-output compliance: valid JSON/YAML following a requested schema, without constrained decoding"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["instruction_following"] }
reason = "Leaderboard API (2026-10-18): 6 rows, 6 models, 0 verified, 6 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: instruction_following

## Related benchmarks

- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)

## Sources

- <https://huggingface.co/datasets/LiquidAI/ifstruct-v1.0>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
