---
title: >-
  Anthropic: Introducing Claude Fable 5.2 and Claude Mythos 5.2
category: references
tags: [source, anthropic, fable, mythos, frontier-models, benchmarks]
sources:
  - "url:https://www.anthropic.com/claude-fable-and-mythos-5-2"
  - "url:https://www.anthropic.com/document/claude-fable-5-2-mythos-5-2-system-card"
source_url: "https://www.anthropic.com/claude-fable-and-mythos-5-2"
created: 2026-11-10T00:25:00Z
updated: 2026-11-10T00:25:00Z
as_of: 2026-11-10
summary: >-
  Official Anthropic release of Claude Fable 5.2 & Claude Mythos 5.2: two safeguard tiers, $8/$40 per M tokens, fast mode, 1M context, state-of-the-art benchmarks in SWE-bench Pro (93.0%) and FrontierCode.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-11-10
tier: primary
snapshots:
  - "[[_raw/_archived/2026-11-10-anthropic-fable-5-2-mythos-5-2-announcement|2026-11-10-anthropic-fable-5-2-mythos-5-2-announcement]]"
  - "[[_raw/_archived/2026-11-10-anthropic-fable-5-2-mythos-5-2-system-card|2026-11-10-anthropic-fable-5-2-mythos-5-2-system-card]]"
  - "[[_raw/_archived/2026-11-10-anthropic-fable-5-2-model-overview|2026-11-10-anthropic-fable-5-2-model-overview]]"
---

# Anthropic: Introducing Claude Fable 5.2 and Claude Mythos 5.2

On November 9, 2026, Anthropic announced **Claude Fable 5.2** and **Claude Mythos 5.2**, their new frontier models engineered for long-horizon technical challenges, advanced reasoning, coding, and scientific research.

## Core Characteristics & Two-Tier Architecture

- **Shared Underlying Model:** Fable 5.2 and Mythos 5.2 share the exact same weights, technical architecture, and raw capabilities.
- **Safeguard Tiering:**
  - **Claude Fable 5.2 (`claude-fable-5-2`):** Broadly available version with strong cybersecurity and biology safeguards against misuse, accessible via Claude API, Claude Code, AWS Bedrock, Google Cloud, and Microsoft Foundry.
  - **Claude Mythos 5.2:** Features more permissive guardrails in dual-use domains, strictly restricted to vetted institutions via Anthropic's Cyber Verification Program and Life Sciences Verification Program. Also powers Claude Security for Enterprise.
- **Context & Pricing:**
  - Context window: 1,000,000 tokens (1M); maximum output: 128,000 tokens (128K).
  - Standard pricing: **$8.00 per million input tokens** / **$40.00 per million output tokens** (approx. 20% cheaper than Fable 5.1's $10/$50).
  - Optional Fast Mode: speeds up token generation by up to 2.5× at **$16.00 / $80.00 per million tokens**.
  - Output speed: generates responses up to 30% faster than Fable 5.1.

## Official Benchmark Highlights (System Card Table 8.1.A)

- **SWE-bench Pro:** **93.0%** (vs Opus 5.5: 89.9%, Fable 5.1: 81.2%)
- **SWE-bench Multilingual:** **96.6%** (vs Opus 5.5: 93.9%, Fable 5.1: 89.1%)
- **SWE-bench Multimodal:** **74.1%** (vs Opus 5.5: 61.4%, Fable 5.1: 54.7%)
- **DeepSWE v1.1:** **74.3%**
- **FrontierCode 2.0:** **49.1** (vs Opus 5.5: 45.5, Fable 5.1: 32.4, GPT-6 Astra: 42.8)
- **FrontierSWE v2:** **69.9** (vs Opus 5.5: 62.3, Fable 5.1: 56.3, GPT-6 Astra: 65.5)
- **Humanity’s Last Exam (HLE):** **74.2%** with tools (vs Opus 5.5: 67.7%, GPT-6 Astra: 57.2%)
- **OSWorld 2.1 (Offline set):** **89.3%** (vs Opus 5.5: 87.2%, GPT-6 Astra: 79.5%)
- **CursorBench 4.0:** **60.0%** at max effort (vs Opus 5.5: 57.8%, Fable 5.1: 51.8%)
- **Remote Labor Index (RLI):** **41.3** (vs Opus 5.5: 21.3, GPT-6 Astra: 20.8)

## Official Positioning

Anthropic recommends:
> For most coding and knowledge tasks, start with **Claude Opus 5.5**, our strongest daily driver, and switch to **Claude Fable 5.2** as an **Advisor** (where Haiku, Sonnet, or Opus models consult it at decision inflection points) or **Orchestrator** (where it plans and delegates simpler tasks to smaller models).
