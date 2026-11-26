---
title: >-
  Vendor-guided model selection — research map
category: synthesis
tags: [agentic, reasoning, coding]
sources:
  - "url:https://developers.openai.com/api/docs/guides/model-selection"
  - "url:https://platform.claude.com/docs/en/about-claude/models/choosing-a-model"
  - "url:https://platform.claude.com/docs/en/build-with-claude/effort"
  - "url:https://ai.google.dev/gemini-api/docs/models"
  - "url:https://ai.google.dev/gemini-api/docs/thinking"
  - "conversation:2026-10-19"
  - "conversation:2026-10-22"
created: 2026-10-19T01:52:29Z
updated: 2026-11-26T00:32:19Z
as_of: 2026-11-26
summary: >-
  Entry point for official vendor guidance, the current bench-router policy audit, and a proposed approach to selecting model/effort configurations.
provenance:
  extracted: 0.6
  inferred: 0.4
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: core
snapshots:
  - "[[_raw/_archived/2026-10-19-openai-model-selection|2026-10-19-openai-model-selection]]"
  - "[[_raw/_archived/2026-10-19-anthropic-model-selection|2026-10-19-anthropic-model-selection]]"
  - "[[_raw/_archived/2026-10-19-anthropic-effort|2026-10-19-anthropic-effort]]"
  - "[[_raw/_archived/2026-10-19-google-gemini-models|2026-10-19-google-gemini-models]]"
  - "[[_raw/_archived/2026-10-19-google-gemini-thinking|2026-10-19-google-gemini-thinking]]"
  - "[[_raw/_archived/2026-10-19-routing-research-context|2026-10-19-routing-research-context]]"
  - "[[_raw/_archived/2026-11-13-anthropic-fable-5-2-prompting|2026-11-13-anthropic-fable-5-2-prompting]]"
  - "[[_raw/_archived/2026-11-13-google-gemini-thinking|2026-11-13-google-gemini-thinking]]"
  - "[[_raw/_archived/2026-11-13-openai-model-selection|2026-11-13-openai-model-selection]]"
  - "[[_raw/_archived/2026-11-18-openai-model-selection|2026-11-18-openai-model-selection]]"
  - "[[_raw/_archived/2026-11-18-openai-latest-model-gpt-6-2|2026-11-18-openai-latest-model-gpt-6-2]]"
  - "[[_raw/_archived/2026-11-26-google-gemini-choosing-a-model|2026-11-26-google-gemini-choosing-a-model]]"
  - "[[_raw/_archived/2026-11-26-google-gemini-thinking|2026-11-26-google-gemini-thinking]]"
  - "[[_raw/_archived/2026-11-26-anthropic-effort|2026-11-26-anthropic-effort]]"
  - "[[_raw/_archived/2026-11-26-anthropic-model-selection|2026-11-26-anthropic-model-selection]]"
  - "[[_raw/_archived/2026-11-26-openai-model-selection|2026-11-26-openai-model-selection]]"
  - "[[_raw/_archived/2026-11-26-openai-codex-models|2026-11-26-openai-codex-models]]"
---

# Vendor-guided model selection — research map

Official guidance supplies starting recommendations. The routing audit and original proposal retain their 2026-10-19 evidence scope. The project overview links current policy documentation; a separate multi-agent proposal covers pattern selection and workflow evidence.

## Read by question

| Question | Owner page |
|---|---|
| Which official OpenAI model/effort combinations were found? | [[references/sources/openai-model-selection]] |
| How does Anthropic choose a starting model? | [[references/sources/anthropic-model-selection]] |
| How does Claude effort depend on the model? | [[references/sources/anthropic-effort]] |
| How does Google position Gemini models? | [[references/sources/google-gemini-models]] |
| Which thinking level fits a Gemini workload? | [[references/sources/google-gemini-thinking]] |
| Why separate model and effort decisions? | [[concepts/model-effort-selection]] |
| What does bench-router currently calculate? | [[projects/bench-router/synthesis/routing-selection-audit]] |
| How could the findings inform routing? | [[projects/bench-router/synthesis/vendor-guided-routing-proposal]] |
| When should collaboration patterns be selected, and which benchmark evidence matters? | [[projects/bench-router/synthesis/multi-agent-pattern-selection]] |

## Findings

The inspected OpenAI guide offers workload/configuration examples. Anthropic separates model choice from model-specific effort tuning. Google documents model roles and workload-based thinking guidance. None of these inspected pages supplies a calibrated formula for comparing all three providers.

Vendor recommendations can narrow plausible configurations; workflow evidence is still needed to establish that a candidate meets a project's requirements. Treating recommendations as priors preserves their usefulness without presenting them as measured cross-vendor superiority. ^[inferred]

## Evidence boundaries

| Evidence | Supported conclusion | Unsupported shortcut |
|---|---|---|
| Official recommendation | A vendor recommends a configuration for a workload | It must beat another provider |
| Public benchmark | Performance under recorded evaluation conditions | Success probability for this repository task |
| Code inspection | The current policy uses particular inputs and constants | The constants are empirically optimal |
| Proposed routing procedure | A reviewable design derived from these findings | The procedure is already implemented or validated |

These boundaries are research interpretations. ^[inferred]

## Open questions

- Which model/effort combinations are actually available in each configured CLI?
- What quality criterion and representative workload should guide selection?
- How should unresolved candidates be compared when task-specific measurements are missing?
- Who will maintain source dates and review changed vendor recommendations?

## Related

- [[projects/bench-router/bench-router]]
- [[concepts/facets/task]]
- [[concepts/facets/difficulty]]
- [[concepts/facets/agent_signal]]

## Current vendor calibration (2026-11-26)

Google's official model-selection and thinking guides (`aistudio.google.com/docs/choosing-a-model.md`, `thinking.md`, `models.md`) now position **Gemini 4 Hydrogen** (`high` default; `low`/`medium`/`high`/`xhigh`) as the everyday default, **Gemini 4 Neon** (released 2026-11-18; `high` default; `low`/`medium`/`high`/`xhigh`) between Hydrogen and Carbon for complex high-frequency engineering, and **Gemini 4 Carbon** (`medium` default; `low`/`medium`/`high`; promo $2/$10 thru 2026-11-30, $4/$20 from 2026-12-01) for the hardest architecture, debugging, and security work. `gemini-4-argon` remains in the catalog (`medium` default; `low`/`medium`/`high`). **Gemini 4 Helium** is not officially released (404 on official docs; unconfirmed rumors only). ^[extracted]

See [[references/sources/google-gemini-choosing-a-model]], [[references/sources/google-gemini-thinking]], [[references/sources/google-gemini-models]], [[synthesis/Research: Google Gemini 4 Neon]], and [[synthesis/Research: Google Gemini 4 Lineup and Benchmark Status (Nov 2026)]].

For **Anthropic**, the full `.md` effort guide (`platform.claude.com/docs/en/build-with-claude/effort.md`) restores per-model tabs across all five levels: **Fable 5.2** and **Mythos 5.2** default to `high` (always-on adaptive thinking; reserve `max` for ceiling checks), **Opus 5.5** defaults to `medium` (always-on adaptive thinking; `disabled` returns HTTP 400), **Sonnet 5.5** defaults to `high` (uses `between_tools` rather than `disabled`, 400 at `xhigh`/`max`), and **Haiku 5.5** defaults to `medium` (`disabled` allowed at `high` or below; `low` skips checks in long agent prompts). All five support cache-preserving per-message `output_config.effort` changes under adaptive thinking. No Claude 5.6 or Fable 5.3 has been released. ^[extracted]

For **OpenAI**, `model-selection.md` explicitly recommends starting most API workflows with **GPT-6.2 Sol** at `medium` reasoning effort, and `codex/models.md` distinguishes **Max** (longer single-task reasoning) from **Ultra** (parallel subagents for decomposable work; unsupported on **GPT-6 Luna**). Released specialized/domain offerings absent from general tables include **GPT-6 Cyber** (`gpt-6-cyber`, restricted Daybreak Red), **Astra for Law 6.2** (`astra-for-law-6-2`), and Nov 24 **Healthcare** API configurations. ^[extracted]

See [[references/sources/anthropic-effort]], [[references/sources/anthropic-model-selection]], [[references/sources/openai-model-selection]], [[references/sources/openai-specialized-models]], and [[synthesis/Research: Anthropic and OpenAI Unreflected Models and Benchmarks (Nov 2026)]].

## Current vendor calibration (2026-11-18)

OpenAI's 2026-11-17 release of GPT-6.2 Astra and GPT-6.2 Sol updates its model-selection table to place `GPT-6.2 Astra` (`low`, `medium`, `xhigh`) and `GPT-6.2 Sol` (`medium`, `xhigh`) ahead of `GPT-6.1 Terra` (`medium`) and `GPT-6 Luna` across all six work categories, with `medium` as the recommended integration starting effort and `none`/`minimal` unsupported on GPT-6.2. ^[extracted]

See [[references/sources/openai-model-selection]], [[references/sources/openai-gpt-6-2-prompting]], and [[synthesis/Research: OpenAI GPT-6.2 Astra and GPT-6.2 Sol]].

## Current vendor calibration (2026-11-13)

Fable 5.2 starts at high, with xhigh conditional on measured gains and max reserved for ceiling measurement or rare unconstrained work. Gemini 4 Hydrogen starts at high for complex work and reserves xhigh for cases where high falls short. Terra has a published workload role but no fixed effort recommendation in the new capture. Preserve role-only guidance rather than inventing a vendor-endorsed effort. ^[inferred]

See [[references/sources/anthropic-prompting-fable-5-2]], [[references/sources/google-gemini-thinking]] and [[references/sources/openai-model-selection]].

## Sources

- [[_raw/_archived/2026-10-19-openai-model-selection]]
- [[_raw/_archived/2026-10-19-anthropic-model-selection]]
- [[_raw/_archived/2026-10-19-anthropic-effort]]
- [[_raw/_archived/2026-10-19-google-gemini-models]]
- [[_raw/_archived/2026-10-19-google-gemini-thinking]]
- [[_raw/_archived/2026-10-19-routing-research-context]]

Source captures contain bounded excerpts and origin links, not complete copies of the official documents.

- [[_raw/_archived/2026-11-13-anthropic-fable-5-2-prompting]]

- [[_raw/_archived/2026-11-13-google-gemini-thinking]]

- [[_raw/_archived/2026-11-13-openai-model-selection]]
- [[_raw/_archived/2026-11-26-google-gemini-choosing-a-model]]
- [[_raw/_archived/2026-11-26-google-gemini-thinking]]
- [[_raw/_archived/2026-11-26-anthropic-effort]]
- [[_raw/_archived/2026-11-26-anthropic-model-selection]]
- [[_raw/_archived/2026-11-26-openai-model-selection]]
- [[_raw/_archived/2026-11-26-openai-codex-models]]
