---
title: "HLE Search Leaderboard"
site: "OpenRouter"
published: Sep 15, 2026, 6:51 PM UTC
source: "https://openrouter.ai/benchmarks/hle"
domain: "openrouter.ai"
language: "en-US"
description: "Compare HLE answer quality, cost, and speed across OpenRouter search engines, models, and search budgets."
word_count: 1080
---

## HLE

Humanity's Last Exam collects expert-written questions at the frontier of human knowledge, spanning mathematics, the sciences, and the humanities. We run its 2,158 text-only questions as a search benchmark: the model answers with live web search rather than from stored knowledge alone, and a judge grades whether its final answer matches the reference. We hold the model fixed and vary the search engine, request format, and maximum search budget. Where BrowseComp stresses persistent multi-step browsing, HLE shows what live search adds to questions that are difficult because they require expert knowledge.

[Paper](https://arxiv.org/abs/2501.14249) [Dataset](https://huggingface.co/datasets/cais/hle)

Search providers

5 search providers

compared across configurations

Models

![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

3 models

Claude Opus 5, GPT-5.6 Sol, and Auto

Test configurations

1 / Default / 5 / 25

search budgets and plugin mode

## Which search configuration leads HLE?

Claude Opus 5 · high, using Perplexity with 25-turn as of Aug 11, 2026 leads at 77.4% benchmark accuracy. Displayed scores are rounded to one decimal place, so configurations listed together are co-leaders at that displayed precision. The comparison uses the same verified SSR lanes and benchmark methodology shown below.

Highest quality

Perplexity25-turn

![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

Claude Opus 5 · high

77.4%answers matched the reference

95% confidence range 67.4%–85.0%

Winning result in detail

Correct answers

65 of 84

Incorrect answers

19 of 84

Cost / question

$0.46

Mean generation time / question

83s

Best value

$0.16 / question

Perplexity

![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

Claude Opus 5 · high1-turn search budget 75.3% correct

Fastest strong result

48s / question

Perplexity

![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

Claude Opus 5 · high1-turn search budget 75.3% correct

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg) ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

Perplexity

Claude Opus 5 · high 25-turn

77.4%Exa

Claude Opus 5 · high 25-turn

74.2%OpenAI Native

GPT-5.6 Sol · high 25-turn

71.1%Parallel

Claude Opus 5 · high 25-turn

68.6%Auto policy

Auto · high default budget

52.5%

## Why we run this benchmark

HLE sits at the opposite end of the search spectrum from BrowseComp. Its questions were written by subject-matter experts to be unambiguous but extremely hard, so a model's baseline score is mostly a function of what it already knows. Adding web search turns that into a different question: how much expert-level knowledge can a search configuration retrieve on demand?

We run it with the model held fixed because that isolates the variables OpenRouter users actually control. Those are which engine handles the searches, whether search runs as a server tool or a plugin, and how many agent turns the loop is allowed. Those knobs are exactly what you can set on a request today.

## What the scores can and can't tell you

These scores compare search configurations, not agent products. The model reads search result excerpts only, with no full-page fetching and no code tools, so absolute numbers sit below published agent leaderboards, which allow both. Compare configurations rather than raw levels.

Because HLE leans on expertise rather than browsing depth, differences between search configurations are smaller here than on BrowseComp: many questions are answered (or missed) the same way at every budget. Engine gaps with overlapping confidence ranges are treated as unresolved here, not as proof of equality. A configuration's cost is as real as its score, so read quality and efficiency together.

We use the text-only subset of the public dataset (multi-modal questions are excluded), so scores are not directly comparable to full-HLE leaderboards. The questions are public, which means memorization can inflate absolute scores over time; differences between search configurations remain meaningful because every configuration shares the same model.

## How tasks are scored

Each task is one question with a short reference answer. The model answers in a fixed format (explanation, exact answer, stated confidence), and a judge model grades whether the extracted answer is semantically equivalent to the reference — the same answer-equivalence grading BrowseComp uses. The grade is binary with no partial credit, and failed or refused tasks score zero.

```
reward = judge(extracted_answer ≡ reference_answer)   // ∈ {0, 1}
judge  = gpt-4.1 at temperature 0, strict json_schema verdict
empty or refused answers skip the judge and score 0
```

A search configuration is one model, search engine, request format, and maximum search budget. Scores are weighted by the number of questions in each verified run; small smoke tests are excluded.

### Real run example

Fixed historical runs, independent of the model filter above. Long results and operational metadata are trimmed; selected queries may be edited or omitted.

Task

#### Trace a hummingbird tail sesamoid

Hummingbirds within Apodiformes uniquely have a bilaterally paired oval bone, a sesamoid embedded in the caudolateral portion of the expanded, cruciate aponeurosis of insertion of m. depressor caudae. How many paired tendons are supported by this sesamoid bone? Answer with a number.

This question is published verbatim on the official HLE site and in Figure 3 of the official paper. The public sources do not publish its reference answer, so both fresh runs are shown as ungraded.

[Official HLE dataset example](https://lastexam.ai/)

Reference

Reference answer withheld.

Ungraded · answer 3

PerplexityClaude Opus 4.8 1 turn

Final answer

Based on the anatomy of the hummingbird tail depressor system, this unique sesamoid bone embedded in the cross-shaped aponeurosis of the m. depressor caudae supports three paired tendons.

Exact Answer: 3 Confidence: 45%

What happened

The shallow run made one search and answered 3, but its selected independent source only established the anatomical context, not that count. With no official public reference, the result remains ungraded.

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
OpenRouter (2026). HLE search results on OpenRouter, 2026-10-30 snapshot. https://openrouter.ai/benchmarks/hle. Licensed under CC BY 4.0.
```