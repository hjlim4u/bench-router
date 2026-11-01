---
title: "τ²-Bench Airline Leaderboard"
site: "OpenRouter"
published: Oct 30, 2026, 7:12 AM UTC
source: "https://openrouter.ai/benchmarks/tau2-bench-airline"
domain: "openrouter.ai"
language: "en-US"
description: "Live leaderboard for τ²-Bench verified airline runs across models and providers on OpenRouter. Compare agentic accuracy, cost per task, and speed, measured continuously on real provider endpoints."
word_count: 2696
---

## τ²-Bench: Airline

τ²-Bench Airline tests whether a model can do an airline support agent's job: follow a policy manual, talk to a simulated customer, and call the right tools to search flights, change bookings, and issue refunds. The model doesn't need any domain knowledge; it's scored entirely on how well it executes tool calls across multi-step task trajectories. We run it continuously against the same provider endpoints that serve OpenRouter traffic, so a score reflects both the model and the provider running it. We use this benchmark because it has a high floor, so we can assess provider variance and not model capability. Our routing algorithm for tool call requests uses these same signals to send traffic to the best performing endpoints.

[Paper](https://arxiv.org/abs/2506.07982) [GitHub](https://github.com/sierra-research/tau2-bench)

## Which model leads the τ²-Bench Airline benchmark?

OpenAI: GPT-5.1 leads τ²-Bench Airline at 80.0% as of Oct 30, 2026, 7:12 AM UTC. Airline tasks, policy, simulator and customer setup, step budget, and grading are held fixed across production provider endpoints, so the displayed results compare models and the providers serving them under the same evaluation conditions.

Tool-call errors before → after Auto Exacto

3.9% → 1.7%

Tool-call error rate on models enrolled in [Auto Exacto](https://openrouter.ai/docs/guides/routing/auto-exacto), OpenRouter's automatic provider optimization for tool-calling requests.

## Model comparison

Most Accurate

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

[OpenAI: GPT-5.1](https://openrouter.ai/openai/gpt-5.1)

80.0%

Best Value

![Favicon for xiaomi](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.mi.com&size=256)

[Xiaomi: MiMo-V2.6-Flash](https://openrouter.ai/xiaomi/mimo-v2.6-flash)

$0.014/task

Fastest

![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)

[Anthropic: Claude Sonnet 5.5](https://openrouter.ai/anthropic/claude-sonnet-5.5)

74s

Accuracy

Representative-run accuracy, best first.

Cost per task

Average cost per graded task, cheapest first.

Time per task

Average wall-clock time per task, fastest first; agents that loop or stall run long.

## Cost efficiency

Accuracy vs. cost (Pareto frontier)

One point per model, using default routing (not pinned to a provider) when available. The line is the Pareto frontier: no model beats these on both accuracy and cost.

## Tool-call reliability

## Leaderboard

Top-level rows use default routing where available; click a row to expand provider-pinned results.

| # | Model | Accuracy | Std dev | Cost / task | Time / task | Output tok / task |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [OpenAI: GPT-5.1](https://openrouter.ai/openai/gpt-5.1)  Pareto | 80.0% | ±0.0pp | $0.39 | 8.0m | 34.1k |
| 2 | [Anthropic: Claude Fable 5](https://openrouter.ai/anthropic/claude-fable-5) | 79.8% | ±2.7pp | $0.89 | 2.0m | 5.75k |
| 3 | [inclusionAI: Ling 3.1 Flash](https://openrouter.ai/inclusionai/ling-3.1-flash)  Pareto | 79.3% | \-- | $0.031 | 10.6m | 16.7k |
| 4 | [Anthropic: Claude Fable 5.1](https://openrouter.ai/anthropic/claude-fable-5.1) | 79.2% | ±1.3pp | $0.72 | 1.9m | 6.9k |
| 5 | [Anthropic: Claude Opus 5](https://openrouter.ai/anthropic/claude-opus-5) | 78.9% | ±2.1pp | $0.48 | 2.0m | 7.06k |
| 6 | [Google: Gemini 4 Argon](https://openrouter.ai/google/gemini-4-argon)  Google | 78.7% | \-- | $0.50 | 5.8m | 22k |
| 7 | [Anthropic: Claude Sonnet 5.5](https://openrouter.ai/anthropic/claude-sonnet-5.5) | 78.7% | ±2.5pp | $0.16 | 74s | 6.3k |
| 8 | [Qwen: Qwen3.5 397B A17B](https://openrouter.ai/qwen/qwen3.5-397b-a17b) | 78.3% | ±2.4pp | $0.19 | 13.0m | 30.8k |
| 9 | [Google: Gemini 3.7 Flash](https://openrouter.ai/google/gemini-3.7-flash) | 78.3% | ±1.7pp | $0.15 | 3.1m | 16.3k |
| 10 | [Xiaomi: MiMo-V2.6-Flash](https://openrouter.ai/xiaomi/mimo-v2.6-flash)  Pareto | 78.2% | ±1.5pp | $0.014 | 6.7m | 21.1k |
| 11 | [Qwen: Qwen3.8 27B](https://openrouter.ai/qwen/qwen3.8-27b) | 78.0% | ±2.4pp | $0.069 | 4.5m | 14.2k |
| 12 | [DeepSeek: DeepSeek V4 Pro 0813](https://openrouter.ai/deepseek/deepseek-v4-pro-0813) | 77.9% | ±2.4pp | $0.099 | 5.0m | 20.7k |
| 13 | [Qwen: Qwen3.5-122B-A10B](https://openrouter.ai/qwen/qwen3.5-122b-a10b) | 77.3% | ±2.9pp | $0.17 | 9.8m | 36.4k |
| 14 | [Anthropic: Claude Opus 4.5](https://openrouter.ai/anthropic/claude-opus-4.5) | 77.0% | ±2.1pp | $0.54 | 2.9m | 10.7k |
| 15 | [Google: Gemini 3.1 Pro Preview](https://openrouter.ai/google/gemini-3.1-pro-preview) | 77.0% | ±0.3pp | $0.35 | 3.0m | 12.7k |
| 16 | [Google: Gemini 3.5 Flash Lite](https://openrouter.ai/google/gemini-3.5-flash-lite) | 76.9% | ±2.2pp | $0.098 | 1.7m | 23.9k |
| 17 | [Z.ai: GLM 5.3](https://openrouter.ai/z-ai/glm-5.3) | 76.8% | ±3.3pp | $0.059 | 1.9m | 6.15k |
| 18 | [DeepSeek: DeepSeek V4 Pro 0423](https://openrouter.ai/deepseek/deepseek-v4-pro) | 76.8% | ±2.4pp | $0.050 | 3.8m | 12.6k |
| 19 | [Xiaomi: MiMo-V2.6-Pro](https://openrouter.ai/xiaomi/mimo-v2.6-pro) | 76.8% | ±4.7pp | $0.073 | 16.9m | 47k |
| 20 | [Anthropic: Claude Opus 4.8](https://openrouter.ai/anthropic/claude-opus-4.8) | 76.8% | ±2.0pp | $0.49 | 2.1m | 8.07k |
| 21 | [Anthropic: Claude Opus 4.7](https://openrouter.ai/anthropic/claude-opus-4.7) | 76.7% | ±2.4pp | $0.42 | 1.6m | 5.61k |
| 22 | [Amazon: Nova Micro 1.0](https://openrouter.ai/amazon/nova-micro-v1) | 76.7% | ±0.0pp | $1.28 | 1.6m | 5.71k |
| 23 | [Qwen: Qwen3.6 27B](https://openrouter.ai/qwen/qwen3.6-27b) | 76.2% | ±3.6pp | $0.14 | 14.3m | 31.9k |
| 24 | [GLM 5.3](https://openrouter.ai/z-ai/glm-5.3)  digitalocean | 76.0% | \-- | $0.016 | 42s | 1.76k |
| 25 | [Tencent: Hy4 preview](https://openrouter.ai/tencent/hy4-preview) | 75.8% | ±3.5pp | $0.12 | 17.0m | 26.2k |
| 26 | [DeepSeek: DeepSeek V4.1 Flash](https://openrouter.ai/deepseek/deepseek-v4.1-flash) | 75.8% | ±2.6pp | $0.034 | 3.8m | 35.2k |
| 27 | [Z.ai: GLM 5](https://openrouter.ai/z-ai/glm-5) | 75.8% | ±3.1pp | $0.045 | 3.1m | 9.38k |
| 28 | [Z.ai: GLM 5.3 Flash](https://openrouter.ai/z-ai/glm-5.3-flash)  Pareto | 75.6% | ±2.0pp | $0.009 | 2.0m | 4.71k |
| 29 | [Anthropic: Claude Sonnet 5](https://openrouter.ai/anthropic/claude-sonnet-5) | 75.5% | ±3.0pp | $0.20 | 2.0m | 7.81k |
| 30 | [Google: Gemini 3.6 Flash](https://openrouter.ai/google/gemini-3.6-flash) | 75.3% | ±2.7pp | $0.17 | 2.5m | 22.9k |
| 31 | [SpaceXAI: Grok 4.6](https://openrouter.ai/x-ai/grok-4.6) | 75.3% | ±0.7pp | $0.33 | 4.0m | 12k |
| 32 | [Qwen: Qwen3.8 2.4T A95B](https://openrouter.ai/qwen/qwen3.8-2.4t-a95b) | 75.3% | ±1.5pp | $0.19 | 4.9m | 11.8k |
| 33 | [Google: Gemma 4 31B](https://openrouter.ai/google/gemma-4-31b-it) | 75.3% | ±3.1pp | $0.030 | 8.0m | 11.8k |
| 34 | [Google: Gemini 3 Flash Preview](https://openrouter.ai/google/gemini-3-flash-preview) | 75.3% | ±3.3pp | $0.12 | 2.5m | 19.8k |
| 35 | [OpenAI: GPT-5.3-Codex](https://openrouter.ai/openai/gpt-5.3-codex)  OpenAI | 75.3% | \-- | $0.30 | 3.0m | 13.6k |
| 36 | [Anthropic: Claude Opus 5.5](https://openrouter.ai/anthropic/claude-opus-5.5) | 75.2% | ±1.9pp | $0.34 | 2.0m | 7.11k |
| 37 | [Anthropic: Claude Opus 4.6](https://openrouter.ai/anthropic/claude-opus-4.6) | 75.2% | ±2.7pp | $0.50 | 3.2m | 10.1k |
| 38 | [MiniMax: MiniMax M3](https://openrouter.ai/minimax/minimax-m3) | 75.0% | ±2.8pp | $0.025 | 2.6m | 9.06k |
| 39 | [OpenAI: GPT-5.4](https://openrouter.ai/openai/gpt-5.4) | 75.0% | ±0.3pp | $0.29 | 2.9m | 10.4k |
| 40 | [DeepSeek: DeepSeek V4 Flash Vision Exp](https://openrouter.ai/deepseek/deepseek-v4-flash-vision-exp) | 74.8% | ±2.0pp | $0.030 | 3.3m | 18.7k |
| 41 | [DeepSeek: DeepSeek V4 Flash 0423](https://openrouter.ai/deepseek/deepseek-v4-flash) | 74.8% | ±2.0pp | $0.011 | 3.8m | 13.9k |
| 42 | [Meta: Muse Spark Open](https://openrouter.ai/meta/muse-spark-open) | 74.7% | \-- | $0.087 | 60s | 8.64k |
| 43 | [Meta: Muse Glimmer 30B](https://openrouter.ai/meta/muse-glimmer-30b) | 74.7% | ±3.4pp | $0.037 | 3.3m | 13.6k |
| 44 | [DeepSeek: DeepSeek V3.2](https://openrouter.ai/deepseek/deepseek-v3.2) | 74.5% | ±2.4pp | $0.039 | 10.2m | 16k |
| 45 | [Anthropic: Claude Sonnet 4.6](https://openrouter.ai/anthropic/claude-sonnet-4.6) | 74.4% | ±2.8pp | $0.33 | 3.3m | 11.6k |
| 46 | [Xiaomi: MiMo-V2.5-Pro](https://openrouter.ai/xiaomi/mimo-v2.5-pro) | 74.3% | ±3.4pp | $0.028 | 7.3m | 14.7k |
| 47 | [DeepSeek: DeepSeek V4 Flash 0731](https://openrouter.ai/deepseek/deepseek-v4-flash-0731) | 74.1% | ±5.0pp | $0.009 | 5.0m | 15.2k |
| 48 | [MoonshotAI: Kimi K2.6](https://openrouter.ai/moonshotai/kimi-k2.6) | 73.9% | ±2.1pp | $0.066 | 4.3m | 12.7k |
| 49 | [MoonshotAI: Kimi K2.7 Code](https://openrouter.ai/moonshotai/kimi-k2.7-code) | 73.8% | ±2.7pp | $0.079 | 2.6m | 8.79k |
| 50 | [OpenAI: GPT-5.5](https://openrouter.ai/openai/gpt-5.5) | 73.7% | ±1.0pp | $0.48 | 2.1m | 7.21k |
| 51 | [Z.ai: GLM 5.1](https://openrouter.ai/z-ai/glm-5.1) | 73.4% | ±4.0pp | $0.090 | 3.8m | 10.1k |
| 52 | [OpenAI: GPT-5.6 Sol](https://openrouter.ai/openai/gpt-5.6-sol) | 73.3% | ±2.7pp | $0.13 | 1.8m | 5.15k |
| 53 | [MoonshotAI: Kimi K3](https://openrouter.ai/moonshotai/kimi-k3) | 73.3% | ±2.6pp | $0.29 | 6.0m | 10.5k |
| 54 | [DeepSeek: DeepSeek V4.1 Flash 1017](https://openrouter.ai/deepseek/deepseek-v4.1-flash-1017) | 73.3% | \-- | $0.015 | 88s | 12.3k |
| 55 | [NVIDIA: Nemotron 3.5 Super VL](https://openrouter.ai/nvidia/nemotron-3.5-super-vl) | 73.3% | ±2.0pp | $0.039 | 2.6m | 14.5k |
| 56 | [Google: Gemini 3.5 Flash](https://openrouter.ai/google/gemini-3.5-flash) | 73.1% | ±2.3pp | $0.40 | 2.9m | 27.1k |
| 57 | [Anthropic: Claude Sonnet 4.5](https://openrouter.ai/anthropic/claude-sonnet-4.5) | 72.8% | ±3.4pp | $0.33 | 3.5m | 10.4k |
| 58 | [OpenAI: GPT-6 Astra Pro](https://openrouter.ai/openai/gpt-6-astra-pro) | 72.7% | \-- | $2.91 | 5.5m | 12.4k |
| 59 | [Anthropic: Claude Haiku 5.5](https://openrouter.ai/anthropic/claude-haiku-5.5) | 72.7% | ±4.7pp | $0.011 | 87s | 10.7k |
| 60 | [Xiaomi: MiMo-V2.5](https://openrouter.ai/xiaomi/mimo-v2.5) | 72.5% | ±3.9pp | $0.010 | 6.2m | 14.2k |
| 61 | [OpenAI: GPT-5.6 Terra](https://openrouter.ai/openai/gpt-5.6-terra) | 72.3% | ±0.3pp | $0.11 | 83s | 3.74k |
| 62 | [Qwen: Qwen3.6 35B A3B](https://openrouter.ai/qwen/qwen3.6-35b-a3b) | 72.3% | ±8.2pp | $0.042 | 4.5m | 23.8k |
| 63 | [Z.ai: GLM 4.6](https://openrouter.ai/z-ai/glm-4.6) | 72.3% | ±1.6pp | $0.052 | 6.4m | 9.41k |
| 64 | [MoonshotAI: Kimi K2 Thinking](https://openrouter.ai/moonshotai/kimi-k2-thinking) | 72.0% | \-- | $0.054 | 4.4m | 8.79k |
| 65 | [NVIDIA: Nemotron 3 Ultra](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b) | 72.0% | \-- | $0.15 | 1.8m | 13.1k |
| 66 | [Qwen: Qwen3.7 Max](https://openrouter.ai/qwen/qwen3.7-max)  AtlasCloud | 72.0% | \-- | $0.40 | 3.3m | 16.3k |
| 67 | [Google: Gemini 3.1 Flash Lite](https://openrouter.ai/google/gemini-3.1-flash-lite) | 72.0% | ±0.9pp | $0.093 | 2.5m | 49.3k |
| 68 | [Qwen: Qwen3.5-9B](https://openrouter.ai/qwen/qwen3.5-9b) | 71.7% | ±4.9pp | $0.035 | 18.6m | 50.7k |
| 69 | [DeepSeek: DeepSeek V3.1 Terminus](https://openrouter.ai/deepseek/deepseek-v3.1-terminus) | 71.7% | ±1.5pp | $0.059 | 8.6m | 13.9k |
| 70 | [DeepSeek: DeepSeek V3.2 Exp](https://openrouter.ai/deepseek/deepseek-v3.2-exp) | 71.5% | \-- | $0.073 | 9.3m | 12.3k |
| 71 | [Z.ai: GLM 5.2](https://openrouter.ai/z-ai/glm-5.2) | 71.4% | ±3.3pp | $0.043 | 2.0m | 8.45k |
| 72 | [Z.ai: GLM 4.7](https://openrouter.ai/z-ai/glm-4.7) | 71.3% | ±2.2pp | $0.064 | 5.1m | 9.73k |
| 73 | [Qwen: Qwen3.8 Flash](https://openrouter.ai/qwen/qwen3.8-flash)  Alibaba | 71.3% | \-- | $0.017 | 5.5m | 17.2k |
| 74 | [Google: Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash) | 71.3% | \-- | $0.21 | 4.4m | 27.6k |
| 75 | [inclusionAI: Ling 3.0 Flash Fin](https://openrouter.ai/inclusionai/ling-3.0-flash-fin)  Pareto | 70.7% | \-- | $0.005 | 2.7m | 17k |
| 76 | [MiniMax: MiniMax M2.7](https://openrouter.ai/minimax/minimax-m2.7) | 70.7% | ±1.2pp | $0.026 | 3.4m | 10k |
| 77 | [OpenAI: GPT-5.6 Sol Pro](https://openrouter.ai/openai/gpt-5.6-sol-pro) | 70.7% | \-- | $0.71 | 4.8m | 22.9k |
| 78 | [Qwen: Qwen3.5-35B-A3B](https://openrouter.ai/qwen/qwen3.5-35b-a3b) | 70.6% | ±10.4pp | $0.075 | 12.4m | 45.6k |
| 79 | [OpenAI: GPT-5.6 Luna Pro](https://openrouter.ai/openai/gpt-5.6-luna-pro) | 70.3% | ±0.3pp | $0.085 | 5.8m | 32.9k |
| 80 | [Qwen: Qwen3.7 Plus](https://openrouter.ai/qwen/qwen3.7-plus)  Alibaba | 70.3% | \-- | $0.054 | 6.6m | 20.7k |
| 81 | [OpenAI: GPT-5.6 Luna](https://openrouter.ai/openai/gpt-5.6-luna) | 70.0% | ±0.9pp | $0.011 | 1.9m | 5.35k |
| 82 | [OpenAI: GPT-5 Mini](https://openrouter.ai/openai/gpt-5-mini) | 70.0% | ±2.5pp | $0.13 | 9.9m | 57.5k |
| 83 | [Anthropic: Claude Sonnet 4](https://openrouter.ai/anthropic/claude-sonnet-4) | 70.0% | \-- | $0.30 | 2.1m | 8.5k |
| 84 | [GLM 5.3 Flash](https://openrouter.ai/z-ai/glm-5.3-flash)  digitalocean | 70.0% | \-- | $0.004 | 49s | 1.57k |
| 85 | [inclusionAI: Ling 3.0 Flash VL](https://openrouter.ai/inclusionai/ling-3.0-flash-vl)  Pareto | 70.0% | \-- | $0.003 | 1.6m | 17.1k |
| 86 | [OpenAI: GPT-6.1 Sol](https://openrouter.ai/openai/gpt-6.1-sol) | 70.0% | \-- | $0.10 | 2.4m | 3.64k |
| 87 | [MoonshotAI: Kimi K2.5](https://openrouter.ai/moonshotai/kimi-k2.5) | 69.5% | ±3.1pp | $0.050 | 5.9m | 9.14k |
| 88 | [OpenAI: GPT-6 Sol](https://openrouter.ai/openai/gpt-6-sol) | 69.3% | \-- | $0.13 | 1.6m | 4.98k |
| 89 | [Reflection: Beam 1.0 501B A23B](https://openrouter.ai/reflection/beam-1.0-501b-a23b)  Io Net | 69.3% | \-- | $0.028 | 3.5m | 14.9k |
| 90 | [Z.ai: GLM 4.5 Air](https://openrouter.ai/z-ai/glm-4.5-air) | 69.3% | \-- | $0.017 | 4.8m | 9.63k |
| 91 | [Google: Gemma 4 26B A4B](https://openrouter.ai/google/gemma-4-26b-a4b-it) | 68.7% | ±4.5pp | $0.018 | 6.4m | 20.1k |
| 92 | [inclusionAI: Ling 3.0 Flash](https://openrouter.ai/inclusionai/ling-3.0-flash)  Pareto | 68.7% | \-- | $0.002 | 78s | 11.7k |
| 93 | [OpenAI: GPT-6.1 Terra](https://openrouter.ai/openai/gpt-6.1-terra) | 68.7% | \-- | $0.068 | 79s | 4.78k |
| 94 | [OpenAI: GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra) | 68.0% | \-- | $0.58 | 2.4m | 3.73k |
| 95 | [Z.ai: GLM 4.7 Flash](https://openrouter.ai/z-ai/glm-4.7-flash) | 67.5% | ±2.2pp | $0.008 | 4.4m | 9.57k |
| 96 | [OpenAI: GPT-5](https://openrouter.ai/openai/gpt-5) | 67.3% | ±2.7pp | $0.63 | 12.2m | 54.9k |
| 97 | [OpenAI: GPT-6 Luna](https://openrouter.ai/openai/gpt-6-luna) | 67.3% | \-- | $0.009 | 2.0m | 8.9k |
| 98 | [Thinking Machines: Inkling](https://openrouter.ai/thinkingmachines/inkling) | 67.2% | ±2.8pp | $0.080 | 81s | 3.53k |
| 99 | [OpenAI: GPT-6 Luna Pro](https://openrouter.ai/openai/gpt-6-luna-pro) | 66.7% | \-- | $0.039 | 5.2m | 32k |
| 100 | [MiniMax: MiniMax M2.5](https://openrouter.ai/minimax/minimax-m2.5) | 66.4% | ±2.8pp | $0.023 | 5.4m | 10.4k |
| 101 | [Anthropic: Claude Haiku 4.5](https://openrouter.ai/anthropic/claude-haiku-4.5) | 66.2% | ±3.1pp | $0.12 | 2.1m | 12.6k |
| 102 | [MiniMax: MiniMax M3.1 Flash](https://openrouter.ai/minimax/minimax-m3.1-flash) | 66.0% | \-- | $0.013 | 4.6m | 15.1k |
| 103 | [NVIDIA: Nemotron 3.5 Lightning](https://openrouter.ai/nvidia/nemotron-3.5-lightning) | 65.7% | ±2.0pp | $0.017 | 5.4m | 22.9k |
| 104 | [OpenAI: gpt-oss-120b](https://openrouter.ai/openai/gpt-oss-120b) | 65.4% | ±3.4pp | $0.013 | 6.9m | 18.1k |
| 105 | [OpenAI: GPT-5.4 Nano](https://openrouter.ai/openai/gpt-5.4-nano) | 65.3% | ±2.4pp | $0.032 | 2.4m | 17.4k |
| 106 | [OpenAI: GPT-5.4 Mini](https://openrouter.ai/openai/gpt-5.4-mini) | 63.8% | ±4.2pp | $0.089 | 2.0m | 12.6k |
| 107 | [Qwen: Qwen3 235B A22B Thinking 2507](https://openrouter.ai/qwen/qwen3-235b-a22b-thinking-2507) | 61.6% | ±1.0pp | $0.13 | 10.5m | 29.6k |
| 108 | [MiniMax: MiniMax M2.1](https://openrouter.ai/minimax/minimax-m2.1) | 61.3% | \-- | $0.025 | 2.9m | 11.3k |
| 109 | [Z.ai: GLM 4.6V](https://openrouter.ai/z-ai/glm-4.6v) | 60.7% | \-- | $0.032 | 5.6m | 8.85k |
| 110 | [Thinking Machines: Inkling Small](https://openrouter.ai/thinkingmachines/inkling-small) | 60.7% | ±2.7pp | $0.047 | 3.5m | 3.67k |
| 111 | [MoonshotAI: Kimi K2 0905](https://openrouter.ai/moonshotai/kimi-k2-0905)  Novita | 59.7% | \-- | $0.093 | 2.0m | 3.56k |
| 112 | [IBM: Granite 4.2 8B](https://openrouter.ai/ibm-granite/granite-4.2-8b)  DeepInfra | 58.3% | \-- | $0.015 | 13.9m | 38.6k |
| 113 | [Google: Gemini 2.5 Pro](https://openrouter.ai/google/gemini-2.5-pro) | 58.0% | ±2.7pp | $0.21 | 3.0m | 12.1k |
| 114 | [Google: Gemini 2.5 Flash](https://openrouter.ai/google/gemini-2.5-flash) | 57.1% | ±0.8pp | $0.029 | 78s | 8k |
| 115 | [Qwen: Qwen3 Coder Next](https://openrouter.ai/qwen/qwen3-coder-next) | 55.4% | ±11.0pp | $0.040 | 1.7m | 4.36k |
| 116 | [OpenAI: gpt-oss-20b](https://openrouter.ai/openai/gpt-oss-20b) | 53.6% | ±1.7pp | $0.019 | 21.3m | 84.7k |
| 117 | [DeepSeek: DeepSeek V3.1](https://openrouter.ai/deepseek/deepseek-chat-v3.1) | 52.3% | ±8.8pp | $0.050 | 6.9m | 7.61k |
| 118 | [NVIDIA: Nemotron 3 Nano 30B A3B](https://openrouter.ai/nvidia/nemotron-3-nano-30b-a3b) | 51.8% | ±2.5pp | $0.028 | 7.4m | 58.3k |
| 119 | [Google: Gemini 2.5 Flash Lite](https://openrouter.ai/google/gemini-2.5-flash-lite) | 50.3% | ±3.0pp | $0.018 | 2.3m | 31k |
| 120 | [DeepSeek: R1 0528](https://openrouter.ai/deepseek/deepseek-r1-0528) | 50.0% | ±3.5pp | $0.16 | 33.6m | 38.5k |
| 121 | [OpenAI: GPT-5 Nano](https://openrouter.ai/openai/gpt-5-nano) | 48.3% | ±3.7pp | $0.041 | 11.2m | 93.9k |
| 122 | [Google: Gemma 3 12B](https://openrouter.ai/google/gemma-3-12b-it)  DeepInfra | 48.0% | \-- | $0.011 | 80s | 3.76k |
| 123 | [Qwen: Qwen3 Coder 480B A35B](https://openrouter.ai/qwen/qwen3-coder) | 47.7% | ±3.0pp | $0.078 | 1.7m | 2.76k |
| 124 | [Qwen: Qwen3 Next 80B A3B Instruct](https://openrouter.ai/qwen/qwen3-next-80b-a3b-instruct) | 47.7% | ±2.3pp | $0.025 | 2.1m | 3.73k |
| 125 | [OpenAI: GPT-4.1](https://openrouter.ai/openai/gpt-4.1) | 47.7% | ±1.7pp | $0.13 | 53s | 2.67k |
| 126 | [Qwen: Qwen3 30B A3B](https://openrouter.ai/qwen/qwen3-30b-a3b) | 46.7% | \-- | $0.032 | 7.3m | 22.6k |
| 127 | [Qwen: Qwen3 32B](https://openrouter.ai/qwen/qwen3-32b) | 46.5% | ±2.1pp | $0.021 | 10.8m | 20.1k |
| 128 | [Mistral: Mistral Small 4](https://openrouter.ai/mistralai/mistral-small-2603)  Mistral | 46.0% | \-- | $0.011 | 87s | 9.09k |
| 129 | [Qwen: Qwen3 14B](https://openrouter.ai/qwen/qwen3-14b)  DeepInfra | 44.0% | ±0.7pp | $0.031 | 11.3m | 16.7k |
| 130 | [OpenAI: GPT-4.1 Mini](https://openrouter.ai/openai/gpt-4.1-mini) | 43.8% | ±1.1pp | $0.026 | 66s | 2.41k |
| 131 | [DeepSeek: DeepSeek V3 0324](https://openrouter.ai/deepseek/deepseek-chat-v3-0324) | 43.5% | ±2.1pp | $0.074 | 13.0m | 20.3k |
| 132 | [Meta: Llama 4 Maverick](https://openrouter.ai/meta-llama/llama-4-maverick) | 42.9% | ±1.4pp | $0.047 | 2.3m | 2.14k |
| 133 | [Qwen: Qwen3 Coder 30B A3B Instruct](https://openrouter.ai/qwen/qwen3-coder-30b-a3b-instruct) | 42.7% | ±0.0pp | $0.030 | 4.6m | 3.55k |
| 134 | [OpenAI: GPT-4o (2024-08-06)](https://openrouter.ai/openai/gpt-4o-2024-08-06)  OpenAI | 42.7% | ±0.7pp | $0.21 | 52s | 2.19k |
| 135 | [OpenAI: GPT-4o](https://openrouter.ai/openai/gpt-4o)  OpenAI | 41.7% | ±3.0pp | $0.20 | 53s | 2.09k |
| 136 | [Qwen: Qwen3 VL 235B A22B Instruct](https://openrouter.ai/qwen/qwen3-vl-235b-a22b-instruct) | 41.0% | ±2.0pp | $0.064 | 6.0m | 9.12k |
| 137 | [DeepSeek: DeepSeek V3](https://openrouter.ai/deepseek/deepseek-chat) | 39.8% | ±1.8pp | $0.069 | 5.3m | 7.31k |
| 138 | [Qwen: Qwen3 235B A22B Instruct 2507](https://openrouter.ai/qwen/qwen3-235b-a22b-2507) | 39.5% | ±12.0pp | $0.024 | 3.2m | 3.37k |
| 139 | [Qwen: Qwen3 30B A3B Instruct 2507](https://openrouter.ai/qwen/qwen3-30b-a3b-instruct-2507) | 39.0% | ±1.9pp | $0.026 | 4.0m | 4.33k |
| 140 | [Qwen: Qwen3 VL 8B Instruct](https://openrouter.ai/qwen/qwen3-vl-8b-instruct) | 36.3% | \-- | $0.039 | 2.0m | 4.04k |
| 141 | [Qwen: Qwen3 VL 30B A3B Instruct](https://openrouter.ai/qwen/qwen3-vl-30b-a3b-instruct) | 35.2% | ±2.2pp | $0.079 | 3.5m | 7.35k |
| 142 | [Meta: Llama 3.3 70B Instruct](https://openrouter.ai/meta-llama/llama-3.3-70b-instruct) | 32.7% | ±4.3pp | $0.040 | 1.6m | 1.3k |
| 143 | [OpenAI: GPT-4o-mini](https://openrouter.ai/openai/gpt-4o-mini)  OpenAI | 28.4% | ±3.2pp | $0.021 | 62s | 3.8k |
| 144 | [Qwen2.5 72B Instruct](https://openrouter.ai/qwen/qwen-2.5-72b-instruct) | 24.0% | ±3.3pp | $0.073 | 11.0m | 5.32k |
| 145 | [Meta: Llama 3.1 8B Instruct](https://openrouter.ai/meta-llama/llama-3.1-8b-instruct) | 22.2% | ±6.0pp | $0.004 | 17s | 1.55k |
| 146 | [OpenAI: GPT-4.1 Nano](https://openrouter.ai/openai/gpt-4.1-nano) | 11.0% | ±1.0pp | $0.007 | 64s | 2.31k |

## Why we run this benchmark

It's a tool-calling benchmark that is hard to game. Grading depends on live tool-call trajectories rather than memorized answers, so it resists training-data leakage better than Q&A-style evals. It exercises every tool-calling failure mode (wrong arguments, skipped policy checks, giving up, hallucinated confirmations) at a relatively low cost per run. The relative scores also carry more signal than the absolute ones. The same model can score differently across providers, and those deltas are what [Exacto](https://openrouter.ai/blog/announcements/provider-variance-introducing-exacto/) routing uses to pick higher-accuracy endpoints.

Each task is a simulated airline support conversation with a scripted user, a toolbox (flight search, booking changes, refunds, loyalty policies), and a gold reference solution. A task passes only if the final database state and the messages to the user match the reference; partial credit is not awarded.

## What the scores can and can't tell you

There is still headroom. Top models fail roughly one in five tasks, and the airline domain is the hardest τ²-Bench split. Accuracy differences here separate models that follow multi-step policies from ones that merely chat well.

The floor is high, though. Many tasks reward inaction. A refusal task with an empty gold action list passes for any agent that changes nothing. Even weak models score well above zero, so the meaningful spread sits at the top of the range.

The benchmark is public, so tasks may appear in training corpora. Contamination inflates scores less here than in Q&A-style evals, though, since a leaked task still has to be executed correctly, step by step, against a live database.

Scoring fidelity has limits. The checker verifies two things: the final database hash and exact substring matches in the agent's messages. Each task's natural-language assertions ("agent should refuse the cancellation") are metadata, and no judge model reads the transcript. So a savings calculation fails if the agent says "$23,552.50" when the checker greps for "23553".

The user simulator matters too. We pin it to gemini-2.5-flash so agent scores stay comparable, but the sim is itself an LLM with failure modes of its own. It can stop the conversation before the agent finishes, leak its hidden task instructions, or keep a stuck agent looping until the 200-step ceiling kills the run. Swapping the sim model shifts absolute scores, which is why cross-paper τ²-Bench numbers rarely line up exactly.

## How a task is scored

Every task ships a gold solution: a list of tool calls, strings the agent must say, and natural-language assertions. After the conversation ends, the checker replays the gold tool calls against a fresh database and compares hashes with the agent's final database. It then greps the agent's messages for each required string. The reward is the product of those two checks:

```
reward = db_match × communicate_met   // each ∈ {0, 1}
db_match        = hash(agent DB) == hash(gold DB)
communicate_met = every required string appears in an agent message
any run that hits MAX_STEPS instead of a clean stop scores 0 outright
```

The rollouts below are from real runs, with gemini-2.5-flash as the user simulator throughout.

reward = 1

### Pass: three changes in one request, all three land

Task 17 agent: openai/gpt-5.1

For reservation FQ8APE: add 3 checked bags, swap the passenger to Omar Rossi, and upgrade basic economy to economy, paying with a gift card.

- Database must match the gold state: update\_reservation\_flights (economy upgrade), update\_reservation\_passengers, and update\_reservation\_baggages with exact arguments
- communicate\_info is empty, so no string check applies

db ✓

communicate ✓

USER\_STOP

The agent looked up the user, found the right reservation among several, confirmed the changes and payment method, then made all three writes: passenger swap, cabin upgrade, and bags. The final database hashes match the gold state and the run ends on USER\_STOP, so reward is 1. This is what the eval is designed to measure: multi-step tool use under policy constraints, done correctly.

## Methodology

Scores aggregate successful runs from the newest 90 days, weighted by task count, with a minimum of 45 graded tasks per model-provider pair. A model's headline score uses its default routing (not pinned to a provider) when one exists; otherwise it falls back to the median provider. The standard deviation is measured across runs for that representative result. Cost, time, and token figures are per-task averages from the same runs. Best value is the cheapest Pareto-optimal model within 5 points of the top score.

These are the same measurements that power [Exacto routing](https://openrouter.ai/docs/guides/routing/auto-exacto). See the [docs](https://openrouter.ai/docs) for how routing works, or browse [all models](https://openrouter.ai/models) to try one.

## API access

These scores are available through OpenRouter's public benchmarks API, so you can retrieve the same model-level results programmatically.

```
GET https://openrouter.ai/api/v1/benchmarks?source=openrouter
Authorization: Bearer <API key>
```

Use `task_type=agentic` to filter to `tau_bench_verified_airline`. Each item represents one model and includes `accuracy`, `accuracy_stddev`, `avg_cost_per_task`, `total_tasks`, and `last_run_timestamp`. See the [benchmarks API docs](https://openrouter.ai/docs/api/api-reference/benchmarks/list-benchmarks).

## Download and cite

A snapshot of this leaderboard is published in the `benchmark-leaderboard` open dataset (filter on the `benchmark` column), regenerated daily with no API key required. The current snapshot was generated on Oct 30, 2026, 1:45 AM UTC. It is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), so you can reuse and republish it with attribution to OpenRouter.

- [Download CSV](https://openrouter.ai/api/v1/datasets/exports/benchmark-leaderboard/2026-10-30.csv) (text/csv)
- [Download JSON](https://openrouter.ai/api/v1/datasets/exports/benchmark-leaderboard/2026-10-30.json) (application/json)
- [Snapshot manifest](https://openrouter.ai/api/v1/datasets/exports/benchmark-leaderboard/2026-10-30.manifest.json) (SHA-256 checksums of the files above)
- [Latest manifest](https://openrouter.ai/api/v1/datasets/exports/benchmark-leaderboard/latest.manifest.json) (mutable alias, updated as snapshots are published)

Column definitions, methodology and redaction rules are in the [dataset README](https://openrouter.ai/api/v1/datasets/exports/README.md).

### Cite this leaderboard

```
OpenRouter (2026). τ²-Bench: Airline results on OpenRouter, 2026-10-30 snapshot. https://openrouter.ai/benchmarks/tau2-bench-airline. Licensed under CC BY 4.0.
```