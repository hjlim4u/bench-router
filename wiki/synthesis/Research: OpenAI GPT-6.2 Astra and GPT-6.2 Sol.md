---
title: >-
  Research: OpenAI GPT-6.2 Astra and GPT-6.2 Sol
category: synthesis
tags: [openai, gpt-6.2, astra, sol, benchmarks, research]
sources:
  - "url:https://openai.com/index/introducing-gpt-6-2-astra-sol"
  - "url:https://developers.openai.com/api/docs/guides/model-selection"
  - "url:https://developers.openai.com/api/docs/guides/latest-model"
  - "url:https://deploymentsafety.openai.com/content/gpt-6-2-system-card"
created: 2026-11-18T08:00:21Z
updated: 2026-11-26T00:49:17Z
summary: >-
  Synthesis of 3-round research on GPT-6.2 Astra and GPT-6.2 Sol: official model-selection & prompting guides, API migration rules, launch benchmarks, and bench-router integration status.
provenance:
  extracted: 0.85
  inferred: 0.15
  ambiguous: 0.0
base_confidence: 0.65
lifecycle: draft
lifecycle_changed: 2026-11-18
---

# Research: OpenAI GPT-6.2 Astra and GPT-6.2 Sol

## Overview

OpenAI released **GPT-6.2 Astra** (`gpt-6.2-astra`) and **GPT-6.2 Sol** (`gpt-6.2-sol`) on **2026-11-17** across ChatGPT Work, Codex, the OpenAI API, Azure, and Amazon Bedrock. Astra cuts API token prices by ~20% ($8/$40 per 1M, $0.40 cached) while advancing frontier agentic and scientific scores, whereas Sol holds $2/$10 pricing and narrows the coding gap to within 0.5 points of Astra on FrontierCode 2.0. Both models require `low` or higher reasoning effort (`none`/`minimal` are rejected) and introduce strict Responses API prefix-immutability rules.

## Key Findings

- **Model positioning & selection**: OpenAI's Model Selection guide ranks `GPT-6.2 Astra > GPT-6.2 Sol > GPT-6.1 Terra > GPT-6 Luna` across all six work categories, recommending `medium` as the default integration starting point. [[references/sources/openai-model-selection]]
- **Prompting & API migration**: Tool calling requires the Responses API; top-level `instructions` are now appended *after* `input` (so stable prompts must move to a leading `developer` message for caching); prefix edits drop reasoning items; and `temperature`/`top_p`/`logprobs` must be omitted. [[references/sources/openai-gpt-6-2-prompting]]
- **Launch benchmarks**:
  - **AA Intelligence Index v5**: GPT-6.2 Astra (max) **62** (#2 behind Claude Fable 5.2 at 65); GPT-6.2 Sol **57**. [[references/sources/openai-gpt-6-2-release]]
  - **Agents' Last Exam**: GPT-6.2 Astra **78.3%** (+5.2 pts vs GPT-6 Astra, +5.5 pts vs Claude Fable 5.2). [[references/sources/openai-gpt-6-2-release]]
  - **Terminal-Bench-Science 0.1**: GPT-6.2 Astra **+9 pp** over GPT-6 Astra; **Terminal-Bench 4.1**: GPT-6.2 Sol (max) **61.5% (±2.8%)**. [[references/sources/openai-gpt-6-2-release]]
  - **FrontierCode 2.0**: GPT-6.2 Sol (max) **43.8%**, within **0.5 pts** of Astra at ~1/5 cost. [[references/sources/openai-gpt-6-2-release]]
- **bench-router state (2026-11-18)**: `profiles discover --merge` added 12 Codex profiles (`codex-gpt-6-2-astra-{low,medium,high,xhigh,max,ultra}` at `cost_tier=high` and `codex-gpt-6-2-sol-*` at `cost_tier=medium`). Automated `refresh` (`aa`, `arena`, `mg`, `or`, `tb_auto`) has not yet received upstream `6.2` rows, so routing currently proxies to `codex-gpt-6-astra-high` and `codex-gpt-6-1-sol-high`. ^[inferred]

## Independent Benchmarks & Specialized Configurations (checked 2026-11-26)

- **Artificial Analysis Intelligence Index (2026-11-24 snapshot)**:
  - **GPT-6.2 Astra**: **62.1** (`max` / top config; ~$4.00/task), **61.6** (`xhigh`), **60.1** (`high`), **57.0** (`medium`), **45.7** (`low`).
  - **GPT-6.2 Sol**: **57.3** (`max`), **55.7** (`xhigh`), **54.9** (`high`), **52.7** (`medium`), **40.6** (`low`).
  - **GPT-6.1 Terra**: **51.3** (`max`), **45.3** (`xhigh`), **42.4** (`high`), **38.2** (`medium`), **29.4** (`low`), **30.5** (non-reasoning).
- **Vals AI (checked 2026-11-26)**:
  - **GPT-6.2 Astra**: Vals Index **66.27% ± 1.00** (#8/43, $10.68/test, 52m 16s latency); **#1/29** Vals Science Index (**68.44% ± 2.13**), **#1/49** Terminal-Bench-Science (**71.43% ± 5.44**), **#1/8** Autoform-Hard (**87.50% ± 4.46**), **#1/11** Vibe Code Bench 1-100 v1.1 (**55.16% ± 5.78**), **#1/11** Robo-bench (**32.71%**), Terminal-Bench 4.0 **63.13% ± 1.34** (#5/70), Vibe Code Bench v1.1.1 **78.57% ± 3.47** (#6/51).
  - **GPT-6.2 Sol**: Vals Index **65.07% ± 0.98** (#9/43, $3.179/test, 41m 47s latency — within 1.2 pp of Astra at ~30% cost); Vibe Code Bench v1.1.1 **79.48% ± 3.66** (#4/51, ahead of Astra), Autoform-Hard **85.71% ± 4.72** (#3/8), Terminal-Bench 4.0 **60.61%** (#8/70), Terminal-Bench-Science **58.57% ± 5.93** (#4/49).
- **LMArena & Terminal-Bench Proxy (2026-11-24 snapshot)**: Astra (`max`) scores Arena Text **1466.7**, WebDev **1759.4** (HTML **1850.5**, React **1762.5**), TB 4.0 **62.12%**; Sol (`max`) scores Arena Text **1463.7** (Coding **1513.9**), WebDev **1755.1**, TB 4.0 **61.52%**.
- **Specialized models & domain configurations**: See [[references/sources/openai-specialized-models]] for `gpt-6-cyber` (restricted Daybreak Red), `astra-for-law-6-2`, and the Nov 24 Healthcare API configurations.

## Core Concepts

- [[concepts/responses-api-prefix-continuity]] — Prefix immutability, `instructions` placement after `input`, and ZDR encrypted reasoning replay in GPT-6.2.
- [[concepts/model-effort-selection]] — Separating model choice from reasoning effort tuning.

## Entities & Tools

- [[references/openai-gpt-6-2]] — Model IDs, pricing, effort levels, and benchmark summary for `gpt-6.2-astra` and `gpt-6.2-sol`.

## Contradictions & Open Questions

- **Upstream benchmark lag (resolved 2026-11-24/26)**: While 2026-11-18 snapshots lacked `gpt-6.2-astra` and `gpt-6.2-sol`, 2026-11-24 `aa`, `arena`, and `tb_auto` snapshots plus 2026-11-26 Vals AI evaluations now publish full scores for both models. (`mg` and `or` snapshots checked 2026-11-24 still carry `gpt-6-1-terra` rather than 6.2 rows.)
- **Agents' Last Exam figure for Sol**: Some secondary summaries conflate Astra's 78.3% with Sol (73.0%–78.3% across rubrics); verify directly against the System Card once accessible.
- **Direct blog/system-card fetch**: `openai.com/index/introducing-gpt-6-2-astra-sol` returned HTTP 403 and `deploymentsafety.openai.com/content/gpt-6-2-system-card` returned HTTP 404 to automated HTTP clients on 2026-11-18.

## Sources

- [[references/sources/openai-gpt-6-2-release]]
- [[references/sources/openai-gpt-6-2-prompting]]
- [[references/sources/openai-model-selection]]
- [[references/sources/openai-specialized-models]]
- [[_raw/_archived/2026-11-18-openai-model-selection]]
- [[_raw/_archived/2026-11-18-openai-latest-model-gpt-6-2]]
- [[_raw/_archived/2026-11-26-openai-model-selection]]
- [[_raw/_archived/2026-11-26-openai-codex-models]]
