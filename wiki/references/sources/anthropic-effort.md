---
title: >-
  Anthropic effort is model-specific
category: references
tags: [source, reasoning, coding]
sources: ["url:https://platform.claude.com/docs/en/build-with-claude/effort"]
created: 2026-10-19T01:52:29Z
updated: 2026-10-24T12:45:00Z
as_of: 2026-10-24
summary: >-
  Claude effort affects response, tool-call, and thinking tokens; per-model recommendations, quoted verbatim, override the general level table.
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
  - "[[_raw/_archived/2026-10-24-anthropic-effort|2026-10-24-anthropic-effort]]"
---

# Anthropic effort is model-specific

Claude's effort setting influences text, tool-call, and thinking token use. The API field is `output_config.effort`; this does not establish the equivalent switch in an agent CLI.

> Most Claude models default to high effort, spending as many tokens as needed for excellent results; Claude Opus 5.5 and Claude Haiku 5.5 default to medium.

> The per-model recommendations that follow override this table where they differ.

## Per-model recommendations as of 2026-10-24 (verbatim)

| Model | Recommendation |
|---|---|
| Fable 5.1 | **Start with `high`, the default.** Step up to `xhigh` or `max` for the most capability-sensitive agentic and coding work, and step down to `medium` or `low` for routine or latency-sensitive work once your evals show quality holds. |
| Opus 5.5 | Claude Opus 5.5 supports all five effort levels, and `medium` is the default. Run an effort sweep on your own evals rather than carrying settings over from an earlier model, and set a large `max_tokens` at the higher levels |
| Sonnet 5.5 | Start with `high` unless your workload is agentic or latency-sensitive. For agentic coding and multistep tool use, start with `medium` for well-specified tasks and move to `high` for harder or longer ones. For chat and other latency-sensitive work, start with `medium` or `low`. Use `xhigh` or `max` only where your evals show a quality gain. |
| Haiku 5.5 | **Start with `medium`** for most work, including agentic coding. Use `low`, the cheapest and fastest level, for chat, short tool tasks, and simple, high-volume requests. Use `high` for knowledge work, longer agent tasks, and strict instruction following. Use `xhigh` or `max` only where your evals show a quality gain, and compare them with Claude Sonnet 5.5 on performance, cost, and speed. |

For Sonnet 5.5 and Haiku 5.5, `xhigh` and `max` are conditional on measured quality gains. For Fable 5.1 they are a step up from the `high` starting point.

## Limits

Model-specific recommendations take precedence over the general table. Support and defaults vary by model/version. Higher effort needs sufficient output budget, which also includes thinking.

> In long agent prompts, the model is more likely to skip a search, stop early, or skip a check at `low`.

(Haiku 5.5 section.)

## Related

- [[references/sources/anthropic-model-selection]]
- [[concepts/model-effort-selection]]
- [[concepts/facets/agent_signal]]

## Sources

- [[_raw/_archived/2026-10-24-anthropic-effort]] — verbatim per-model excerpts.
- [[_raw/_archived/2026-10-19-anthropic-effort]] — earlier bounded excerpt and canonical origin.
