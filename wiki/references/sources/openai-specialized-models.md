---
title: >-
  OpenAI specialized models and domain configurations (Cyber, Law, Healthcare)
category: references
tags: [source, openai, gpt-6, cyber, healthcare, legal]
sources:
  - "url:https://developers.openai.com/api/docs/models/gpt-6-cyber.md"
  - "url:https://developers.openai.com/api/docs/models/all.md"
  - "url:https://openai.com/index/introducing-gpt-6-cyber"
created: 2026-11-26T00:49:17Z
updated: 2026-11-26T00:49:17Z
as_of: 2026-11-26
summary: >-
  OpenAI restricted and domain-specific models/configs absent from general selection tables: GPT-6 Cyber (Daybreak Red), Astra for Law 6.2, and Nov 24 Healthcare API configurations.
provenance:
  extracted: 0.85
  inferred: 0.15
  ambiguous: 0.0
base_confidence: 0.67
lifecycle: draft
lifecycle_changed: 2026-11-26
tier: supporting
---

# OpenAI specialized models and domain configurations

Beyond the four featured general-purpose models (`gpt-6.2-astra`, `gpt-6.2-sol`, `gpt-6.1-terra`, `gpt-6-luna`), OpenAI ships restricted cybersecurity models and vertical enterprise configurations that were not reflected in the general model-selection wiki pages. ^[extracted]

## GPT-6 Cyber (`gpt-6-cyber`)

- **Release & purpose**: Released **2026-11-05** (`developers.openai.com/api/docs/models/gpt-6-cyber.md`) for authorized vulnerability research, exploit reproduction, and fix verification. Listed alongside earlier `gpt-5.6-cyber` (while `gpt-daybreak-red-latest` and `gpt-daybreak-blue-latest` are marked deprecated in `models/all.md`). ^[extracted]
- **Access & safety tier**: Requires **Daybreak Red** organization approval through an OpenAI account team; rated *Critical* under OpenAI's Preparedness Framework. ^[extracted]
- **Benchmarks**: Reported at **~48.5%** on ExploitGym in secondary technical coverage. ^[inferred]

## Astra for Law 6.2 (`astra-for-law-6-2`)

- **Purpose**: Legal-vertical configuration built on the GPT-6.2 Astra backbone, integrating a legal search index spanning 230M+ URLs (U.S. case law, statutes, regulations, CourtListener / Free Law Project) and structured legal drafting guidance. ^[extracted]
- **Benchmark tracking**: Appears as slug `astra-for-law-6-2` in the 2026-11-24 Artificial Analysis (`aa`) snapshot, currently with `null` aggregate Intelligence/Coding Index values (`unmatched_sample` in `bench-router status`). ^[extracted]

## Healthcare Model Configurations (2026-11-24)

- **Purpose**: Announced **2026-11-24** for the OpenAI Responses API, pairing Astra and Sol with clinical harnesses that query a dedicated medical evidence index with structured citations (alongside ChatGPT for Healthcare workflows). ^[extracted]
- **API documentation status**: As of 2026-11-26, standalone public model pages (`developers.openai.com/api/docs/models/gpt-6.2-astra-healthcare.md` and `/api/docs/guides/healthcare.md`) return HTTP 404. ^[extracted]

## Related

- [[references/openai-gpt-6-2]]
- [[references/sources/openai-model-selection]]
- [[synthesis/Research: OpenAI GPT-6.2 Astra and GPT-6.2 Sol]]
- [[synthesis/Research: Anthropic and OpenAI Unreflected Models and Benchmarks (Nov 2026)]]

## Sources

- `https://developers.openai.com/api/docs/models/gpt-6-cyber.md` — Official API model specification (checked 2026-11-26).
- `https://developers.openai.com/api/docs/models/all.md` — Full OpenAI API model catalog listing `gpt-6-cyber`, `gpt-5.6-cyber`, and deprecated Daybreak aliases (checked 2026-11-26).
- `https://platform.claude.com` / `bench-router status` (2026-11-24 AA snapshot) — `astra-for-law-6-2` unmatched slug record.
