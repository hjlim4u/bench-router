---
title: >-
    AA-AnalystAgent
category: entities
tags: [benchmark, themodelgap, agentic]
relationships:
  - target: "[[entities/benchmarks/mg/toolathlon-verified]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/agents-last-exam]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://artificialanalysis.ai/evaluations/aa-analyst-agent"]
summary: >-
    Whether an agent can answer the kind of quantitative question a business or data analyst faces day to day — working from a folder of real spreadsheets and documents, running Python in a sandbox, and r
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# AA-AnalystAgent

Whether an agent can answer the kind of quantitative question a business or data analyst faces day to day — working from a folder of real spreadsheets and documents, running Python in a sandbox, and returning the one right value on all five of five attempts.

## Key Ideas

- 분류: agentic / Spreadsheet & document analysis
- 상태: current, 신뢰 등급 B, 의미 있는 점수 차 11.2점, 문항 80개
- 변형: default
- 과제 형태: One task drops the agent into a workspace holding a folder of reference spreadsheets and documents (.xlsx and .docx, in some cases zipped) — real-world material such as a government expenditure report, a commodity trade release, a hydrology dataset, an energy cost model or a company valuation sheet — and asks one quantitative question about them: locate the right source figure and diagnose a discrepancy, filter and total a category, compute a ratio, project a trend or sensitivity, or work a P&L, cash-flow, balance-sheet or valuation calculation. The agent gets sandboxed Python 3.12 with pandas, openpyxl and the usual data libraries preinstalled, URL fetching, image viewing for vision-capable models, and a submit tool, under a 100-turn cap. It must submit only the answer value — a number, a percentage or a label, no explanation — and is graded correct or incorrect against a human-authored reference answer it never sees. Each question is run five times, and the headline metric counts it solved only if all five submissions are right. Artificial Analysis publishes example tasks (prompt and reference answer) on the leaderboard page; none is reproduced here, in keeping with this site's policy of never republishing a real test item.

관련: [[entities/benchmarks/mg/toolathlon-verified]], [[entities/benchmarks/mg/agents-last-exam]]

## Index

```toml
[[unit]]
id = "mg:aa-analyst-agent/default"
desc = "Whether an agent can answer the kind of quantitative question a business or data analyst faces day to day — working from a folder of real spreadsheets and documents, running Python in a sandbox, and returning the one right value on all five of five attempts."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["data_analysis"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 11.2
trust_grade = "B"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://artificialanalysis.ai/evaluations/aa-analyst-agent>
