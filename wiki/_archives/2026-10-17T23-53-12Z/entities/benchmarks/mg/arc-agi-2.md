---
title: >-
    ARC-AGI-2
category: entities
tags: [benchmark, themodelgap, reasoning]
relationships:
  - target: "[[entities/benchmarks/mg/hle]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/hmmt-feb-2026]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://arcprize.org/leaderboard"]
summary: >-
    Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# ARC-AGI-2

Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one.

## Key Ideas

- 분류: reasoning / Compositional visual reasoning
- 상태: current, 신뢰 등급 B, 의미 있는 점수 차 9.2점, 문항 120개
- 변형: max, high, xhigh, untiered
- 과제 형태: One task presents a small handful of demonstration pairs — a colored grid (up to 30x30 cells, up to 10 colors) paired with the grid that results from applying a hidden transformation to it. The rule behind the pairs can be a single operation (recoloring, reflecting, resizing, counting, completing a pattern) or several rules composed and applied conditionally, and it is never stated in words — only shown. The model then sees one new, unseen input grid and must output the exact resulting grid: correct dimensions, correct colors, correct cell-by-cell layout, with no free-text reasoning credited. Grading is exact match only, so a single wrong cell fails the task; there is no partial credit and no LLM judge. No task's actual grids are reproduced here — ARC Prize keeps the scored Semi-Private and Private splits undisclosed specifically to keep this exact route out of training data, and publishing example grids on a benchmark whose whole premise is resisting memorization would work against the thing it's cited for.

관련: [[entities/benchmarks/mg/hle]], [[entities/benchmarks/mg/hmmt-feb-2026]]

## Index

```toml
[[unit]]
id = "mg:arc-agi-2/max"
desc = "Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["abstract_reasoning"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.2
trust_grade = "B"

[[unit]]
id = "mg:arc-agi-2/high"
desc = "Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["abstract_reasoning"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.2
trust_grade = "B"

[[unit]]
id = "mg:arc-agi-2/xhigh"
desc = "Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["abstract_reasoning"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.2
trust_grade = "B"

[[unit]]
id = "mg:arc-agi-2/untiered"
desc = "Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["abstract_reasoning"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.2
trust_grade = "B"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://arcprize.org/leaderboard>
