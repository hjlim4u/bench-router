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
updated: 2026-11-01T00:00:00Z
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
adoption = "archive"
facets = { task = ["coding"] }
reason = "AA no longer publishes a Coding Index (site and Free API checked 2026-11-01); coding is folded into Intelligence Index v5.0 via Terminal-Bench 4.0 and FrontierCode 2.0"
```

## Open Questions

- Checked with a key on 2026-11-01 (`x-aa-tier: free`, 719 models, 4 pages): field names are unchanged, but `artificial_analysis_coding_index` and `artificial_analysis_agentic_index` are null for every model. The intelligence index and the domain indexes (finance, strategy/ops, legal, healthcare, engineering, economics) are filled only for about 90–110 models, all released on or after 2026-03-16. Current profile models (Claude 5.5, Fable 5.1, GPT-6.1 Sol, Gemini 4 Argon) do have intelligence values. The AA site (model pages, `/models`, intelligence methodology, checked in a browser 2026-11-01) shows no Coding Index either: its Capability Indexes are Finance & Accounting, Strategy & Ops, Legal, Healthcare & Medical, Engineering and Economics, and Intelligence Index v5.0 lists 9 evaluations (AA-Briefcase v1.1, AutomationBench-AA, Terminal-Bench 4.0, FrontierCode 2.0, AA-Omniscience v1.1, GDP.pdf, HLE-Diamond, CritPt v2 Hard Subset, Terminal-Bench-Science 0.1). So the Coding Index was discontinued, not moved to a paid tier.
- OpenRouter's keyed `/api/v1/benchmarks` (checked 2026-11-01) still returns `coding_index` for 152 of 167 AA models, but only for models released before the change (e.g. GPT-5.6, GPT-6 Astra, Fable 5.1, Gemini 3.8 Flash); Claude 5.5, GPT-6.1 and Gemini 4 Argon are null and no index version is given. These are legacy values and are not collected. ^[inferred]
- As of 2026-10-31 the Intelligence Index is v5.0: nine evaluations in four categories at 25% each (see [[references/sources/artificial-analysis-methodology]]). The methodology capture does not say which evaluations the Coding Index averages. Whether the adapter records the index version with each score is unchecked.
- OpenRouter's benchmarks API re-serves AA `intelligence_index`, `coding_index` and `agentic_index` per model ([[references/sources/openrouter-benchmarks]]). It is a possible keyed fallback route, not yet evaluated. The keyless daily export carries only `gpqa_diamond` and `tau_bench_verified_airline` rows (checked 2026-11-01), so it is no substitute; `/api/v1/benchmarks` returns 401 without an OpenRouter key.

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
