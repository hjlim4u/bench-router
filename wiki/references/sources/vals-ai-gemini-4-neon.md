---
title: >-
  Vals AI: Gemini 4 Neon Benchmarks
category: references
tags: [source, vals-ai, gemini-4, neon, benchmarks]
sources:
  - "url:https://www.vals.ai/models/google_gemini-4-neon"
source_url: "https://www.vals.ai/models/google_gemini-4-neon"
created: 2026-11-19T08:02:38Z
updated: 2026-11-19T08:02:38Z
as_of: 2026-11-19
summary: >-
  Independent Vals AI evaluation of Gemini 4 Neon across 14 leaderboards (Vals Index 70.87% #2/42, #1 Finance & Legal, Pareto frontier on 7 boards).
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.52
lifecycle: draft
lifecycle_changed: 2026-11-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-11-19-vals-ai-gemini-4-neon|2026-11-19-vals-ai-gemini-4-neon]]"
---

# Vals AI: Gemini 4 Neon Benchmarks

Evaluated 2026-11-18 with default Google provider settings (`reasoning_effort: xhigh`, `max_output_tokens: 1,048,576`). **Gemini 4 Neon** ranks **#2 of 42** models on the **Vals Index** at **70.87% ± 0.94** ($7.405/test, 31m 25s latency) and sits on the score–cost Pareto frontier on **7 of 14** leaderboards. ^[extracted]

## Leaderboard Results (2026-11-18)

| Benchmark | Score (±95% CI) | Rank | Pareto Frontier |
|---|---|---|---|
| **Vals Index** | 70.87% ± 0.94 | #2 / 42 | Yes ($7.405/test) |
| **Vals Finance Index** | 68.31% ± 1.38 | #1 / 45 | Yes ($4.88/test) |
| **Vals Legal Index** | 78.36% ± 1.83 | #1 / 43 | Yes ($6.10/test) |
| **Vals Science Index** | 62.63% ± 2.33 | #4 / 28 | No ($8.26/test) |
| **EMB v1.1** (Earnings Modeling) | 76.46% ± 2.06 | #4 / 47 | Yes ($3.82/test) |
| **Finance Agent v2.1** | 68.56% ± 1.94 | #2 / 45 | No |
| **Legal Research Bench** | 56.25% ± 3.45 | #1 / 99 | Yes ($7.37/test) |
| **MysteryMechanism** | 45.05% ± 3.35 | #9 / 34 | No |
| **Tax Agent Bench** | 54.89% ± 3.59 | #1 / 90 | Yes ($4.95/test) |
| **Vibe Code Bench v1.1** | 93.70% ± 1.17 | #2 / 133 | Yes ($6.76/test) |
| **BioMysteryBench** | 80.00% ± 1.93 | #4 / 34 | No |
| **HLAB-Vals-1.1** (Harvey Legal) | 19.58% ± 3.31 | #8 / 43 | No |
| **Terminal-Bench 4.0** | 61.62% ± 2.02 | #7 / 69 | No |
| **Terminal-Bench-Science** | 62.86% ± 5.82 | #2 / 48 | No |

## Related

- [[references/google-gemini-4-neon]]
- [[references/sources/google-gemini-4-neon-release]]
- [[references/sources/artificial-analysis-gemini-4-neon]]
- [[synthesis/Research: Google Gemini 4 Neon]]
