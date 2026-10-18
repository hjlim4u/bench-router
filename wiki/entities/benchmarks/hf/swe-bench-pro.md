---
title: >-
    SWE-bench Pro
category: entities
tags: [benchmark, hf-official, coding]
sources: ["url:https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Long-horizon software engineering tasks from real PRs in 11 open-source repositories, graded by hidden tests
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# SWE-bench Pro

Long-horizon software engineering tasks from real PRs in 11 open-source repositories, graded by hidden tests.

From the dataset card (`ScaleAI/SWE-bench_Pro`):

> SWE-bench Pro V2 SWE-bench Pro is a benchmark of long-horizon software engineering tasks drawn from real pull requests in 11 open-source repositories (Go, Python, JavaScript, TypeScript). Each task gives an agent a repository at a base commit plus a PR description with explicit requirements and interfaces; the agent's patch is graded by hidden fail-to-pass and pass-to-pass tests in a pristine container.

## Index

```toml
[[unit]]
id = "hf:ScaleAI/SWE-bench_Pro"
desc = "Long-horizon software engineering tasks from real PRs in 11 open-source repositories, graded by hidden tests"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["repo_coding"], shape = ["long_horizon"] }
reason = "Leaderboard API (2026-10-18): 47 rows, 47 models, 0 verified, 13 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/shape|shape]]: long_horizon
- [[concepts/facets/task|task]]: repo_coding

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/hf/swe-bench-multilingual]] — SWE-bench Multilingual
- [[entities/benchmarks/hf/swe-bench-multimodal]] — SWE-bench Multimodal
- [[entities/benchmarks/mg/deepswe]] — DeepSWE
- [[entities/benchmarks/mg/swe-bench-verified]] — SWE-bench Verified
- [[entities/benchmarks/swe-bench-verified-exact]] — SWE-bench Verified (exact import)

## Sources

- <https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
