---
title: >-
    SWE-bench Verified (exact import)
category: entities
tags: [benchmark, exact, coding]
relationships:
  - target: "[[entities/benchmarks/mg/swe-bench-verified]]"
    type: related_to
sources: ["repo:bench_router/data.py"]
summary: >-
    Manual SWE-bench Verified import matched to the profile's harness and effort. Saturated, so it discriminates poorly.
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# SWE-bench Verified (exact import)

Manual SWE-bench Verified import matched to the profile's harness and effort. Saturated, so it discriminates poorly. The import contract is `EXACT_PINS` in `bench_router/data.py`.

Related: [[entities/benchmarks/mg/swe-bench-verified]]

## Index

```toml
[[unit]]
id = "swe_verified_exact"
desc = "Share of real GitHub issues whose patch passes the hidden tests"
metric = "pass_pct"
status = "saturated"
adoption = "archive"
reason = "Saturated, like its model-proxy page; kept for lookup. The legacy categories.toml path still reads swe_verified_exact"
facets = { task = ["repo_coding"] }
```

## Facets

- [[concepts/facets/task|task]]: repo_coding

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/hf/swe-bench-multilingual]] — SWE-bench Multilingual
- [[entities/benchmarks/hf/swe-bench-multimodal]] — SWE-bench Multimodal
- [[entities/benchmarks/hf/swe-bench-pro]] — SWE-bench Pro
- [[entities/benchmarks/mg/deepswe]] — DeepSWE
- [[entities/benchmarks/mg/swe-bench-verified]] — SWE-bench Verified
- [[entities/benchmarks/terminal-bench-exact]] — Terminal-Bench 4.0 (exact import)

## Sources

- `bench_router/data.py` `EXACT_PINS`, `validate_import`
