---
title: >-
  Anthropic effort — bounded source capture (2026-10-24)
source: "url:https://platform.claude.com/docs/en/build-with-claude/effort"
captured_at: 2026-10-24T12:45:00Z
capture_kind: bounded-excerpt
immutable: true
---

# Claude effort

Origin: [Effort — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/effort).

This record preserves verbatim excerpts from the fetched official page on 2026-10-24. It is not a complete copy; recommendations for older models (Fable 5, Opus 5, Opus 4.8, Opus 4.7, Sonnet 5, Sonnet 4.6) and API details are omitted. The remote page remains mutable. The earlier capture [[_raw/_archived/2026-10-19-anthropic-effort]] stays unchanged; its excerpt still appears on the page.

## Verbatim excerpts — How effort works

> Most Claude models default to high effort, spending as many tokens as needed for excellent results; Claude Opus 5.5 and Claude Haiku 5.5 default to medium.

> The per-model recommendations that follow override this table where they differ.

## Verbatim excerpt — Recommended effort levels for Claude Fable 5.1

> Claude Fable 5.1 supports all five effort levels. **Start with `high`, the default.** Step up to `xhigh` or `max` for the most capability-sensitive agentic and coding work, and step down to `medium` or `low` for routine or latency-sensitive work once your evals show quality holds.

## Verbatim excerpt — Recommended effort levels for Claude Opus 5.5

> Claude Opus 5.5 supports all five effort levels, and `medium` is the default (Claude Opus 5 and earlier Opus models default to `high`, so a request that omits `effort` runs one level lower than it did on Claude Opus 5).

> Run an effort sweep on your own evals rather than carrying settings over from an earlier model, and set a large `max_tokens` at the higher levels: it's a hard limit on total output (thinking plus response text).

## Verbatim excerpt — Recommended effort levels for Claude Sonnet 5.5

> Claude Sonnet 5.5 supports all five effort levels, and `high` is the default on the Claude API. Its levels are recalibrated, so a level doesn't produce the same amount of thinking as the same level on Claude Sonnet 5. Run a fresh effort sweep on your evals rather than carrying over the setting you used on Claude Sonnet 5. Start with `high` unless your workload is agentic or latency-sensitive. For agentic coding and multistep tool use, start with `medium` for well-specified tasks and move to `high` for harder or longer ones. For chat and other latency-sensitive work, start with `medium` or `low`. Use `xhigh` or `max` only where your evals show a quality gain.

## Verbatim excerpt — Recommended effort levels for Claude Haiku 5.5

> Claude Haiku 5.5 supports all five effort levels, and `medium` is the default. Effort is the main control for how much the model thinks, and with it quality, latency, and cost. **Start with `medium`** for most work, including agentic coding. Use `low`, the cheapest and fastest level, for chat, short tool tasks, and simple, high-volume requests. In long agent prompts, the model is more likely to skip a search, stop early, or skip a check at `low`. Use `high` for knowledge work, longer agent tasks, and strict instruction following. Use `xhigh` or `max` only where your evals show a quality gain, and compare them with Claude Sonnet 5.5 on performance, cost, and speed.
