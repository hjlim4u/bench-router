---
title: >-
    τ²-Bench Airline (OpenRouter)
category: entities
tags: [benchmark, agentic]
relationships:
  - target: "[[references/sources/openrouter-benchmarks]]"
    type: derived_from
  - target: "[[entities/benchmarks/mg/toolathlon-verified]]"
    type: related_to
sources: ["url:https://openrouter.ai/benchmarks/tau2-bench-airline", "url:https://openrouter.ai/api/v1/datasets/exports/README.md"]
summary: >-
    Multi-turn airline service agent making tool calls under strict policy constraints, run by OpenRouter against production provider endpoints.
base_confidence: 0.45
lifecycle: reviewed
lifecycle_changed: 2026-11-01
lifecycle_reason: "Reviewed 2026-11-01 at the user's request (assistant review, not independent): grading, step cap, simulator pin, aggregation window and sample floor, provider-variance quote and checker limits checked against _raw/_archived/2026-10-30-openrouter-tau2-bench-airline.md; coverage against the 2026-11-01 export. Adoption stays candidate pending a measurement-validity decision."
tier: supporting
created: 2026-11-01T00:00:00Z
updated: 2026-11-01T00:00:00Z
---
# τ²-Bench Airline (OpenRouter)

Multi-turn service agents making tool calls under strict policy constraints. OpenRouter runs it continuously on its benchmark harness against public endpoints, so a score reflects the model **and** the provider serving it.

## Key Ideas

- Grading: `db_match × communicate_met`, binary per task; hitting the 200-step cap scores 0. The user simulator is pinned to gemini-2.5-flash, so absolute scores rarely match other papers.
- Aggregation: task-weighted mean over the newest 90 days of successful, non-zero runs. At least 45 graded tasks per model–provider pair.
- OpenRouter states it uses τ² "because it has a high floor, so we can assess provider variance and not model capability". Its provider deltas drive Exacto routing.
- Known checker limits: many tasks reward inaction, and the checker greps exact substrings, so "$23,552.50" fails a check for "23553".
- Collection: the keyless daily `benchmark-leaderboard` export (CC BY 4.0), checked against the manifest's SHA-256. For each model the collector takes the newest model version, then its `auto-routing` (default routing) row, else the median provider row. The choice is kept in the observation `conditions.representative`.

## Index

```toml
[[unit]]
id = "or:tau_bench_verified_airline/default"
desc = "Multi-turn airline service agent with tool calls under policy constraints; OpenRouter auto-routing row per model, else the median provider."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"] }
reason = "Coverage 2026-11-01: 13 enabled profile models (12 auto-routing rows, gpt-6.1-terra via median provider). Kept candidate: OpenRouter says it measures provider variance more than model capability, and the pinned user simulator and substring checker limit what a score says about CLI-agent tool use. Promotion needs a separate measurement-validity review"
trust_grade = "C"
```

## Facets

- [[concepts/facets/task|task]]: multi_tool

## Open Questions

- Whether an auto-routing deployment score is a fair model proxy for a CLI agent profile that calls the vendor directly.
- No `meaningful_gap` is set. Run-level `accuracy_std_dev` (population std dev across runs, null with one run) is kept in the observation conditions, but it is not a confidence interval.
- The export has no per-row harness version; the harness repository history is the version record.

## Related benchmarks

- [[entities/benchmarks/mg/toolathlon-verified]] — Toolathlon Verified (`multi_tool`)

## Sources

- [[references/sources/openrouter-benchmarks]]
- [[_raw/_archived/2026-10-30-openrouter-tau2-bench-airline]] — leaderboard page capture with methodology.
- <https://openrouter.ai/api/v1/datasets/exports/README.md> — export column definitions and methodology.
