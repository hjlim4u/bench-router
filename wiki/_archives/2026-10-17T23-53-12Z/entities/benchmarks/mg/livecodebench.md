---
title: >-
    LiveCodeBench
category: entities
tags: [benchmark, themodelgap, coding]
relationships:
  - target: "[[entities/benchmarks/mg/swe-bench-verified]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/deepswe]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://github.com/LiveCodeBench/LiveCodeBench"]
summary: >-
    Coding contest problems dated after each model's training cutoff, so scores can't be inflated by memorization.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LiveCodeBench

Coding contest problems dated after each model's training cutoff, so scores can't be inflated by memorization.

## Key Ideas

- 분류: coding / Contest coding
- 상태: saturated, 신뢰 등급 D, 의미 있는 점수 차 3.1점, 문항 1055개
- 변형: default
- 과제 형태: One task is a single competitive-programming problem pulled from a real contest on LeetCode, AtCoder, or Codeforces, tagged with the date it was published. The model is given the natural-language problem statement — the scenario, constraints, and required input/output format — and must produce a complete program or function that solves it. Grading is fully automated and execution-based: the submitted code is run against a hidden suite of test cases under a time and memory limit, using an APPS-style checker, and the problem counts as solved only if every hidden test passes. No human or model judge is involved, and there is no multiple-choice floor since the model must generate original code.

관련: [[entities/benchmarks/mg/swe-bench-verified]], [[entities/benchmarks/mg/deepswe]]

## Index

```toml
[[unit]]
id = "mg:livecodebench/default"
desc = "Coding contest problems dated after each model's training cutoff, so scores can't be inflated by memorization."
metric = "pass_pct"
status = "saturated"
adoption = "archive"
facets = { task = ["coding"] }
reason = "Model Gap 표시 saturated"
meaningful_gap = 3.1
trust_grade = "D"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://github.com/LiveCodeBench/LiveCodeBench>
