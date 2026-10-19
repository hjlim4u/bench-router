---
title: >-
  Anthropic effort is model-specific
category: references
tags: [source, reasoning, coding]
sources: ["url:https://platform.claude.com/docs/en/build-with-claude/effort"]
created: 2026-10-19T01:52:29Z
updated: 2026-10-19T01:52:29Z
as_of: 2026-10-19
summary: >-
  Claude effort affects response, tool-call, and thinking tokens; model-specific recommendations override general level descriptions.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-anthropic-effort|2026-10-19-anthropic-effort]]"
---

# Anthropic effort is model-specific

Claude's effort setting influences text, tool-call, and thinking token use. The API field is `output_config.effort`; this does not establish the equivalent switch in an agent CLI.

## Documented examples as of 2026-10-19

| Model | Starting guidance, paraphrased |
|---|---|
| Sonnet 5.5 | Try `medium` for clearly specified coding/tool workflows; raise to `high` for harder or longer work. Use `xhigh/max` when evaluations show improvement. |
| Opus 5.5 | Begin with its `medium` default and evaluate effort settings afresh. |
| Haiku 5.5 | Begin with `medium` for most tasks; `low` suits short, simple, latency-sensitive work. |
| Fable 5.1 | Start at `high`; adjust upward for demanding work or downward when quality holds. |

## Limits

Model-specific recommendations take precedence over the general table. Support and defaults vary by model/version. Higher effort needs sufficient output budget, which also includes thinking. Low effort can omit useful steps in long agent workflows.

## Related

- [[references/sources/anthropic-model-selection]]
- [[concepts/model-effort-selection]]
- [[concepts/facets/agent_signal]]

## Sources

- [[_raw/_archived/2026-10-19-anthropic-effort]] — bounded original excerpt and canonical origin.
