---
title: >-
    ScreenSpot-Pro
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/likaixin/ScreenSpot-Pro", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    GUI grounding on high-resolution screens of professional applications
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# ScreenSpot-Pro

GUI grounding on high-resolution screens of professional applications.

From the dataset card (`likaixin/ScreenSpot-Pro`):

> ScreenSpot-Pro: GUI Grounding for Professional High-Resolution Computer Use Note: Data viewer is not configured because the large size of the images will trigger loading errors. Data Details Category Abbr. ApplicationEdition & Version OS Icons Texts Development and Programming VSC Visual Studio Code 1.95 macOS 22 33 PyC PyCharm 2023.3 macOS 38 40 AS Android Studio 2022.2 macOS 44 36 Qrs Quartus II 13.0

## Index

```toml
[[unit]]
id = "hf:likaixin/ScreenSpot-Pro"
desc = "GUI grounding on high-resolution screens of professional applications"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["gui_grounding"] }
reason = "Leaderboard API (2026-10-18): 23 rows, 23 models, 0 verified, 19 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active. Mixes general LLMs (Qwen3.5) with dedicated GUI-grounding models (UI-Venus, GTA1)"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: gui_grounding

## Sources

- <https://huggingface.co/datasets/likaixin/ScreenSpot-Pro>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
