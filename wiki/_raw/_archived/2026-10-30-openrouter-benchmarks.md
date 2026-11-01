---
title: "AI Model Benchmarks"
site: "OpenRouter"
source: "https://openrouter.ai/benchmarks"
domain: "openrouter.ai"
language: "en-US"
description: "Independent, continuously-run benchmarks of OpenRouter models, providers, and search engines. Browse every leaderboard with live model and run counts."
word_count: 378
---

## Benchmarks

Independent, reproducible measurements of the knobs you can actually set on an OpenRouter request: models, providers, search engines, and tool budgets. Every score links to the configuration, costs, and telemetry behind it.

13 benchmarks2,302,647 task evaluationslast run Oct 30, 2026[Benchmarks API](https://openrouter.ai/docs/api/api-reference/benchmarks/list-benchmarks)

[

Fetch benchmark results and metadata via the API

](https://openrouter.ai/docs/api/api-reference/benchmarks/list-benchmarks)

## Agents & tools

BenchmarkQualityValueSpeed

- ### [τ²-Bench Airline](https://openrouter.ai/benchmarks/tau2-bench-airline)
	Multi-turn service agents making tool calls under strict policy constraints.
	146 modelslast run Oct 30, 2026
	80.0%
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	GPT-5.1
	$0.009
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	GLM 5.3 Flash
	42s
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	GLM 5.3

## Artifact generation

Text models take on unconventional tasks like creating drawings and playable games.

BenchmarkSamplesValueSpeed

- ### [Sketch](https://openrouter.ai/benchmarks/media/sketch)
	Text models create drawings from prompts. The results are graded as images.
	242 models
	![Amazon: Nova Lite 1.0 output for Pelican on a bike](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Famazon%2Fnova-lite-v1%2F615adb7f-9c2d-48e3-b715-65f08211e1ee%2Fthumb-0.webp&w=128&q=75) ![Amazon: Nova 2 Lite output for Penguin with an umbrella](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Famazon%2Fnova-2-lite-v1%2F99c4957b-d35b-4027-b0e4-8d961c0a3715%2Fthumb-0.webp&w=128&q=75) ![Amazon: Nova Premier 1.0 output for Pelican riding a bicycle](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Famazon%2Fnova-premier-v1%2F56f01d8c-2750-48da-bfd7-a8eb37a6857c%2Fthumb-0.webp&w=128&q=75)
	$0.000034
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	Mistral: Mistral Nemo
	2s
	![Favicon for meta-llama](https://openrouter.ai/images/icons/Meta.png)
	Meta: Llama 3.2 3B Instruct
- ### [Games](https://openrouter.ai/benchmarks/media/games)
	Text models create playable games from a single brief in one attempt.
	50 models
	![Anthropic: Claude Opus 4.8 output for Fruit ninja](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4.8-opus-20260528%2F455e1283-039f-4e33-957f-b965dd02be42%2Fstill-0-2395590044.jpg&w=128&q=75) ![Anthropic: Claude Opus 5 output for Marble ball maze](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-opus-5-20260723%2Ff3ef90de-34ce-437c-afa4-f7e25f4f4df5%2Fstill-0-1013640886.jpg&w=128&q=75) ![DeepSeek: DeepSeek V4.1 Flash output for First-person shooter](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4.1-flash-20260910%2F58d3bb4a-08f0-4b01-82f9-e86f909ef710%2Fstill-0-1986223547.jpg&w=128&q=75)
	$0.004
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	OpenAI: gpt-oss-120b
	16s
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	Google: Gemini 3.1 Flash Lite Preview

## Reasoning

BenchmarkQualityValueSpeed

- ### [GPQA Diamond](https://openrouter.ai/benchmarks/gpqa-diamond)
	Graduate-level science questions that resist retrieval and reward careful reasoning.
	167 modelslast run Oct 30, 2026
	96.5%
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	Gemini 4 Argon
	$0.003
	![Favicon for unbiased](https://openrouter.ai/images/icons/Unbiased.png)
	Pareto 26.10 Preview
	20s
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	Claude Sonnet 5.5
- ### [VGI-Bench](https://openrouter.ai/benchmarks/vgi-bench)
	Multiple-choice questions about long videos: what was shown, said, or never happened.
	60 modelslast run Oct 30, 2026
	66.2%
	![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)
	Seed 1.6
	$0.039
	![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)
	Seed 1.6
	64s
	![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)
	Seed 1.6

## Search

BenchmarkQualityValueSpeed

- ### [BrowseComp](https://openrouter.ai/benchmarks/browsecomp)
	Hard-to-locate facts on the live web, scored on persistent multi-step research.
	4 modelslast run Aug 18, 2026
	89.0%
	Perplexity
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	Claude Opus 5 · high
	$0.99
	Perplexity
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	Claude Opus 5 · high
	1.9m
	Perplexity
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	Claude Opus 5 · high
- ### [DeepSearchQA](https://openrouter.ai/benchmarks/deepsearchqa)
	Questions whose answers are lists, scored for exhaustive retrieval with no padding.
	4 modelslast run Aug 18, 2026
	77.0%
	Parallel
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	Claude Opus 5 · high
	$0.10
	Perplexity
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	GPT-5.6 Luna · xhigh
	1.6m
	Perplexity
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	GPT-5.6 Luna · xhigh
- ### [HLE](https://openrouter.ai/benchmarks/hle)
	Humanity's Last Exam as a search benchmark: expert questions answered with live search.
	3 modelslast run Sep 15, 2026
	77.4%
	Perplexity
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	Claude Opus 5 · high
	$0.16
	Perplexity
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	Claude Opus 5 · high
	48s
	Perplexity
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	Claude Opus 5 · high
- ### [WideSearch](https://openrouter.ai/benchmarks/widesearch)
	Fill an entire table; answer-item accuracy scores partial matches.
	4 modelslast run Aug 18, 2026
	84.0%
	Perplexity
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	GPT-5.6 Sol · high
	$0.063
	Perplexity
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	GPT-5.6 Luna · xhigh
	1.9m
	Perplexity
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	GPT-5.6 Sol · high

For usage-based views of the same models, see the [model rankings](https://openrouter.ai/rankings) and the [full model list](https://openrouter.ai/models).