---
title: >-
  Thinking block continuity and prefix immutability
category: concepts
tags: [concept, reasoning, adaptive-thinking, api-contracts, claude]
sources:
  - "[[references/sources/anthropic-fable-5-2-migration]]"
  - "[[references/sources/anthropic-claude-fable-and-mythos-5-2]]"
created: 2026-11-10T00:30:00Z
updated: 2026-11-10T00:30:00Z
summary: >-
  API constraint where thinking blocks require strict prefix immutability (no turn mutation) and are cryptographically or architecturally bound to the specific model version that generated them.
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.92
lifecycle: draft
lifecycle_changed: 2026-11-10
---

# Thinking block continuity and prefix immutability

In Claude Fable 5.2 and Claude Mythos 5.2, Anthropic enforces two architectural rules governing extended reasoning blocks (`thinking` blocks):

## 1. Prefix Immutability Check

Any downstream turn that appends to a conversation containing thinking blocks must preserve the entire preceding conversation history exactly as returned by the API:
- System prompts and tool specifications cannot change mid-conversation without the compaction beta header.
- Assistant message content (including tool calls and thinking blocks) cannot be edited, reordered, or truncated.
- Violating the prefix check invalidates the cached thinking state and results in an API error.

## 2. Model-Tied Continuity

Unlike regular text messages, thinking blocks are tied to the exact model checkpoint:
- Only **Claude Fable 5.2** and **Claude Mythos 5.2** can process prior Fable 5.2 thinking blocks.
- When an agent orchestrator switches models mid-task (e.g. from Fable 5.2 down to Opus 5.5 or Sonnet 5.5), thinking blocks must be stripped from previous assistant turns before submission.
