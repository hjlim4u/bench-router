---
title: >-
  OpenRouter benchmarks
category: references
tags: [source, benchmark, agentic, search]
sources:
  - "url:https://openrouter.ai/benchmarks"
  - "url:https://openrouter.ai/docs/api/api-reference/benchmarks/list-benchmarks"
created: 2026-10-31T00:00:00Z
updated: 2026-10-31T00:00:00Z
as_of: 2026-10-30
summary: >-
  OpenRouter's continuously run benchmark suite (GPQA, τ²-Airline, VGI, search, artifact/media, routers): what each measures, how it is graded, and how to read it.
provenance:
  extracted: 0.85
  inferred: 0.12
  ambiguous: 0.03
base_confidence: 0.58
lifecycle: draft
lifecycle_changed: 2026-10-31
tier: supporting
relationships:
  - target: "[[entities/benchmarks/mg/gpqa-diamond]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/hle]]"
    type: related_to
  - target: "[[references/sources/artificial-analysis-methodology]]"
    type: related_to
  - target: "[[projects/bench-router/synthesis/openrouter-router-benchmarks]]"
    type: related_to
snapshots:
  - "[[_raw/_archived/2026-10-30-openrouter-benchmarks-api|2026-10-30-openrouter-benchmarks-api]]"
  - "[[_raw/_archived/2026-10-30-openrouter-benchmarks|2026-10-30-openrouter-benchmarks]]"
  - "[[_raw/_archived/2026-10-30-openrouter-browsecomp|2026-10-30-openrouter-browsecomp]]"
  - "[[_raw/_archived/2026-10-30-openrouter-gpqa-diamond|2026-10-30-openrouter-gpqa-diamond]]"
  - "[[_raw/_archived/2026-10-30-openrouter-tau2-bench-airline|2026-10-30-openrouter-tau2-bench-airline]]"
  - "[[_raw/_archived/2026-10-31-openrouter-deepsearchqa|2026-10-31-openrouter-deepsearchqa]]"
  - "[[_raw/_archived/2026-10-31-openrouter-games|2026-10-31-openrouter-games]]"
  - "[[_raw/_archived/2026-10-31-openrouter-hle|2026-10-31-openrouter-hle]]"
  - "[[_raw/_archived/2026-10-31-openrouter-media-images|2026-10-31-openrouter-media-images]]"
  - "[[_raw/_archived/2026-10-31-openrouter-media-memes|2026-10-31-openrouter-media-memes]]"
  - "[[_raw/_archived/2026-10-31-openrouter-media-speech|2026-10-31-openrouter-media-speech]]"
  - "[[_raw/_archived/2026-10-31-openrouter-media-videos|2026-10-31-openrouter-media-videos]]"
  - "[[_raw/_archived/2026-10-31-openrouter-sketch|2026-10-31-openrouter-sketch]]"
  - "[[_raw/_archived/2026-10-31-openrouter-vgi-bench|2026-10-31-openrouter-vgi-bench]]"
  - "[[_raw/_archived/2026-10-31-openrouter-widesearch|2026-10-31-openrouter-widesearch]]"
---

# OpenRouter benchmarks

OpenRouter publishes "independent, reproducible measurements of the knobs you can actually set on an OpenRouter request: models, providers, search engines, and tool budgets." On 2026-10-30 the index listed 13 benchmarks and 2,302,647 task evaluations. Runs execute on Kepler, OpenRouter's benchmark harness, against production provider endpoints, so a score reflects the model **and** the provider serving it.

The suite is a mirror and complement to collectors already in this wiki, not a new unit source: no `[[unit]]` id format exists for OpenRouter (see Open Questions).

## Leaderboards

| Group | Benchmark | What varies | Grading | Snapshot leader (as of capture) |
|---|---|---|---|---|
| Agents & tools | τ²-Bench Airline | model × provider | `db_match × communicate_met`, binary; hitting the 200-step cap scores 0 | GPT-5.1, 80.0% (146 models) |
| Reasoning | GPQA Diamond | model × provider | multiple-choice accuracy | Gemini 4 Argon (Google provider), 96.5% (167 models) |
| Reasoning | VGI-Bench | model × provider | multiple-choice letter on final `Answer:` line, 439-question public split, ≥395 answered to be listed | Seed 1.6, 66.2% (60 models) |
| Search | BrowseComp | engine × request surface × search budget, model fixed | GPT-4.1 judge, answer equivalence, binary | Perplexity + Claude Opus 5 (high), 25-turn, 89.0% |
| Search | HLE (search) | same | same judge; 2,158 text-only questions | Perplexity + Claude Opus 5 (high), 25-turn, 77.4% |
| Search | DeepSearchQA | same | Gemini 2.5 Flash judge; all expected list parts and no extras, binary | Parallel + Claude Opus 5 (high), 25-turn, 77.0% |
| Search | WideSearch | same | answer-item F1; complete-table rate also shown | Perplexity + GPT-5.6 Sol (high), 25-turn, 84.0% item F1, 21% complete tables |
| Artifact generation | Sketch, Games | model | per-prompt galleries with cost and time; Sketch shows model-judged scores | — |
| Media | Images, Memes, Speech, Videos | model | per-prompt pass counts (e.g. 4/4, Pass, Correctness %) | — |
| Routing | Model routers | router or model × effort | "Model Routing Index" across six benchmarks | see [[projects/bench-router/synthesis/openrouter-router-benchmarks]] |

Search leaders are dated Aug 11–Sep 15, 2026, not Oct 30; those leaderboards compare only 3–5 models.

## Aggregation rules

- Classic leaderboards (GPQA, τ², VGI) aggregate successful runs from the newest 90 days, weighted by question or task count. τ² requires at least 45 graded tasks per model-provider pair.
- The headline row uses default routing (not pinned to a provider) when available, else the median provider. Provider-pinned rows expand under it.
- "Best value" is the cheapest Pareto-optimal model within five percentage points of the top score.
- Cost, time and output tokens are per-question or per-task averages from the same runs.
- Search scores weight by questions per verified run and exclude small smoke tests. Overlapping 95% confidence ranges are "treated as unresolved here, not as proof of equality."

## How OpenRouter says to read each benchmark

- **GPQA Diamond** is run as "a cheap, high-floor signal that a deployment is healthy." A large accuracy gap between providers serving the same model points to a degraded endpoint. OpenRouter calls it "a narrow, high-difficulty evaluation, not a complete measure of general intelligence."
- **τ²-Bench Airline** is used "because it has a high floor, so we can assess provider variance and not model capability." Its provider deltas drive Exacto routing; tool-call errors on Auto Exacto–enrolled models fell from 3.9% to 1.7%. Limits it states: many tasks reward inaction, the checker greps exact substrings (so "$23,552.50" fails a check for "23553"), and the user simulator is pinned to gemini-2.5-flash, so absolute scores rarely match other papers.
- **Search benchmarks** hold the model fixed to isolate what a request controls: engine, server-tool vs plugin, and agent-turn budget. The model reads search excerpts only, with no page fetch or code tools, so "absolute numbers sit below published agent leaderboards." Compare configurations, not levels.
- BrowseComp shows the budget effect most clearly: the winning configuration scored 35.8% at 1 turn, 66.5% at 5, 89.0% at 25. On HLE the gap is small (75.3% at 1 turn vs 77.4% at 25), because HLE "leans on expertise rather than browsing depth."

## Snapshot: current profile models

From the 2026-10-30 leaderboards, default-routing rows. ^[inferred] (mapping display names to profile ids `claude-opus-5-5`, `gpt-6.1-sol`, `gemini-4-argon`)

| Model | GPQA Diamond | τ²-Bench Airline |
|---|---|---|
| Gemini 4 Argon | 96.0% ($0.029/q; 96.5% on the Google-pinned row) | 78.7% ($0.50/task, rank 6) |
| GPT-6.1 Sol | 94.4% ($0.021/q, Pareto) | 70.0% ($0.10/task, rank 86) |
| Claude Opus 5.5 | 90.2% ±0.6pp ($0.054/q) | 75.2% ±1.9pp ($0.34/task) |

GPT-6.1 Sol's τ² rank sits far below its GPQA rank. With no std dev reported for that row, this may be a sparse or provider-specific result rather than a capability gap. ^[ambiguous]

## API and datasets

- `GET https://openrouter.ai/api/v1/benchmarks` (Bearer key) merges three sources: `artificial-analysis`, `design-arena`, `openrouter`. `task_type` ∈ `coding`, `intelligence`, `agentic`, `search`; `benchmark_type` ∈ `gpqa_diamond`, `tau_bench_verified_airline`, `search_browsecomp`, `search_hle`, `search_dsqa`, `search_widesearch`.
- Artificial Analysis items carry `intelligence_index`, `coding_index`, `agentic_index` and pricing, with the citation "Source: Artificial Analysis (artificialanalysis.ai) via OpenRouter". This is a second route to the AA indexes that [[entities/benchmarks/artificial-analysis]] collects directly. ^[inferred]
- OpenRouter items include `accuracy`, `accuracy_stddev`, `avg_cost_per_task`, `total_tasks`, `last_run_timestamp`.
- Daily keyless CC BY 4.0 snapshots: `benchmark-leaderboard` and `search-benchmark-lanes` under `https://openrouter.ai/api/v1/datasets/exports/`, with SHA-256 manifests.

## Open Questions

- No `[[unit]]` id format covers OpenRouter. Adding one (e.g. `or:<benchmark>`) would need an adapter in `bench_router/data.py` and a schema change in `wiki/AGENTS.md`.
- τ²-Bench Airline overlaps the `multi_tool` task facet, but OpenRouter states it measures provider variance more than model capability. Whether it should feed routing at all is undecided.
- The routers page defines no scale or method for its "Model Routing Index"; the capture is a table extract only.
- Sketch scores ("Toughest critic", "Biggest fan" vs median) imply model judges, but the capture does not state the judging method.

## Related

- [[references/sources/artificial-analysis-methodology]]
- [[references/sources/themodelgap-data]]
- [[entities/benchmarks/mg/gpqa-diamond]]
- [[entities/benchmarks/mg/hle]]
- [[entities/benchmarks/lmarena-search]]
- [[projects/bench-router/synthesis/openrouter-router-benchmarks]]

## Sources

- [[_raw/_archived/2026-10-30-openrouter-benchmarks]] — index page capture.
- [[_raw/_archived/2026-10-30-openrouter-benchmarks-api]] — List Benchmarks API reference.
- [[_raw/_archived/2026-10-30-openrouter-gpqa-diamond]], [[_raw/_archived/2026-10-30-openrouter-tau2-bench-airline]], [[_raw/_archived/2026-10-31-openrouter-vgi-bench]] — classic leaderboards with methodology.
- [[_raw/_archived/2026-10-30-openrouter-browsecomp]], [[_raw/_archived/2026-10-31-openrouter-hle]], [[_raw/_archived/2026-10-31-openrouter-deepsearchqa]], [[_raw/_archived/2026-10-31-openrouter-widesearch]] — search leaderboards.
- [[_raw/_archived/2026-10-31-openrouter-sketch]], [[_raw/_archived/2026-10-31-openrouter-games]], [[_raw/_archived/2026-10-31-openrouter-media-images]], [[_raw/_archived/2026-10-31-openrouter-media-memes]], [[_raw/_archived/2026-10-31-openrouter-media-speech]], [[_raw/_archived/2026-10-31-openrouter-media-videos]] — artifact and media galleries.
- `_raw/web/openrouter-*.json` — structured extracts of the same pages (index, GPQA, τ², VGI, search, artifacts, routers), 2026-10-30.
