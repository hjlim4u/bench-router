---
title: "Sketch benchmarks"
site: "OpenRouter"
source: "https://openrouter.ai/benchmarks/media/sketch"
domain: "openrouter.ai"
language: "en-US"
description: "Compare how text models draw as SVG or pixel grids across curated prompts."
word_count: 900
---

Artifact generation benchmarks

Compare artifact quality across text models

## Pelican on a bike

Why we chose this prompt: Simon Willison's [informal benchmark](https://simonwillison.net/tags/pelican-riding-a-bicycle) for text models, run verbatim since late 2024. Text models cannot draw, but they can write code and SVG is code. The task is hard on purpose. Bicycle frames are difficult to remember, pelicans are difficult to draw, and pelicans cannot ride bicycles. Each model gets the prompt with no examples or style guidance, so the picture reflects its own judgment.

Prompt

Generate an SVG of a pelican riding a bicycle

Toughest critic

![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)

Gemini 3.8 Flash−1.3 vs median

Biggest fan

![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)

GPT-5.6 Sol+0.6 vs median

- ![Anthropic: Claude Fable 5.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-fable-5.1-20260831%2Fe6c79dc0-85a7-4cd0-99a1-730901db45de%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Fable 5.1](https://openrouter.ai/anthropic/claude-fable-5.1-20260831 "Anthropic: Claude Fable 5.1")
	$2.13518.7s 8.8
- ![OpenAI: GPT-6 Astra rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6-astra-20260903%2F175469ef-00f4-4d49-933f-b675844f220b%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra-20260903 "OpenAI: GPT-6 Astra")
	$0.87390.6s 9.1
- ![SpaceXAI: Grok 4.20 Multi-Agent rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-4.20-multi-agent-20260309%2Ffb5b2666-d1d7-4ddc-877e-7c937419c59f%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok 4.20 Multi-Agent](https://openrouter.ai/x-ai/grok-4.20-multi-agent-20260309 "SpaceXAI: Grok 4.20 Multi-Agent")
	$0.79121.3s 8.2
- ![OpenAI: GPT-6 Sol Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6-sol-pro-20260922%2F3c17148e-c602-40ec-942f-41889931641d%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6 Sol Pro](https://openrouter.ai/openai/gpt-6-sol-pro-20260922 "OpenAI: GPT-6 Sol Pro")
	$0.77653.3s 8.7
- ![OpenAI: GPT-5.6 Sol rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.6-sol-20260709%2F6818db07-0132-428d-b00d-077155bda8bd%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.6 Sol](https://openrouter.ai/openai/gpt-5.6-sol-20260709 "OpenAI: GPT-5.6 Sol")
	$0.57363.8s 8.9
- ![Claude Opus 5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-opus-5-20260723%2Fcc12f8dc-5ecd-4105-93ba-43083f36700e%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Opus 5](https://openrouter.ai/anthropic/claude-opus-5-20260723 "Claude Opus 5")
	$0.50275.0s 8.6
- ![Anthropic: Claude Opus 4.6 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4.6-opus-20260205%2Fae968f6c-21f6-468d-9568-951acd231bee%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Opus 4.6](https://openrouter.ai/anthropic/claude-4.6-opus-20260205 "Anthropic: Claude Opus 4.6")
	$0.49233.5s 8.4
- ![Anthropic: Claude Opus 4.8 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4.8-opus-20260528%2F3ec8b5e0-614f-448d-909e-fe2e479fc58c%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Opus 4.8](https://openrouter.ai/anthropic/claude-4.8-opus-20260528 "Anthropic: Claude Opus 4.8")
	$0.46222.1s 8.3
- ![Perplexity: Sonar Deep Research rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fperplexity%2Fsonar-deep-research%2F1f0ed19e-14a9-49c1-8826-e0c8f4790ed9%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for perplexity](https://openrouter.ai/images/icons/Perplexity.png)
	[Sonar Deep Research](https://openrouter.ai/perplexity/sonar-deep-research "Perplexity: Sonar Deep Research")
	$0.41165.2s 6.8
- ![OpenAI: GPT-5.2 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.2-20251211%2F075494e7-21ae-421b-94b3-cc885f72b385%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.2](https://openrouter.ai/openai/gpt-5.2-20251211 "OpenAI: GPT-5.2")
	$0.40414.5s 8.4
- ![OpenAI: GPT-6.1 Sol Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6.1-sol-pro-20260929%2Ff76b6cfe-62e3-4398-b43c-2101ec3d83a4%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6.1 Sol Pro](https://openrouter.ai/openai/gpt-6.1-sol-pro-20260929 "OpenAI: GPT-6.1 Sol Pro")
	$0.40997.2s 9.5
- ![OpenAI: GPT-5.4 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.4-20260305%2F922b00fc-110b-49af-858b-47ccc63c0482%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.4](https://openrouter.ai/openai/gpt-5.4-20260305 "OpenAI: GPT-5.4")
	$0.38429.0s 7.9
- ![OpenAI: GPT-6 Sol rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6-sol-20260922%2F437a24aa-ff94-4e37-beb0-19636ba7c642%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6 Sol](https://openrouter.ai/openai/gpt-6-sol-20260922 "OpenAI: GPT-6 Sol")
	$0.35371.9s 8.6
- ![OpenAI: GPT-5.2-Codex rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.2-codex-20260114%2F26ec28f7-d4b1-45dc-8082-b41f443bced4%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.2-Codex](https://openrouter.ai/openai/gpt-5.2-codex-20260114 "OpenAI: GPT-5.2-Codex")
	$0.33345.8s 8.1
- ![Google: Gemini 3.1 Pro Preview rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.1-pro-preview-20260219%2F25e5b5b7-00b4-459b-81ac-aceb538db9a8%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.1 Pro Preview](https://openrouter.ai/google/gemini-3.1-pro-preview-20260219 "Google: Gemini 3.1 Pro Preview")
	$0.29143.1s 8.6
- ![OpenAI: GPT-5.6 Terra rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.6-terra-20260709%2Feb82b006-1bbe-40a2-aa07-52f9be6de859%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.6 Terra](https://openrouter.ai/openai/gpt-5.6-terra-20260709 "OpenAI: GPT-5.6 Terra")
	$0.29307.6s 8.8
- ![Google: Gemini 3.5 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.5-flash-20260519%2F191d8911-72a7-4051-b3ca-b041cc1cabde%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.5 Flash](https://openrouter.ai/google/gemini-3.5-flash-20260519 "Google: Gemini 3.5 Flash")
	$0.24130.5s 9.0
- ![OpenAI: GPT-5.3-Codex rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.3-codex-20260224%2F4fc5b490-63df-4f98-8206-67b127eb0f9a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.3-Codex](https://openrouter.ai/openai/gpt-5.3-codex-20260224 "OpenAI: GPT-5.3-Codex")
	$0.21155.8s 8.4
- ![Google: Gemini 4 Argon rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-4-argon-20261013%2F441f619c-14b5-4b14-a211-edfd8516f167%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 4 Argon](https://openrouter.ai/google/gemini-4-argon-20261013 "Google: Gemini 4 Argon")
	$0.21249.8s 9.4
- ![MoonshotAI: Kimi K3 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmoonshotai%2Fkimi-k3-20260715%2Fd879e3a3-9043-4fa9-a628-5428de374aa4%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for moonshotai](https://openrouter.ai/images/icons/MoonshotAI.png)
	[Kimi K3](https://openrouter.ai/moonshotai/kimi-k3-20260715 "MoonshotAI: Kimi K3")
	$0.21251.3s 8.6
- ![Qwen: Qwen3.8 2.4T A95B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3.8-2.4t-a95b-20260812%2Fb40a889b-f71c-46f5-88cb-df95c4185131%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3.8 2.4T A95B](https://openrouter.ai/qwen/qwen3.8-2.4t-a95b-20260812 "Qwen: Qwen3.8 2.4T A95B")
	$0.20132.0s 8.6
- ![Google: Gemini 3 Flash Preview rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3-flash-preview-20251217%2Fa8f79ad5-0cc1-49f7-a002-2c4a4d0b2144%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3 Flash Preview](https://openrouter.ai/google/gemini-3-flash-preview-20251217 "Google: Gemini 3 Flash Preview")
	$0.19325.4s 7.9
- ![OpenAI: GPT-6.1 Sol rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6.1-sol-20260929%2F416c3fb3-240b-4c6e-9670-4997aedbe34e%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6.1 Sol](https://openrouter.ai/openai/gpt-6.1-sol-20260929 "OpenAI: GPT-6.1 Sol")
	$0.17619.8s 9.3
- ![Mistral: Mistral Medium 3.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-medium-3.5-20260430%2Fb5b16702-41ca-4a73-8a4b-6134eb11cf5e%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Medium 3.5](https://openrouter.ai/mistralai/mistral-medium-3.5-20260430 "Mistral: Mistral Medium 3.5")
	$0.1692.7s 5.9
- ![OpenAI: GPT-5.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.5-20260423%2Fef624310-a8e3-4401-8d70-ce57ec467076%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.5](https://openrouter.ai/openai/gpt-5.5-20260423 "OpenAI: GPT-5.5")
	$0.1569.2s 8.6
- ![MoonshotAI: Kimi K3.1 Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmoonshotai%2Fkimi-k3.1-pro-20261023%2F28dde465-95ca-4a42-a55c-6b81713ffd4a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for moonshotai](https://openrouter.ai/images/icons/MoonshotAI.png)
	[Kimi K3.1 Pro](https://openrouter.ai/moonshotai/kimi-k3.1-pro-20261023 "MoonshotAI: Kimi K3.1 Pro")
	$0.15193.5s
- ![Z.ai: GLM 5.3 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5.3-20260816%2F937b5cd2-00bf-4e68-9641-ce4d1d9dc7c9%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5.3](https://openrouter.ai/z-ai/glm-5.3-20260816 "Z.ai: GLM 5.3")
	$0.15435.6s 8.5
- ![Google: Gemini 2.5 Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-2.5-pro%2Fa2c8d451-0890-4cf4-a5aa-59ca4f02574c%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 2.5 Pro](https://openrouter.ai/google/gemini-2.5-pro "Google: Gemini 2.5 Pro")
	$0.13166.7s 7.5
- ![OpenAI: GPT-5.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.1-20251113%2F0908cb8d-e463-4428-8bd7-ca569345a11e%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.1](https://openrouter.ai/openai/gpt-5.1-20251113 "OpenAI: GPT-5.1")
	$0.11100.7s 7.1
- ![Fireworks: Ember-1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Ffireworks%2Fember-1-20260923%2F2910e25b-92c4-4bf7-a1ea-4736eff51d7c%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for fireworks](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://fireworks.ai&size=256)
	[Ember-1](https://openrouter.ai/fireworks/ember-1-20260923 "Fireworks: Ember-1")
	$0.11116.4s 9.1
- ![Anthropic: Claude Opus 4.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4.1-opus-20250805%2F7878fd2c-8a80-40e8-9c44-b7e5f2de8f7b%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Opus 4.1](https://openrouter.ai/anthropic/claude-4.1-opus-20250805 "Anthropic: Claude Opus 4.1")
	$0.1170.9s 5.9
- ![OpenAI: GPT-5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5-2025-08-07%2F61e003f5-2909-47a4-a6a4-b19a0978afbe%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5](https://openrouter.ai/openai/gpt-5-2025-08-07 "OpenAI: GPT-5")
	$0.099106.0s 8.1
- ![Anthropic: Claude Opus 4 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4-opus-20250522%2F5766f664-1215-45c6-b27f-037c6a2b2105%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Opus 4](https://openrouter.ai/anthropic/claude-4-opus-20250522 "Anthropic: Claude Opus 4")
	$0.08821.0s 6.1
- ![Google: Gemini 3.7 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.7-flash-20260813%2F62021839-566c-40da-ab39-03f1cdd67383%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.7 Flash](https://openrouter.ai/google/gemini-3.7-flash-20260813 "Google: Gemini 3.7 Flash")
	$0.086122.1s 9.1
- ![Meta: Muse Spark 1.3 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmeta%2Fmuse-spark-1.3-20260902%2F570941a0-7682-429f-827f-2e9532677e6a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for meta](https://openrouter.ai/images/icons/Meta.png)
	[Muse Spark 1.3](https://openrouter.ai/meta/muse-spark-1.3-20260902 "Meta: Muse Spark 1.3")
	$0.07488.6s 8.8
- ![Z.ai: GLM 5.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5.1-20260406%2F6a9c1efc-df97-412d-8855-59a2ae7eab91%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5.1](https://openrouter.ai/z-ai/glm-5.1-20260406 "Z.ai: GLM 5.1")
	$0.066243.4s 8.6
- ![Perplexity: Sonar Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fperplexity%2Fsonar-pro%2F36ce105f-e483-4bac-b3e8-d2797c824568%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for perplexity](https://openrouter.ai/images/icons/Perplexity.png)
	[Sonar Pro](https://openrouter.ai/perplexity/sonar-pro "Perplexity: Sonar Pro")
	$0.06533.1s 7.8
- ![Qwen: Qwen3.8 27B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3.8-27b-20260814%2F5ef6dbfd-4abd-4233-beb8-7fac1920d17d%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3.8 27B](https://openrouter.ai/qwen/qwen3.8-27b-20260814 "Qwen: Qwen3.8 27B")
	$0.065487.7s 8.8
- ![Perplexity: Sonar Pro Search rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fperplexity%2Fsonar-pro-search%2Fe5f991c5-113e-4d3c-8e69-c7e4d97ddafb%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for perplexity](https://openrouter.ai/images/icons/Perplexity.png)
	[Sonar Pro Search](https://openrouter.ai/perplexity/sonar-pro-search "Perplexity: Sonar Pro Search")
	$0.06228.0s 7.5
- ![ByteDance Seed: Seed 2.1 Turbo rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fbytedance-seed%2Fseed-2-1-turbo-20260810%2Faf5f1237-97e6-49fd-a3d0-e23feaf7d3ef%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)
	[Seed 2.1 Turbo](https://openrouter.ai/bytedance-seed/seed-2-1-turbo-20260810 "ByteDance Seed: Seed 2.1 Turbo")
	$0.055265.7s 8.4
- ![Anthropic: Claude Opus 4.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4.5-opus-20251124%2F139b8a8e-3363-4d43-82f8-cd174a13eaaf%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Opus 4.5](https://openrouter.ai/anthropic/claude-4.5-opus-20251124 "Anthropic: Claude Opus 4.5")
	$0.05523.7s 7.9
- ![DeepSeek: DeepSeek V4 Pro 0813 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4-pro-20260813%2Fd14661c9-ca57-4107-8dc9-a0efba3dccdb%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4 Pro 0813](https://openrouter.ai/deepseek/deepseek-v4-pro-20260813 "DeepSeek: DeepSeek V4 Pro 0813")
	$0.055213.6s 8.3
- ![SpaceXAI: Grok 4.6 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-4.6-20260810%2F85346a95-8daf-43a4-9808-68205b517d1d%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok 4.6](https://openrouter.ai/x-ai/grok-4.6-20260810 "SpaceXAI: Grok 4.6")
	$0.054141.2s 8.5
- ![Google: Gemini 3.6 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.6-flash-20260721%2F5f71e0bd-e3c0-4242-9354-5ba73d148a27%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.6 Flash](https://openrouter.ai/google/gemini-3.6-flash-20260721 "Google: Gemini 3.6 Flash")
	$0.05395.5s 8.9
- ![Meta: Muse Spark Open rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmeta%2Fmuse-spark-open-20261015%2F5da2a3db-5da1-42eb-aae7-f3a2f5f18236%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for meta](https://openrouter.ai/images/icons/Meta.png)
	[Muse Spark Open](https://openrouter.ai/meta/muse-spark-open-20261015 "Meta: Muse Spark Open")
	$0.051106.6s 7.3
- ![SpaceXAI: Grok 4.7 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-4.7-20260916%2F00954c2e-04e5-4bb2-9ff3-575f9671a126%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok 4.7](https://openrouter.ai/x-ai/grok-4.7-20260916 "SpaceXAI: Grok 4.7")
	$0.05178.5s 7.4
- ![Google: Gemini 3.8 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.8-flash-20260902%2Fb6e18144-6417-4b01-9757-13cdeec34621%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash-20260902 "Google: Gemini 3.8 Flash")
	$0.05167.4s 8.6
- ![Z.ai: GLM 5.2 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5.2-20260616%2F789a6aec-7d60-45c2-8612-670682c9574b%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5.2](https://openrouter.ai/z-ai/glm-5.2-20260616 "Z.ai: GLM 5.2")
	$0.045244.6s 7.6
- ![OpenAI: GPT-4 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-4%2F7b5c8437-fab9-4846-bf81-184d71051be9%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-4](https://openrouter.ai/openai/gpt-4 "OpenAI: GPT-4")
	$0.0435.4s 5.5
- ![MoonshotAI: Kimi K2.7 Code rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmoonshotai%2Fkimi-k2.7-code-20260612%2Fce870eee-deb8-4074-bec2-cd78d80359e0%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for moonshotai](https://openrouter.ai/images/icons/MoonshotAI.png)
	[Kimi K2.7 Code](https://openrouter.ai/moonshotai/kimi-k2.7-code-20260612 "MoonshotAI: Kimi K2.7 Code")
	$0.043246.1s 8.0
- ![Tencent: Hy4 preview rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Ftencent%2Fhy4-preview-20260827%2F45060638-917a-45ea-895a-20068ec913f4%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for tencent](https://openrouter.ai/images/icons/Tencent.png)
	[Hy4 preview](https://openrouter.ai/tencent/hy4-preview-20260827 "Tencent: Hy4 preview")
	$0.041268.4s 8.5
- ![Google: Gemini 3.5 Flash Lite rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.5-flash-lite-20260721%2Ff94c9604-0481-4bbd-9eef-1d9ad9ae5451%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.5 Flash Lite](https://openrouter.ai/google/gemini-3.5-flash-lite-20260721 "Google: Gemini 3.5 Flash Lite")
	$0.04141.0s 8.5
- ![StepFun: Step 5 Preview rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fstepfun%2Fstep-5-preview-20261008%2Febad9651-6c18-495a-bc57-b94d0db89d30%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for stepfun](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://platform.stepfun.ai/&size=256)
	[Step 5 Preview](https://openrouter.ai/stepfun/step-5-preview-20261008 "StepFun: Step 5 Preview")
	$0.039335.4s 8.8
- ![OpenAI: GPT-6 Luna Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6-luna-pro-20260922%2F65797b16-f3b8-4172-aa70-d6e5bb4c16ad%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6 Luna Pro](https://openrouter.ai/openai/gpt-6-luna-pro-20260922 "OpenAI: GPT-6 Luna Pro")
	$0.037561.1s 9.3
- ![ByteDance Seed: Seed-2.0-Code rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fbytedance-seed%2Fseed-2.0-code-20260730%2F50113e59-660a-4fa0-a7e5-8599251bb97d%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)
	[Seed-2.0-Code](https://openrouter.ai/bytedance-seed/seed-2.0-code-20260730 "ByteDance Seed: Seed-2.0-Code")
	$0.036164.1s 6.3
- ![Anthropic: Claude Sonnet 4.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4.5-sonnet-20250929%2F8c3819f5-f2ae-4e59-adc5-6840de99fc98%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Sonnet 4.5](https://openrouter.ai/anthropic/claude-4.5-sonnet-20250929 "Anthropic: Claude Sonnet 4.5")
	$0.03424.7s 7.8
- ![Qwen: Qwen3 VL 30B A3B Thinking rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-vl-30b-a3b-thinking%2F7fdb445e-c349-41b5-9437-fb84e7d982c3%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 VL 30B A3B Thinking](https://openrouter.ai/qwen/qwen3-vl-30b-a3b-thinking "Qwen: Qwen3 VL 30B A3B Thinking")
	$0.034451.0s 3.9
- ![Z.ai: GLM 5 Turbo rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5-turbo-20260315%2F6c1e79a6-512b-4836-ab50-d231848ca95a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5 Turbo](https://openrouter.ai/z-ai/glm-5-turbo-20260315 "Z.ai: GLM 5 Turbo")
	$0.033196.9s 8.5
- ![Elorian: Glimpse rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Felorian%2Fglimpse-20261016%2F73a7f50a-4d4a-4d30-adb7-d9380458d12d%2Fthumb-0.webp&w=3840&q=75)
	[Glimpse](https://openrouter.ai/elorian/glimpse-20261016 "Elorian: Glimpse")
	$0.03341.5s 7.9
- ![Qwen: Qwen3 VL 235B A22B Thinking rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-vl-235b-a22b-thinking%2Fe9886733-c4f8-439a-9b6c-e1fd839829c8%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 VL 235B A22B Thinking](https://openrouter.ai/qwen/qwen3-vl-235b-a22b-thinking "Qwen: Qwen3 VL 235B A22B Thinking")
	$0.032149.4s 4.8
- ![OpenAI: GPT-5.6 Luna rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.6-luna-20260709%2F5a5bd0b9-3eee-4edb-a36e-edba070bbf3b%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.6 Luna](https://openrouter.ai/openai/gpt-5.6-luna-20260709 "OpenAI: GPT-5.6 Luna")
	$0.032263.2s 8.6
- ![Anthropic: Claude Sonnet 4 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4-sonnet-20250522%2F44f0fed1-4350-48cb-b66f-f75429c9eabd%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Sonnet 4](https://openrouter.ai/anthropic/claude-4-sonnet-20250522 "Anthropic: Claude Sonnet 4")
	$0.02915.6s 7.6
- ![Thinking Machines: Inkling rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fthinkingmachines%2Finkling-20260715%2F207c242d-777b-4f09-8464-c0c37eecb569%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for thinkingmachines](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://thinkingmachines.ai/&size=256)
	[Inkling](https://openrouter.ai/thinkingmachines/inkling-20260715 "Thinking Machines: Inkling")
	$0.02750.9s 7.5
- ![Z.ai: GLM 5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5-20260211%2F8d0e058c-5522-4a28-a709-2d197e1e1684%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5](https://openrouter.ai/z-ai/glm-5-20260211 "Z.ai: GLM 5")
	$0.026131.4s 8.3
- ![OpenAI: GPT-5 Mini rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5-mini-2025-08-07%2Fe45f5dec-b3ef-43dd-9ed0-d8a3d92c151c%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5 Mini](https://openrouter.ai/openai/gpt-5-mini-2025-08-07 "OpenAI: GPT-5 Mini")
	$0.02599.7s 8.3
- ![Perplexity: Sonar Reasoning Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fperplexity%2Fsonar-reasoning-pro%2F8460b351-7cdd-4f37-b6e9-8e9f0da15e59%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for perplexity](https://openrouter.ai/images/icons/Perplexity.png)
	[Sonar Reasoning Pro](https://openrouter.ai/perplexity/sonar-reasoning-pro "Perplexity: Sonar Reasoning Pro")
	$0.02530.6s 7.6
- ![MoonshotAI: Kimi K2.6 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmoonshotai%2Fkimi-k2.6-20260420%2Fc1ddc36e-f7b4-455c-aa3d-5e88f05ffcda%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for moonshotai](https://openrouter.ai/images/icons/MoonshotAI.png)
	[Kimi K2.6](https://openrouter.ai/moonshotai/kimi-k2.6-20260420 "MoonshotAI: Kimi K2.6")
	$0.023107.8s 7.4
- ![SpaceXAI: Grok Build 0.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-build-0.1-20260520%2Fe45b0553-1a58-4698-b4e8-96a8e3c672ac%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok Build 0.1](https://openrouter.ai/x-ai/grok-build-0.1-20260520 "SpaceXAI: Grok Build 0.1")
	$0.02174.6s 7.3
- ![DeepSeek: DeepSeek V4 Flash Vision Exp rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4-flash-vision-exp-20260821%2F231b1278-954f-4ad5-a382-9716aa39192e%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4 Flash Vision Exp](https://openrouter.ai/deepseek/deepseek-v4-flash-vision-exp-20260821 "DeepSeek: DeepSeek V4 Flash Vision Exp")
	$0.02151.2s 8.6
- ![OpenAI: GPT-5.1-Codex-Mini rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.1-codex-mini-20251113%2F01ae9bc4-0b01-4850-97bf-06244cde4b5a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.1-Codex-Mini](https://openrouter.ai/openai/gpt-5.1-codex-mini-20251113 "OpenAI: GPT-5.1-Codex-Mini")
	$0.019171.2s 5.6
- ![DeepSeek: DeepSeek V4.1 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4.1-flash-20260910%2Fe335f437-83bb-4b9d-845e-2cba2f4f6926%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4.1 Flash](https://openrouter.ai/deepseek/deepseek-v4.1-flash-20260910 "DeepSeek: DeepSeek V4.1 Flash")
	$0.01961.9s 8.5
- ![SpaceXAI: Grok 4.3 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-4.3-20260430%2F8825c480-ae80-486b-8b8e-5a67178e4839%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok 4.3](https://openrouter.ai/x-ai/grok-4.3-20260430 "SpaceXAI: Grok 4.3")
	$0.019102.1s 7.4
- ![Qwen: Qwen3 235B A22B Thinking 2507 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-235b-a22b-thinking-2507%2F00d89c46-5aad-429e-a876-5da27975acf0%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 235B A22B Thinking 2507](https://openrouter.ai/qwen/qwen3-235b-a22b-thinking-2507 "Qwen: Qwen3 235B A22B Thinking 2507")
	$0.018186.2s 8.1
- ![OpenAI: GPT-5.1-Codex rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.1-codex-20251113%2F914182dd-8475-4b36-a002-90ac87afc844%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.1-Codex](https://openrouter.ai/openai/gpt-5.1-codex-20251113 "OpenAI: GPT-5.1-Codex")
	$0.01814.2s 7.0
- ![Qwen: Qwen3.6 27B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3.6-27b-20260422%2F06ba6fee-7b7e-4d2b-a8ed-b1a192c79a0f%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3.6 27B](https://openrouter.ai/qwen/qwen3.6-27b-20260422 "Qwen: Qwen3.6 27B")
	$0.01770.5s 8.0
- ![OpenAI: GPT-4.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-4.1-2025-04-14%2F73377121-6797-4e43-b181-1f3011160506%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-4.1](https://openrouter.ai/openai/gpt-4.1-2025-04-14 "OpenAI: GPT-4.1")
	$0.01724.1s 6.4
- ![ByteDance Seed: Seed-2.0-Lite rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fbytedance-seed%2Fseed-2.0-lite-20260309%2Fb7313170-fcff-48d4-9e89-435eaf505c90%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)
	[Seed-2.0-Lite](https://openrouter.ai/bytedance-seed/seed-2.0-lite-20260309 "ByteDance Seed: Seed-2.0-Lite")
	$0.016110.7s 8.1
- ![SpaceXAI: Grok 4.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-4.5-20260708%2F0696707a-c84c-4c72-ab19-f61d5f086532%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok 4.5](https://openrouter.ai/x-ai/grok-4.5-20260708 "SpaceXAI: Grok 4.5")
	$0.01429.2s 8.0
- ![Mistral Large 2407 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-large-2407%2F0fcc364b-cee5-4428-aa09-8c47f814384a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Large 2407](https://openrouter.ai/mistralai/mistral-large-2407 "Mistral Large 2407")
	$0.01218.3s 6.0
- ![Anthropic: Claude Haiku 4.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4.5-haiku-20251001%2F2a770179-06b2-4f94-b5ef-dd78e5c97f1f%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Haiku 4.5](https://openrouter.ai/anthropic/claude-4.5-haiku-20251001 "Anthropic: Claude Haiku 4.5")
	$0.01212.1s 6.5
- ![MiniMax: MiniMax M2.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fminimax%2Fminimax-m2.1%2Fe04a0827-2775-4ff5-8899-e3955d8b5336%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for minimax](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://minimaxi.com/&size=256)
	[MiniMax M2.1](https://openrouter.ai/minimax/minimax-m2.1 "MiniMax: MiniMax M2.1")
	$0.012108.5s 7.4
- ![Qwen: Qwen3 Next 80B A3B Thinking rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-next-80b-a3b-thinking-2509%2F2998f3ff-8864-4c0a-90b9-b142e0855514%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 Next 80B A3B Thinking](https://openrouter.ai/qwen/qwen3-next-80b-a3b-thinking-2509 "Qwen: Qwen3 Next 80B A3B Thinking")
	$0.01152.7s 4.3
- ![MiniMax: MiniMax M2.7 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fminimax%2Fminimax-m2.7-20260318%2F99cd0767-9606-498b-b58a-97cbe6a959e5%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for minimax](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://minimaxi.com/&size=256)
	[MiniMax M2.7](https://openrouter.ai/minimax/minimax-m2.7-20260318 "MiniMax: MiniMax M2.7")
	$0.011134.8s 6.9
- ![Xiaomi: MiMo-V2.5-Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fxiaomi%2Fmimo-v2.5-pro-20260422%2Fd1d906b6-36e8-4ad5-a4c6-0de7408a430a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for xiaomi](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.mi.com&size=256)
	[MiMo-V2.5-Pro](https://openrouter.ai/xiaomi/mimo-v2.5-pro-20260422 "Xiaomi: MiMo-V2.5-Pro")
	$0.011313.9s 8.3
- ![StepFun: Step 3.7 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fstepfun%2Fstep-3.7-flash-20260528%2F985d18c2-cfb0-481b-b70d-b65ce0910f4e%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for stepfun](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://platform.stepfun.ai/&size=256)
	[Step 3.7 Flash](https://openrouter.ai/stepfun/step-3.7-flash-20260528 "StepFun: Step 3.7 Flash")
	$0.01066.9s 6.7
- ![Mistral: Mixtral 8x22B Instruct rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmixtral-8x22b-instruct%2Fe05537d6-c8e3-4595-9cb8-5b40c4a17290%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mixtral 8x22B Instruct](https://openrouter.ai/mistralai/mixtral-8x22b-instruct "Mistral: Mixtral 8x22B Instruct")
	$0.0108.2s 4.4
- ![OpenAI: GPT-5 Nano rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5-nano-2025-08-07%2F66332ab5-b9e5-41b7-9973-16d029f4f8ef%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5 Nano](https://openrouter.ai/openai/gpt-5-nano-2025-08-07 "OpenAI: GPT-5 Nano")
	$0.010143.6s 4.9
- ![Writer: Palmyra X5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fwriter%2Fpalmyra-x5-20250428%2F3ba58108-eb8a-4f97-889d-414c7ad8f124%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for writer](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://writer.com/&size=256)
	[Palmyra X5](https://openrouter.ai/writer/palmyra-x5-20250428 "Writer: Palmyra X5")
	$0.01021.2s 4.6
- ![Amazon: Nova Premier 1.0 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Famazon%2Fnova-premier-v1%2Fb32f10bd-e3ef-48aa-ad06-e070c8e7a590%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for amazon](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://nova.amazon.com/&size=256)
	[Nova Premier 1.0](https://openrouter.ai/amazon/nova-premier-v1 "Amazon: Nova Premier 1.0")
	$0.00919.8s 3.9
- ![Pareto 26.10 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Funbiased%2Fpareto-26.10-20261015%2Fbea42a82-4904-437e-a128-3e63028bdfa1%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for unbiased](https://openrouter.ai/images/icons/Unbiased.png)
	[Pareto 26.10](https://openrouter.ai/unbiased/pareto-26.10-20261015 "Pareto 26.10")
	$0.00976.0s 9.0
- ![MiniMax: MiniMax M3.1 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fminimax%2Fminimax-m3.1-flash-20261019%2Febb6f163-92f2-45b7-b765-a243f5702143%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for minimax](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://minimaxi.com/&size=256)
	[MiniMax M3.1 Flash](https://openrouter.ai/minimax/minimax-m3.1-flash-20261019 "MiniMax: MiniMax M3.1 Flash")
	$0.009145.0s
- ![OpenAI: GPT-6 Luna rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6-luna-20260922%2F2a624839-c2b7-408f-8c58-0284a8093258%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6 Luna](https://openrouter.ai/openai/gpt-6-luna-20260922 "OpenAI: GPT-6 Luna")
	$0.009410.1s 8.2
- ![Tencent: Hy3 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Ftencent%2Fhy3-20260706%2Fa2c043c7-bc67-40cc-b07d-c4814811115a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for tencent](https://openrouter.ai/images/icons/Tencent.png)
	[Hy3](https://openrouter.ai/tencent/hy3-20260706 "Tencent: Hy3")
	$0.009207.4s 8.3
- ![Thinking Machines: Inkling Small rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fthinkingmachines%2Finkling-small-20260730%2Fe44ad47f-e9df-41e7-8d72-7f9c1a629682%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for thinkingmachines](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://thinkingmachines.ai/&size=256)
	[Inkling Small](https://openrouter.ai/thinkingmachines/inkling-small-20260730 "Thinking Machines: Inkling Small")
	$0.00917.6s 7.9
- ![Xiaomi: MiMo-V2.6-Pro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fxiaomi%2Fmimo-v2.6-pro-20260921%2Fe8f22daa-9afe-4e55-bfc0-4292a1b4b040%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for xiaomi](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.mi.com&size=256)
	[MiMo-V2.6-Pro](https://openrouter.ai/xiaomi/mimo-v2.6-pro-20260921 "Xiaomi: MiMo-V2.6-Pro")
	$0.009108.2s 8.0
- ![Particle AI: Particle-1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fparticle-ai%2Fparticle-1-20261027%2F855a3b57-9d0b-4c03-b38d-ef544bb09713%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for particle-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://huggingface.co/&size=256)
	[Particle-1](https://openrouter.ai/particle-ai/particle-1-20261027 "Particle AI: Particle-1")
	$0.00811.7s 7.8
- ![Mistral: Mistral Large 4 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-large-4-0-20261006%2Fef394b96-4236-4727-b32a-2c54e33e3798%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Large 4](https://openrouter.ai/mistralai/mistral-large-4-0-20261006 "Mistral: Mistral Large 4")
	$0.00837.3s 6.6
- ![Reflection: Beam 1.0 501B A23B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Freflection%2Fbeam-1.0-501b-a23b-20261016%2F01d4323d-d58d-4e15-8436-2b5b9cdab59a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for reflection](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://railway.app/&size=256)
	[Beam 1.0 501B A23B](https://openrouter.ai/reflection/beam-1.0-501b-a23b-20261016 "Reflection: Beam 1.0 501B A23B")
	$0.00813.3s 7.3
- ![Perplexity: Sonar rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fperplexity%2Fsonar%2Fda26dba6-3c92-4578-b11d-119f956949f5%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for perplexity](https://openrouter.ai/images/icons/Perplexity.png)
	[Sonar](https://openrouter.ai/perplexity/sonar "Perplexity: Sonar")
	$0.00821.2s 7.8
- ![ByteDance Seed: Seed-2.0-Mini rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fbytedance-seed%2Fseed-2.0-mini-20260224%2Ffc128f56-6985-4404-8473-f3befb27ae51%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)
	[Seed-2.0-Mini](https://openrouter.ai/bytedance-seed/seed-2.0-mini-20260224 "ByteDance Seed: Seed-2.0-Mini")
	$0.007155.9s 6.8
- ![Z.ai: GLM 5.3 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5.3-flash-20260826%2F25fc3a36-a11c-46c3-8b4c-88e6c6000478%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5.3 Flash](https://openrouter.ai/z-ai/glm-5.3-flash-20260826 "Z.ai: GLM 5.3 Flash")
	$0.007263.3s 8.7
- ![Mistral: Mistral Small 4 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-small-2603%2Fc70cf791-3197-4ec5-8709-cb6180c4b1b6%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Small 4](https://openrouter.ai/mistralai/mistral-small-2603 "Mistral: Mistral Small 4")
	$0.00757.1s 4.6
- ![Inception: Mercury 3 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Finception%2Fmercury-3-20261019%2F290cb612-9356-49e9-964c-b69f5350f337%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for inception](https://openrouter.ai/images/icons/Inception.svg)
	[Mercury 3](https://openrouter.ai/inception/mercury-3-20261019 "Inception: Mercury 3")
	$0.00736.3s 7.8
- ![DeepSeek: DeepSeek V4 Flash 0423 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4-flash-20260423%2Fc2c10f56-5993-4639-933f-319dffdb3da8%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4 Flash 0423](https://openrouter.ai/deepseek/deepseek-v4-flash-20260423 "DeepSeek: DeepSeek V4 Flash 0423")
	$0.007449.8s 8.6
- ![NVIDIA: Nemotron 3 Ultra rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fnvidia%2Fnemotron-3-ultra-550b-a55b-20260604%2F29ad6f1b-847d-4e72-96e2-f8dcc2c45be2%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for nvidia](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://nvidia.com/&size=256)
	[Nemotron 3 Ultra](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b-20260604 "NVIDIA: Nemotron 3 Ultra")
	$0.00646.8s 5.6
- ![inclusionAI: Ling 3.1 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Finclusionai%2Fling-3.1-flash-20261002%2Ff35959f6-40c7-4f6f-ab2a-c98a20a98774%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for inclusionai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.inclusion-ai.org/&size=256)
	[Ling 3.1 Flash](https://openrouter.ai/inclusionai/ling-3.1-flash-20261002 "inclusionAI: Ling 3.1 Flash")
	$0.006215.6s 7.9
- ![Qwen: Qwen3.6 35B A3B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3.6-35b-a3b-20260415%2Fbdc88118-6a01-4836-b90e-c048bf651ab2%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3.6 35B A3B](https://openrouter.ai/qwen/qwen3.6-35b-a3b-20260415 "Qwen: Qwen3.6 35B A3B")
	$0.005217.3s 8.4
- ![Meta: Muse Glimmer 30B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmeta%2Fmuse-glimmer-30b-20260810%2F6a95ede9-d27b-4474-939f-3a2c7475fea0%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for meta](https://openrouter.ai/images/icons/Meta.png)
	[Muse Glimmer 30B](https://openrouter.ai/meta/muse-glimmer-30b-20260810 "Meta: Muse Glimmer 30B")
	$0.00557.0s 6.9
- ![Relace: Relace Search rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Frelace%2Frelace-search-20251208%2F730324c3-cd80-4f9d-9f43-43b43858ffed%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for relace](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.relace.ai&size=256)
	[Relace Search](https://openrouter.ai/relace/relace-search-20251208 "Relace: Relace Search")
	$0.0044.9s 4.9
- ![Google: Gemini 2.5 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-2.5-flash%2Fa4c336c5-bbb4-48d2-98d6-9ecc253ff68d%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 2.5 Flash](https://openrouter.ai/google/gemini-2.5-flash "Google: Gemini 2.5 Flash")
	$0.0048.1s 6.1
- ![NVIDIA: Nemotron 3.5 Super VL rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fnvidia%2Fnemotron-3.5-super-vl-20261015%2F1a6945a7-48ba-467f-a76c-adf1396a043f%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for nvidia](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://nvidia.com/&size=256)
	[Nemotron 3.5 Super VL](https://openrouter.ai/nvidia/nemotron-3.5-super-vl-20261015 "NVIDIA: Nemotron 3.5 Super VL")
	$0.00425.7s 6.0
- ![DeepSeek: R1 0528 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-r1-0528%2F2da2c083-08a6-40a9-9e04-e89a372c14a1%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[R1 0528](https://openrouter.ai/deepseek/deepseek-r1-0528 "DeepSeek: R1 0528")
	$0.00493.8s 6.1
- ![SpaceXAI: Grok 4.20 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-4.20-20260309%2F92535da4-3ca8-4320-927d-ea0f22de496f%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok 4.20](https://openrouter.ai/x-ai/grok-4.20-20260309 "SpaceXAI: Grok 4.20")
	$0.00410.7s 6.8
- ![LiquidAI: LFM2.5-24B-A2B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fliquid%2Flfm-2.5-24b-a2b-20261012%2Fe9bd2148-1251-48f0-aaad-16a6c640e5e5%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for liquid](https://openrouter.ai/images/icons/Liquid.png)
	[LFM2.5-24B-A2B](https://openrouter.ai/liquid/lfm-2.5-24b-a2b-20261012 "LiquidAI: LFM2.5-24B-A2B")
	$0.00423.0s 3.0
- ![Z.ai: GLM 4.6 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-4.6%2F5bc8c8df-20b7-4c47-b977-1f1ea84e7890%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 4.6](https://openrouter.ai/z-ai/glm-4.6 "Z.ai: GLM 4.6")
	$0.00321.1s 6.1
- ![Mistral: Mistral Large 3 2512 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-large-2512%2F242746b5-3f0b-4976-bc0e-25ad8ec8c24b%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Large 3 2512](https://openrouter.ai/mistralai/mistral-large-2512 "Mistral: Mistral Large 3 2512")
	$0.00321.6s 5.6
- ![Qwen: Qwen3 32B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-32b-04-28%2F7d88106f-8848-41e1-abe6-9f5ef84a6840%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 32B](https://openrouter.ai/qwen/qwen3-32b-04-28 "Qwen: Qwen3 32B")
	$0.003352.5s 5.6
- ![Perceptron: Perceptron Mk1.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fperceptron%2Fperceptron-mk1.5-20260925%2Ff02e5b0a-109e-422a-83c3-371a72af35a9%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for perceptron](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.perceptron.inc&size=256)
	[Perceptron Mk1.5](https://openrouter.ai/perceptron/perceptron-mk1.5-20260925 "Perceptron: Perceptron Mk1.5")
	$0.0036.4s 5.5
- ![Z.ai: GLM 4.5 Air rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-4.5-air%2F1e4d5266-c1b2-4554-8c6c-dd1137f3358c%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 4.5 Air](https://openrouter.ai/z-ai/glm-4.5-air "Z.ai: GLM 4.5 Air")
	$0.00333.6s 5.1
- ![Mistral: Devstral 2 2512 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fdevstral-2512%2F31843652-9e17-4095-9cb0-cffd5b53cf05%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Devstral 2 2512](https://openrouter.ai/mistralai/devstral-2512 "Mistral: Devstral 2 2512")
	$0.0026.2s 3.5
- ![Mistral: Mistral Medium 3 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-medium-3%2Fcab576d8-fc36-4a72-bf24-501066888293%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Medium 3](https://openrouter.ai/mistralai/mistral-medium-3 "Mistral: Mistral Medium 3")
	$0.0025.9s 3.4
- ![Mistral: Mistral Medium 3.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-medium-3.1%2F96c2d69c-9457-43f0-bc20-ebf3e4f4a21a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Medium 3.1](https://openrouter.ai/mistralai/mistral-medium-3.1 "Mistral: Mistral Medium 3.1")
	$0.0025.7s 3.8
- ![Xiaomi: MiMo-V2.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fxiaomi%2Fmimo-v2.5-20260422%2F8fa016e9-5066-4a3e-b7cb-b9415d06e0ce%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for xiaomi](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.mi.com&size=256)
	[MiMo-V2.5](https://openrouter.ai/xiaomi/mimo-v2.5-20260422 "Xiaomi: MiMo-V2.5")
	$0.002100.1s 4.0
- ![DeepSeek: R1 Distill Llama 70B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-r1-distill-llama-70b%2Fe2f408a2-4b32-4683-8b96-a3f0856fe7b7%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[R1 Distill Llama 70B](https://openrouter.ai/deepseek/deepseek-r1-distill-llama-70b "DeepSeek: R1 Distill Llama 70B")
	$0.002106.8s 7.3
- ![Anthropic: Claude 3 Haiku rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-3-haiku%2F1add6f28-b7bc-4b8c-9afc-346a2f73816a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude 3 Haiku](https://openrouter.ai/anthropic/claude-3-haiku "Anthropic: Claude 3 Haiku")
	$0.00213.3s 2.4
- ![ByteDance Seed: Seed 1.6 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fbytedance-seed%2Fseed-1.6-flash-20250625%2F7569909f-d720-4dd5-8231-118481e78dd3%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for bytedance-seed](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://seed.bytedance.com/&size=256)
	[Seed 1.6 Flash](https://openrouter.ai/bytedance-seed/seed-1.6-flash-20250625 "ByteDance Seed: Seed 1.6 Flash")
	$0.00238.8s 5.3
- ![DeepSeek: DeepSeek V3.1 Terminus rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v3.1-terminus%2F7072325b-6d4a-46fb-b1ad-c304012731b0%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V3.1 Terminus](https://openrouter.ai/deepseek/deepseek-v3.1-terminus "DeepSeek: DeepSeek V3.1 Terminus")
	$0.00276.5s 6.3
- ![Qwen: Qwen3 Coder Next rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-coder-next-2025-02-03%2F3c3c9507-5760-456e-a7a3-30bd4747dc62%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 Coder Next](https://openrouter.ai/qwen/qwen3-coder-next-2025-02-03 "Qwen: Qwen3 Coder Next")
	$0.00223.2s 5.6
- ![Z.ai: GLM 4.7 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-4.7-flash-20260119%2Fd59b5baf-b8b0-405a-9dec-d545bddd40a5%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 4.7 Flash](https://openrouter.ai/z-ai/glm-4.7-flash-20260119 "Z.ai: GLM 4.7 Flash")
	$0.002171.5s 8.5
- ![Upstage: Solar Mini 4 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fupstage%2Fsolar-mini4-20260922%2F7b1da8c5-f083-47c4-bf6c-0f79d0a8784a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for upstage](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.upstage.ai/&size=256)
	[Solar Mini 4](https://openrouter.ai/upstage/solar-mini4-20260922 "Upstage: Solar Mini 4")
	$0.00272.3s 4.6
- ![inclusionAI: Ling 3.0 Flash rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Finclusionai%2Fling-3.0-flash-20260723%2F24136548-d398-4a6c-97b5-c389bc97f157%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for inclusionai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.inclusion-ai.org/&size=256)
	[Ling 3.0 Flash](https://openrouter.ai/inclusionai/ling-3.0-flash-20260723 "inclusionAI: Ling 3.0 Flash")
	$0.00282.3s 7.5
- ![Qwen: Qwen3 Coder 480B A35B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-coder-480b-a35b-07-25%2F09e30ed6-08d4-4c26-ac8d-89292e021648%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 Coder 480B A35B](https://openrouter.ai/qwen/qwen3-coder-480b-a35b-07-25 "Qwen: Qwen3 Coder 480B A35B")
	$0.00210.7s 6.4
- ![Qwen: Qwen3 Next 80B A3B Instruct rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-next-80b-a3b-instruct-2509%2Ffb1e549d-1e0c-453f-8d84-f4fc069a99e1%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 Next 80B A3B Instruct](https://openrouter.ai/qwen/qwen3-next-80b-a3b-instruct-2509 "Qwen: Qwen3 Next 80B A3B Instruct")
	$0.0013.5s 5.6
- ![Nous: Hermes 3 405B Instruct rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fnousresearch%2Fhermes-3-llama-3.1-405b%2F1c07123b-65af-4916-8a9a-1b98ecf048d5%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for nousresearch](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://nousresearch.com/&size=256)
	[Hermes 3 405B Instruct](https://openrouter.ai/nousresearch/hermes-3-llama-3.1-405b "Nous: Hermes 3 405B Instruct")
	$0.00145.7s 2.6
- ![Upstage: Solar Pro 4 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fupstage%2Fsolar-pro4-20260810%2Fe2080305-7bf1-45ee-b136-a4c7df604710%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for upstage](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.upstage.ai/&size=256)
	[Solar Pro 4](https://openrouter.ai/upstage/solar-pro4-20260810 "Upstage: Solar Pro 4")
	$0.001118.1s 6.9
- ![TheDrummer: Cydonia 24B V4.1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fthedrummer%2Fcydonia-24b-v4.1%2F674f67e1-5a85-44ae-9ffd-3d49dc025028%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for thedrummer](https://openrouter.ai/images/icons/TheDrummer.png)
	[Cydonia 24B V4.1](https://openrouter.ai/thedrummer/cydonia-24b-v4.1 "TheDrummer: Cydonia 24B V4.1")
	$0.00150.8s 4.4
- ![Perceptron: Perceptron Mk1 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fperceptron%2Fperceptron-mk1-20260512%2F8df80ecb-5da9-456a-b759-33e747711c9b%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for perceptron](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.perceptron.inc&size=256)
	[Perceptron Mk1](https://openrouter.ai/perceptron/perceptron-mk1-20260512 "Perceptron: Perceptron Mk1")
	$0.00120.0s 5.6
- ![IBM: Granite 4.2 8B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fibm-granite%2Fgranite-4.2-8b-20260831%2F598a8beb-03ec-4a9d-b770-461211046d81%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for ibm-granite](https://openrouter.ai/images/icons/IBMGranite.svg)
	[Granite 4.2 8B](https://openrouter.ai/ibm-granite/granite-4.2-8b-20260831 "IBM: Granite 4.2 8B")
	$0.00175.4s 3.7
- ![DeepSeek: DeepSeek V3.2 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v3.2-20251201%2F02c339c6-02fa-4f90-9a61-6a7a278714bc%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V3.2](https://openrouter.ai/deepseek/deepseek-v3.2-20251201 "DeepSeek: DeepSeek V3.2")
	$0.00124.7s 6.6
- ![Mistral: Saba rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-saba-2502%2F20b1a319-1c6f-463f-92a5-b69d2ec132be%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Saba](https://openrouter.ai/mistralai/mistral-saba-2502 "Mistral: Saba")
	$0.0019.3s 4.3
- ![Baidu: ERNIE 4.5 VL 424B A47B  rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fbaidu%2Fernie-4.5-vl-424b-a47b%2F71cad88c-54cd-4ca1-9de4-609813653163%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for baidu](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.baidu.com/&size=256)
	[ERNIE 4.5 VL 424B A47B](https://openrouter.ai/baidu/ernie-4.5-vl-424b-a47b "Baidu: ERNIE 4.5 VL 424B A47B ")
	$0.00120.9s 5.5
- ![DeepSeek: DeepSeek V3 0324 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-chat-v3-0324%2Fa3f523ee-ee65-47f5-bc89-d58c12882161%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V3 0324](https://openrouter.ai/deepseek/deepseek-chat-v3-0324 "DeepSeek: DeepSeek V3 0324")
	$0.00125.8s 5.1
- ![Amazon: Nova Lite 1.0 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Famazon%2Fnova-lite-v1%2F615adb7f-9c2d-48e3-b715-65f08211e1ee%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for amazon](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://nova.amazon.com/&size=256)
	[Nova Lite 1.0](https://openrouter.ai/amazon/nova-lite-v1 "Amazon: Nova Lite 1.0")
	$0.00117.3s 2.8
- ![Qwen: Qwen3 235B A22B Instruct 2507 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-235b-a22b-07-25%2F930f0a08-c832-445d-9b6f-fc6351fa8cf4%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 235B A22B Instruct 2507](https://openrouter.ai/qwen/qwen3-235b-a22b-07-25 "Qwen: Qwen3 235B A22B Instruct 2507")
	$0.00121.4s 5.1
- ![Qwen: Qwen3 VL 30B A3B Instruct rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-vl-30b-a3b-instruct%2F9fd6f342-fdb3-42f2-be54-2d0ef98c0675%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 VL 30B A3B Instruct](https://openrouter.ai/qwen/qwen3-vl-30b-a3b-instruct "Qwen: Qwen3 VL 30B A3B Instruct")
	$0.0008751.4s 5.4
- ![Mistral: Mistral Small 3.1 24B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-small-3.1-24b-instruct-2503%2F682800f0-fea9-4315-bc4d-ce5d65aeb7d6%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Small 3.1 24B](https://openrouter.ai/mistralai/mistral-small-3.1-24b-instruct-2503 "Mistral: Mistral Small 3.1 24B")
	$0.0006820.4s 3.6
- ![Meta: Llama 4 Maverick rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmeta-llama%2Fllama-4-maverick-17b-128e-instruct%2F85b641a0-f219-45c0-92dc-6713190b89d9%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for meta-llama](https://openrouter.ai/images/icons/Meta.png)
	[Llama 4 Maverick](https://openrouter.ai/meta-llama/llama-4-maverick-17b-128e-instruct "Meta: Llama 4 Maverick")
	$0.0006813.5s 5.8
- ![OpenAI: gpt-oss-120b rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-oss-120b%2F0ddd97d5-1570-40d8-9499-c3ae4bf6a24a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[gpt-oss-120b](https://openrouter.ai/openai/gpt-oss-120b "OpenAI: gpt-oss-120b")
	$0.0006540.4s 4.6
- ![Qwen: Qwen3 VL 235B A22B Instruct rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-vl-235b-a22b-instruct%2F96820bc9-f7d6-4286-9f7e-57517e866123%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 VL 235B A22B Instruct](https://openrouter.ai/qwen/qwen3-vl-235b-a22b-instruct "Qwen: Qwen3 VL 235B A22B Instruct")
	$0.0006343.1s 4.1
- ![TheDrummer: Skyfall 36B V2 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fthedrummer%2Fskyfall-36b-v2%2F41c7b626-515a-45fb-a581-4d311fba47a9%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for thedrummer](https://openrouter.ai/images/icons/TheDrummer.png)
	[Skyfall 36B V2](https://openrouter.ai/thedrummer/skyfall-36b-v2 "TheDrummer: Skyfall 36B V2")
	$0.00068.6s 3.6
- ![Inception: Mercury 2.5 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Finception%2Fmercury-2.5-20260908%2F6f38095f-a465-4468-9498-7d7abbccc16b%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for inception](https://openrouter.ai/images/icons/Inception.svg)
	[Mercury 2.5](https://openrouter.ai/inception/mercury-2.5-20260908 "Inception: Mercury 2.5")
	$0.000596.4s 7.1
- ![Qwen: Qwen3 14B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-14b-04-28%2F3b3327a1-ea48-4b68-894b-b3ee22c323b1%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 14B](https://openrouter.ai/qwen/qwen3-14b-04-28 "Qwen: Qwen3 14B")
	$0.0005330.3s 4.5
- ![Google: Gemma 3 27B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemma-3-27b-it%2Ff0df631e-7521-43a4-b1b8-fe5d7017cc98%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemma 3 27B](https://openrouter.ai/google/gemma-3-27b-it "Google: Gemma 3 27B")
	$0.000532.4s 4.3
- ![Qwen: Qwen3 Coder 30B A3B Instruct rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-coder-30b-a3b-instruct%2F8b2f707b-82e5-406e-b0f8-68c0fd494f4b%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 Coder 30B A3B Instruct](https://openrouter.ai/qwen/qwen3-coder-30b-a3b-instruct "Qwen: Qwen3 Coder 30B A3B Instruct")
	$0.0004313.8s 5.0
- ![Google: Gemma 4 26B A4B  rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemma-4-26b-a4b-it-20260403%2F573275ad-3551-4ec8-be0e-9358e5e83eaa%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemma 4 26B A4B](https://openrouter.ai/google/gemma-4-26b-a4b-it-20260403 "Google: Gemma 4 26B A4B ")
	$0.0004317.3s 7.8
- ![Google: Gemma 4 31B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemma-4-31b-it-20260402%2Fc857103e-6687-4aec-a1fa-29b1b112006c%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemma 4 31B](https://openrouter.ai/google/gemma-4-31b-it-20260402 "Google: Gemma 4 31B")
	$0.0003863.3s 7.6
- ![Qwen: Qwen3 30B A3B Instruct 2507 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3-30b-a3b-instruct-2507%2F71ebcf82-8ca8-481d-b617-76d2e57fd9c5%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3 30B A3B Instruct 2507](https://openrouter.ai/qwen/qwen3-30b-a3b-instruct-2507 "Qwen: Qwen3 30B A3B Instruct 2507")
	$0.0003628.4s 5.0
- ![Mistral: Mistral Small 3.2 24B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fmistral-small-3.2-24b-instruct-2506%2F977db5b0-310e-475d-aacf-d5f518526842%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Mistral Small 3.2 24B](https://openrouter.ai/mistralai/mistral-small-3.2-24b-instruct-2506 "Mistral: Mistral Small 3.2 24B")
	$0.0003518.9s 5.0
- ![Mistral: Ministral 3 14B 2512 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fministral-14b-2512%2Fef11076a-0895-4cbf-9ba3-374becd63465%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Ministral 3 14B 2512](https://openrouter.ai/mistralai/ministral-14b-2512 "Mistral: Ministral 3 14B 2512")
	$0.0003519.5s 4.0
- ![Amazon: Nova Micro 1.0 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Famazon%2Fnova-micro-v1%2F078708d9-5100-4d92-aeb3-5085e98a4f43%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for amazon](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://nova.amazon.com/&size=256)
	[Nova Micro 1.0](https://openrouter.ai/amazon/nova-micro-v1 "Amazon: Nova Micro 1.0")
	$0.000356.3s 3.0
- ![OpenAI: GPT-4o-mini rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-4o-mini%2F694ad7f4-f6cd-430d-a7dc-0d73d73d6749%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-4o-mini](https://openrouter.ai/openai/gpt-4o-mini "OpenAI: GPT-4o-mini")
	$0.000357.9s 2.6
- ![Tencent: Hy-MT2-7B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Ftencent%2Fhy-mt2-7b-20260521%2Fbbd6064c-92aa-452e-84b9-c51d10319f5a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for tencent](https://openrouter.ai/images/icons/Tencent.png)
	[Hy-MT2-7B](https://openrouter.ai/tencent/hy-mt2-7b-20260521 "Tencent: Hy-MT2-7B")
	$0.00038.4s 4.2
- ![Tencent: Hy-MT2-30B-A3B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Ftencent%2Fhy-mt2-30b-a3b-20260521%2F1d46644e-74c6-40ce-abb1-bb9179f69eb7%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for tencent](https://openrouter.ai/images/icons/Tencent.png)
	[Hy-MT2-30B-A3B](https://openrouter.ai/tencent/hy-mt2-30b-a3b-20260521 "Tencent: Hy-MT2-30B-A3B")
	$0.000286.3s 4.8
- ![Qwen2.5 72B Instruct rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen-2.5-72b-instruct%2F01971522-c7af-43a0-b9dd-b985af46daad%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen2.5 72B Instruct](https://openrouter.ai/qwen/qwen-2.5-72b-instruct "Qwen2.5 72B Instruct")
	$0.0002721.0s 3.3
- ![OpenAI: GPT-4.1 Nano rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-4.1-nano-2025-04-14%2Fd648579c-ee20-4390-9fdf-2ca6e8aa9132%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-4.1 Nano](https://openrouter.ai/openai/gpt-4.1-nano-2025-04-14 "OpenAI: GPT-4.1 Nano")
	$0.000276.7s 5.9
- ![Mistral: Ministral 3 8B 2512 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fministral-8b-2512%2Fdc160050-0b44-40bc-9919-94c0fb901539%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Ministral 3 8B 2512](https://openrouter.ai/mistralai/ministral-8b-2512 "Mistral: Ministral 3 8B 2512")
	$0.0002520.1s 4.8
- ![Tencent: Hy-MT2-1.8B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Ftencent%2Fhy-mt2-1.8b-20260521%2F44fdaf90-094a-4fe3-abdd-ddc9aee7b99a%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for tencent](https://openrouter.ai/images/icons/Tencent.png)
	[Hy-MT2-1.8B](https://openrouter.ai/tencent/hy-mt2-1.8b-20260521 "Tencent: Hy-MT2-1.8B")
	$0.000235.6s 0.0
- ![Mistral: Ministral 3 3B 2512 rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmistralai%2Fministral-3b-2512%2F6ac038ba-7a39-4772-9b7f-f54ea3fc1277%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for mistralai](https://openrouter.ai/images/icons/Mistral.png)
	[Ministral 3 3B 2512](https://openrouter.ai/mistralai/ministral-3b-2512 "Mistral: Ministral 3 3B 2512")
	$0.000187.5s 3.3
- ![Google: Gemma 3 12B rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemma-3-12b-it%2Fdc19f9cc-6703-48ae-8d67-25a0097b33f7%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemma 3 12B](https://openrouter.ai/google/gemma-3-12b-it "Google: Gemma 3 12B")
	$0.0001521.7s 3.5
- ![Meta: Llama 4 Scout rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmeta-llama%2Fllama-4-scout-17b-16e-instruct%2F91739457-7b6b-4b9e-bbb7-3fb0dcbae966%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for meta-llama](https://openrouter.ai/images/icons/Meta.png)
	[Llama 4 Scout](https://openrouter.ai/meta-llama/llama-4-scout-17b-16e-instruct "Meta: Llama 4 Scout")
	$0.0001516.8s 3.8
- ![IBM: Granite 4.0 Micro rendering of the pelican on a bike prompt](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fibm-granite%2Fgranite-4.0-h-micro%2F1f280186-909f-4894-9342-88608d0c1575%2Fthumb-0.webp&w=3840&q=75)
	![Favicon for ibm-granite](https://openrouter.ai/images/icons/IBMGranite.svg)
	[Granite 4.0 Micro](https://openrouter.ai/ibm-granite/granite-4.0-h-micro "IBM: Granite 4.0 Micro")
	$0.00006916.4s 1.0