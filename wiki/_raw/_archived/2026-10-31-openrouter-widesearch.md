---
title: "WideSearch Leaderboard"
site: "OpenRouter"
published: Aug 18, 2026, 2:39 AM UTC
source: "https://openrouter.ai/benchmarks/widesearch"
domain: "openrouter.ai"
language: "en-US"
description: "Compare WideSearch answer-item accuracy, strict complete-table success, cost, and speed across OpenRouter search providers and search budgets."
word_count: 2530
---

## WideSearch

WideSearch asks the model to fill in an entire table: given a query and a required column schema, it has to find every entity and every attribute, like all launches of a rocket family with dates and outcomes. Its 200 tasks (100 English, 100 Chinese) are graded strictly — a task counts only when every row and every cell matches the reference table. We run it with the model held fixed and vary the search engine, request format, and maximum search budget. Where BrowseComp goes deep on one hidden fact, WideSearch goes wide across many facts and attributes.

[Paper](https://arxiv.org/abs/2508.07999) [Project](https://widesearch-seed.github.io/) [Dataset](https://huggingface.co/datasets/ByteDance-Seed/WideSearch)

Search providers

4 search providers

compared across configurations

Models

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)

4 models

GPT-5.6 Luna, GPT-5.6 Sol, Claude Opus 5, and DeepSeek V4 Flash 0731

Test configurations

1 / 5 / 25

search budgets and plugin mode

## Which search configuration leads WideSearch?

GPT-5.6 Sol · high, using Perplexity with 25-turn as of Aug 11, 2026 leads at 84.0% Item F1, the benchmark's answer-item accuracy measure. Displayed scores are rounded to one decimal place, so configurations listed together are co-leaders at that displayed precision. The comparison uses the same verified SSR lanes and WideSearch methodology shown below.

Highest quality

Perplexity25-turn

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

GPT-5.6 Sol · high

84.0%answer-item accuracy

Winning result in detail

Complete tables

21.0% · 21 of 100

Incomplete tables

79 of 100

Cost / question

$0.83

Mean generation time / question

2.3m

Best value

$0.063 / question

Perplexity

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

GPT-5.6 Luna · xhigh5-turn search budget 80.0% answer-item accuracy

Fastest strong result

1.9m / question

Perplexity

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

GPT-5.6 Sol · high1-turn search budget 79.8% answer-item accuracy

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg) ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)

Perplexity

GPT-5.6 Sol · high 25-turn

84.0%

21.0% complete tables

OpenAI Native

GPT-5.6 Sol · high 25-turn

81.8%

16.0% complete tables

Parallel

GPT-5.6 Sol · high 25-turn

80.6%

16.5% complete tables

Exa

GPT-5.6 Luna · xhigh 25-turn

78.0%

16.0% complete tables

Answer-item accuracy Complete tables

### Price versus quality

Average cost per question on a logarithmic scale. The line shows the best quality available at each price level.

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg) ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)

- Perplexity
- OpenAI Native
- Parallel
- Exa
- Perplexity, 25-turn: GPT-5.6 Luna · xhigh, 83.4% answer-item accuracy, 22.0% complete tables, $0.17, on the efficiency and quality frontier
- Perplexity, 25-turn: GPT-5.6 Sol · high, 84.0% answer-item accuracy, 21.0% complete tables, $0.83, on the efficiency and quality frontier
- Perplexity, 25-turn: Claude Opus 5 · high, 68.2% answer-item accuracy, 20.2% complete tables, $2.14
- Perplexity, 25-turn: DeepSeek V4 Flash 0731 · high, 77.1% answer-item accuracy, 20.0% complete tables, $0.10
- Perplexity, 5-turn: GPT-5.6 Luna · xhigh, 80.0% answer-item accuracy, 18.0% complete tables, $0.063, on the efficiency and quality frontier
- Perplexity, 5-turn: GPT-5.6 Sol · high, 81.4% answer-item accuracy, 18.0% complete tables, $0.45
- Perplexity, 5-turn: DeepSeek V4 Flash 0731 · high, 72.1% answer-item accuracy, 17.3% complete tables, $0.050, on the efficiency and quality frontier
- OpenAI Native, 5-turn: GPT-5.6 Sol · high, 78.4% answer-item accuracy, 17.0% complete tables, $0.53
- Parallel, 25-turn: GPT-5.6 Sol · high, 80.6% answer-item accuracy, 16.5% complete tables, $1.46
- Exa, 25-turn: GPT-5.6 Luna · xhigh, 78.0% answer-item accuracy, 16.0% complete tables, $0.22
- OpenAI Native, 25-turn: GPT-5.6 Sol · high, 81.8% answer-item accuracy, 16.0% complete tables, $0.98
- Exa, 25-turn: DeepSeek V4 Flash 0731 · high, 74.5% answer-item accuracy, 15.0% complete tables, $0.15
- Parallel, 25-turn: Claude Opus 5 · high, 65.9% answer-item accuracy, 13.6% complete tables, $4.42
- Parallel, 5-turn: GPT-5.6 Sol · high, 77.8% answer-item accuracy, 13.5% complete tables, $0.60
- Perplexity, 5-turn: Claude Opus 5 · high, 67.8% answer-item accuracy, 13.1% complete tables, $0.74
- Perplexity, 1-turn: GPT-5.6 Sol · high, 79.8% answer-item accuracy, 13.0% complete tables, $0.26
- Parallel, 1-turn: GPT-5.6 Sol · high, 77.4% answer-item accuracy, 13.0% complete tables, $0.33
- OpenAI Native, 1-turn: GPT-5.6 Sol · high, 76.9% answer-item accuracy, 13.0% complete tables, $0.35
- Exa, 5-turn: Claude Opus 5 · high, 65.8% answer-item accuracy, 12.1% complete tables, $0.62
- Exa, 25-turn: Claude Opus 5 · high, 67.0% answer-item accuracy, 12.1% complete tables, $1.85
- Exa, 5-turn: GPT-5.6 Luna · xhigh, 75.7% answer-item accuracy, 12.0% complete tables, $0.075
- Exa, 25-turn: GPT-5.6 Sol · high, 77.4% answer-item accuracy, 11.6% complete tables, $0.86
- Exa, 5-turn: GPT-5.6 Sol · high, 74.4% answer-item accuracy, 11.6% complete tables, $0.47
- Parallel, 5-turn: Claude Opus 5 · high, 65.2% answer-item accuracy, 11.5% complete tables, $0.95
- Parallel, 25-turn: GPT-5.6 Luna · xhigh, 74.4% answer-item accuracy, 11.5% complete tables, $0.12
- Perplexity, 1-turn: GPT-5.6 Luna · xhigh, 71.1% answer-item accuracy, 11.0% complete tables, $0.037, on the efficiency and quality frontier
- Parallel, 5-turn: GPT-5.6 Luna · xhigh, 72.9% answer-item accuracy, 11.0% complete tables, $0.058, on the efficiency and quality frontier
- Perplexity, 1-turn: Claude Opus 5 · high, 65.8% answer-item accuracy, 10.0% complete tables, $0.23
- Parallel, 25-turn: DeepSeek V4 Flash 0731 · high, 71.2% answer-item accuracy, 9.8% complete tables, $0.089
- Exa, 5-turn: DeepSeek V4 Flash 0731 · high, 66.3% answer-item accuracy, 9.2% complete tables, $0.059
- Exa, 1-turn: GPT-5.6 Sol · high, 68.2% answer-item accuracy, 8.5% complete tables, $0.29
- Parallel, 1-turn: GPT-5.6 Luna · xhigh, 67.9% answer-item accuracy, 8.5% complete tables, $0.039
- Parallel, 1-turn: Claude Opus 5 · high, 61.7% answer-item accuracy, 8.0% complete tables, $0.26
- Exa, 1-turn: GPT-5.6 Luna · xhigh, 69.1% answer-item accuracy, 8.0% complete tables, $0.038
- Parallel, 5-turn: DeepSeek V4 Flash 0731 · high, 66.2% answer-item accuracy, 8.0% complete tables, $0.040
- Exa, 1-turn: Claude Opus 5 · high, 59.6% answer-item accuracy, 5.5% complete tables, $0.26
- Parallel, 1-turn: DeepSeek V4 Flash 0731 · high, 59.4% answer-item accuracy, 4.0% complete tables, $0.019, on the efficiency and quality frontier

### Mean generation time versus quality

Sample-weighted mean generation time per question. The line shows the best quality available at each time level.

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg) ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)

- Perplexity
- OpenAI Native
- Parallel
- Exa
- Perplexity, 25-turn: GPT-5.6 Luna · xhigh, 83.4% answer-item accuracy, 22.0% complete tables, 2.7m
- Perplexity, 25-turn: GPT-5.6 Sol · high, 84.0% answer-item accuracy, 21.0% complete tables, 2.3m, on the efficiency and quality frontier
- Perplexity, 25-turn: Claude Opus 5 · high, 68.2% answer-item accuracy, 20.2% complete tables, 2.5m
- Perplexity, 25-turn: DeepSeek V4 Flash 0731 · high, 77.1% answer-item accuracy, 20.0% complete tables, 2.0m
- Perplexity, 5-turn: GPT-5.6 Luna · xhigh, 80.0% answer-item accuracy, 18.0% complete tables, 2.4m
- Perplexity, 5-turn: GPT-5.6 Sol · high, 81.4% answer-item accuracy, 18.0% complete tables, 2.2m, on the efficiency and quality frontier
- Perplexity, 5-turn: DeepSeek V4 Flash 0731 · high, 72.1% answer-item accuracy, 17.3% complete tables, 2.6m
- OpenAI Native, 5-turn: GPT-5.6 Sol · high, 78.4% answer-item accuracy, 17.0% complete tables, 2.7m
- Parallel, 25-turn: GPT-5.6 Sol · high, 80.6% answer-item accuracy, 16.5% complete tables, 2.7m
- Exa, 25-turn: GPT-5.6 Luna · xhigh, 78.0% answer-item accuracy, 16.0% complete tables, 2.9m
- OpenAI Native, 25-turn: GPT-5.6 Sol · high, 81.8% answer-item accuracy, 16.0% complete tables, 3.9m
- Exa, 25-turn: DeepSeek V4 Flash 0731 · high, 74.5% answer-item accuracy, 15.0% complete tables, 2.3m
- Parallel, 25-turn: Claude Opus 5 · high, 65.9% answer-item accuracy, 13.6% complete tables, 3.5m
- Parallel, 5-turn: GPT-5.6 Sol · high, 77.8% answer-item accuracy, 13.5% complete tables, 2.6m
- Perplexity, 5-turn: Claude Opus 5 · high, 67.8% answer-item accuracy, 13.1% complete tables, 1.8m, on the efficiency and quality frontier
- Perplexity, 1-turn: GPT-5.6 Sol · high, 79.8% answer-item accuracy, 13.0% complete tables, 1.9m, on the efficiency and quality frontier
- Parallel, 1-turn: GPT-5.6 Sol · high, 77.4% answer-item accuracy, 13.0% complete tables, 2.0m
- OpenAI Native, 1-turn: GPT-5.6 Sol · high, 76.9% answer-item accuracy, 13.0% complete tables, 2.7m
- Exa, 5-turn: Claude Opus 5 · high, 65.8% answer-item accuracy, 12.1% complete tables, 2.0m
- Exa, 25-turn: Claude Opus 5 · high, 67.0% answer-item accuracy, 12.1% complete tables, 2.8m
- Exa, 5-turn: GPT-5.6 Luna · xhigh, 75.7% answer-item accuracy, 12.0% complete tables, 2.4m
- Exa, 25-turn: GPT-5.6 Sol · high, 77.4% answer-item accuracy, 11.6% complete tables, 3.4m
- Exa, 5-turn: GPT-5.6 Sol · high, 74.4% answer-item accuracy, 11.6% complete tables, 3.1m
- Parallel, 5-turn: Claude Opus 5 · high, 65.2% answer-item accuracy, 11.5% complete tables, 2.1m
- Parallel, 25-turn: GPT-5.6 Luna · xhigh, 74.4% answer-item accuracy, 11.5% complete tables, 3.0m
- Perplexity, 1-turn: GPT-5.6 Luna · xhigh, 71.1% answer-item accuracy, 11.0% complete tables, 2.4m
- Parallel, 5-turn: GPT-5.6 Luna · xhigh, 72.9% answer-item accuracy, 11.0% complete tables, 2.5m
- Perplexity, 1-turn: Claude Opus 5 · high, 65.8% answer-item accuracy, 10.0% complete tables, 70s, on the efficiency and quality frontier
- Parallel, 25-turn: DeepSeek V4 Flash 0731 · high, 71.2% answer-item accuracy, 9.8% complete tables, 3.3m
- Exa, 5-turn: DeepSeek V4 Flash 0731 · high, 66.3% answer-item accuracy, 9.2% complete tables, 2.8m
- Exa, 1-turn: GPT-5.6 Sol · high, 68.2% answer-item accuracy, 8.5% complete tables, 2.8m
- Parallel, 1-turn: GPT-5.6 Luna · xhigh, 67.9% answer-item accuracy, 8.5% complete tables, 2.5m
- Parallel, 1-turn: Claude Opus 5 · high, 61.7% answer-item accuracy, 8.0% complete tables, 77s
- Exa, 1-turn: GPT-5.6 Luna · xhigh, 69.1% answer-item accuracy, 8.0% complete tables, 2.4m
- Parallel, 5-turn: DeepSeek V4 Flash 0731 · high, 66.2% answer-item accuracy, 8.0% complete tables, 2.9m
- Exa, 1-turn: Claude Opus 5 · high, 59.6% answer-item accuracy, 5.5% complete tables, 90s
- Parallel, 1-turn: DeepSeek V4 Flash 0731 · high, 59.4% answer-item accuracy, 4.0% complete tables, 1.8m

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg) ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)

| Search provider | 1-turn | 5-turn | 25-turn |
| --- | --- | --- | --- |
| Perplexity | 79.8%  13.0% complete tables  GPT-5.6 Sol · high | 81.4%  18.0% complete tables  GPT-5.6 Sol · high | 84.0%  21.0% complete tables  GPT-5.6 Sol · high |
| OpenAI Native | 76.9%  13.0% complete tables  GPT-5.6 Sol · high | 78.4%  17.0% complete tables  GPT-5.6 Sol · high | 81.8%  16.0% complete tables  GPT-5.6 Sol · high |
| Parallel | 77.4%  13.0% complete tables  GPT-5.6 Sol · high | 77.8%  13.5% complete tables  GPT-5.6 Sol · high | 80.6%  16.5% complete tables  GPT-5.6 Sol · high |
| Exa | 69.1%  8.0% complete tables  GPT-5.6 Luna · xhigh | 75.7%  12.0% complete tables  GPT-5.6 Luna · xhigh | 78.0%  16.0% complete tables  GPT-5.6 Luna · xhigh |

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg) ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)

| # | Model | Search provider | Search budget | Reasoning effort | Answer-item accuracy | Complete tables | Cost / question | Mean generation time / question | Questions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Sol | Perplexity | 25-turn | high | 84.0% | 21.0% | $0.83 | 2.3m | 100 |
| 2 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Luna | Perplexity | 25-turn | xhigh | 83.4% | 22.0% | $0.17 | 2.7m | 100 |
| 3 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Sol | OpenAI Native | 25-turn | high | 81.8% | 16.0% | $0.98 | 3.9m | 100 |
| 4 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Sol | Perplexity | 5-turn | high | 81.4% | 18.0% | $0.45 | 2.2m | 100 |
| 5 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Sol | Parallel | 25-turn | high | 80.6% | 16.5% | $1.46 | 2.7m | 200 |
| 6 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Luna | Perplexity | 5-turn | xhigh | 80.0% | 18.0% | $0.063 | 2.4m | 100 |
| 7 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Sol | Perplexity | 1-turn | high | 79.8% | 13.0% | $0.26 | 1.9m | 100 |
| 8 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Sol | OpenAI Native | 5-turn | high | 78.4% | 17.0% | $0.53 | 2.7m | 100 |
| 9 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Luna | Exa | 25-turn | xhigh | 78.0% | 16.0% | $0.22 | 2.9m | 100 |
| 10 | ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)  GPT-5.6 Sol | Parallel | 5-turn | high | 77.8% | 13.5% | $0.60 | 2.6m | 200 |

## Why we run this benchmark

WideSearch measures breadth. The agent has to enumerate a full entity set, chase down each attribute, and emit a structured table — closer to real research workflows (market scans, literature surveys, competitive tables) than single-answer trivia. Half the tasks are in Chinese, so it also exercises engines outside English-language results.

We run it with the model held fixed because that isolates the variables OpenRouter users actually control. Those are which engine handles the searches, whether search runs as a server tool or a plugin, and how many agent turns the loop is allowed. Those knobs are exactly what you can set on a request today.

## What the scores can and can't tell you

These scores compare search configurations, not agent products. The model reads search result excerpts only, with no full-page fetching and no code tools, so absolute numbers sit below published agent leaderboards, which allow both. Compare configurations rather than raw levels.

The headline score is answer-item accuracy, which gives partial credit for matched table items so near-misses remain visible. Strict WideSearch Success Rate remains the secondary measure and requires every row and cell in the table to be correct. Even frontier models score low upstream — the paper reports about 4.5% single-agent success for OpenAI o3 (Avg@4), with answer-item accuracy around 52–58% for leading single-agent systems. Engine gaps smaller than the confidence ranges are unresolved, and a configuration's cost should be read alongside its quality.

The questions are public, which means memorization can inflate absolute scores over time; differences between search configurations remain meaningful because every configuration shares the same model.

## How tasks are scored

Each task is one query with a reference table. The model's table is parsed, its rows and columns are aligned to the reference by a judge model, and each cell is compared — exact match where possible, judge-graded equivalence otherwise. A task succeeds only when every reference row is found and every cell matches, with no missing or extra rows.

```
reward = all_rows_aligned ∧ every_cell_correct   // ∈ {0, 1}
judge  = gpt-4.1 at temperature 0 for alignment and fuzzy cells
unparseable or empty tables score 0
```

A search configuration is one model, search engine, request format, and maximum search budget. Scores are weighted by the number of questions in each verified run; small smoke tests are excluded.

### Real run example

Fixed historical runs, independent of the model filter above. Long results and operational metadata are trimmed; selected queries may be edited or omitted.

Task

#### Build a verified clinic table for the Fresno area

Make a comprehensive, verified list of abortion clinics operating in California during 2024 within 65 miles of E Fedora Ave in Fresno. Omit facilities that closed during 2024. Return clinic, county, full address, phone number, and Saturday hours in one Markdown table.

This is a historical 2024 benchmark snapshot, not current healthcare-service guidance.

Reference

Six rows: Planned Parenthood Fulton Street, FPA Women's Health Fresno, Planned Parenthood Family First, Planned Parenthood Madera, Planned Parenthood Merced, and FPA Women's Health Tulare. The reference marks only Fulton Street as open Saturday.

Answer-item accuracy 62.2%

ExaClaude Opus 4.8 1 turn

Final answer

| Clinic | County | Address | Phone | Saturday hours |
| --- | --- | --- | --- | --- |
| Planned Parenthood - Fulton Street | Fresno | 650 N. Fulton Street, Fresno, CA 93728 | (559) 488-4900 | 8:00 am - 4:30 pm |
| Planned Parenthood - Family First | Fresno | 6095 N. 1st Street, Fresno, CA 93710 | (559) 446-1515 | 8:00 am - 4:30 pm |
| FPA Women's Health - Fresno | Fresno | 165 N. Clark Street, Fresno, CA 93701 | (559) 233-8657 | Not available |

What happened

The one-turn run found three of six clinics. Two rows were fully correct; Family First had the wrong Saturday hours. Answer-item accuracy was 62.2%, and the complete-table verdict was incorrect.

## Methodology

Runs execute on Kepler, OpenRouter's benchmark harness, against production endpoints. Server-tool configurations set a request-level tool-call budget on the [web search server tool](https://openrouter.ai/docs/guides/features/server-tools/web-search). Plugin configurations make one pre-inference search of the question with the [web search plugin](https://openrouter.ai/docs/guides/features/plugins/web-search). Engines use the same default configurations that serve production traffic.

Every run persists its exact model, engine, request format, search budget, cost, and available timing telemetry. Missing configurations stay missing in the comparison table, and absent or zero timing telemetry is not treated as instantaneous performance.

## Download and cite

A snapshot of this leaderboard is published in the `search-benchmark-lanes` open dataset (filter on the `benchmark` column), regenerated daily with no API key required. The current snapshot was generated on Oct 30, 2026, 1:45 AM UTC. It is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), so you can reuse and republish it with attribution to OpenRouter.

- [Download CSV](https://openrouter.ai/api/v1/datasets/exports/search-benchmark-lanes/2026-10-30.csv) (text/csv)
- [Download JSON](https://openrouter.ai/api/v1/datasets/exports/search-benchmark-lanes/2026-10-30.json) (application/json)
- [Snapshot manifest](https://openrouter.ai/api/v1/datasets/exports/search-benchmark-lanes/2026-10-30.manifest.json) (SHA-256 checksums of the files above)
- [Latest manifest](https://openrouter.ai/api/v1/datasets/exports/search-benchmark-lanes/latest.manifest.json) (mutable alias, updated as snapshots are published)

Column definitions, methodology and redaction rules are in the [dataset README](https://openrouter.ai/api/v1/datasets/exports/README.md).

### Cite this leaderboard

```
OpenRouter (2026). WideSearch search results on OpenRouter, 2026-10-30 snapshot. https://openrouter.ai/benchmarks/widesearch. Licensed under CC BY 4.0.
```