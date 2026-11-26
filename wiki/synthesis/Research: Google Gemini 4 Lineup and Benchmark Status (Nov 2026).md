---
title: >-
  Research: Google Gemini 4 Lineup and Benchmark Status (Nov 2026)
category: synthesis
tags: [google, gemini-4, neon, carbon, hydrogen, helium, model-selection, benchmarks, research]
sources:
  - "url:https://aistudio.google.com/docs/choosing-a-model.md"
  - "url:https://aistudio.google.com/docs/thinking.md"
  - "url:https://aistudio.google.com/docs/models.md"
  - "url:https://aistudio.google.com/docs/models/gemini-4-carbon.md"
  - "url:https://aistudio.google.com/docs/models/gemini-4-hydrogen.md"
  - "url:https://aistudio.google.com/docs/models/gemini-4-argon.md"
  - "url:https://artificialanalysis.ai/articles/gemini-4-neon-intelligence-gain"
  - "url:https://www.vals.ai/models/google_gemini-4-neon"
created: 2026-11-26T00:32:19Z
updated: 2026-11-26T00:32:19Z
summary: >-
  Status check as of 2026-11-26 of Google Gemini 4 models (Carbon, Neon, Hydrogen, Argon; Helium unreleased), updated thinking/selection docs, and latest benchmark standings.
provenance:
  extracted: 0.85
  inferred: 0.15
  ambiguous: 0.0
base_confidence: 0.89
lifecycle: draft
lifecycle_changed: 2026-11-26
---

# Research: Google Gemini 4 Lineup and Benchmark Status (Nov 2026)

## Overview

As of **2026-11-26**, Google's officially released Gemini 4 lineup consists of **Gemini 4 Carbon** (`gemini-4-carbon`), **Gemini 4 Neon** (`gemini-4-neon`, released 2026-11-18), **Gemini 4 Hydrogen** (`gemini-4-hydrogen`, released 2026-11-12), and **Gemini 4 Argon** (`gemini-4-argon`). **Gemini 4 Helium (`gemini-4-helium`) has not been officially released**: its official doc URL (`aistudio.google.com/docs/models/gemini-4-helium.md`) returns HTTP 404 and it does not appear in `llms.txt`, `models.md`, `choosing-a-model.md`, or `thinking.md`. Official Google `thinking.md` and `models.md` pages were updated since the 2026-11-13 wiki captures to add `gemini-4-neon` (`high` default, `xhigh` supported, 65,536 non-streaming synchronous cap).

## Key Findings

- **Official Lineup & Helium Status**: Official docs list Carbon, Neon, Hydrogen, and Argon (all 1M unified context window, `64K / 1M` max output). Community sightings of "Gemini 4 Helium" in web UI dropdowns remain unconfirmed rumors with no official model card, pricing, thinking levels, or benchmarks. [[references/sources/google-gemini-models]]
- **Updated Thinking & Effort Guidelines**: `thinking.md` now lists `gemini-4-neon` alongside `gemini-4-hydrogen` with `high` as default and `low`, `medium`, `high`, `xhigh` supported (reserve `xhigh` for hard multi-step coding/agentic tasks where `high` falls short). `gemini-4-carbon` and `gemini-4-argon` default to `medium` and support `low`, `medium`, `high` (max). `minimal` is unsupported on all Gemini 4 models. [[references/sources/google-gemini-thinking]]
- **Updated Selection & Pricing Notes**: `choosing-a-model.md` retains the 4-model recommendation table (`gemini-4-hydrogen` $1.50/$7.50 default; `gemini-4-neon` $3.00/$15.00 paid tier; `gemini-4-carbon` $2.00/$10.00 promotional thru 2026-11-30, $4.00/$20.00 from 2026-12-01; `gemini-3.5-flash-lite` $0.30/$2.50) and clarifies AI Studio plan access (Hydrogen/Flash-Lite free on all plans; Neon on AI Pro/Ultra; Carbon on AI Ultra). [[references/sources/google-gemini-choosing-a-model]]
- **Benchmark Standings Across Gemini 4**:
  - **Gemini 4 Neon**: Artificial Analysis Intelligence Index **61** (`xhigh`, #3 overall), AA Coding Agent Index **58.6** (#1 overall, Antigravity CLI), Vals Index **70.87%** (#2/42, #1 Finance & Legal). [[references/sources/artificial-analysis-gemini-4-neon]] [[references/sources/vals-ai-gemini-4-neon]]
  - **Gemini 4 Carbon**: AA Intelligence Index **59–60** (`high`), Vals Index **68.83%**, Arena Text Leaderboard **#1 (~1,527 Elo)**, SEC-bench Pro **88.2%** / CWE-bench **71.0%**.
  - **Gemini 4 Hydrogen**: AA Intelligence Index **51** (`high` default) / **54** (`xhigh`, high verbosity), optimized for fast everyday execution.
  - **Gemini 4 Argon**: AA Intelligence Index **50**, Vals Index **~68.9%**.
  - **Gemini 4 Helium**: No official benchmarks or API endpoints exist as of 2026-11-26.

## Core Concepts

- [[concepts/model-effort-selection]] — Separating model tier selection from thinking-level (`low`/`medium`/`high`/`xhigh`) calibration.
- [[synthesis/vendor-guided-model-selection]] — Cross-vendor official selection guidance.

## Entities & Tools

- [[references/google-gemini-4-neon]] — Full specifications and pricing for `gemini-4-neon`.

## Contradictions & Open Questions

- **Helium rumors vs official catalog**: Community threads speculate Helium is a Flash-Lite-tier Gemini 4 model, but official Google AI Studio endpoints return 404 and list `gemini-3.5-flash-lite` as the sub-second budget tier.
- **Carbon promotional pricing cliff**: Carbon's $2.00/$10.00 promotional pricing expires **2026-11-30**, doubling to $4.00/$20.00 on **2026-12-01** (making Neon cheaper per token and faster per task from December 1).

## Sources

- [[_raw/_archived/2026-11-26-google-gemini-choosing-a-model]]
- [[_raw/_archived/2026-11-26-google-gemini-thinking]]
- [[_raw/_archived/2026-11-26-google-gemini-models]]
- [[references/sources/google-gemini-choosing-a-model]]
- [[references/sources/google-gemini-thinking]]
- [[references/sources/google-gemini-models]]
- [[synthesis/Research: Google Gemini 4 Neon]]
