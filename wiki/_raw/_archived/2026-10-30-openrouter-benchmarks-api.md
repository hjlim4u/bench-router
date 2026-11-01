---
title: "List Benchmarks"
site: "OpenRouter | Documentation"
source: "https://openrouter.ai/docs/api/api-reference/benchmarks/list-benchmarks"
domain: "openrouter.ai"
language: "en"
description: "Unified benchmark endpoint that aggregates scores from multiple benchmark sources (Artificial Analysis, Design Arena, and OpenRouter's own tau-bench, GPQA, and web-search evals). Filter by source to reproduce the exact shapes from the legacy per-source endpoints, or use task_type to find models suited for specific workloads. Use task_type=search (or a search_* benchmark_type) for OpenRouter's search benchmarks, which publish each model's highest-scoring eligible evaluation configuration with same-configuration runs combined by task-weighted mean. Authenticate with any valid OpenRouter API key. Rate-limited to 30 requests/minute per key and 500 requests/day per account."
word_count: 351
---

List Benchmarks

GET

/

benchmarks

List Benchmarks

#### Query Parameterssource

enum\<string>

Benchmark source to query. Determines the shape of the returned items. When omitted, returns results from all sources.

Available options:

`artificial-analysis`,

`design-arena`,

`openrouter`

Example:

`"artificial-analysis"`task\_type

enum\<string>

Filter results by task type. For Artificial Analysis, maps to the corresponding index. For Design Arena, maps to the matching category. `search` returns OpenRouter search benchmark results only.

Available options:

`coding`,

`intelligence`,

`agentic`,

`search`

Example:

`"coding"`benchmark\_type

enum\<string>

Return results for one exact OpenRouter benchmark. A `search_*` value narrows the response to search results only; a classic value narrows the OpenRouter items and leaves other sources' items as they are.

Available options:

`gpqa_diamond`,

`tau_bench_verified_airline`,

`search_browsecomp`,

`search_hle`,

`search_dsqa`,

`search_widesearch`

Example:

`"search_widesearch"`include\_run\_config

boolean

default:false

Search benchmarks only: include the published lane configuration whitelist in each search item. Defaults to false. The whitelist is limited to agent turn count, reasoning effort, and temperature so future harness configuration changes do not change the public contract.

Example:

`true`

OpenRouter search benchmarks only: filter by the search engine used.

Example:

`"exa"`

OpenRouter search benchmarks only: filter by the request surface the lane ran on.

Available options:

`server-tool`,

`plugin`

Example:

`"server-tool"`arena

enum\<string>

Design Arena only: arena to query. Defaults to `models` when source is `design-arena`.

Available options:

`models`,

`builders`,

`agents`

Example:

`"models"`category

string

Design Arena only: category within the arena (e.g. `codecategories`, `uicomponent`, `gamedev`, `3d`, `dataviz`, `image`, `video`, `svg`). When omitted, returns all categories.

Example:

`"codecategories"`max\_results

integer

Maximum number of items to return. When omitted, all matching results are returned.

Required range: `x >= 1`

Example:

`50`

#### Response

Benchmark results filtered by the specified source and optional task type.data

object\[\]

required

Show child attributes

```
{
  "agentic_index": 58.3,
  "coding_index": 65.8,
  "display_name": "GPT-4o",
  "intelligence_index": 71.2,
  "model_permaslug": "openai/gpt-4o",
  "pricing": {
    "completion": "0.00001",
    "prompt": "0.0000025"
  },
  "source": "artificial-analysis"
}
```meta

object

required

Show child attributes

```
{
  "as_of": "2026-06-03T12:00:00Z",
  "citation": "Source: Artificial Analysis (artificialanalysis.ai) via OpenRouter (openrouter.ai/rankings).",
  "model_count": 50,
  "source": "artificial-analysis",
  "source_url": "https://artificialanalysis.ai",
  "task_type": null,
  "version": "v1"
}
```