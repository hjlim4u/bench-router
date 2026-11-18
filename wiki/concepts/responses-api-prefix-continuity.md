---
title: >-
  Responses API prefix continuity and prompt caching (GPT-6.2)
category: concepts
tags: [concept, openai, responses-api, prompt-caching, reasoning]
sources:
  - "url:https://developers.openai.com/api/docs/guides/latest-model"
  - "url:https://developers.openai.com/api/docs/guides/model-selection"
created: 2026-11-18T08:00:21Z
updated: 2026-11-18T08:00:21Z
summary: >-
  How GPT-6.2 Responses API preserves reasoning items and prompt cache hits by keeping conversation prefixes immutable and placing stable instructions in a leading developer message.
provenance:
  extracted: 0.85
  inferred: 0.15
  ambiguous: 0.0
base_confidence: 0.50
lifecycle: draft
lifecycle_changed: 2026-11-18
---

# Responses API prefix continuity and prompt caching (GPT-6.2)

Starting with **GPT-6.2**, the OpenAI Responses API enforces strict prefix immutability to preserve both internal reasoning state and prompt-cache eligibility across multi-turn agentic loops. ^[extracted]

## Key Mechanics

1. **Prefix edits drop reasoning items**: Editing earlier conversation history (e.g., mutating prior `developer` messages or tool calls), changing models (including downgrades), or changing end-user/org identifiers causes the Responses API to drop reasoning items and invalidate prompt caching for subsequent turns. When reasoning items are dropped, answer quality can decline and token usage rises as the model repeats earlier work. ^[extracted]
2. **Top-level `instructions` move after `input`**: Unlike earlier models, GPT-6.2 appends top-level `instructions` *after* `input`. Stable system/developer instructions must be placed in a `developer` message as the first item of `input` to qualify for prefix caching. ^[extracted]
3. **ZDR encrypted reasoning replay**: With Zero Data Retention (`store: false`), callers must pass prior output items back in order, including encrypted reasoning items, to maintain reasoning continuity. ^[extracted]

## Implications for Agent Harnesses

Agent orchestrators and routers should avoid mid-session model downgrades or dynamic system-prompt mutations in the prefix when using `gpt-6.2-astra` or `gpt-6.2-sol`, and should configure `prompt_cache_options.ttl = "30m"` when migrating from GPT-5.5 or earlier. ^[inferred]

## Related

- [[references/sources/openai-gpt-6-2-prompting]]
- [[references/sources/openai-gpt-6-2-release]]
- [[concepts/thinking-block-continuity]]
- [[references/openai-gpt-6-2]]
