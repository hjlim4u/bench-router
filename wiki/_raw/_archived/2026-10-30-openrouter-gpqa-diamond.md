---
title: "GPQA Diamond Leaderboard"
site: "OpenRouter"
published: Oct 30, 2026, 6:35 AM UTC
source: "https://openrouter.ai/benchmarks/gpqa-diamond"
domain: "openrouter.ai"
language: "en-US"
description: "Live GPQA Diamond leaderboard across models and providers on OpenRouter. Compare graduate-level science accuracy, cost per question, and provider performance."
word_count: 2640
---

## GPQA Diamond

GPQA Diamond is a graduate-level multiple-choice benchmark in biology, physics, and chemistry. Each question is written by a subject-matter expert and designed so that even domain specialists need careful reasoning to identify the correct answer. We run the same fixed question set across provider endpoints to compare model capability, routing, and the practical cost of solving difficult scientific problems.

[Paper](https://arxiv.org/abs/2311.12022) [GitHub](https://github.com/idavidrein/gpqa)

## Which model leads the GPQA Diamond benchmark?

Google: Gemini 4 Argon leads GPQA Diamond at 96.5% as of Oct 30, 2026, 6:35 AM UTC. The same fixed GPQA Diamond question set and scoring are held fixed across production provider endpoints. The headline row uses default routing where available; otherwise, it uses a representative provider result.

## Model comparison

Most Accurate

![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)

[Google: Gemini 4 Argon](https://openrouter.ai/google/gemini-4-argon)

96.5%

Best Value

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

[OpenAI: GPT-6.1 Sol](https://openrouter.ai/openai/gpt-6.1-sol)

$0.021/question

Fastest

![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)

[Gemini 4 Argon](https://openrouter.ai/google/gemini-4-argon)

40s

Accuracy

Representative-run accuracy, best first.

Cost per question

Average cost per question, cheapest first.

Time per question

Average wall-clock time per question, fastest first.

## Cost efficiency

Accuracy vs. cost (Pareto frontier)

One point per model, using default routing (not pinned to a provider) when available. The line is the Pareto frontier: no model beats these on both accuracy and cost.

## Leaderboard

Top-level rows use default routing where available; click a row to expand provider-pinned results.

| # | Model | Accuracy | Std dev | Cost / question | Time / question | Output tok / question |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [Google: Gemini 4 Argon](https://openrouter.ai/google/gemini-4-argon)  Pareto  Google | 96.5% | \-- | $0.095 | 1.7m | 8.44k |
| 2 | [Gemini 4 Argon](https://openrouter.ai/google/gemini-4-argon)  Pareto | 96.0% | \-- | $0.029 | 40s | 2.87k |
| 3 | [Google: Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash) | 95.6% | \-- | $0.068 | 2.2m | 18k |
| 4 | [OpenAI: GPT-6 Astra Pro](https://openrouter.ai/openai/gpt-6-astra-pro) | 95.5% | \-- | $0.33 | 75s | 4.53k |
| 5 | [Fugu Ultra](https://openrouter.ai/sakana/fugu-ultra) | 94.6% | \-- | $1.15 | 5.5m | 33.3k |
| 6 | [Google: Gemini 3.1 Pro Preview](https://openrouter.ai/google/gemini-3.1-pro-preview) | 94.5% | ±0.1pp | $0.20 | 2.2m | 16.7k |
| 7 | [OpenAI: GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra) | 94.4% | \-- | $0.11 | 57s | 2.11k |
| 8 | [OpenAI: GPT-6.1 Sol](https://openrouter.ai/openai/gpt-6.1-sol)  Pareto | 94.4% | \-- | $0.021 | 52s | 1.98k |
| 9 | [OpenAI: GPT-5.6 Sol Pro](https://openrouter.ai/openai/gpt-5.6-sol-pro) | 94.1% | \-- | $0.15 | 1.6m | 11.6k |
| 10 | [OpenAI: GPT-5.5](https://openrouter.ai/openai/gpt-5.5) | 93.9% | ±0.3pp | $0.31 | 2.5m | 10.3k |
| 11 | [Google: Gemini 3.7 Flash](https://openrouter.ai/google/gemini-3.7-flash) | 93.9% | ±0.4pp | $0.029 | 59s | 7.68k |
| 12 | [Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash) | 93.4% | \-- | $0.023 | 44s | 6.13k |
| 13 | [Fugu Ultra V2](https://openrouter.ai/sakana/fugu-ultra-v2) | 93.3% | \-- | $0.50 | 3.2m | 13.8k |
| 14 | [TypeSafe: Jev Router](https://openrouter.ai/typesafe/jev-router) | 93.3% | ±0.5pp | $0.035 | 58s | 6.07k |
| 15 | [SpaceXAI: Grok 4.6](https://openrouter.ai/x-ai/grok-4.6) | 92.8% | ±0.4pp | $0.12 | 6.0m | 20.3k |
| 16 | [Google: Gemini 3.6 Flash](https://openrouter.ai/google/gemini-3.6-flash) | 92.8% | ±0.5pp | $0.044 | 62s | 11.7k |
| 17 | [Anthropic: Claude Sonnet 5.5](https://openrouter.ai/anthropic/claude-sonnet-5.5) | 92.7% | ±0.7pp | $0.025 | 20s | 2.27k |
| 18 | [Google: Gemini 3.5 Flash](https://openrouter.ai/google/gemini-3.5-flash) | 92.6% | ±0.4pp | $0.14 | 82s | 15.6k |
| 19 | [OpenAI: GPT-5.6 Sol](https://openrouter.ai/openai/gpt-5.6-sol) | 92.4% | ±0.0pp | $0.039 | 63s | 3.71k |
| 20 | [Pareto 26.10 Preview](https://openrouter.ai/unbiased/pareto-26.10-preview)  Pareto | 92.4% | \-- | $0.003 | 38s | 904 |
| 21 | [OpenAI: GPT-6 Sol](https://openrouter.ai/openai/gpt-6-sol) | 91.9% | \-- | $0.025 | 32s | 2.37k |
| 22 | [MoonshotAI: Kimi K3](https://openrouter.ai/moonshotai/kimi-k3) | 91.8% | ±1.1pp | $0.13 | 4.6m | 10.5k |
| 23 | [GPT-6.1-Terra](https://openrouter.ai/openai/gpt-6.1-terra) | 91.4% | \-- | $0.008 | 21s | 1.4k |
| 24 | [OpenAI: GPT-6.1 Terra](https://openrouter.ai/openai/gpt-6.1-terra) | 91.1% | \-- | $0.011 | 28s | 2.13k |
| 25 | [GLM 5.3 Flash](https://openrouter.ai/z-ai/glm-5.3-flash)  digitalocean | 90.9% | \-- | $0.005 | 3.9m | 10.7k |
| 26 | [Qwen: Qwen3.7 Max](https://openrouter.ai/qwen/qwen3.7-max)  AtlasCloud | 90.9% | \-- | $0.22 | 5.0m | 29.4k |
| 27 | [DeepSeek: DeepSeek V4.1 Flash 1017](https://openrouter.ai/deepseek/deepseek-v4.1-flash-1017) | 90.7% | \-- | $0.010 | 1.8m | 18.4k |
| 28 | [NVIDIA: Switchyard](https://openrouter.ai/nvidia/switchyard) | 90.7% | ±3.4pp | $0.016 | 64s | 3.6k |
| 29 | [Meta: Muse Spark Open](https://openrouter.ai/meta/muse-spark-open) | 90.6% | \-- | $0.069 | 1.7m | 16k |
| 30 | [Kimi K3.1 Pro](https://openrouter.ai/moonshotai/kimi-k3.1-pro) | 90.4% | \-- | $0.021 | 58s | 2.04k |
| 31 | [MiniMax: MiniMax M3](https://openrouter.ai/minimax/minimax-m3) | 90.4% | ±1.8pp | $0.034 | 5.3m | 30.1k |
| 32 | [OpenAI: GPT-5.4](https://openrouter.ai/openai/gpt-5.4) | 90.2% | ±0.0pp | $0.14 | 2.5m | 9.46k |
| 33 | [Anthropic: Claude Opus 5.5](https://openrouter.ai/anthropic/claude-opus-5.5) | 90.2% | ±0.6pp | $0.054 | 31s | 2.5k |
| 34 | [DeepSeek: DeepSeek V4 Pro 0813](https://openrouter.ai/deepseek/deepseek-v4-pro-0813) | 90.2% | ±1.7pp | $0.11 | 9.4m | 37.1k |
| 35 | [Deepseek V4.1 Flash 1017](https://openrouter.ai/deepseek/deepseek-v4.1-flash-1017) | 90.2% | \-- | $0.007 | 73s | 11.6k |
| 36 | [Tencent: Hy4 preview](https://openrouter.ai/tencent/hy4-preview) | 90.0% | ±0.6pp | $0.12 | 14.1m | 47.4k |
| 37 | [Anthropic: Claude Fable 5.1](https://openrouter.ai/anthropic/claude-fable-5.1) | 89.9% | ±0.7pp | $0.13 | 31s | 2.4k |
| 38 | [GPT-6-Luna](https://openrouter.ai/openai/gpt-6-luna) | 89.8% | \-- | $0.003 | 73s | 6.83k |
| 39 | [Anthropic: Claude Opus 4.8](https://openrouter.ai/anthropic/claude-opus-4.8) | 89.7% | ±1.1pp | $0.20 | 1.6m | 7.77k |
| 40 | [OpenAI: GPT-5.6 Luna Pro](https://openrouter.ai/openai/gpt-5.6-luna-pro) | 89.6% | ±0.3pp | $0.038 | 2.4m | 27k |
| 41 | [Anthropic: Claude Opus 4.7](https://openrouter.ai/anthropic/claude-opus-4.7) | 89.5% | ±1.0pp | $0.23 | 1.8m | 9.01k |
| 42 | [DeepSeek: DeepSeek V4.1 Flash](https://openrouter.ai/deepseek/deepseek-v4.1-flash) | 89.2% | ±0.9pp | $0.024 | 4.1m | 30.5k |
| 43 | [Xiaomi: MiMo-V2.6-Pro](https://openrouter.ai/xiaomi/mimo-v2.6-pro) | 88.7% | ±0.4pp | $0.033 | 12.8m | 38.4k |
| 44 | [Amazon: Nova Micro 1.0](https://openrouter.ai/amazon/nova-micro-v1) | 88.6% | ±0.3pp | $0.22 | 1.8m | 8.64k |
| 45 | [Fugu Max](https://openrouter.ai/sakana/fugu-max) | 88.6% | \-- | $0.076 | 3.8m | 12.3k |
| 46 | [Qwen: Qwen3.8 Flash](https://openrouter.ai/qwen/qwen3.8-flash) | 88.6% | \-- | $0.021 | 11.2m | 45.5k |
| 47 | [Google: Gemini 3 Flash Preview](https://openrouter.ai/google/gemini-3-flash-preview) | 88.4% | ±0.1pp | $0.13 | 4.1m | 43.8k |
| 48 | [OpenAI: GPT-5.6 Terra](https://openrouter.ai/openai/gpt-5.6-terra) | 88.4% | ±0.0pp | $0.041 | 55s | 3.32k |
| 49 | [OpenAI: GPT-6 Luna Pro](https://openrouter.ai/openai/gpt-6-luna-pro) | 88.4% | \-- | $0.008 | 73s | 13.1k |
| 50 | [Reflection: Beam 1.0 501B A23B](https://openrouter.ai/reflection/beam-1.0-501b-a23b) | 88.4% | \-- | $0.014 | 55s | 13.4k |
| 51 | [MoonshotAI: Kimi K2 Thinking](https://openrouter.ai/moonshotai/kimi-k2-thinking) | 88.2% | \-- | $0.10 | 14.6m | 41.5k |
| 52 | [DeepSeek: DeepSeek V4 Flash Vision Exp](https://openrouter.ai/deepseek/deepseek-v4-flash-vision-exp) | 88.0% | ±1.1pp | $0.023 | 3.9m | 25.3k |
| 53 | [Auto Router](https://openrouter.ai/openrouter/auto) | 88.0% | ±2.6pp | $0.089 | 3.3m | 37.4k |
| 54 | [Deepseek V4.1 Flash](https://openrouter.ai/deepseek/deepseek-v4.1-flash) | 87.9% | \-- | $0.011 | 2.1m | 14.3k |
| 55 | [Mimo V2.6 Pro](https://openrouter.ai/xiaomi/mimo-v2.6-pro) | 87.9% | \-- | $0.012 | 5.3m | 14.2k |
| 56 | [Qwen: Qwen3.7 Plus](https://openrouter.ai/qwen/qwen3.7-plus)  Alibaba | 87.9% | \-- | $0.044 | 9.8m | 34.2k |
| 57 | [OpenAI: GPT-5.6 Luna](https://openrouter.ai/openai/gpt-5.6-luna) | 87.9% | ±0.6pp | $0.008 | 80s | 7.83k |
| 58 | [Anthropic: Claude Opus 5](https://openrouter.ai/anthropic/claude-opus-5) | 87.8% | ±1.7pp | $0.13 | 63s | 4.92k |
| 59 | [NVIDIA: Nemotron 3.5 Super VL](https://openrouter.ai/nvidia/nemotron-3.5-super-vl) | 87.4% | ±0.7pp | $0.023 | 8.4m | 48k |
| 60 | [OpenAI: GPT-6 Luna](https://openrouter.ai/openai/gpt-6-luna)  Pareto | 87.4% | \-- | $0.003 | 50s | 5.75k |
| 61 | [Qwen: Qwen3.8 2.4T A95B](https://openrouter.ai/qwen/qwen3.8-2.4t-a95b) | 87.1% | ±1.1pp | $0.086 | 3.2m | 14k |
| 62 | [DeepSeek: DeepSeek V4 Pro 0423](https://openrouter.ai/deepseek/deepseek-v4-pro) | 86.9% | ±1.6pp | $0.038 | 11.5m | 34.8k |
| 63 | [Anthropic: Claude Haiku 5.5](https://openrouter.ai/anthropic/claude-haiku-5.5) | 86.9% | ±0.5pp | $0.004 | 39s | 7.82k |
| 64 | [MiniMax: MiniMax M2.1](https://openrouter.ai/minimax/minimax-m2.1) | 86.8% | \-- | $0.028 | 4.8m | 21.4k |
| 65 | [MiniMax: MiniMax M3.1 Flash](https://openrouter.ai/minimax/minimax-m3.1-flash) | 86.7% | \-- | $0.014 | 3.0m | 22.7k |
| 66 | [OpenAI: GPT-5.1](https://openrouter.ai/openai/gpt-5.1) | 86.7% | ±0.0pp | $0.22 | 4.4m | 22.2k |
| 67 | [DeepSeek: DeepSeek V4 Flash 0731](https://openrouter.ai/deepseek/deepseek-v4-flash-0731) | 86.7% | ±2.6pp | $0.008 | 7.4m | 25.8k |
| 68 | [Anthropic: Claude Fable 5](https://openrouter.ai/anthropic/claude-fable-5) | 86.6% | ±4.1pp | $0.18 | 44s | 3.35k |
| 69 | [Thinking Machines: Inkling Small](https://openrouter.ai/thinkingmachines/inkling-small) | 86.6% | ±0.8pp | $0.025 | 3.9m | 20.8k |
| 70 | [Anthropic: Claude Opus 4.6](https://openrouter.ai/anthropic/claude-opus-4.6) | 86.4% | ±1.4pp | $0.75 | 8.3m | 29.8k |
| 71 | [Anthropic: Claude Opus 4.5](https://openrouter.ai/anthropic/claude-opus-4.5) | 86.3% | ±1.0pp | $0.84 | 6.9m | 33.5k |
| 72 | [MoonshotAI: Kimi K2.7 Code](https://openrouter.ai/moonshotai/kimi-k2.7-code) | 86.2% | ±1.7pp | $0.099 | 7.8m | 26.3k |
| 73 | [MoonshotAI: Kimi K2.6](https://openrouter.ai/moonshotai/kimi-k2.6) | 86.0% | ±4.0pp | $0.16 | 16.5m | 55.2k |
| 74 | [OpenAI: GPT-5](https://openrouter.ai/openai/gpt-5) | 85.7% | ±0.3pp | $0.21 | 4.4m | 20.9k |
| 75 | [DeepSeek: DeepSeek V4 Flash 0423](https://openrouter.ai/deepseek/deepseek-v4-flash) | 85.5% | ±0.9pp | $0.005 | 8.9m | 30.2k |
| 76 | [Z.ai: GLM 5.3](https://openrouter.ai/z-ai/glm-5.3) | 85.2% | ±1.3pp | $0.10 | 7.9m | 30.7k |
| 77 | [Qwen: Qwen3.5 397B A17B](https://openrouter.ai/qwen/qwen3.5-397b-a17b) | 85.2% | ±2.7pp | $0.074 | 8.0m | 22.7k |
| 78 | [inclusionAI: Ling 3.0 Flash VL](https://openrouter.ai/inclusionai/ling-3.0-flash-vl)  Pareto | 84.8% | \-- | $0.001 | 88s | 17.5k |
| 79 | [MiniMax: MiniMax M2.7](https://openrouter.ai/minimax/minimax-m2.7) | 84.8% | ±2.2pp | $0.047 | 10.3m | 38k |
| 80 | [Z.ai: GLM 5.2](https://openrouter.ai/z-ai/glm-5.2) | 84.8% | ±1.8pp | $0.13 | 8.0m | 47.7k |
| 81 | [Anthropic: Claude Sonnet 5](https://openrouter.ai/anthropic/claude-sonnet-5) | 84.7% | ±4.6pp | $0.17 | 2.8m | 16.5k |
| 82 | [Z.ai: GLM 5.3 Flash](https://openrouter.ai/z-ai/glm-5.3-flash) | 84.4% | ±2.3pp | $0.014 | 8.8m | 38.1k |
| 83 | [MoonshotAI: Kimi K2.5](https://openrouter.ai/moonshotai/kimi-k2.5) | 84.2% | ±4.2pp | $0.10 | 18.7m | 39.8k |
| 84 | [Google: Gemini 3.5 Flash Lite](https://openrouter.ai/google/gemini-3.5-flash-lite) | 84.1% | ±0.9pp | $0.037 | 51s | 14.6k |
| 85 | [OpenAI: GPT-5.4 Mini](https://openrouter.ai/openai/gpt-5.4-mini) | 83.5% | ±0.6pp | $0.062 | 84s | 13.6k |
| 86 | [Thinking Machines: Inkling](https://openrouter.ai/thinkingmachines/inkling) | 83.4% | ±1.1pp | $0.095 | 4.9m | 23.4k |
| 87 | [Qwen: Qwen3.5-122B-A10B](https://openrouter.ai/qwen/qwen3.5-122b-a10b) | 83.3% | ±3.3pp | $0.054 | 4.2m | 23k |
| 88 | [Google: Gemini 2.5 Pro](https://openrouter.ai/google/gemini-2.5-pro) | 82.6% | ±1.6pp | $0.26 | 3.9m | 26k |
| 89 | [Qwen: Qwen3.6 27B](https://openrouter.ai/qwen/qwen3.6-27b) | 82.5% | ±4.4pp | $0.086 | 12.7m | 31.4k |
| 90 | [Xiaomi: MiMo-V2.5-Pro](https://openrouter.ai/xiaomi/mimo-v2.5-pro) | 82.4% | ±6.0pp | $0.029 | 11.7m | 29.7k |
| 91 | [GLM 5.3](https://openrouter.ai/z-ai/glm-5.3)  digitalocean | 82.3% | \-- | $0.026 | 2.7m | 9.04k |
| 92 | [MiniMax: MiniMax M2.5](https://openrouter.ai/minimax/minimax-m2.5) | 82.1% | ±3.1pp | $0.026 | 8.3m | 24k |
| 93 | [Anthropic: Claude Sonnet 4.5](https://openrouter.ai/anthropic/claude-sonnet-4.5) | 81.9% | ±1.3pp | $0.31 | 4.8m | 20.7k |
| 94 | [Qwen: Qwen3.8 27B](https://openrouter.ai/qwen/qwen3.8-27b) | 81.8% | ±1.4pp | $0.034 | 3.6m | 13.8k |
| 95 | [Google: Gemma 4 31B](https://openrouter.ai/google/gemma-4-31b-it) | 81.7% | ±1.7pp | $0.007 | 8.5m | 18.2k |
| 96 | [Z.ai: GLM 4.7](https://openrouter.ai/z-ai/glm-4.7) | 81.7% | ±2.9pp | $0.084 | 16.1m | 41.9k |
| 97 | [Google: Gemini 3.1 Flash Lite](https://openrouter.ai/google/gemini-3.1-flash-lite) | 81.6% | ±2.1pp | $0.041 | 83s | 27.5k |
| 98 | [Z.ai: GLM 5.1](https://openrouter.ai/z-ai/glm-5.1) | 81.5% | ±2.4pp | $0.22 | 16.5m | 59.2k |
| 99 | [DeepSeek: DeepSeek V3.2 Exp](https://openrouter.ai/deepseek/deepseek-v3.2-exp) | 81.5% | \-- | $0.007 | 9.2m | 17.7k |
| 100 | [inclusionAI: Ling 3.1 Flash](https://openrouter.ai/inclusionai/ling-3.1-flash) | 81.3% | \-- | $0.008 | 5.9m | 33.9k |
| 101 | [NVIDIA: Nemotron 3 Ultra](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b) | 81.2% | \-- | $0.14 | 5.1m | 39.8k |
| 102 | [DeepSeek: DeepSeek V3.2](https://openrouter.ai/deepseek/deepseek-v3.2) | 81.1% | ±2.4pp | $0.009 | 9.5m | 18.9k |
| 103 | [OpenAI: GPT-5 Mini](https://openrouter.ai/openai/gpt-5-mini) | 80.8% | ±1.8pp | $0.044 | 3.6m | 22.1k |
| 104 | [Meta: Muse Glimmer 30B](https://openrouter.ai/meta/muse-glimmer-30b) | 80.6% | ±1.4pp | $0.023 | 4.2m | 17.5k |
| 105 | [Qwen: Qwen3.5-35B-A3B](https://openrouter.ai/qwen/qwen3.5-35b-a3b) | 80.1% | ±4.1pp | $0.027 | 5.5m | 25.6k |
| 106 | [Qwen: Qwen3.6 35B A3B](https://openrouter.ai/qwen/qwen3.6-35b-a3b) | 79.4% | ±3.9pp | $0.043 | 8.3m | 42.5k |
| 107 | [Anthropic: Claude Sonnet 4](https://openrouter.ai/anthropic/claude-sonnet-4) | 78.6% | \-- | $0.26 | 3.0m | 17.4k |
| 108 | [Xiaomi: MiMo-V2.5](https://openrouter.ai/xiaomi/mimo-v2.5) | 78.0% | ±4.4pp | $0.013 | 12.9m | 38.6k |
| 109 | [Z.ai: GLM 5](https://openrouter.ai/z-ai/glm-5) | 77.8% | ±5.3pp | $0.16 | 16.4m | 64.5k |
| 110 | [OpenAI: GPT-5.4 Nano](https://openrouter.ai/openai/gpt-5.4-nano) | 77.7% | ±0.3pp | $0.013 | 68s | 10.3k |
| 111 | [Qwen: Qwen3.5-9B](https://openrouter.ai/qwen/qwen3.5-9b) | 77.7% | ±2.0pp | $0.006 | 11.1m | 36.4k |
| 112 | [Qwen: Qwen3 235B A22B Thinking 2507](https://openrouter.ai/qwen/qwen3-235b-a22b-thinking-2507) | 77.5% | ±2.2pp | $0.058 | 10.5m | 23k |
| 113 | [DeepSeek: R1 0528](https://openrouter.ai/deepseek/deepseek-r1-0528) | 77.2% | ±3.5pp | $0.052 | 14.5m | 23.2k |
| 114 | [DeepSeek: DeepSeek V3.1 Terminus](https://openrouter.ai/deepseek/deepseek-v3.1-terminus) | 76.8% | ±1.9pp | $0.016 | 7.4m | 16k |
| 115 | [MoonshotAI: Kimi K2 0905](https://openrouter.ai/moonshotai/kimi-k2-0905) | 76.4% | \-- | $0.017 | 73s | 5.94k |
| 116 | [Mistral: Mistral Small 4](https://openrouter.ai/mistralai/mistral-small-2603) | 75.8% | \-- | $0.015 | 2.9m | 24k |
| 117 | [Z.ai: GLM 4.6](https://openrouter.ai/z-ai/glm-4.6) | 75.6% | ±4.1pp | $0.055 | 16.6m | 28.4k |
| 118 | [inclusionAI: Ling 3.0 Flash](https://openrouter.ai/inclusionai/ling-3.0-flash) | 74.9% | ±1.9pp | $0.003 | 2.8m | 31k |
| 119 | [Qwen: Qwen3 Coder Next](https://openrouter.ai/qwen/qwen3-coder-next) | 74.8% | ±1.0pp | $0.015 | 1.8m | 14.5k |
| 120 | [Xiaomi: MiMo-V2.6-Flash](https://openrouter.ai/xiaomi/mimo-v2.6-flash) | 74.2% | ±1.5pp | $0.017 | 12.8m | 59.3k |
| 121 | [Anthropic: Claude Haiku 4.5](https://openrouter.ai/anthropic/claude-haiku-4.5) | 72.9% | ±0.9pp | $0.19 | 4.1m | 37.8k |
| 122 | [Qwen: Qwen3 235B A22B Instruct 2507](https://openrouter.ai/qwen/qwen3-235b-a22b-2507) | 72.7% | ±1.5pp | $0.005 | 4.9m | 7.94k |
| 123 | [OpenAI: gpt-oss-120b](https://openrouter.ai/openai/gpt-oss-120b) | 72.7% | ±2.4pp | $0.006 | 5.8m | 18.5k |
| 124 | [Google: Gemini 2.5 Flash](https://openrouter.ai/google/gemini-2.5-flash) | 72.6% | ±0.4pp | $0.060 | 2.1m | 23.9k |
| 125 | [Qwen: Qwen3 Next 80B A3B Instruct](https://openrouter.ai/qwen/qwen3-next-80b-a3b-instruct) | 71.2% | ±0.9pp | $0.011 | 1.6m | 10.4k |
| 126 | [Google: Gemma 4 26B A4B](https://openrouter.ai/google/gemma-4-26b-a4b-it) | 70.5% | ±4.9pp | $0.016 | 16.7m | 49.4k |
| 127 | [OpenAI: GPT-5 Nano](https://openrouter.ai/openai/gpt-5-nano) | 70.5% | ±0.4pp | $0.013 | 3.9m | 33.3k |
| 128 | [NVIDIA: Nemotron 3.5 Lightning](https://openrouter.ai/nvidia/nemotron-3.5-lightning) | 70.3% | ±2.7pp | $0.009 | 6.1m | 44.7k |
| 129 | [Qwen: Qwen3 VL 235B A22B Instruct](https://openrouter.ai/qwen/qwen3-vl-235b-a22b-instruct) | 69.3% | ±2.0pp | $0.010 | 4.3m | 6.46k |
| 130 | Gemma 4 26B A4B IT (free)  Darkbloom | 68.5% | \-- | \-- | 6.4m | 6.99k |
| 131 | [Anthropic: Claude Sonnet 4.6](https://openrouter.ai/anthropic/claude-sonnet-4.6) | 68.3% | ±14.0pp | $0.62 | 10.6m | 40.9k |
| 132 | [Z.ai: GLM 4.6V](https://openrouter.ai/z-ai/glm-4.6v) | 66.8% | \-- | $0.014 | 5.4m | 15.3k |
| 133 | [Meta: Llama 4 Maverick](https://openrouter.ai/meta-llama/llama-4-maverick) | 66.6% | ±0.6pp | $0.003 | 87s | 2.95k |
| 134 | [DeepSeek: DeepSeek V3.1](https://openrouter.ai/deepseek/deepseek-chat-v3.1) | 66.2% | ±13.3pp | $0.015 | 6.8m | 13.1k |
| 135 | [IBM: Granite 4.2 8B](https://openrouter.ai/ibm-granite/granite-4.2-8b) | 65.7% | \-- | $0.015 | 28.6m | 64.4k |
| 136 | [OpenAI: GPT-4.1 Mini](https://openrouter.ai/openai/gpt-4.1-mini) | 64.9% | ±1.1pp | $0.004 | 29s | 2.35k |
| 137 | [OpenAI: gpt-oss-20b](https://openrouter.ai/openai/gpt-oss-20b) | 64.5% | ±2.2pp | $0.007 | 10.2m | 45k |
| 138 | [Qwen: Qwen3 30B A3B Instruct 2507](https://openrouter.ai/qwen/qwen3-30b-a3b-instruct-2507) | 64.3% | ±1.2pp | $0.003 | 2.4m | 9.63k |
| 139 | [Qwen: Qwen3 VL 30B A3B Instruct](https://openrouter.ai/qwen/qwen3-vl-30b-a3b-instruct) | 64.2% | ±1.4pp | $0.007 | 4.0m | 11.4k |
| 140 | [OpenAI: GPT-4.1](https://openrouter.ai/openai/gpt-4.1) | 63.7% | ±0.4pp | $0.016 | 15s | 1.75k |
| 141 | [NVIDIA: Nemotron 3 Nano 30B A3B](https://openrouter.ai/nvidia/nemotron-3-nano-30b-a3b) | 62.9% | ±2.1pp | $0.017 | 10.5m | 83.9k |
| 142 | [DeepSeek: DeepSeek V3](https://openrouter.ai/deepseek/deepseek-chat) | 62.1% | ±1.2pp | $0.002 | 65s | 2.17k |
| 143 | [Qwen: Qwen3 30B A3B](https://openrouter.ai/qwen/qwen3-30b-a3b) | 60.9% | \-- | $0.008 | 3.5m | 15.1k |
| 144 | [Qwen: Qwen3 32B](https://openrouter.ai/qwen/qwen3-32b) | 60.6% | ±1.0pp | $0.008 | 5.0m | 17.2k |
| 145 | [Qwen: Qwen3 Coder 480B A35B](https://openrouter.ai/qwen/qwen3-coder) | 60.4% | ±0.7pp | $0.004 | 57s | 2.12k |
| 146 | [Qwen: Qwen3 14B](https://openrouter.ai/qwen/qwen3-14b) | 59.2% | ±0.3pp | $0.003 | 8.7m | 11.7k |
| 147 | [Z.ai: GLM 4.5 Air](https://openrouter.ai/z-ai/glm-4.5-air) | 57.5% | \-- | $0.037 | 17.6m | 47.8k |
| 148 | [Google: Gemini 2.5 Flash Lite](https://openrouter.ai/google/gemini-2.5-flash-lite) | 54.9% | ±0.6pp | $0.017 | 2.0m | 42.9k |
| 149 | [Z.ai: GLM 4.7 Flash](https://openrouter.ai/z-ai/glm-4.7-flash) | 52.4% | ±0.8pp | $0.017 | 12.3m | 42.4k |
| 150 | [OpenAI: GPT-4o (2024-08-06)](https://openrouter.ai/openai/gpt-4o-2024-08-06) | 52.0% | ±0.3pp | $0.018 | 16s | 1.56k |
| 151 | [Qwen: Qwen3 Coder 30B A3B Instruct](https://openrouter.ai/qwen/qwen3-coder-30b-a3b-instruct) | 51.9% | ±0.3pp | $0.003 | 1.8m | 2.73k |
| 152 | [Qwen: Qwen3 VL 8B Instruct](https://openrouter.ai/qwen/qwen3-vl-8b-instruct) | 51.3% | \-- | $0.005 | 2.0m | 10.7k |
| 153 | [OpenAI: GPT-4o](https://openrouter.ai/openai/gpt-4o) | 51.1% | ±0.1pp | $0.013 | 13s | 1.12k |
| 154 | [DeepSeek: DeepSeek V3 0324](https://openrouter.ai/deepseek/deepseek-chat-v3-0324) | 50.7% | ±13.6pp | $0.005 | 1.9m | 4.23k |
| 155 | [inclusionAI: Ling 3.0 Flash Fin](https://openrouter.ai/inclusionai/ling-3.0-flash-fin) | 50.5% | \-- | $0.010 | 11.7m | 64.8k |
| 156 | [OpenAI: GPT-4.1 Nano](https://openrouter.ai/openai/gpt-4.1-nano)  Pareto | 49.1% | ±0.9pp | $0.00084 | 23s | 1.9k |
| 157 | [Meta: Llama 3.3 70B Instruct](https://openrouter.ai/meta-llama/llama-3.3-70b-instruct) | 47.3% | ±1.0pp | $0.001 | 75s | 2.34k |
| 158 | [Qwen2.5 72B Instruct](https://openrouter.ai/qwen/qwen-2.5-72b-instruct) | 46.0% | ±1.3pp | $0.001 | 1.6m | 1.85k |
| 159 | [OpenAI: GPT-4o-mini](https://openrouter.ai/openai/gpt-4o-mini) | 43.2% | ±0.8pp | $0.001 | 21s | 1.48k |
| 160 | [Qwen: Qwen2.5 VL 72B Instruct](https://openrouter.ai/qwen/qwen2.5-vl-72b-instruct) | 42.9% | \-- | $0.002 | 59s | 1.66k |
| 161 | [Tencent: Hy-MT2-30B-A3B](https://openrouter.ai/tencent/hy-mt2-30b-a3b)  Pareto  Reka | 38.9% | \-- | $0.00023 | 9s | 711 |
| 162 | [Google: Gemma 3 12B](https://openrouter.ai/google/gemma-3-12b-it) | 37.9% | ±1.7pp | $0.00034 | 46s | 2.04k |
| 163 | [Meta: Llama 3.2 3B Instruct](https://openrouter.ai/meta-llama/llama-3.2-3b-instruct)  Cloudflare | 28.6% | \-- | $0.00059 | 15s | 1.64k |
| 164 | [Meta: Llama 3.1 8B Instruct](https://openrouter.ai/meta-llama/llama-3.1-8b-instruct) | 28.2% | ±2.1pp | $0.001 | 2.3m | 19.1k |
| 165 | [Sao10K: Llama 3 8B Lunaris](https://openrouter.ai/sao10k/l3-lunaris-8b)  Pareto | 27.7% | ±0.1pp | $0.000062 | 9s | 580 |
| 166 | [Google: Gemma 3 4B](https://openrouter.ai/google/gemma-3-4b-it)  Parasail | 27.1% | \-- | $0.00011 | 11s | 1.8k |
| 167 | [Google: Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)](https://openrouter.ai/google/gemini-3.1-flash-lite-image) | 10.3% | ±0.0pp | $0.018 | 22s | 11.8k |

## Example problems

GPQA uses four-choice questions that require more than recalling a definition. These representative examples show the format and the range of scientific domains without reproducing items from the benchmark's protected question pool.

### Biology

A researcher observes that a membrane protein is synthesized on ribosomes attached to the rough endoplasmic reticulum. Which destination is most consistent with this protein entering the secretory pathway?

1. A.The cytosol, where it remains soluble
2. B.The nucleus, after import through a nuclear pore
3. C.A membrane of the endomembrane system or the cell surface
4. D.The mitochondrial matrix through a TOM/TIM complex

Answer: C

Ribosomes on the rough ER synthesize proteins destined for secretion or insertion into the endomembrane system, including the plasma membrane.

### Physics

A spacecraft is far from other bodies and fires its engine in the direction opposite to its velocity. Ignoring mass loss during the brief burn, what happens immediately to its speed?

1. A.It increases because the exhaust carries away backward momentum
2. B.It decreases because the thrust points opposite to its velocity
3. C.It remains unchanged because thrust only changes direction
4. D.It becomes zero because the spacecraft is in free space

Answer: B

An impulse opposite the velocity vector reduces the spacecraft’s momentum and therefore its speed during the burn.

### Chemistry

Why does adding a small amount of a common ion generally reduce the solubility of a sparingly soluble ionic solid in water?

1. A.The common ion increases the solid’s lattice energy
2. B.The common ion shifts the dissolution equilibrium toward the solid
3. C.The common ion converts every dissolved ion into a neutral molecule
4. D.The common ion removes solvent molecules from the solution

Answer: B

The added ion raises the concentration of a dissolution product, so Le Chatelier’s principle shifts the equilibrium toward the undissolved solid.

## Why we run this benchmark

GPQA is a broad graduate-level reasoning test across biology, physics, and chemistry, so it gives us a cheap, high-floor signal that a deployment is healthy. A model that normally clears these questions but suddenly drops usually points to something broken in the endpoint or routing rather than the questions themselves.

Because we run the same fixed question set across provider endpoints, a large accuracy gap between providers serving the same model is a quick way to catch a misconfigured or degraded endpoint. The cost and latency columns show what that reasoning quality costs to serve.

## What the scores can and can't tell you

GPQA is a narrow, high-difficulty evaluation, not a complete measure of general intelligence or usefulness. A score reflects performance on expert-written multiple-choice science questions and should be considered alongside coding, instruction-following, factuality, and other evaluations.

Scores can be sensitive to sampling settings, answer-position handling, and the number of repeated runs. Small differences may not be meaningful when models have similar sample counts, so the leaderboard includes run variability and cost context rather than presenting accuracy alone.

The benchmark is publicly described, and some questions may eventually appear in training data. We avoid reproducing the private question pool here, but no public benchmark can guarantee that every future evaluation item is uncontaminated.

## Methodology

Scores aggregate successful runs from the newest 90 days, weighted by question count, with a minimum sample threshold per model-provider pair. A model's headline score uses default routing when available; otherwise it falls back to the median provider. Cost, time, and output-token figures are per-question averages from the same runs. Best value is the cheapest Pareto-optimal model within five percentage points of the top score.

GPQA Diamond is described in the [original paper](https://arxiv.org/abs/2311.12022). See the [docs](https://openrouter.ai/docs) for routing details, or browse [all models](https://openrouter.ai/models) to try one.

## API access

These scores are available through OpenRouter's public benchmarks API, so you can retrieve the same model-level results programmatically.

```
GET https://openrouter.ai/api/v1/benchmarks?source=openrouter
Authorization: Bearer <API key>
```

Use `task_type=intelligence` to filter to `gpqa_diamond`. Each item represents one model and includes `accuracy`, `accuracy_stddev`, `avg_cost_per_task`, `total_tasks`, and `last_run_timestamp`. See the [benchmarks API docs](https://openrouter.ai/docs/api/api-reference/benchmarks/list-benchmarks).

## Download and cite

A snapshot of this leaderboard is published in the `benchmark-leaderboard` open dataset (filter on the `benchmark` column), regenerated daily with no API key required. The current snapshot was generated on Oct 30, 2026, 1:45 AM UTC. It is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), so you can reuse and republish it with attribution to OpenRouter.

- [Download CSV](https://openrouter.ai/api/v1/datasets/exports/benchmark-leaderboard/2026-10-30.csv) (text/csv)
- [Download JSON](https://openrouter.ai/api/v1/datasets/exports/benchmark-leaderboard/2026-10-30.json) (application/json)
- [Snapshot manifest](https://openrouter.ai/api/v1/datasets/exports/benchmark-leaderboard/2026-10-30.manifest.json) (SHA-256 checksums of the files above)
- [Latest manifest](https://openrouter.ai/api/v1/datasets/exports/benchmark-leaderboard/latest.manifest.json) (mutable alias, updated as snapshots are published)

Column definitions, methodology and redaction rules are in the [dataset README](https://openrouter.ai/api/v1/datasets/exports/README.md).

### Cite this leaderboard

```
OpenRouter (2026). GPQA Diamond results on OpenRouter, 2026-10-30 snapshot. https://openrouter.ai/benchmarks/gpqa-diamond. Licensed under CC BY 4.0.
```