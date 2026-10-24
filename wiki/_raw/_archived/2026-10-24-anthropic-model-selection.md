---
title: >-
  Anthropic model selection — bounded source capture (2026-10-24)
source: "url:https://platform.claude.com/docs/en/about-claude/models/choosing-a-model"
captured_at: 2026-10-24T12:45:00Z
capture_kind: bounded-excerpt
immutable: true
---

# Choosing the right Claude model

Origin: [Choosing the right model — Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model).

This record preserves verbatim excerpts from the fetched official page on 2026-10-24. It is not a complete copy. The remote page remains mutable. The earlier capture [[_raw/_archived/2026-10-19-anthropic-model-selection]] stays unchanged; its excerpt still appears on the page.

## Verbatim excerpt — Establish key criteria

> **Effort:** Several Claude models support an effort parameter that trades intelligence for latency and cost within a single model. Tuning effort is often a better lever than switching models. On Claude Fable 5.1, Claude Opus 5, and Claude Sonnet 5.5, start with the default (`high`) and adjust up or down based on your evals. On Claude Opus 5.5 and Claude Haiku 5.5 the default is `medium`; start there and adjust the same way.

## Verbatim excerpts — Option 1: Start efficiency-first

> For many applications, starting with a faster, more cost-effective model such as Claude Haiku 5.5 can be the optimal approach:

> 4. Upgrade only if necessary for specific capability gaps.

> This approach is best for: Initial prototyping and development; Applications with tight latency requirements; Cost-sensitive implementations; High-volume, straightforward tasks

(The list items are joined with semicolons here; the wording is verbatim.)

## Verbatim excerpts — Option 2: Start capability-first

> For complex tasks where intelligence and advanced capabilities are paramount, you might want to start capability-first: implement with the strongest starting point for your task, then optimize to more efficient models later:

> 1. Implement with Claude Opus 5.5.

> 5. If your evals at `xhigh` or `max` effort still fall short on demanding reasoning or long-horizon agentic work, move to Claude Fable 5.1.

> This approach is best for: Complex reasoning tasks; Scientific or mathematical applications; Tasks requiring nuanced understanding; Applications where accuracy outweighs cost considerations; Advanced coding and high-autonomy agentic work

## Verbatim excerpts — Model selection matrix

> Most workloads start with Claude Opus 5.5.

| When you need... | Consider starting with... | Example use cases |
|---|---|---|
| The highest available capability | Claude Fable 5.1 | Agent sessions that run for hours, multistep deep research, analysis carried through to a finished document, spreadsheet, or deck |
| Complex agentic coding and enterprise work | Claude Opus 5.5 | Multihour autonomous coding agents, large-scale refactoring, complex systems engineering, vision-heavy workflows, computer use |
| Speed and capability for everyday coding, agent, and enterprise workloads | Claude Sonnet 5.5 | Code generation, data analysis, content creation, visual understanding, agentic tool use |
| The lowest latency and price | Claude Haiku 5.5 | Real-time applications, high-volume intelligent processing, cost-sensitive deployments needing strong reasoning, subagent tasks |
