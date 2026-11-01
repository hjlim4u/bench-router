---
title: "Game benchmarks"
site: "OpenRouter"
source: "https://openrouter.ai/benchmarks/media/games"
domain: "openrouter.ai"
language: "en-US"
description: "Compare playable Three.js games written by text models from the same brief."
word_count: 539
---

Artifact generation benchmarks

Compare artifact quality across text models

## Fruit ninja

Why we chose this prompt: A fast swipe crosses several fruit between two frames, so checking the cursor position each frame is not enough. The slice has to be a swept segment, and the fruit has to split along it, which is the collision problem most quick implementations get wrong.

Prompt

Build a Fruit Ninja style slicing game. Fruit of at least four shapes and colors, are tossed up from below in arcs and fall back out of view. Hold the left mouse button and drag to slice; the slice is the cursor's path between frames, so a fast swipe must cut every fruit it crosses. Sliced fruit splits into two halves that fly apart with spin plus a burst of juice particles. Bombs are tossed among the fruit, and slicing one ends the game, as does letting three fruit fall unsliced. One point per fruit, with a combo bonus for three or more in one swipe. Draw a blade trail while dragging. Show score, misses and a game over screen.

Sort by

- ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4 Flash 0423](https://openrouter.ai/deepseek/deepseek-v4-flash-20260423 "DeepSeek: DeepSeek V4 Flash 0423")
	Baidu
	![Still from the DeepSeek: DeepSeek V4 Flash 0423 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4-flash-20260423%2F5d91a81b-342e-4858-965d-9151897cd5dd%2Fstill-0-1372049416.jpg&w=3840&q=75) Play
	Cost$0.002
	Generation time218.5s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[gpt-oss-120b](https://openrouter.ai/openai/gpt-oss-120b "OpenAI: gpt-oss-120b")
	Near AI
	![Still from the OpenAI: gpt-oss-120b game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-oss-120b%2F5aefb1f6-8500-46c9-b20f-83effc5008ed%2Fstill-0-557178364.jpg&w=3840&q=75) Play
	Cost$0.003
	Generation time388.3s
- ![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.1 Flash Lite](https://openrouter.ai/google/gemini-3.1-flash-lite-20260507 "Google: Gemini 3.1 Flash Lite")
	Google AI Studio
	Play
	Cost$0.008
	Generation time14.9s
- ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4 Flash 0731](https://openrouter.ai/deepseek/deepseek-v4-flash-20260731 "DeepSeek: DeepSeek V4 Flash 0731")
	Sail Research
	![Still from the DeepSeek: DeepSeek V4 Flash 0731 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4-flash-20260731%2F02dbf1fb-7676-4166-831a-6634f54d2201%2Fstill-0-541165267.jpg&w=3840&q=75) Play
	Cost$0.009
	Generation time733.8s
- ![Favicon for tencent](https://openrouter.ai/images/icons/Tencent.png)
	[Hy3](https://openrouter.ai/tencent/hy3-20260706 "Tencent: Hy3")
	Tencent
	Play
	Cost$0.011
	Generation time288.1s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5 Nano](https://openrouter.ai/openai/gpt-5-nano-2025-08-07 "OpenAI: GPT-5 Nano")
	OpenAI
	![Still from the OpenAI: GPT-5 Nano game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5-nano-2025-08-07%2F6101ab5e-b40c-4ba8-a23c-a7ffab039f66%2Fstill-0-4233841297.jpg&w=3840&q=75) Play
	Cost$0.011
	Generation time168.2s
- ![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.1 Flash Lite Preview](https://openrouter.ai/google/gemini-3.1-flash-lite-preview-20260303 "Google: Gemini 3.1 Flash Lite Preview")
	Google AI Studio
	![Still from the Google: Gemini 3.1 Flash Lite Preview game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.1-flash-lite-preview-20260303%2F8eb1a9c9-b8ea-444c-b4b0-41f925281163%2Fstill-0-2356812759.jpg&w=3840&q=75) Play
	Cost$0.011
	Generation time21.3s
- ![Favicon for inception](https://openrouter.ai/images/icons/Inception.svg)
	[Mercury 3](https://openrouter.ai/inception/mercury-3-20261019 "Inception: Mercury 3")
	Inception
	![Still from the Inception: Mercury 3 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Finception%2Fmercury-3-20261019%2F3a54c590-5587-4d6b-9de3-daef8dfb8ef6%2Fstill-0-1083438728.jpg&w=3840&q=75) Play
	Cost$0.015
	Generation time91.7s
- ![Favicon for reflection](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://railway.app/&size=256)
	[Beam 1.0 501B A23B](https://openrouter.ai/reflection/beam-1.0-501b-a23b-20261016 "Reflection: Beam 1.0 501B A23B")
	Nebius
	![Still from the Reflection: Beam 1.0 501B A23B game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Freflection%2Fbeam-1.0-501b-a23b-20261016%2Fe8ab7564-cf51-4d96-b64c-bbcdaa2ed906%2Fstill-0-2213054509.jpg&w=3840&q=75) Play
	Cost$0.016
	Generation time46.4s
- ![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5.3 Flash](https://openrouter.ai/z-ai/glm-5.3-flash-20260826 "Z.ai: GLM 5.3 Flash")
	Relace
	![Still from the Z.ai: GLM 5.3 Flash game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5.3-flash-20260826%2Fbea2126c-ffc2-4464-8d82-3cda524b26c7%2Fstill-0-2120875337.jpg&w=3840&q=75) Play
	Cost$0.018
	Generation time675.1s
- ![Favicon for nvidia](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://nvidia.com/&size=256)
	[Nemotron 3 Ultra](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b-20260604 "NVIDIA: Nemotron 3 Ultra")
	BaseTen
	![Still from the NVIDIA: Nemotron 3 Ultra game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fnvidia%2Fnemotron-3-ultra-550b-a55b-20260604%2F6c3897a2-a11d-448c-890d-381a57a50949%2Fstill-0-3010921890.jpg&w=3840&q=75) Play
	Cost$0.021
	Generation time25.9s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6 Luna](https://openrouter.ai/openai/gpt-6-luna-20260922 "OpenAI: GPT-6 Luna")
	OpenAI
	Play
	Cost$0.031
	Generation time588.5s
- ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4 Flash Vision Exp](https://openrouter.ai/deepseek/deepseek-v4-flash-vision-exp-20260821 "DeepSeek: DeepSeek V4 Flash Vision Exp")
	DeepInfra
	![Still from the DeepSeek: DeepSeek V4 Flash Vision Exp game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4-flash-vision-exp-20260821%2F861a89df-f632-42d8-b813-c629df7d77d1%2Fstill-0-2088233190.jpg&w=3840&q=75) Play
	Cost$0.033
	Generation time278.3s
- ![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.5 Flash Lite](https://openrouter.ai/google/gemini-3.5-flash-lite-20260721 "Google: Gemini 3.5 Flash Lite")
	Google
	![Still from the Google: Gemini 3.5 Flash Lite game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.5-flash-lite-20260721%2F42d9b6f0-511f-4721-8af7-def7509808bd%2Fstill-0-2651967221.jpg&w=3840&q=75) Play
	Cost$0.038
	Generation time39.8s
- ![Favicon for thinkingmachines](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://thinkingmachines.ai/&size=256)
	[Inkling Small](https://openrouter.ai/thinkingmachines/inkling-small-20260730 "Thinking Machines: Inkling Small")
	DeepInfra
	![Still from the Thinking Machines: Inkling Small game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fthinkingmachines%2Finkling-small-20260730%2Fdff32e64-b383-4673-b7c4-14680e3e3ac3%2Fstill-0-337663187.jpg&w=3840&q=75) Play
	Cost$0.040
	Generation time322.7s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5 Mini](https://openrouter.ai/openai/gpt-5-mini-2025-08-07 "OpenAI: GPT-5 Mini")
	OpenAI
	![Still from the OpenAI: GPT-5 Mini game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5-mini-2025-08-07%2Fc1d9dfd0-26e8-4a42-8453-1c0f9d91b4a4%2Fstill-0-2490351535.jpg&w=3840&q=75) Play
	Cost$0.043
	Generation time237.0s
- ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4.1 Flash](https://openrouter.ai/deepseek/deepseek-v4.1-flash-20260910 "DeepSeek: DeepSeek V4.1 Flash")
	Novita
	![Still from the DeepSeek: DeepSeek V4.1 Flash game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4.1-flash-20260910%2F817cc3a8-fc7d-4881-865c-5cd464533d14%2Fstill-0-1409979996.jpg&w=3840&q=75) Play
	Cost$0.055
	Generation time187.3s
- ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4.1 Flash 1017](https://openrouter.ai/deepseek/deepseek-v4.1-flash-20261017 "DeepSeek: DeepSeek V4.1 Flash 1017")
	Relace
	![Still from the DeepSeek: DeepSeek V4.1 Flash 1017 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4.1-flash-20261017%2F8ed121b4-90f5-49bb-bd0d-d65ee00ad27d%2Fstill-0-2140855235.jpg&w=3840&q=75) Play
	Cost$0.063
	Generation time359.4s
- ![Favicon for deepseek](https://openrouter.ai/images/icons/DeepSeek.png)
	[DeepSeek V4 Pro 0423](https://openrouter.ai/deepseek/deepseek-v4-pro-20260423 "DeepSeek: DeepSeek V4 Pro 0423")
	StreamLake
	![Still from the DeepSeek: DeepSeek V4 Pro 0423 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fdeepseek%2Fdeepseek-v4-pro-20260423%2Fe0b71f33-992d-4d96-aa51-40afd5930388%2Fstill-0-971708355.jpg&w=3840&q=75) Play
	Cost$0.068
	Generation time595.3s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6 Luna Pro](https://openrouter.ai/openai/gpt-6-luna-pro-20260922 "OpenAI: GPT-6 Luna Pro")
	OpenAI
	Play
	Cost$0.071
	Generation time1086.2s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.6 Luna](https://openrouter.ai/openai/gpt-5.6-luna-20260709 "OpenAI: GPT-5.6 Luna")
	OpenAI
	![Still from the OpenAI: GPT-5.6 Luna game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.6-luna-20260709%2F0b0147d1-d036-4a3b-8ac9-ed339c8743df%2Fstill-0-2011397264.jpg&w=3840&q=75) Play
	Cost$0.073
	Generation time434.1s
- ![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.6 Flash](https://openrouter.ai/google/gemini-3.6-flash-20260721 "Google: Gemini 3.6 Flash")
	Google AI Studio
	![Still from the Google: Gemini 3.6 Flash game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.6-flash-20260721%2Fc98a6166-5dfe-430e-b856-b1dc24407b99%2Fstill-0-211310009.jpg&w=3840&q=75) Play
	Cost$0.080
	Generation time105.7s
- ![Favicon for thinkingmachines](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://thinkingmachines.ai/&size=256)
	[Inkling](https://openrouter.ai/thinkingmachines/inkling-20260715 "Thinking Machines: Inkling")
	BaseTen
	![Still from the Thinking Machines: Inkling game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fthinkingmachines%2Finkling-20260715%2F81df4a4b-c4f9-46f2-8653-d34acca5c924%2Fstill-0-2025287633.jpg&w=3840&q=75) Play
	Cost$0.084
	Generation time87.3s
- ![Favicon for tencent](https://openrouter.ai/images/icons/Tencent.png)
	[Hy4 preview](https://openrouter.ai/tencent/hy4-preview-20260827 "Tencent: Hy4 preview")
	Tencent
	![Still from the Tencent: Hy4 preview game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Ftencent%2Fhy4-preview-20260827%2F8e00064a-b8ef-4d0e-bf22-7bb400b6c764%2Fstill-0-3725387753.jpg&w=3840&q=75) Play
	Cost$0.084
	Generation time497.7s
- ![Favicon for stepfun](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://platform.stepfun.ai/&size=256)
	[Step 5 Preview](https://openrouter.ai/stepfun/step-5-preview-20261008 "StepFun: Step 5 Preview")
	InferenceNet
	Play
	Cost$0.092
	Generation time333.1s
- ![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash-20260902 "Google: Gemini 3.8 Flash")
	Google AI Studio
	![Still from the Google: Gemini 3.8 Flash game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.8-flash-20260902%2F6293bb00-e949-413b-b634-2a6978245fa3%2Fstill-0-3388377309.jpg&w=3840&q=75) Play
	Cost$0.11
	Generation time91.0s
- ![Favicon for google](https://openrouter.ai/images/icons/GoogleGemini.svg)
	[Gemini 3.7 Flash](https://openrouter.ai/google/gemini-3.7-flash-20260813 "Google: Gemini 3.7 Flash")
	Google AI Studio
	![Still from the Google: Gemini 3.7 Flash game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fgoogle%2Fgemini-3.7-flash-20260813%2F62601c2c-6a29-4b05-b160-a9b2e9c8a179%2Fstill-0-591138960.jpg&w=3840&q=75) Play
	Cost$0.14
	Generation time123.7s
- ![Favicon for meta](https://openrouter.ai/images/icons/Meta.png)
	[Muse Spark Open](https://openrouter.ai/meta/muse-spark-open-20261015 "Meta: Muse Spark Open")
	Makora
	Play
	Cost$0.15
	Generation time408.5s
- ![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3.8 27B](https://openrouter.ai/qwen/qwen3.8-27b-20260814 "Qwen: Qwen3.8 27B")
	Novita
	![Still from the Qwen: Qwen3.8 27B game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3.8-27b-20260814%2F07d9732a-31d1-4b29-ac50-d95b469caca3%2Fstill-0-3869158180.jpg&w=3840&q=75) Play
	Cost$0.18
	Generation time1470.3s
- ![Favicon for meta](https://openrouter.ai/images/icons/Meta.png)
	[Muse Spark 1.3](https://openrouter.ai/meta/muse-spark-1.3-20260902 "Meta: Muse Spark 1.3")
	Meta
	![Still from the Meta: Muse Spark 1.3 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmeta%2Fmuse-spark-1.3-20260902%2Fbdf22564-5a65-4b65-93e2-3a8eca66d3ad%2Fstill-0-500495725.jpg&w=3840&q=75) Play
	Cost$0.20
	Generation time228.2s
- ![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok 4.6](https://openrouter.ai/x-ai/grok-4.6-20260810 "SpaceXAI: Grok 4.6")
	xAI
	![Still from the SpaceXAI: Grok 4.6 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-4.6-20260810%2F933ceb4e-9673-40a5-8571-e6d40ba33e00%2Fstill-0-3111792329.jpg&w=3840&q=75) Play
	Cost$0.20
	Generation time504.0s
- ![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5.2](https://openrouter.ai/z-ai/glm-5.2-20260616 "Z.ai: GLM 5.2")
	DigitalOcean
	![Still from the Z.ai: GLM 5.2 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5.2-20260616%2F3fc2f386-9b5e-4947-97a6-25323f04d471%2Fstill-0-1028165767.jpg&w=3840&q=75) Play
	Cost$0.21
	Generation time618.5s
- ![Favicon for moonshotai](https://openrouter.ai/images/icons/MoonshotAI.png)
	[Kimi K3](https://openrouter.ai/moonshotai/kimi-k3-20260715 "MoonshotAI: Kimi K3")
	Sail Research
	![Still from the MoonshotAI: Kimi K3 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmoonshotai%2Fkimi-k3-20260715%2Fe7504b44-b891-4fad-a072-7c807a259655%2Fstill-0-2462986875.jpg&w=3840&q=75) Play
	Cost$0.24
	Generation time193.5s
- ![Favicon for qwen](https://openrouter.ai/images/icons/Qwen.png)
	[Qwen3.8 Max](https://openrouter.ai/qwen/qwen3.8-max-20260902 "Qwen: Qwen3.8 Max (0902)")
	Alibaba
	![Still from the Qwen: Qwen3.8 Max (0902) game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fqwen%2Fqwen3.8-max-20260902%2F4b97fd63-4bf9-488b-a9b1-41f314bdc68b%2Fstill-0-2986043346.jpg&w=3840&q=75) Play
	Cost$0.30
	Generation time1082.6s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6.1 Terra](https://openrouter.ai/openai/gpt-6.1-terra-20261026 "OpenAI: GPT-6.1 Terra")
	OpenAI
	![Still from the OpenAI: GPT-6.1 Terra game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6.1-terra-20261026%2F95af669e-9aa8-4d17-8335-ef9300d3e505%2Fstill-0-3181307232.jpg&w=3840&q=75) Play
	Cost$0.33
	Generation time779.5s
- ![Favicon for z-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://z.ai/&size=256)
	[GLM 5.3](https://openrouter.ai/z-ai/glm-5.3-20260816 "Z.ai: GLM 5.3")
	Relace
	![Still from the Z.ai: GLM 5.3 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fz-ai%2Fglm-5.3-20260816%2Ff244b48b-2847-4486-afb8-1fb38dcbace5%2Fstill-0-3618821389.jpg&w=3840&q=75) Play
	Cost$0.42
	Generation time1025.8s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-6.1 Sol](https://openrouter.ai/openai/gpt-6.1-sol-20260929 "OpenAI: GPT-6.1 Sol")
	OpenAI
	![Still from the OpenAI: GPT-6.1 Sol game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-6.1-sol-20260929%2Ff57e8e79-3193-431e-acfd-4bd60b0eab92%2Fstill-0-3384262772.jpg&w=3840&q=75) Play
	Cost$0.49
	Generation time1058.5s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.6 Sol](https://openrouter.ai/openai/gpt-5.6-sol-20260709 "OpenAI: GPT-5.6 Sol")
	OpenAI
	![Still from the OpenAI: GPT-5.6 Sol game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.6-sol-20260709%2Ff89f4403-8003-4f9d-b3a5-ff9789744f59%2Fstill-0-1682118098.jpg&w=3840&q=75) Play
	Cost$0.49
	Generation time785.8s
- ![Favicon for moonshotai](https://openrouter.ai/images/icons/MoonshotAI.png)
	[Kimi K3.1 Pro](https://openrouter.ai/moonshotai/kimi-k3.1-pro-20261023 "MoonshotAI: Kimi K3.1 Pro")
	Moonshot AI
	Play
	Cost$0.50
	Generation time1094.3s
- ![Favicon for meta](https://openrouter.ai/images/icons/Meta.png)
	[Muse Wonder](https://openrouter.ai/meta/muse-wonder-20261012 "Meta: Muse Wonder")
	Meta
	![Still from the Meta: Muse Wonder game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fmeta%2Fmuse-wonder-20261012%2F374fc42d-cd61-4e74-8251-717cf58dc9f7%2Fstill-0-2077314375.jpg&w=3840&q=75) Play
	Cost$0.55
	Generation time254.1s
- ![Favicon for openai](https://openrouter.ai/images/icons/OpenAI.svg)
	[GPT-5.6 Terra](https://openrouter.ai/openai/gpt-5.6-terra-20260709 "OpenAI: GPT-5.6 Terra")
	OpenAI
	![Still from the OpenAI: GPT-5.6 Terra game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fopenai%2Fgpt-5.6-terra-20260709%2Ff69a24d1-0b83-4d2c-b273-1a370eef2a84%2Fstill-0-3952382900.jpg&w=3840&q=75) Play
	Cost$0.79
	Generation time648.2s
- ![Favicon for x-ai](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://x.ai/&size=256)
	[Grok 4.7](https://openrouter.ai/x-ai/grok-4.7-20260916 "SpaceXAI: Grok 4.7")
	xAI
	![Still from the SpaceXAI: Grok 4.7 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fx-ai%2Fgrok-4.7-20260916%2Ff28846df-cd07-4927-8082-f316d0661f4d%2Fstill-0-917400534.jpg&w=3840&q=75) Play
	Cost$0.80
	Generation time1200.9s
- ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Opus 5](https://openrouter.ai/anthropic/claude-opus-5-20260723 "Anthropic: Claude Opus 5")
	Azure
	![Still from the Anthropic: Claude Opus 5 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-opus-5-20260723%2Fc3f4ab6e-e7db-4ac3-bb95-df678920ed64%2Fstill-0-4088586514.jpg&w=3840&q=75) Play
	Cost$1.31
	Generation time591.7s
- ![Favicon for anthropic](https://openrouter.ai/images/icons/Anthropic.svg)
	[Claude Opus 4.8](https://openrouter.ai/anthropic/claude-4.8-opus-20260528 "Anthropic: Claude Opus 4.8")
	Claude Platform on AWS
	![Still from the Anthropic: Claude Opus 4.8 game](https://openrouter.ai/_next/image?url=https%3A%2F%2Fmodel-assets.openrouter.ai%2Fmodel-examples%2Fanthropic%2Fclaude-4.8-opus-20260528%2F455e1283-039f-4e33-957f-b965dd02be42%2Fstill-0-2395590044.jpg&w=3840&q=75) Play
	Cost$1.64
	Generation time906.3s