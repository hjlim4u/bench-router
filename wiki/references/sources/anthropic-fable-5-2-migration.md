---
title: >-
  Claude Fable 5.2 and Claude Mythos 5.2 migration guide
category: references
tags: [source, anthropic, fable, mythos, migration, breaking-changes]
sources:
  - "url:https://platform.claude.com/docs/en/models/fable-5-2/migration-guide"
  - "url:https://platform.claude.com/docs/en/models/fable-5-2/whats-new-fable-5-2"
source_url: "https://platform.claude.com/docs/en/models/fable-5-2/migration-guide"
created: 2026-11-10T00:30:00Z
updated: 2026-11-10T00:30:00Z
as_of: 2026-11-10
summary: >-
  Official migration guide for Claude Fable 5.2 and Mythos 5.2: prefix check rules, model-tied thinking blocks, deprecated computer use tools, and advisor pairing restrictions.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-11-10
tier: primary
snapshots:
  - "[[_raw/_archived/2026-11-10-anthropic-whats-new-fable-5-2|2026-11-10-anthropic-whats-new-fable-5-2]]"
  - "[[_raw/_archived/2026-11-10-anthropic-fable-5-2-migration-guide|2026-11-10-anthropic-fable-5-2-migration-guide]]"
---

# Claude Fable 5.2 and Claude Mythos 5.2 migration guide

The official Anthropic migration guide outlines the breaking changes and requirements when upgrading to Claude Fable 5.2 or Claude Mythos 5.2.

## Breaking Changes from Fable 5.1

1. **Prefix Check Applies to Every Account:**
   - Any modification, truncation, or reordering of prior conversation turns invalidates existing thinking blocks and throws an API error. Assistant turns must be returned verbatim.
2. **Thinking Blocks are Model-Tied:**
   - Thinking blocks produced by Claude Fable 5.2 can only be read and resumed by Claude Fable 5.2 or Claude Mythos 5.2. Cross-model handoffs must drop thinking blocks before continuing on Opus or Sonnet.
3. **Computer Use Tool Deprecation:**
   - The older `computer_20251124` tool is replaced by `computer_toolset_20260801`. Calling the earlier tool throws an error.
4. **Advisor Tool Compatibility Constraint:**
   - A Claude Fable 5.2 main model cannot be paired with an Opus or Sonnet advisor. An advisor for Fable 5.2 must also be Fable 5.2 or Mythos 5.2.
5. **Adaptive Thinking Configuration:**
   - Adaptive thinking is always enabled. Specifying `budget_tokens` or attempting to set `thinking: {"type": "disabled"}` produces an HTTP 400 validation error.

## Claude Code Automated Migration

```bash
/claude-api migrate this project to claude-fable-5-2
```

## Sources

- [[_raw/_archived/2026-11-10-anthropic-fable-5-2-migration-guide]]
- [[_raw/_archived/2026-11-10-anthropic-whats-new-fable-5-2]]
