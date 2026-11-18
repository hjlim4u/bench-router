---
title: >-
  OpenAI GPT-6.2 Astra and GPT-6.2 Sol
category: entities
tags: [entity, openai, gpt-6.2, astra, sol, codex]
sources:
  - "url:https://openai.com/index/introducing-gpt-6-2-astra-sol"
  - "url:https://developers.openai.com/api/docs/guides/model-selection"
  - "url:https://developers.openai.com/api/docs/guides/latest-model"
created: 2026-11-18T08:00:21Z
updated: 2026-11-18T08:00:21Z
summary: >-
  OpenAI's November 2026 flagship (gpt-6.2-astra) and cost-efficient (gpt-6.2-sol) reasoning models for agentic coding, scientific workflows, and professional deliverables.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.0
base_confidence: 0.65
lifecycle: draft
lifecycle_changed: 2026-11-18
---

# OpenAI GPT-6.2 Astra and GPT-6.2 Sol

Released **2026-11-17**, **GPT-6.2 Astra** (`gpt-6.2-astra`) and **GPT-6.2 Sol** (`gpt-6.2-sol`) form OpenAI's primary frontier and everyday-efficiency tier across ChatGPT Work, Codex, and the OpenAI API. ^[extracted]

## Model Profiles

| Model ID | Role | API Pricing (Input / Cached / Output per 1M) | Supported Effort (`medium` default) |
|---|---|---|---|
| `gpt-6.2-astra` | Complex professional work, scientific analysis, 3D/design, open-ended research | $8.00 / $0.40 / $40.00 | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` (`none`/`minimal` rejected) |
| `gpt-6.2-sol` | Efficient everyday coding, document drafting, multistep app workflows | $2.00 / $0.10 / $10.00 | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` (`none`/`minimal` rejected) |

## Benchmark Snapshot (2026-11-18)

- **AA Intelligence Index v5**: Astra **62** (#2 overall), Sol **57**. ^[extracted]
- **Agents' Last Exam**: Astra **78.3%** (+5.2 pts vs GPT-6 Astra, +5.5 pts vs Claude Fable 5.2). ^[extracted]
- **Terminal-Bench-Science 0.1**: Astra **+9 pp** vs GPT-6 Astra. ^[extracted]
- **Terminal-Bench 4.1 (Codex)**: Sol (max) **61.5% (±2.8%)**. ^[extracted]
- **FrontierCode 2.0**: Sol (max) **43.8%**, within 0.5 pts of Astra at ~1/5 cost. ^[extracted]

## Related

- [[references/sources/openai-gpt-6-2-release]]
- [[references/sources/openai-gpt-6-2-prompting]]
- [[references/sources/openai-model-selection]]
- [[concepts/responses-api-prefix-continuity]]
- [[synthesis/Research: OpenAI GPT-6.2 Astra and GPT-6.2 Sol]]
