---
title: >-
  Artificial Analysis: Gemini 4 Neon Evaluation
category: references
tags: [source, artificial-analysis, gemini-4, neon, benchmarks]
sources:
  - "url:https://artificialanalysis.ai/articles/gemini-4-neon-intelligence-gain"
source_url: "https://artificialanalysis.ai/articles/gemini-4-neon-intelligence-gain"
created: 2026-11-19T08:02:38Z
updated: 2026-11-19T08:02:38Z
as_of: 2026-11-19
summary: >-
  Independent Artificial Analysis evaluation of Gemini 4 Neon: Intelligence Index (61), Coding Agent Index (59), Cost/Time per Task, GDP.pdf, AA-Briefcase, and MKA.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.52
lifecycle: draft
lifecycle_changed: 2026-11-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-11-19-artificial-analysis-gemini-4-neon|2026-11-19-artificial-analysis-gemini-4-neon]]"
---

# Artificial Analysis: Gemini 4 Neon Evaluation

Published 2026-11-18, Artificial Analysis evaluated **Gemini 4 Neon** as Google DeepMind's fourth model release in seven weeks, finding small intelligence gains over Gemini 4 Carbon alongside substantially lower cost and time per task. ^[extracted]

## Key Benchmark Results

- **AA Intelligence Index (v5.0.1)**: Neon (`xhigh`) scores **61**, **#3 overall** (behind GPT-6.2 Astra `max` and Claude Fable 5.2 `max`) and **+1 pt** ahead of Gemini 4 Carbon (`high`, 60). At `high` effort, Neon matches Carbon (`high`) at less than half the Cost per Task using Carbon's standard ($4/$20) pricing. ^[extracted]
- **Cost & Time per Task (Intelligence Index, `xhigh` vs Carbon `high`)**:
  - **Cost per Task**: **$6.44** vs Carbon **$7.76** (~17% lower at non-discounted Carbon pricing). Neon uses ~15% more output tokens per task, so savings come from its 25% lower standard token price ($3/$15 vs $4/$20). ^[extracted]
  - **Time per Task**: **~21 minutes** vs Carbon **~36 minutes** (~40% faster), driven by higher output speed (~110 vs ~57 output tokens/s). ^[extracted]
- **AA Coding Agent Index (Antigravity CLI)**: Neon (`xhigh`) scores **59** (3 pts ahead of Carbon `high` at 55), in line with Claude Code + Claude Fable 5.2 (`xhigh`, 58) and Claude Opus 5.5 (`max`, 58) at much lower Cost per Task (**$6.86** vs **$12.61** for Opus 5.5 `max` and **$15.47** for Fable 5.2 `xhigh`). ^[extracted]
- **Visual Reasoning & Knowledge Work**:
  - **GDP.pdf**: Neon (`high`) scores **33.4%** (+5 pts over Carbon `high` at 28.4%); Neon (`xhigh`) scores **28.0%**. ^[extracted]
  - **AA-Briefcase**: Neon (`xhigh`) scores **1700 Elo** overall and leads Presentation Quality at **1771 Elo** (+45 pts over Claude Sonnet 5.5 `max` at 1726). ^[extracted]
  - **Multimodal Knowledge Agent (MKA)**: **56% Climb WSR** (+2 pts over Carbon, near leader Claude Fable 5.2 `max` at 57%). ^[extracted]

## Related

- [[references/google-gemini-4-neon]]
- [[references/sources/google-gemini-4-neon-release]]
- [[references/sources/artificial-analysis-methodology]]
- [[synthesis/Research: Google Gemini 4 Neon]]
