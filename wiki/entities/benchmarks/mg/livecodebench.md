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
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LiveCodeBench

Coding contest problems dated after each model's training cutoff, so scores can't be inflated by memorization.

## Key Ideas

- Category: coding / Contest coding
- Lifecycle: saturated, trust grade D, meaningful gap 3.1 points, 1055 items
- Variants: default
- Task shape: One task is a single competitive-programming problem pulled from a real contest on LeetCode, AtCoder, or Codeforces, tagged with the date it was published. The model is given the natural-language problem statement — the scenario, constraints, and required input/output format — and must produce a complete program or function that solves it. Grading is fully automated and execution-based: the submitted code is run against a hidden suite of test cases under a time and memory limit, using an APPS-style checker, and the problem counts as solved only if every hidden test passes. No human or model judge is involved, and there is no multiple-choice floor since the model must generate original code.

Related: [[entities/benchmarks/mg/swe-bench-verified]], [[entities/benchmarks/mg/deepswe]]

## Index

```toml
[[unit]]
id = "mg:livecodebench/default"
desc = "Coding contest problems dated after each model's training cutoff, so scores can't be inflated by memorization."
metric = "pass_pct"
status = "saturated"
adoption = "archive"
facets = { task = ["coding"] }
reason = "The Model Gap marks it saturated"
meaningful_gap = 3.1
trust_grade = "D"
```

## Facets

- [[concepts/facets/task|task]]: coding

## Related benchmarks

- [[entities/benchmarks/artificial-analysis]] — Artificial Analysis indexes
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://github.com/LiveCodeBench/LiveCodeBench>
