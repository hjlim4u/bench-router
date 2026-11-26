---
title: >-
  Research: Anthropic and OpenAI Unreflected Models and Benchmarks (Nov 2026)
category: synthesis
tags: [anthropic, openai, claude, gpt-6.2, effort, benchmarks, research]
sources:
  - "url:https://platform.claude.com/docs/en/build-with-claude/effort.md"
  - "url:https://platform.claude.com/docs/en/about-claude/models/choosing-a-model.md"
  - "url:https://platform.claude.com/docs/en/about-claude/models/overview.md"
  - "url:https://developers.openai.com/api/docs/guides/model-selection.md"
  - "url:https://developers.openai.com/codex/models.md"
  - "url:https://developers.openai.com/api/docs/models/gpt-6-cyber.md"
  - "url:https://www.vals.ai/models/anthropic_claude-fable-5-2"
  - "url:https://www.vals.ai/models/openai_gpt-6.2-astra"
  - "url:https://www.vals.ai/models/openai_gpt-6.2-sol"
created: 2026-11-26T00:49:17Z
updated: 2026-11-26T00:49:17Z
summary: >-
  Audit as of 2026-11-26 of Anthropic and OpenAI models, effort guidelines, and AA/Vals/Arena benchmarks missing from prior wiki notes.
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.92
lifecycle: draft
lifecycle_changed: 2026-11-26
---

# Research: Anthropic and OpenAI Unreflected Models and Benchmarks (Nov 2026)

## Overview

A 2026-11-26 audit of official Anthropic and OpenAI documentation, the 2026-11-24 `bench-router` benchmark snapshots (`aa`, `arena`, `tb_auto`), and live Vals AI model pages found **no unreleased general-purpose Anthropic models** beyond Fable/Mythos 5.2 (2026-11-09), but surfaced **three OpenAI specialized offerings** (`gpt-6-cyber`, `astra-for-law-6-2`, and Nov 24 Healthcare API configurations), **recovered Anthropic per-model effort tabs** (previously omitted by defuddle on 2026-11-13), **Codex Max/Ultra & GPT-6.2 Sol API default guidance**, and **complete independent benchmarks** resolving the 2026-11-18 GPT-6.2 upstream lag.

## Key Findings

- **Unreflected Released Models & Domain Configs**:
  - **OpenAI**: `gpt-6-cyber` (released 2026-11-05; Daybreak Red gated; Critical Preparedness tier; ~48.5% ExploitGym), `astra-for-law-6-2` (230M+ legal URL index; present in AA snapshot with null aggregate scores), and Healthcare API configurations (announced 2026-11-24 for Astra/Sol). [[references/sources/openai-specialized-models]]
  - **Anthropic**: Public lineup remains `claude-fable-5-2` ($8/$40), `claude-opus-5-5` ($4/$20, default starting point), `claude-sonnet-5-5` ($2/$10), and `claude-haiku-5-5` ($0.10/$0.50), plus restricted `claude-mythos-5-2`. Rumors of Claude 5.6 or Fable 5.3 remain unconfirmed stealth-routing reports. [[references/sources/anthropic-model-selection]]
- **Newly Reflected Official Effort & Selection Guidance**:
  - **Anthropic `.md` effort tabs**: Fable/Mythos 5.2 (`high` default; adaptive thinking always on), Opus 5.5 (`medium` default; `thinking: disabled` returns 400), Sonnet 5.5 (`high` default; `between_tools` allowed only at `low`/`medium`/`high`), Haiku 5.5 (`medium` default; `disabled` allowed at `high` or below; `low` skips checks in long prompts), plus cache-preserving per-message `output_config.effort` on all five models. [[references/sources/anthropic-effort]]
  - **OpenAI API & Codex**: API guide explicitly sets **GPT-6.2 Sol at `medium`** as the default for most API workflows; Codex `models.md` defines **Max** (longer single-task reasoning) vs **Ultra** (parallel subagents; unsupported on `GPT-6 Luna`) and records `GPT-5.3-Codex-Spark` (2026-09-14) and `GPT-5.5` ChatGPT-auth Codex (2026-10-14) retirements. [[references/sources/openai-model-selection]]
- **Newly Reflected Independent Benchmarks (AA 2026-11-24 / Arena 2026-11-24 / Vals 2026-11-26)**:

| Model | AA Intelligence Index (`low`/`med`/`high`/`xhigh`/`max`) | Vals Index (Rank, Cost/Test) | Notable #1 / Top Vals & Other Scores | Arena Text / WebDev / TB 4.0 |
|---|---|---|---|---|
| **Claude Fable 5.2** | `53.9` / `56.4` / `61.8` / `62.2` / **`64.6`** (~$26.54/task) | **70.06% ± 1.02** (#1/43, $17.94) | #1 TB 4.0, #1 Vibe Code v1.1.1 (83.52%), #1 ProofBench (100%), #1 Finance Agent v2.1 (69.47%) | Text **1502.2** (Coding 1525.4) / TB 4.0 **65.76%** |
| **Claude Opus 5.5** | `34.8` / `48.2` / `51.8` / `57.4` / **`59.1`** | — | MG: ARC-AGI-2 `high` 93.3%, DeepSWE 74.2%, TB 2.1 87.64% | — |
| **Claude Sonnet 5.5** | `25.6` / `30.8` / `41.5` / `49.9` / **`54.5`** | ~69.45% (search summary) | MG: DeepSWE 71.0%, TB 4.0 `max` 64.14% | — |
| **Claude Haiku 5.5** | `18.6` / `24.6` / `29.9` / `34.6` / **`36.5`** | — | MG: OSWorld 2.1 offline 72.4%, LiveBench `xhigh` 72.07% | — |
| **GPT-6.2 Astra** | `45.7` / `57.0` / `60.1` / `61.6` / **`62.1`** (~$4.00/task) | **66.27% ± 1.00** (#8/43, $10.68) | #1 Science Index (68.44%), #1 TB-Science (71.43%), #1 Autoform-Hard (87.50%), #1 Robo-bench (32.71%) | Text **1466.7** / WebDev **1759.4** / TB 4.0 **62.12%** |
| **GPT-6.2 Sol** | `40.6` / `52.7` / `54.9` / `55.7` / **`57.3`** | **65.07% ± 0.98** (#9/43, $3.18) | Vibe Code v1.1.1 **79.48%** (#4/51, ahead of Astra), TB 4.0 60.61% (#8/70) | Text **1463.7** (Coding 1513.9) / WebDev **1755.1** / TB 4.0 **61.52%** |
| **GPT-6.1 Terra** | `29.4` / `38.2` / `42.4` / `45.3` / **`51.3`** (non-reas. `30.5`) | — | OR: GPQA Diamond 91.08%, τ-bench Airline 68.44% | — |

## Core Concepts

- [[concepts/model-effort-selection]] — Matching model tier and effort level across vendor guidelines and independent benchmarks.
- [[synthesis/vendor-guided-model-selection]] — Unified cross-vendor official calibration map.

## Entities & Tools

- [[references/openai-gpt-6-2]] — Core `gpt-6.2-astra` and `gpt-6.2-sol` specifications.
- [[references/sources/openai-specialized-models]] — `gpt-6-cyber`, `astra-for-law-6-2`, and Healthcare configurations.

## Contradictions & Open Questions

- **Vals Index snapshot drift**: On 2026-11-19 (`vals-ai-gemini-4-neon.md`), Gemini 4 Neon showed 70.87% (#2/42), whereas on 2026-11-26 the Claude Fable 5.2 page lists Fable 5.2 at **70.06% (#1/43)** (and search summaries note 71.31% in newer snapshots). Board additions or weight updates shift rankings slightly between snapshots.
- **`astra-for-law-6-2` null metrics**: Present in the 2026-11-24 AA snapshot with `null` Intelligence/Coding scores.
- **Healthcare docs unavailable**: OpenAI's Nov 24 Healthcare API configurations are announced on openai.com but lack public `/api/docs/models/*.md` pages (HTTP 404 on `gpt-6.2-astra-healthcare.md`).
- **Anthropic 5.6 rumors**: Unconfirmed stealth-routing speculation in Claude Code; no official Anthropic release or model ID exists.

## Sources

- [[references/sources/anthropic-effort]]
- [[references/sources/anthropic-model-selection]]
- [[references/sources/openai-model-selection]]
- [[references/sources/openai-specialized-models]]
- [[synthesis/Research: Claude Fable 5.2 and Mythos 5.2]]
- [[synthesis/Research: OpenAI GPT-6.2 Astra and GPT-6.2 Sol]]
- [[_raw/_archived/2026-11-26-anthropic-effort]]
- [[_raw/_archived/2026-11-26-anthropic-model-selection]]
- [[_raw/_archived/2026-11-26-openai-model-selection]]
- [[_raw/_archived/2026-11-26-openai-codex-models]]
