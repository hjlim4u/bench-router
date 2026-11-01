---
title: "DeepSearchQA Leaderboard"
site: "OpenRouter"
published: Aug 18, 2026, 2:37 AM UTC
source: "https://openrouter.ai/benchmarks/deepsearchqa"
domain: "openrouter.ai"
language: "en-US"
description: "Compare DeepSearchQA answer completeness, cost, and speed across OpenRouter search engines, models, and search budgets."
word_count: 1003
---

## DeepSearchQA

DeepSearchQA asks questions whose answers are lists: every member of a category, every event matching a set of constraints. Its 900 questions each carry a reference list of answer parts, and a response only counts when it finds all of them without padding the list with extras. We hold the model fixed and vary the search engine, request format, and maximum search budget. Where BrowseComp rewards locating one hidden fact, DeepSearchQA rewards finding the complete answer list.

[Dataset](https://huggingface.co/datasets/google/deepsearchqa)

Search providers

4 search providers

compared across configurations

Models

![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)

4 models

Claude Opus 5, GPT-5.6 Sol, GPT-5.6 Luna, and DeepSeek V4 Flash 0731

Test configurations

1 / 5 / 25

search budgets and plugin mode

## Which search configuration leads DeepSearchQA?

Claude Opus 5 · high, using Parallel with 25-turn as of Aug 14, 2026 leads at 77.0% benchmark accuracy. Displayed scores are rounded to one decimal place, so configurations listed together are co-leaders at that displayed precision. The comparison uses the same verified SSR lanes and benchmark methodology shown below.

Highest quality

Parallel25-turn

![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

Claude Opus 5 · high

77.0%answers matched the full reference set

95% confidence range 73.9%–79.9%

Winning result in detail

Complete answers

574 of 745

Incomplete answers

171 of 745

Cost / question

$3.32

Mean generation time / question

2.4m

Best value

$0.10 / question

Perplexity

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

GPT-5.6 Luna · xhigh25-turn search budget 73.0% correct

Fastest strong result

1.6m / question

Perplexity

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

GPT-5.6 Luna · xhigh25-turn search budget 73.0% correct

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg) ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)

Parallel

Claude Opus 5 · high 25-turn

77.0%Perplexity

Claude Opus 5 · high 25-turn

76.5%OpenAI Native

GPT-5.6 Sol · high 25-turn

75.0%Exa

Claude Opus 5 · high 25-turn

70.5%

## Why we run this benchmark

Finding one fact and finding *every* fact are different search problems. A single lucky query can land a BrowseComp answer; a DeepSearchQA answer has to be assembled across searches, with the agent tracking what it has found and what is still missing. That coverage pressure exercises a different part of the search stack: result breadth and deduplication matter as much as ranking.

We run it with the model held fixed because that isolates the variables OpenRouter users actually control. Those are which engine handles the searches, whether search runs as a server tool or a plugin, and how many agent turns the loop is allowed. Those knobs are exactly what you can set on a request today.

## What the scores can and can't tell you

These scores compare search configurations, not agent products. The model reads search result excerpts only, with no full-page fetching and no code tools, so absolute numbers sit below published agent leaderboards, which allow both. Compare configurations rather than raw levels.

The all-or-nothing grade makes this suite strict: missing one list member scores the same as missing them all, so scores run low and small engine gaps are noisy. Overlapping confidence intervals are treated as unresolved here, not as proof of equality. A configuration's cost is as real as its score, so read quality and efficiency together.

The questions are public, which means memorization can inflate absolute scores over time; differences between search configurations remain meaningful because every configuration shares the same model.

## How tasks are scored

Each task is one question with a reference list of expected answer parts. A judge model checks the response against every expected part and also flags excessive answers — parts the response asserts that are not in the reference. A task is correct only when the judge finds every expected part and finds no excessive answers. The grade is binary with no partial credit, and failed or refused tasks score zero.

```
reward = all_expected_parts_found ∧ no_excessive_answers   // ∈ {0, 1}
judge  = gemini-2.5-flash, strict json_schema completeness verdict
empty or refused answers skip the judge and score 0
```

A search configuration is one model, search engine, request format, and maximum search budget. Scores are weighted by the number of questions in each verified run; small smoke tests are excluded.

### Real run example

Fixed historical runs, independent of the model filter above. Long results and operational metadata are trimmed; selected queries may be edited or omitted.

Task

#### Intersect three QS university rankings

Which universities in the top 20 of the QS World University Rankings for 2021 were also in the top 10 US University Rankings and the top 10 (world) Arts and Humanities Rankings? Please only use information from the QS 2021 rankings and list the schools in alphabetical order.

Reference

Columbia University, Harvard University, Princeton University, Stanford University, Yale University

Incorrect

ExaClaude Opus 4.8 1 turn

Final answer

Using the QS 2021 lists I could verify, the intersection is Harvard University and Yale University. Confidence: 55%.

What happened

The run found only two of five universities. It never made a distinct query for the QS USA top 10 and missed Columbia, Princeton, and Stanford, so the complete-list grader failed it.

## Methodology

Runs execute on Kepler, OpenRouter's benchmark harness, against production endpoints. Server-tool configurations set a request-level tool-call budget on the [web search server tool](https://openrouter.ai/docs/guides/features/server-tools/web-search). Plugin configurations make one pre-inference search of the question with the [web search plugin](https://openrouter.ai/docs/guides/features/plugins/web-search). Engines use the same default configurations that serve production traffic.

Every run persists its exact model, engine, request format, search budget, cost, and available timing telemetry. Missing configurations stay missing in the comparison table, and absent or zero telemetry is not treated as free or instantaneous performance.

## Download and cite

A snapshot of this leaderboard is published in the `search-benchmark-lanes` open dataset (filter on the `benchmark` column), regenerated daily with no API key required. The current snapshot was generated on Oct 30, 2026, 1:45 AM UTC. It is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), so you can reuse and republish it with attribution to OpenRouter.

- [Download CSV](https://openrouter.ai/api/v1/datasets/exports/search-benchmark-lanes/2026-10-30.csv) (text/csv)
- [Download JSON](https://openrouter.ai/api/v1/datasets/exports/search-benchmark-lanes/2026-10-30.json) (application/json)
- [Snapshot manifest](https://openrouter.ai/api/v1/datasets/exports/search-benchmark-lanes/2026-10-30.manifest.json) (SHA-256 checksums of the files above)
- [Latest manifest](https://openrouter.ai/api/v1/datasets/exports/search-benchmark-lanes/latest.manifest.json) (mutable alias, updated as snapshots are published)

Column definitions, methodology and redaction rules are in the [dataset README](https://openrouter.ai/api/v1/datasets/exports/README.md).

### Cite this leaderboard

```
OpenRouter (2026). DeepSearchQA search results on OpenRouter, 2026-10-30 snapshot. https://openrouter.ai/benchmarks/deepsearchqa. Licensed under CC BY 4.0.
```