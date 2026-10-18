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
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Toolathlon-Verified

Realistic multi-step chores that require an agent to juggle many real software tools over a long session, not just answer questions.

## Key Ideas

- 분류: agentic / Multi-tool chores
- 상태: current, 신뢰 등급 B, 의미 있는 점수 차 9.7점, 문항 108개
- 변형: default
- 과제 형태: A single task gives the agent one natural-language goal embedded in an already-populated, live multi-application environment — it is a chore to carry out end-to-end via MCP tool calls, not a question to answer in text. Reaching the goal typically takes on the order of 20 sequential tool-calling turns spanning more than one application (e.g. an inbox plus a calendar, or a spreadsheet plus a database). The benchmark's own team has published short summaries of a few illustrative tasks of this shape: one has the agent pull student submissions out of an email inbox and enter the corresponding grades into a course on Canvas (the LMS); another has the agent gather several quarters of institutional-ownership data, adjust the figures for a stock split, and populate a specific spreadsheet template with only the holdings that are common across quarters. In both, correctness is judged purely by whether the live application(s) end up in the correct final state — not by anything the agent says.

관련: [[entities/benchmarks/mg/agents-last-exam]], [[entities/benchmarks/mg/terminal-bench-2-1]]

## Index

```toml
[[unit]]
id = "mg:toolathlon-verified/default"
desc = "Realistic multi-step chores that require an agent to juggle many real software tools over a long session, not just answer questions."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.7
trust_grade = "B"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://github.com/hkust-nlp/Toolathlon>
- <https://huggingface.co/datasets/hkust-nlp/Toolathlon> — HF 공식 미러 (점수 행 `verified=false`)
