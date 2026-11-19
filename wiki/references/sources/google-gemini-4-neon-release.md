---
title: >-
  Google: Introducing Gemini 4 Neon
category: references
tags: [source, google, gemini-4, neon, benchmarks]
sources:
  - "url:https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/"
  - "url:https://antigravity.google/blog/gemini-4-neon-in-google-antigravity"
  - "url:https://aistudio.google.com/docs/whats-new-gemini-4-neon"
source_url: "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/"
created: 2026-11-19T08:02:38Z
updated: 2026-11-19T08:02:38Z
as_of: 2026-11-19
summary: >-
  Official launch announcement, pricing, rollout channels, thinking levels, cybersecurity benchmarks, and safety metrics for Gemini 4 Neon (released 2026-11-18).
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.0
base_confidence: 0.67
lifecycle: draft
lifecycle_changed: 2026-11-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-11-19-google-blog-introducing-gemini-4-neon|2026-11-19-google-blog-introducing-gemini-4-neon]]"
  - "[[_raw/_archived/2026-11-19-antigravity-gemini-4-neon|2026-11-19-antigravity-gemini-4-neon]]"
  - "[[_raw/_archived/2026-11-19-google-whats-new-gemini-4-neon|2026-11-19-google-whats-new-gemini-4-neon]]"
---

# Google: Introducing Gemini 4 Neon

Google announced **Gemini 4 Neon** (`gemini-4-neon`) on **2026-11-18**, positioning it between **Gemini 4 Hydrogen** (fast everyday execution) and **Gemini 4 Carbon** (hardest long-horizon projects) for complex software engineering, knowledge work, and science workflows. ^[extracted]

## Pricing, Specs & Availability

- **Pricing**: $3.00 / 1M input tokens ($0.15 / 1M cached input tokens, 95% discount, implicit caching only) and $15.00 / 1M output tokens. Paid tier only (no free API tier). ^[extracted]
- **Context & output**: Unified 1,048,576-token input/output context window; 65,536 default synchronous output tokens, extendable up to 1,048,576 via long decode (`background=true` or continuation). ^[extracted]
- **Modalities & tools**: Accepts text, image, video, audio, and PDF; text output. Supports Google Search grounding, Google Maps grounding, code execution, computer use, function calling, structured outputs, file search, URL context, Batch API, Flex inference, and Priority inference. Does not support explicit caching, image/audio generation, or Live API. ^[extracted]
- **Thinking levels**: `low`, `medium`, `high` (default), and `xhigh`. ^[extracted]
- **Rollout**: Gemini API (Google AI Studio, `generateContent` and Interactions API), Gemini for business (API and dropdown), Google Antigravity (Pro/Ultra subscribers and business; supports Orchestrator pairing Neon as planner + Hydrogen as executor), Android Studio, and Gemini app (Pro/Ultra subscribers). ^[extracted]

## Reported Launch Benchmarks

- **General & Knowledge Work**:
  - **Artificial Analysis Intelligence Index (xhigh)**: **61** (#3 overall). ^[extracted]
  - **Vals Index**: **70.9%** (#2 overall, on Pareto frontier); #1 on **Legal Research Bench** and **Tax Agent Bench**; #1 across most Surge AI finance, accounting, spreadsheet modeling, and complex constraint-following categories. ^[extracted]
  - **Agent Arena Index**: **1336** (#2 globally across 4,200+ real-world sessions; #2 on steerability). ^[extracted]
  - **Chartography**: **73.5%**; **Agents' Last Exam v1.1**: **75.8%**; **Zapier AutomationBench**: **56.3%** (#1); **Vending-Bench 2**: **$16,843** (#1). ^[extracted]
- **Coding & Science**:
  - **AA Coding Agent Index**: **58.6** (#1 overall). ^[extracted]
  - **Terminal-Bench 4.1**: **65.2%**; **FrontierCode 2.0 (high)**: **46.2%**. ^[extracted]
  - **SWE-sweep**: **12.8%** on mini-SWE harness, **39.0%** in Google Antigravity harness. ^[extracted]
  - **Terminal-Bench Science**: **70.5%**; **RiemannBench**: **84.0%**; **HLE-Diamond**: **71.3%**. ^[extracted]
- **Cybersecurity (Neon for Cyber / Fairwind Program)**:
  - **AutoBaxBench (hard)**: **76%** (SOTA); **WebExploitBench v1.2**: **51.26%** (SOTA at half cost of competing large models); **SEC-bench Pro**: **90.5%** (SOTA); **CWE-bench v2**: **70.7%** (+3.4% over Carbon); **ExploitGym**: frontier-level at half the tokens of Carbon. ^[extracted]

## Safety & Alignment

- **Refusal & cheating**: Refused 1.98% of tasks on Terminal-Bench 4.0 and 0% on Terminal-Bench-Science; 0.0% cheating on Terminal-Bench 4.0; 2.45% shortcut rate on internal coding cheating eval (lowest in Gemini 4); 0.09% misaligned action rate on agentic safety suite; 99.2% pass rate on agent honesty eval. ^[extracted]
- **Agentic discipline & IPI**: Reduced under-service by 43%–56% and overreach by 15%–35% vs Carbon across effort levels; 0.0% attack success rate on Gray Swan IPI benchmark at `xhigh` with real-time safeguards. ^[extracted]

## Related

- [[references/google-gemini-4-neon]]
- [[references/sources/google-gemini-choosing-a-model]]
- [[references/sources/artificial-analysis-gemini-4-neon]]
- [[references/sources/vals-ai-gemini-4-neon]]
- [[synthesis/Research: Google Gemini 4 Neon]]
