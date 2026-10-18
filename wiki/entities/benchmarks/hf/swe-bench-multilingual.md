---
title: >-
    SWE-bench Multilingual
category: entities
tags: [benchmark, hf-official, coding]
sources: ["url:https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Real GitHub issues across 9 programming languages from 41 repositories, verified by unit tests
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# SWE-bench Multilingual

Real GitHub issues across 9 programming languages from 41 repositories, verified by unit tests.

From the dataset card (`SWE-bench/SWE-bench_Multilingual`):

> SWE-bench Multilingual Dataset Summary SWE-bench Multilingual is a dataset that tests systems' ability to resolve real-world GitHub issues across a broad range of programming languages. The original SWE-bench is Python-only; this dataset extends the same task format to 9 languages drawn from 41 popular repositories. The dataset collects 300 test Issue-Pull Request pairs.

## Index

```toml
[[unit]]
id = "hf:SWE-bench/SWE-bench_Multilingual"
desc = "Real GitHub issues across 9 programming languages from 41 repositories, verified by unit tests"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["repo_coding"] }
reason = "Leaderboard API (2026-10-18): 28 rows, 28 models, 0 verified, 0 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: repo_coding

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/hf/swe-bench-multimodal]] — SWE-bench Multimodal
- [[entities/benchmarks/hf/swe-bench-pro]] — SWE-bench Pro
- [[entities/benchmarks/mg/deepswe]] — DeepSWE
- [[entities/benchmarks/mg/swe-bench-verified]] — SWE-bench Verified
- [[entities/benchmarks/swe-bench-verified-exact]] — SWE-bench Verified (exact import)

## Sources

- <https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
