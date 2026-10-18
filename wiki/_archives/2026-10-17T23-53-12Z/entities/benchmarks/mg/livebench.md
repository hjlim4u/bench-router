---
title: >-
    LiveBench
category: entities
tags: [benchmark, themodelgap, composite]
relationships:
  - target: "[[entities/benchmarks/mg/hle]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/swe-bench-verified]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://livebench.ai/"]
summary: >-
    LiveBench's tracked "Overall" score is a composite average across seven independently-graded categories — reasoning, coding, agentic coding, math, data analysis, language, and instruction following — 
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LiveBench

LiveBench's tracked "Overall" score is a composite average across seven independently-graded categories — reasoning, coding, agentic coding, math, data analysis, language, and instruction following — each scored against an objective, verifiable ground-truth answer rather than any single skill.

## Key Ideas

- 분류: composite / Composite score across 7 domains
- 상태: current, 신뢰 등급 A, 의미 있는 점수 차 2.7점, 문항 1436개
- 변형: default
- 과제 형태: LiveBench is unlike every other benchmark tracked on this site in one specific way: the tracked "Overall" score isn't built from one uniform question type, because it averages seven separately-run categories, each with its own task format. Reasoning and Language items are closed-ended questions or short-answer puzzles graded against a single fixed correct answer. Math items are drawn from recent competition-style problems with a numeric or symbolic final answer. Coding items ask for a single-turn program that must pass hidden held-out test cases, while Agentic Coding items pose a similar goal but require the model to work iteratively inside a tool-using environment rather than emit one finished answer in one shot. Data Analysis items hand the model a real or synthetic dataset and ask it to compute or transform something checkable against a known result. Instruction Following items test whether a response obeys a set of stated constraints — length, format, required or forbidden content — that can be verified programmatically rather than judged by feel. Across all seven categories, source material is deliberately current: recent arXiv papers, news articles, Kaggle/Socrata datasets, IMDb synopses, and newly-published math-competition problems, refreshed periodically so older, possibly-memorized questions get retired. No example item is reproduced here — only the general shape of each category is described.

관련: [[entities/benchmarks/mg/hle]], [[entities/benchmarks/mg/swe-bench-verified]]

## Index

```toml
[[unit]]
id = "mg:livebench/default"
desc = "LiveBench's tracked \"Overall\" score is a composite average across seven independently-graded categories — reasoning, coding, agentic coding, math, data analysis, language, and instruction following — each scored against an objective, verifiable ground-truth answer rather than any single skill."
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 2.7
trust_grade = "A"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://livebench.ai/>
