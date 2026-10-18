---
title: >-
    Toolathlon-Verified
category: entities
tags: [benchmark, themodelgap, agentic]
relationships:
  - target: "[[entities/benchmarks/mg/agents-last-exam]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/terminal-bench-2-1]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://github.com/hkust-nlp/Toolathlon", "url:https://huggingface.co/datasets/hkust-nlp/Toolathlon"]
summary: >-
    Realistic multi-step chores that require an agent to juggle many real software tools over a long session, not just answer questions.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Toolathlon-Verified

Realistic multi-step chores that require an agent to juggle many real software tools over a long session, not just answer questions.

## Key Ideas

- Category: agentic / Multi-tool chores
- Lifecycle: current, trust grade B, meaningful gap 9.7 points, 108 items
- Variants: default
- Task shape: A single task gives the agent one natural-language goal embedded in an already-populated, live multi-application environment — it is a chore to carry out end-to-end via MCP tool calls, not a question to answer in text. Reaching the goal typically takes on the order of 20 sequential tool-calling turns spanning more than one application (e.g. an inbox plus a calendar, or a spreadsheet plus a database). The benchmark's own team has published short summaries of a few illustrative tasks of this shape: one has the agent pull student submissions out of an email inbox and enter the corresponding grades into a course on Canvas (the LMS); another has the agent gather several quarters of institutional-ownership data, adjust the figures for a stock split, and populate a specific spreadsheet template with only the holdings that are common across quarters. In both, correctness is judged purely by whether the live application(s) end up in the correct final state — not by anything the agent says.

Related: [[entities/benchmarks/mg/agents-last-exam]], [[entities/benchmarks/mg/terminal-bench-2-1]]

## Index

```toml
[[unit]]
id = "mg:toolathlon-verified/default"
desc = "Realistic multi-step chores that require an agent to juggle many real software tools over a long session, not just answer questions."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"] }
reason = "0 current profile models on the 17-row leaderboard (newest entry is claude-sonnet-5-5=77.8 self-reported; claude-opus-5-5, gpt-6.1-sol, gemini-4-argon not yet evaluated)"
meaningful_gap = 9.7
trust_grade = "B"
```

## Facets

- [[concepts/facets/task|task]]: multi_tool

## Related benchmarks

- [[entities/benchmarks/hf/claw-eval]] — Claw-Eval
- [[entities/benchmarks/hf/skillsbench]] — SkillsBench
- [[entities/benchmarks/hf/wildclawbench]] — WildClawBench
- [[entities/benchmarks/hf/yc-bench]] — YC-Bench

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://github.com/hkust-nlp/Toolathlon>
- <https://huggingface.co/datasets/hkust-nlp/Toolathlon> — HF official mirror (score rows `verified=false`)
