---
title: >-
    SWE-bench Verified
category: entities
tags: [benchmark, themodelgap, coding]
relationships:
  - target: "[[entities/benchmarks/mg/deepswe]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/livecodebench]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://www.swebench.com/verified.html", "url:https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified"]
summary: >-
    Gives an agent a real closed GitHub issue and checks whether its patch fixes it and passes the project's real test suite.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# SWE-bench Verified

Gives an agent a real closed GitHub issue and checks whether its patch fixes it and passes the project's real test suite.

## Key Ideas

- 분류: coding / Bug fixing
- 상태: saturated, 신뢰 등급 D, 의미 있는 점수 차 4.5점, 문항 500개
- 변형: default
- 과제 형태: One task = a real, previously-closed GitHub issue (bug report or feature request) from one of a fixed set of popular open-source Python repositories, paired with a snapshot of that repo's code at the commit right before the human fix was merged. The AI agent gets the issue description and access to the codebase, has to figure out which files to change and how, and outputs a patch. It never sees the human's actual fix or any later commit history. Grading is automatic: the project's own test suite is run against the patched code, and the task counts as solved only if specific tests that used to fail now pass and nothing that used to pass now breaks.

관련: [[entities/benchmarks/mg/deepswe]], [[entities/benchmarks/mg/livecodebench]]

## Index

```toml
[[unit]]
id = "mg:swe-bench-verified/default"
desc = "Gives an agent a real closed GitHub issue and checks whether its patch fixes it and passes the project's real test suite."
metric = "pass_pct"
status = "saturated"
adoption = "archive"
facets = { task = ["repo_coding"] }
reason = "Model Gap 표시 saturated"
meaningful_gap = 4.5
trust_grade = "D"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://www.swebench.com/verified.html>
- <https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified> — HF 공식 미러 (점수 행 `verified=false`)
