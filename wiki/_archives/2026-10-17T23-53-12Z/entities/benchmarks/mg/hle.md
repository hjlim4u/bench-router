---
title: >-
    Humanity's Last Exam
category: entities
tags: [benchmark, themodelgap, reasoning]
relationships:
  - target: "[[entities/benchmarks/mg/gpqa-diamond]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/arc-agi-2]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://arxiv.org/abs/2501.14249", "url:https://huggingface.co/datasets/cais/hle"]
summary: >-
    Expert-written questions across dozens of subjects, built to be hard enough that today's best models still fail most of them.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Humanity's Last Exam

Expert-written questions across dozens of subjects, built to be hard enough that today's best models still fail most of them.

## Key Ideas

- 분류: reasoning / Reasoning
- 상태: current, 신뢰 등급 B, 의미 있는 점수 차 2점, 문항 2500개
- 변형: no_tools, with_tools
- 과제 형태: One HLE item is a single question written by a named subject-matter expert in one of dozens of academic fields — mathematics, physics, chemistry, biology, medicine, computer science, humanities, and more — and included specifically because the frontier models available when the dataset was built answered it wrong. About three-quarters of items are "exact-match": the model must output one specific short string (a number, a term, a formula) that an LLM judge checks against a fixed reference answer, tolerating equivalent formats. The remaining roughly one-quarter are multiple-choice, with several answer options rather than a fixed four-choice layout. A minority of items also pair the question text with an image the model has to interpret. HLE's own site (lastexam.ai) has published real sample questions publicly; one such public sample is a graduate-level biology question that asks for a single precise number as its answer, illustrating the level of domain specificity involved — its exact wording is not reproduced here.

관련: [[entities/benchmarks/mg/gpqa-diamond]], [[entities/benchmarks/mg/arc-agi-2]]

## Index

```toml
[[unit]]
id = "mg:hle/no_tools"
desc = "Expert-written questions across dozens of subjects, built to be hard enough that today's best models still fail most of them."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["science_reasoning"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 2
trust_grade = "B"

[[unit]]
id = "mg:hle/with_tools"
desc = "Expert-written questions across dozens of subjects, built to be hard enough that today's best models still fail most of them."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["science_reasoning"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 2
trust_grade = "B"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://arxiv.org/abs/2501.14249>
- <https://huggingface.co/datasets/cais/hle> — HF 공식 미러 (점수 행 `verified=false`)
