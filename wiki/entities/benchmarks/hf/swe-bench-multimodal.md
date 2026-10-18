---
title: >-
    SWE-bench Multimodal
category: entities
tags: [benchmark, hf-official, coding, vision]
sources: ["url:https://huggingface.co/datasets/SWE-bench/SWE-bench_Multimodal", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    GitHub issues in visual JS/TS software domains, each with at least one image asset
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# SWE-bench Multimodal

GitHub issues in visual JS/TS software domains, each with at least one image asset.

From the dataset card (`SWE-bench/SWE-bench_Multimodal`):

> SWE-bench Multimodal Dataset Summary SWE-bench Multimodal is a dataset that tests systems' ability to resolve real-world GitHub issues in visual software domains.

## Index

```toml
[[unit]]
id = "hf:SWE-bench/SWE-bench_Multimodal"
desc = "GitHub issues in visual JS/TS software domains, each with at least one image asset"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["repo_coding", "vision"] }
reason = "Leaderboard API (2026-10-18) returned no rows; no model scores are published yet. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: repo_coding, vision

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/hf/mmmu-pro]] — MMMU-Pro
- [[entities/benchmarks/hf/swe-bench-multilingual]] — SWE-bench Multilingual
- [[entities/benchmarks/hf/swe-bench-pro]] — SWE-bench Pro
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)
- [[entities/benchmarks/mg/deepswe]] — DeepSWE

## Sources

- <https://huggingface.co/datasets/SWE-bench/SWE-bench_Multimodal>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
