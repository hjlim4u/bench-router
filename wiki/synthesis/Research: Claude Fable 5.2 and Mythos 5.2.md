---
title: >-
  Research: Claude Fable 5.2 and Mythos 5.2
category: synthesis
tags: [research, anthropic, fable, mythos, swe-bench, benchmarks, claude-code, advisor, frontier-models]
sources:
  - "[[references/sources/anthropic-claude-fable-and-mythos-5-2]]"
  - "[[references/sources/anthropic-claude-code-advisor-fable]]"
  - "[[_raw/_archived/2026-11-10-anthropic-fable-5-2-mythos-5-2-announcement]]"
  - "[[_raw/_archived/2026-11-10-anthropic-fable-5-2-mythos-5-2-system-card]]"
  - "[[_raw/_archived/2026-11-10-anthropic-advisor-tool]]"
  - "[[_raw/_archived/2026-11-10-claudedev-multi-agent-teams-fable-5-2]]"
created: 2026-11-10T00:25:00Z
updated: 2026-11-26T00:49:17Z
summary: >-
  Comprehensive synthesis of Anthropic's Claude Fable 5.2 & Mythos 5.2: benchmarks (SWE-bench Pro 93.0%, FrontierCode 49.1, HLE 74.2%), dual-safeguard architecture, Claude Code advisor guide, and multi-agent scaling.
provenance:
  extracted: 0.85
  inferred: 0.12
  ambiguous: 0.03
base_confidence: 0.94
lifecycle: draft
lifecycle_changed: 2026-11-10
---

# Research: Claude Fable 5.2 and Mythos 5.2

## Overview

On November 9, 2026, Anthropic released **Claude Fable 5.2** and **Claude Mythos 5.2**, succeeding the Fable 5.1 generation. The release establishes new frontier benchmarks across software engineering, mathematical formalization, multimodal desktop agency, and scientific modeling. Anthropic deploys this underlying foundation model in two safeguard tiers: **Fable 5.2** (public/commercial release with strict cyber and bio guardrails) and **Mythos 5.2** (restricted to vetted cyber and life sciences researchers under the Cyber and Life Sciences Verification Programs).

## Key Findings

### 1. Model Specifications & Pricing
- **Context & Output:** 1,000,000 tokens (1M) context window with up to 128,000 tokens (128K) maximum output.
- **Pricing:** **$8.00 per million input tokens** / **$40.00 per million output tokens** (~20% cheaper than Fable 5.1 at $10/$50).
- **Fast Mode:** Optional token speedup (up to 2.5× faster generation) at **$16.00 / $80.00 per million tokens**.
- **Execution Speed:** Outputs generate up to 30% faster than Fable 5.1 under standard sampling.

### 2. Benchmark Performance (Official System Card Table 8.1.A)

| Benchmark / Evaluation | Fable 5.2 | Fable 5.1 | Opus 5.5 | GPT-6 Astra | Distinction |
|---|---|---|---|---|---|
| **SWE-bench Pro** | **93.0%** | 81.2% | 89.9% | – | Real-world active repos with multi-file diffs |
| **SWE-bench Multilingual** | **96.6%** | 89.1% | 93.9% | – | 300 problems across 9 languages |
| **SWE-bench Multimodal** | **74.1%** | 54.7% | 61.4% | – | Screenshots & design mockups in issue descriptions |
| **DeepSWE v1.1** | **74.3%** | – | – | – | 113 long-horizon SWE tasks |
| **FrontierCode 2.0** | **49.1** | 32.4 | 45.5 | 42.8 | Cognition agentic coding from real PRs (mean@5) |
| **FrontierSWE v2** | **69.9** | 56.3 | 62.3 | 65.5 | Agentic SWE benchmark |
| **Humanity’s Last Exam (No tools)** | **73.2** | 60.9 | 64.4 | – | Multidisciplinary expert questions |
| **Humanity’s Last Exam (With tools)** | **74.2** | 65.6 | 67.7 | 57.2 | Multidisciplinary expert questions + tools |
| **WANDR (Relaxed score)** | **82.1** | 68.7 | 72.3 | – | Deep research and document synthesis |
| **OSWorld 2.1 (Offline set)** | **89.3%** | 83.5% | 87.2% | 79.5% | Desktop GUI & OS agent benchmark |
| **CursorBench 4.0 (Max effort)** | **60.0%** | 51.8% | 57.8% | 52.8% (Gemini 4 Argon) | Cursor production agent harness evaluation |
| **Remote Labor Index (RLI)** | **41.3** | 17.9 | 21.3 | 20.8 | Autonomous real-world task benchmark |
| **AutomationBench** | **51.4** | 31.4 | 42.5 | 41.4 | Workflow automation evaluations |
| **CVE Rediscovery** | **89.6%** | 78.3% | 81.3% | – | Zero-day & historical vulnerability detection |

### 3. Claude Code Integration & Guidance
- **CLI Requirements:** Claude Code **v2.1.321 or later** is required.
- **Advisor Mode (`/advisor fable` or `--advisor fable`):**
  - Allows pairing a faster, cheaper primary model (e.g. Sonnet 5.5 or Opus 5.5) with Fable 5.2 acting as an advisor.
  - Claude Code escalates hard architectural decisions to Fable 5.2 without running all file read/write loops through Fable.
- **Prompting & Operational Paradigm Shift:**
  - Anthropic advises moving away from rigid step-by-step scaffolding and micro-management. Fable 5.2 achieves best results when given high-level outcome definitions and autonomous room to plan.
  - Built-in Adaptive Thinking dynamically allocates reasoning budget; manual attempts to disable thinking throw an API 400 error.
- **Billing:** On Claude Pro and Team plans, Fable usage bills to **usage credits** rather than subscription quotas. Requires explicit one-time user authorization.

### 4. Multi-Agent Scaling (Fermat's Last Theorem Reproduction)
- In a research experiment published on claude.dev, a team of **1,000 Claude Fable 5.2 agents** formalized Fermat's Last Theorem in Lean 4 in **28.7 hours**.
- Unlike prior formalizations (which required researcher steering and Prove2Me scaffolding), Fable 5.2 required 1/3 as many output tokens and produced a proof 1/7 the length, utilizing an SQLite shared state database, sandbox isolation, and command classifier monitoring.

## Independent Benchmarks (checked 2026-11-26)

- **Artificial Analysis Intelligence Index (2026-11-24 snapshot)**:
  - **Claude Fable 5.2**: **64.6** (`max` / default top config; ~$26.54/task, ~40.5 min), **62.2** (`xhigh`), **61.8** (`high`), **56.4** (`medium`), **53.9** (`low`).
  - **Claude Opus 5.5**: **59.1** (`max`), **57.4** (`xhigh`), **51.8** (`high`), **48.2** (`medium`), **34.8** (`low`).
  - **Claude Sonnet 5.5**: **54.5** (`max`), **49.9** (`xhigh`), **41.5** (`high`), **30.8** (`medium`), **25.6** (`low`).
  - **Claude Haiku 5.5**: **36.5** (`max`), **34.6** (`xhigh`), **29.9** (`high`), **24.6** (`medium`), **18.6** (`low`).
- **Vals AI (checked 2026-11-26)**: Fable 5.2 ranks **#1/43** on the Vals Index (**70.06% ± 1.02**, $17.94/test, 43m 42s latency, 1.88% fallback, 0.00% refusal), **#1/29** Vals RSI Index (**37.88%**), **#1/70** Terminal-Bench 4.0, **#1/51** Vibe Code Bench v1.1.1 (**83.52% ± 3.25**), **#1/46** Finance Agent v2.1 (**69.47% ± 1.98**), **#1/54** ProofBench v1.1 (**100.00%**), **#1/48** EMB v1.1 (**77.38% ± 2.19**), **#1/35** BioMysteryBench (**83.70% ± 0.74**), and **#2/31** Code Migration v1.1 (**83.27% ± 3.12**); Vals Science Index **63.74% ± 2.30** (#3/29), Vals Finance Index **63.58% ± 1.38** (#8/46), Vals Legal Index **69.17% ± 1.81** (#24/44).
- **LMArena & Terminal-Bench Proxy (2026-11-24 snapshot)**: Fable 5.2 (`max`) achieves Arena Text overall **1502.2** (Coding **1525.4**, Expert **1532.1**, Factuality **1483.2**) and Terminal-Bench 4.0 `max` **65.76%**.

## Core Concepts

- [[concepts/dual-safeguard-deployment]]: Releasing identical foundation model weights under two safeguard regimes (Fable vs Mythos).
- [[concepts/fable-advisor-pattern]]: Escalating complex decisions from daily drivers (Sonnet/Opus) to Fable 5.2 via Claude Code's advisor tool.

## Sources

- [[references/sources/anthropic-claude-fable-and-mythos-5-2]] — Official release announcement and System Card data.
- [[references/sources/anthropic-claude-code-advisor-fable]] — Official Claude Code guide for advisor tool and Fable configuration.
- [[references/sources/anthropic-effort]] — Official effort guide including Fable 5.2 / Mythos 5.2 / Opus 5.5 / Sonnet 5.5 / Haiku 5.5 per-model recommendations (2026-11-26 capture).
- [[references/sources/anthropic-model-selection]] — Official Anthropic model selection guide (2026-11-26 capture).
- [[_raw/_archived/2026-11-10-anthropic-fable-5-2-mythos-5-2-announcement]] — Verbatim release announcement.
- [[_raw/_archived/2026-11-10-anthropic-fable-5-2-mythos-5-2-system-card]] — Verbatim System Card Section 8 capability evaluations.
- [[_raw/_archived/2026-11-10-anthropic-advisor-tool]] — Verbatim Claude Code advisor tool documentation.
- [[_raw/_archived/2026-11-10-claudedev-multi-agent-teams-fable-5-2]] — Verbatim multi-agent scaling publication.
