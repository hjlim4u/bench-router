---
title: "VGI-Bench Leaderboard"
site: "OpenRouter"
published: Oct 30, 2026, 5:45 PM UTC
source: "https://openrouter.ai/benchmarks/vgi-bench"
domain: "openrouter.ai"
language: "en-US"
description: "VGI-Bench compares video models by accuracy and cost, with real trajectories showing each model's video, reasoning trace, and committed answer."
word_count: 1080
---

## VGI-Bench

VGI-Bench (Video General Intelligence Bench, by Seldon) asks multiple-choice questions about long-form videos: what appeared first, what was on screen at the same time as something else, what a narrator said while a specific shot was up, and questions whose premise never happens. Each sample below is a real run through OpenRouter. The model received the full video and the question in one turn at temperature 0, and the graded answer is the letter on its final `Answer:` line.

[Dataset](https://huggingface.co/datasets/Seldon-Technologies/VGIBench) [GitHub](https://github.com/Seldon-Foundation/VGIBench)

## Model comparison

Most Accurate

![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)

[ByteDance Seed: Seed 1.6](https://openrouter.ai/bytedance-seed/seed-1.6)

66.2%

Best Value

![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)

[ByteDance Seed: Seed 1.6](https://openrouter.ai/bytedance-seed/seed-1.6)

$0.039/question

Fastest

![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)

[ByteDance Seed: Seed 1.6](https://openrouter.ai/bytedance-seed/seed-1.6)

64s

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

Accuracy over the public split (439 questions, runs need at least 395 answered to be listed), with cost, time, and input and output tokens per question for each provider endpoint the model was run on. Scores aggregate successful runs from the newest 90 days.

| # | Model | Accuracy | Std dev | Cost / question | Time / question | Input tok / question | Output tok / question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [ByteDance Seed: Seed 1.6](https://openrouter.ai/bytedance-seed/seed-1.6)  Pareto | 66.2% | ±1.0pp | $0.039 | 64s | 141k | 2.03k |
| 2 | [Qwen: Qwen3.8 Omni Flash](https://openrouter.ai/qwen/qwen3.8-omni-flash)  Alibaba | 65.5% | \-- | $0.046 | 4.6m | 412k | 11.5k |
| 3 | [ByteDance Seed: Seed-2.0-Lite](https://openrouter.ai/bytedance-seed/seed-2.0-lite)  Seed | 63.7% | ±4.8pp | $0.073 | 2.5m | 241k | 6.5k |
| 4 | [Qwen: Qwen3.8 Max (0902)](https://openrouter.ai/qwen/qwen3.8-max-0902)  Alibaba | 63.7% | \-- | $0.55 | 8.6m | 613k | 20.1k |
| 5 | [Meta: Muse Wonder](https://openrouter.ai/meta/muse-wonder)  Meta | 63.6% | \-- | $1.03 | 3.1m | 233k | 8.62k |
| 6 | [Google: Gemini 2.5 Pro](https://openrouter.ai/google/gemini-2.5-pro)  Google AI Studio | 61.4% | ±0.7pp | $0.061 | 1.8m | 341 | 6.04k |
| 7 | [Meta: Muse Spark 1.3](https://openrouter.ai/meta/muse-spark-1.3)  Meta | 61.1% | \-- | $0.22 | 4.2m | 227k | 14.3k |
| 8 | [Qwen: Qwen3.8 Max (0803)](https://openrouter.ai/qwen/qwen3.8-max)  Alibaba | 58.0% | \-- | $0.33 | 8.2m | 579k | 13.6k |
| 9 | [Qwen: Qwen3.8 Flash](https://openrouter.ai/qwen/qwen3.8-flash)  Alibaba | 56.8% | \-- | $0.11 | 6.2m | 1.52M | 24.1k |
| 10 | [Google: Gemini 3 Flash Preview](https://openrouter.ai/google/gemini-3-flash-preview)  Google AI Studio | 54.8% | ±0.5pp | $0.14 | 4.7m | 111k | 40.2k |
| 11 | [Qwen: Qwen3.7 Flash](https://openrouter.ai/qwen/qwen3.7-flash)  Alibaba | 54.8% | ±0.5pp | $0.27 | 5.6m | 1.48M | 10.9k |
| 12 | [Meta: Muse Spark 1.1](https://openrouter.ai/meta/muse-spark-1.1)  Meta | 54.2% | ±0.5pp | $0.24 | 2.6m | 151k | 21.8k |
| 13 | [Meta: Muse Spark 1.2](https://openrouter.ai/meta/muse-spark-1.2)  Meta | 51.0% | ±0.6pp | $0.16 | 2.0m | 150k | 15.3k |
| 14 | [Google: Gemma 4 31B](https://openrouter.ai/google/gemma-4-31b-it)  Pareto | 50.8% | \-- | $0.008 | 8.1m | 7.43k | 21.1k |
| 15 | [Qwen: Qwen3.6 Plus](https://openrouter.ai/qwen/qwen3.6-plus)  Alibaba | 50.6% | ±0.4pp | $0.21 | 7.1m | 532k | 20.9k |
| 16 | [Meta: Muse Spark Open](https://openrouter.ai/meta/muse-spark-open) | 50.5% | \-- | $0.084 | 2.8m | 23.9k | 12.7k |
| 17 | [Google: Gemini 2.5 Flash](https://openrouter.ai/google/gemini-2.5-flash)  Google AI Studio | 50.0% | ±0.3pp | $0.024 | 1.9m | 341 | 9.42k |
| 18 | [Google: Gemini 2.5 Flash Lite](https://openrouter.ai/google/gemini-2.5-flash-lite)  Google AI Studio | 48.0% | \-- | $0.012 | 2.4m | 340 | 29.7k |
| 19 | [Qwen: Qwen3.8 27B](https://openrouter.ai/qwen/qwen3.8-27b) | 47.6% | ±2.0pp | $0.026 | 2.3m | 36.9k | 7.18k |
| 20 | [Xiaomi: MiMo-V2.5](https://openrouter.ai/xiaomi/mimo-v2.5)  Xiaomi | 46.5% | ±2.9pp | $0.018 | 6.4m | 272k | 13.2k |
| 21 | [Perceptron: Perceptron Mk1](https://openrouter.ai/perceptron/perceptron-mk1)  Perceptron | 46.2% | ±0.1pp | $0.008 | 2.7m | 46.4k | 817 |
| 22 | [Qwen: Qwen3.5-Flash](https://openrouter.ai/qwen/qwen3.5-flash-02-23)  Alibaba | 46.2% | ±1.2pp | $0.10 | 4.9m | 1.49M | 20.2k |
| 23 | [Qwen: Qwen3.5 397B A17B](https://openrouter.ai/qwen/qwen3.5-397b-a17b) | 46.0% | ±0.7pp | $0.95 | 8.8m | 1.46M | 21.8k |
| 24 | [Xiaomi: MiMo-X-Pro Preview](https://openrouter.ai/xiaomi/mimo-x-pro-preview)  Xiaomi | 45.6% | \-- | $0.027 | 4.6m | 77.4k | 14.7k |
| 25 | [Qwen: Qwen3.5 Plus 2026-02-15](https://openrouter.ai/qwen/qwen3.5-plus-02-15)  Alibaba | 45.5% | ±0.7pp | $0.17 | 7.5m | 532k | 21.3k |
| 26 | [Xiaomi: MiMo-X-Flash Preview](https://openrouter.ai/xiaomi/mimo-x-flash-preview)  Xiaomi | 45.4% | \-- | $0.034 | 5.2m | 337k | 11.9k |
| 27 | [Qwen: Qwen3.6 Flash](https://openrouter.ai/qwen/qwen3.6-flash)  Alibaba | 45.2% | ±0.8pp | $1.14 | 6.7m | 1.49M | 19.4k |
| 28 | [Qwen: Qwen3.5 Plus 2026-04-20](https://openrouter.ai/qwen/qwen3.5-plus-20260420)  Alibaba | 45.1% | ±0.6pp | $0.17 | 4.9m | 440k | 18.6k |
| 29 | [Xiaomi: MiMo-V2.6-Pro](https://openrouter.ai/xiaomi/mimo-v2.6-pro) | 44.9% | ±0.8pp | $0.035 | 6.9m | 77.3k | 18.5k |
| 30 | [ByteDance Seed: Seed-2.0-Mini](https://openrouter.ai/bytedance-seed/seed-2.0-mini)  Seed | 43.4% | ±2.9pp | $0.027 | 1.9m | 232k | 9.34k |
| 31 | [Xiaomi: MiMo-V2.6-Pro-UltraSpeed](https://openrouter.ai/xiaomi/mimo-v2.6-pro-ultraspeed)  Xiaomi | 43.4% | \-- | $0.34 | 3.2m | 77k | 21.1k |
| 32 | [Xiaomi: MiMo-V2.6-Flash](https://openrouter.ai/xiaomi/mimo-v2.6-flash) | 35.5% | ±3.4pp | $0.016 | 5.2m | 150k | 12k |
| 33 | [Z.ai: GLM 5.3 Flash](https://openrouter.ai/z-ai/glm-5.3-flash) | 34.6% | ±2.7pp | $0.028 | 8.3m | 58.2k | 43.9k |
| 34 | [MiniMax: MiniMax M3](https://openrouter.ai/minimax/minimax-m3) | 30.1% | ±2.6pp | $0.081 | 9.8m | 53.4k | 75.3k |
| 35 | [NVIDIA: Nemotron 3.5 Super VL](https://openrouter.ai/nvidia/nemotron-3.5-super-vl) | 28.9% | ±0.5pp | $0.015 | 1.8m | 15.6k | 27.8k |
| 36 | [Perceptron: Perceptron Mk1.5](https://openrouter.ai/perceptron/perceptron-mk1.5)  Perceptron | 28.9% | \-- | $0.019 | 1.6m | 49k | 7.48k |
| 37 | [MiniMax: MiniMax M3.1 Flash](https://openrouter.ai/minimax/minimax-m3.1-flash) | 27.2% | \-- | $0.013 | 2.1m | 120k | 16.6k |
| 38 | [Google: Gemma 4 26B A4B](https://openrouter.ai/google/gemma-4-26b-a4b-it)  Pareto | 26.1% | ±7.6pp | $0.004 | 3.2m | 4.59k | 9.83k |
| 39 | [Reka Edge](https://openrouter.ai/rekaai/reka-edge)  Pareto  Reka | 21.4% | ±0.2pp | $0.00015 | 31s | 1.49k | 30.5 |
| 40 | [inclusionAI: Ling 3.0 Flash VL](https://openrouter.ai/inclusionai/ling-3.0-flash-vl) | 19.2% | \-- | $0.001 | 1.8m | 5.71k | 9.46k |
| 41 | [Google: Gemini 4 Argon](https://openrouter.ai/google/gemini-4-argon) | 15.5% | \-- | $0.050 | 44s | 1.58k | 4.7k |
| 42 | [Google: Gemini 4 Carbon (EAP)](https://openrouter.ai/google/gemini-4-carbon-eap)  Google AI Studio | 14.7% | \-- | $0.32 | 3.0m | 1.63k | 15.5k |
| 43 | [Google: Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash) | 14.4% | \-- | $0.039 | 76s | 1.42k | 10.3k |
| 44 | [Elorian: Glimpse](https://openrouter.ai/elorian/glimpse)  Together | 13.8% | \-- | $0.022 | 47s | 6.28k | 6.46k |
| 45 | [Qwen: Qwen3.6 35B A3B](https://openrouter.ai/qwen/qwen3.6-35b-a3b) | 13.8% | \-- | $0.025 | 14.9m | 11k | 25.1k |
| 46 | [Qwen: Qwen3.5-122B-A10B](https://openrouter.ai/qwen/qwen3.5-122b-a10b)  Alibaba | 13.2% | \-- | $0.022 | 4.4m | 35.5k | 6.17k |
| 47 | [Google: Gemini 3.7 Flash](https://openrouter.ai/google/gemini-3.7-flash)  Google | 12.4% | \-- | $0.013 | 24s | 1.19k | 3.29k |
| 48 | [Z.ai: GLM 5V Turbo](https://openrouter.ai/z-ai/glm-5v-turbo)  Z.AI | 12.3% | ±0.5pp | $0.13 | 6.9m | 124k | 2.42k |
| 49 | [Qwen: Qwen3.5-35B-A3B](https://openrouter.ai/qwen/qwen3.5-35b-a3b) | 12.2% | ±0.3pp | $0.015 | 56s | 38.4k | 6.56k |
| 50 | [Qwen: Qwen3.6 27B](https://openrouter.ai/qwen/qwen3.6-27b) | 11.8% | ±0.4pp | $0.030 | 4.0m | 32.5k | 5.83k |
| 51 | [Google: Gemini 3.6 Flash](https://openrouter.ai/google/gemini-3.6-flash)  Google AI Studio | 11.5% | \-- | $0.016 | 24s | 1.39k | 3.97k |
| 52 | [Google: Gemini 3.1 Pro Preview](https://openrouter.ai/google/gemini-3.1-pro-preview)  Google AI Studio | 10.9% | \-- | $0.098 | 59s | 1.39k | 7.96k |
| 53 | [Google: Gemini 3.1 Pro Preview Custom Tools](https://openrouter.ai/google/gemini-3.1-pro-preview-customtools)  Google AI Studio | 10.6% | \-- | $0.098 | 60s | 1.39k | 8.02k |
| 54 | [Google: Gemini 3.5 Flash](https://openrouter.ai/google/gemini-3.5-flash)  Google AI Studio | 10.1% | \-- | $0.088 | 39s | 1.38k | 9.59k |
| 55 | [Google: Gemini 3.5 Flash Lite](https://openrouter.ai/google/gemini-3.5-flash-lite)  Google AI Studio | 8.4% | \-- | $0.006 | 13s | 1.39k | 2.08k |
| 56 | [Google: Gemini 3.1 Flash Lite](https://openrouter.ai/google/gemini-3.1-flash-lite)  Google AI Studio | 8.2% | \-- | $0.038 | 58s | 1.39k | 25.1k |
| 57 | [Google: Gemini 3.1 Flash Lite Preview](https://openrouter.ai/google/gemini-3.1-flash-lite-preview)  Google AI Studio | 8.2% | \-- | $0.038 | 58s | 1.38k | 25.1k |
| 58 | [MoonshotAI: Kimi K3](https://openrouter.ai/moonshotai/kimi-k3) | 6.3% | ±5.7pp | $0.025 | 36s | 5.46k | 1.69k |
| 59 | [Z.ai: GLM 4.6V](https://openrouter.ai/z-ai/glm-4.6v)  Z.AI | 5.6% | ±4.3pp | $0.017 | 1.9m | 69.2k | 804 |
| 60 | [Qwen: Qwen3.5-9B](https://openrouter.ai/qwen/qwen3.5-9b) | 1.8% | ±0.3pp | $0.003 | 11.0m | 612 | 27.7k |

## Trajectories

The reasoning trace is the model's perception: the moments it says it saw and the timestamps it attaches to them. Reading it against the video shows how the answer was reached, and on the failed runs, where the description parts from the footage.

correct

### Which window the pointer hovers over most

Happy path: The model locates the moment and reads it correctly.

Question 1187 global-graph/interaction\_partner Qwen3.8 27B

<video controls="" src="https://vgi-bench-mirror.openrouter.ai/pNH9LySHA8o.mp4"></video>

The full video the model was sent, served from the OpenRouter mirror used by the harness.

Which option does the mouse pointer hover over most often?

answered A ✓key A

The trace tracks the pointer across the whole recording rather than one frame, names the Premiere Pro cameo near the end as a distractor, and lands on the window that dominates the session.