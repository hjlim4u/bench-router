---
title: >-
    HMMT Feb 2026
category: entities
tags: [benchmark, themodelgap, reasoning]
relationships:
  - target: "[[entities/benchmarks/mg/gpqa-diamond]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/arc-agi-2]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://matharena.ai/?comp=hmmt--hmmt_feb_2026", "url:https://huggingface.co/datasets/MathArena/hmmt_feb_2026"]
summary: >-
    Whether a model can solve HMMT Feb 2026's short-answer competition math problems — pre-college-level algebra, number theory, combinatorics, and geometry, each with one objectively-checkable numeric or
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# HMMT Feb 2026

Whether a model can solve HMMT Feb 2026's short-answer competition math problems — pre-college-level algebra, number theory, combinatorics, and geometry, each with one objectively-checkable numeric or symbolic answer.

## Key Ideas

- 분류: reasoning / Competition mathematics
- 상태: contaminated, 신뢰 등급 C, 의미 있는 점수 차 17.5점, 문항 33개
- 변형: default
- 과제 형태: One task presents a single HMMT-style problem stated in a few sentences of prose (any needed diagram is described rather than rendered as a complex image), drawn from algebra, number theory, combinatorics, or geometry. The model must work through to one specific final value — an integer, a fraction, or a simple closed-form expression — with no multiple-choice options offered and no partial credit for correct intermediate steps. Grading is exact match against the competition's official answer key, not an LLM judge, so a right method with a slipped final value still scores zero. No official HMMT item is reproduced here: the problems are the competition's own published material, and this site's standing policy is to never republish a real test item regardless of a benchmark's specific copyright terms — only the format is described above.

관련: [[entities/benchmarks/mg/gpqa-diamond]], [[entities/benchmarks/mg/arc-agi-2]]

## Index

```toml
[[unit]]
id = "mg:hmmt-feb-2026/default"
desc = "Whether a model can solve HMMT Feb 2026's short-answer competition math problems — pre-college-level algebra, number theory, combinatorics, and geometry, each with one objectively-checkable numeric or symbolic answer."
metric = "pass_pct"
status = "contaminated"
adoption = "archive"
facets = { task = ["math"] }
reason = "Model Gap 표시 contaminated"
meaningful_gap = 17.5
trust_grade = "C"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://matharena.ai/?comp=hmmt--hmmt_feb_2026>
- <https://huggingface.co/datasets/MathArena/hmmt_feb_2026> — HF 공식 미러 (점수 행 `verified=false`)
