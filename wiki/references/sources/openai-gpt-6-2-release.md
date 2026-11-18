---
title: >-
  OpenAI: Introducing GPT-6.2 Astra and GPT-6.2 Sol
category: references
tags: [source, openai, astra, sol, benchmarks]
sources:
  - "url:https://openai.com/index/introducing-gpt-6-2-astra-sol"
  - "url:https://deploymentsafety.openai.com/content/gpt-6-2-system-card"
source_url: "https://openai.com/index/introducing-gpt-6-2-astra-sol"
created: 2026-11-18T08:00:21Z
updated: 2026-11-18T08:00:21Z
as_of: 2026-11-18
summary: >-
  Launch announcement, API pricing, rollout channels, safety thresholds, and benchmark highlights for GPT-6.2 Astra and GPT-6.2 Sol (released 2026-11-17).
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.57
lifecycle: draft
lifecycle_changed: 2026-11-18
tier: supporting
---

# OpenAI: Introducing GPT-6.2 Astra and GPT-6.2 Sol

OpenAI released **GPT-6.2 Astra** (`gpt-6.2-astra`) and **GPT-6.2 Sol** (`gpt-6.2-sol`) on **2026-11-17** across ChatGPT Work, Codex (app, CLI, IDE extensions), the OpenAI API, and cloud platforms (Azure, Amazon Bedrock). ^[extracted]

## Pricing & Service Tiers

- **GPT-6.2 Astra (`gpt-6.2-astra`)**: $8.00 / 1M input tokens, $0.40 / 1M cached input tokens (60% cached discount vs prior Astra), $40.00 / 1M output tokens (~20% lower input/output rates than GPT-6 Astra). Long-context tier (>272K tokens) scales to $16.00 input / $60.00 output. ^[extracted]
- **GPT-6.2 Sol (`gpt-6.2-sol`)**: $2.00 / 1M input tokens, $0.10 / 1M cached input tokens, $10.00 / 1M output tokens (unchanged from GPT-6.1 Sol). ^[extracted]
- **Ultrafast mode**: Introduced for higher-tier subscribers (Pro 500 for both models; Pro 200 starting with GPT-6.2 Sol) and US data residency only on the API; Standard, Fast, and Batch support US and EU data residency. ^[extracted]

## Reported Launch Benchmarks

- **Agents' Last Exam**: GPT-6.2 Astra reached **78.3%**, +5.2 pts over GPT-6 Astra at <1/3 the cost, and +5.5 pts ahead of Claude Fable 5.2. ^[extracted]
- **Terminal-Bench-Science 0.1**: GPT-6.2 Astra scored **+9 percentage points** higher than GPT-6 Astra at <1/3 the cost. ^[extracted]
- **Terminal-Bench 4.1**: GPT-6.2 Sol (max) scored **61.5% (±2.8%)** via Codex. ^[extracted]
- **FrontierCode 2.0**: GPT-6.2 Sol (max) scored **43.8%**, within **0.5 points** of GPT-6.2 Astra at ~1/5 the cost. ^[extracted]
- **Artificial Analysis Intelligence Index v5**: GPT-6.2 Astra (max) scored **62** (#2 globally behind Claude Fable 5.2 at 65; +5 pts over GPT-6 Astra); GPT-6.2 Sol scored **57** (+2 pts over GPT-6.1 Sol). ^[extracted]
- **Domain / Reasoning**: GPQA Diamond (97% on Astra), Vals Science Index, GDPval v2 (+6.2 pts), Harvey LAB-AA v1.1. ^[extracted]

## Safety & Preparedness

According to OpenAI's System Card, both models cross critical Preparedness Framework thresholds for cybersecurity capabilities (exploit development awareness) and biological/chemical reasoning, triggering tighter default safeguards and "Control Room" monitoring. ^[extracted]

## Limitations

Direct HTTP fetch of `openai.com/index/introducing-gpt-6-2-astra-sol` returned 403 Forbidden and `deploymentsafety.openai.com/content/gpt-6-2-system-card` returned 404; claims above are synthesized from search-indexed summaries of the official announcement and third-party benchmark trackers as of 2026-11-18. ^[inferred]

## Related

- [[references/openai-gpt-6-2]]
- [[references/sources/openai-model-selection]]
- [[references/sources/openai-gpt-6-2-prompting]]
- [[concepts/responses-api-prefix-continuity]]
- [[synthesis/Research: OpenAI GPT-6.2 Astra and GPT-6.2 Sol]]
