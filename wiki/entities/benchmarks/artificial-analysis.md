---
title: >-
    Artificial Analysis indexes
category: entities
tags: [benchmark, aa, coding, general]
sources: ["url:https://artificialanalysis.ai/api/v2/language/models/free"]
summary: >-
    Per-model aggregate indexes from the Artificial Analysis Free API. Collected only when an API key is set.
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-31T00:00:00Z
---
# Artificial Analysis indexes

Per-model aggregate indexes from the Artificial Analysis Free API (`/api/v2/language/models/free`). The adapter reads only `artificial_analysis_intelligence_index` and `artificial_analysis_coding_index` (`AA_FIELDS` in `bench_router/data.py`).

## Index

```toml
[[unit]]
id = "aa_intelligence"
desc = "AA Intelligence Index (aggregate of several evaluations)"
metric = "index"
status = "current"
adoption = "active"
facets = { task = ["general"] }
reason = "Collected only when ARTIFICIAL_ANALYSIS_API_KEY is set"

[[unit]]
id = "aa_coding"
desc = "AA Coding Index (aggregate of coding evaluations)"
metric = "index"
status = "current"
adoption = "active"
facets = { task = ["coding"] }
reason = "Collected only when ARTIFICIAL_ANALYSIS_API_KEY is set"
```

## Open Questions

- Without an API key the other evaluation fields of the Free response were not checked. Decide on extra fields at ingest time once a key is available.
- As of 2026-10-31 the Intelligence Index is v5.0: nine evaluations in four categories at 25% each (see [[references/sources/artificial-analysis-methodology]]). The methodology capture does not say which evaluations the Coding Index averages. Whether the adapter records the index version with each score is unchecked.
- OpenRouter's benchmarks API re-serves AA `intelligence_index`, `coding_index` and `agentic_index` per model ([[references/sources/openrouter-benchmarks]]). It is a possible keyed fallback route, not yet evaluated.

## Facets

- [[concepts/facets/task|task]]: coding, general

## Related benchmarks

- [[entities/benchmarks/hf/ace]] — ACE
- [[entities/benchmarks/hf/evasionbench]] — EvasionBench
- [[entities/benchmarks/hf/mmlu-pro]] — MMLU-Pro
- [[entities/benchmarks/hf/typed-decisions]] — Typed Decisions
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)

## Sources

- <https://artificialanalysis.ai/api/v2/language/models/free>
- `bench_router/data.py` `AA_FIELDS`
- [[references/sources/artificial-analysis-methodology]] — Index v5.0 composition and testing parameters, captured 2026-10-31.
