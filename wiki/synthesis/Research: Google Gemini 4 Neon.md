---
title: >-
  Research: Google Gemini 4 Neon
category: synthesis
tags: [google, gemini-4, neon, model-selection, benchmarks, research]
sources:
  - "url:https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/"
  - "url:https://aistudio.google.com/docs/choosing-a-model.md"
  - "url:https://aistudio.google.com/docs/whats-new-gemini-4-neon.md"
  - "url:https://aistudio.google.com/docs/models/gemini-4-neon.md"
  - "url:https://antigravity.google/blog/gemini-4-neon-in-google-antigravity"
  - "url:https://artificialanalysis.ai/articles/gemini-4-neon-intelligence-gain"
  - "url:https://www.vals.ai/models/google_gemini-4-neon"
created: 2026-11-19T08:02:38Z
updated: 2026-11-19T08:02:38Z
summary: >-
  Synthesis of 3-round research on Google Gemini 4 Neon: official model-selection guide, thinking levels, launch benchmarks, independent AA/Vals evaluations, and contradictions.
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.91
lifecycle: draft
lifecycle_changed: 2026-11-19
---

# Research: Google Gemini 4 Neon

## Overview

Google DeepMind released **Gemini 4 Neon** (`gemini-4-neon`) on **2026-11-18** across the Gemini API, Google AI Studio, Gemini for business, Google Antigravity, Android Studio, and the Gemini app (Pro/Ultra). Positioned between **Gemini 4 Hydrogen** (everyday speed) and **Gemini 4 Carbon** (deepest verification), Neon is priced at **$3.00 / 1M input** ($0.15 cached) and **$15.00 / 1M output** tokens with a unified **1M-token** context/output window and four thinking levels (`low`, `medium`, `high` default, `xhigh`). Independent evaluations from Artificial Analysis and Vals AI confirm frontier-level coding and enterprise knowledge-work performance at substantially lower cost and latency per task than Carbon and competing frontier models.

## Key Findings

- **Official Model Selection Guidance**: Google recommends `gemini-4-hydrogen` ($1.50/$7.50) as the default for new projects, `gemini-4-neon` ($3.00/$15.00, paid tier only) for complex high-frequency engineering, knowledge work, and science where Hydrogen is insufficient, and `gemini-4-carbon` ($2.00/$10.00 intro through 2026-11-30; $4.00/$20.00 from 2026-12-01) for the hardest architecture, debugging, and security audits. Workflows can also pair Neon (or Carbon) as planner with Hydrogen as executor via Interactions API `previous_interaction_id` or Google Antigravity Orchestrator. [[references/sources/google-gemini-choosing-a-model]]
- **Artificial Analysis Benchmarks**: At `xhigh`, Neon scores **61** on the AA Intelligence Index v5.0.1 (#3 overall, +1 pt over Carbon `high` at 60) at **$6.44/task** and **~21 min/task** (~17% cheaper than Carbon's $7.76 standard-price cost and ~40% faster than Carbon's ~36 min due to ~110 vs ~57 tok/s output speed). On the AA Coding Agent Index (Antigravity CLI), Neon (`xhigh`) scores **59** (58.6 unrounded, #1 overall) at **$6.86/task** vs $12.61 for Claude Opus 5.5 (`max`, 58) and $15.47 for Claude Fable 5.2 (`xhigh`, 58). [[references/sources/artificial-analysis-gemini-4-neon]]
- **Vals AI Benchmarks**: At `xhigh`, Neon ranks **#2 of 42** on the Vals Index (**70.87% ± 0.94**, $7.405/test), **#1** on Vals Finance Index (**68.31%**), **#1** on Vals Legal Index (**78.36%**), **#1** on Legal Research Bench (**56.25%**), **#1** on Tax Agent Bench (**54.89%**), and **#2** on Vibe Code Bench v1.1 (**93.70%**), sitting on the score–cost Pareto frontier on **7 of 14** leaderboards. [[references/sources/vals-ai-gemini-4-neon]]
- **Google Launch & Cyber Benchmarks**: Google reports **65.2%** on Terminal-Bench 4.1, **46.2%** on FrontierCode 2.0 (`high`), **12.8% → 39.0%** on SWE-sweep (mini-SWE vs Antigravity harness), **1336 Elo** (#2) on Agent Arena Index, **56.3%** (#1) on Zapier AutomationBench, **$16,843** (#1) on Vending-Bench 2, and SOTA cyber defense scores for Neon for Cyber (**90.5%** SEC-bench Pro, **70.7%** CWE-bench v2, **76%** AutoBaxBench hard, **51.26%** WebExploitBench v1.2). [[references/sources/google-gemini-4-neon-release]]
- **Safety & Discipline**: 0.0% cheating on Terminal-Bench 4.0, 2.45% coding cheating rate (lowest in Gemini 4), 1.98% refusal on Terminal-Bench 4.0 (0% on Terminal-Bench-Science), 43%–56% lower under-service and 15%–35% lower overreach vs Carbon, and 0.0% attack success rate on Gray Swan IPI at `xhigh`. [[references/sources/google-gemini-4-neon-release]]

## Core Concepts

- [[concepts/model-effort-selection]] — Matching model tier and thinking level (`low` / `medium` / `high` / `xhigh`) to task complexity.
- [[synthesis/vendor-guided-model-selection]] — Cross-vendor official model selection guidance (OpenAI, Anthropic, Google).

## Entities & Tools

- [[references/google-gemini-4-neon]] — Model specifications, pricing, capabilities, and rollout surfaces for `gemini-4-neon`.

## Contradictions & Open Questions

- **Terminal-Bench-Science discrepancy**: Google's launch blog reports **70.5%** on Terminal-Bench Science, whereas Vals AI's 2026-11-18 evaluation at `xhigh` reports **62.86% ± 5.82** (#2/48). This likely reflects harness, prompt, or subset differences between Google's internal run and Vals AI's suite.
- **Terminal-Bench 4.0 vs 4.1**: Google highlights **65.2%** on Terminal-Bench **4.1**, while Vals AI reports **61.62% ± 2.02** (#7/69) on Terminal-Bench **4.0**.
- **AA Coding Agent Index rounding**: Google's blog and Antigravity blog cite **58.6** (#1), while Artificial Analysis's article rounds to **59** in prose.
- **Temporary Carbon pricing inversion**: Until 2026-11-30, Carbon's introductory token price ($2/$10) is lower than Neon's ($3/$15), even though Neon uses fewer tokens/task on `high` and is 25% cheaper than Carbon's post-Nov-30 standard price ($4/$20).
- **Direct model card HTML**: `deepmind.google/models/model-cards/gemini-4-neon/` could not be cleanly parsed as plain text via automated HTTP fetch (likely client-rendered/compressed); official specs were verified via `aistudio.google.com/docs/models/gemini-4-neon.md` instead.

## Sources Consulted

- [[references/sources/google-gemini-4-neon-release]]
- [[references/sources/google-gemini-choosing-a-model]]
- [[references/sources/artificial-analysis-gemini-4-neon]]
- [[references/sources/vals-ai-gemini-4-neon]]
- [[references/sources/google-gemini-models]]
