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
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# ARC-AGI-2

Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one.

## Key Ideas

- Category: reasoning / Compositional visual reasoning
- Lifecycle: current, trust grade B, meaningful gap 9.2 points, 120 items
- Variants: max, high, xhigh, untiered
- Task shape: One task presents a small handful of demonstration pairs — a colored grid (up to 30x30 cells, up to 10 colors) paired with the grid that results from applying a hidden transformation to it. The rule behind the pairs can be a single operation (recoloring, reflecting, resizing, counting, completing a pattern) or several rules composed and applied conditionally, and it is never stated in words — only shown. The model then sees one new, unseen input grid and must output the exact resulting grid: correct dimensions, correct colors, correct cell-by-cell layout, with no free-text reasoning credited. Grading is exact match only, so a single wrong cell fails the task; there is no partial credit and no LLM judge. No task's actual grids are reproduced here — ARC Prize keeps the scored Semi-Private and Private splits undisclosed specifically to keep this exact route out of training data, and publishing example grids on a benchmark whose whole premise is resisting memorization would work against the thing it's cited for.

Related: [[entities/benchmarks/mg/hle]], [[entities/benchmarks/mg/hmmt-feb-2026]]

## Index

```toml
[[unit]]
id = "mg:arc-agi-2/max"
desc = "Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["abstract_reasoning"] }
reason = "MG stores 1 row per model (its peak tier), placing gpt-6.1-sol=94.2 in max and claude-opus-5-5=93.3 in high; arcprize.org has both at max (gpt-6.1-sol 94.2%, claude-opus-5-5 91.7%) and high (claude-opus-5-5 93.3%, gpt-6.1-sol 91.7%), but MG snapshot splits them across variants"
meaningful_gap = 9.2
trust_grade = "B"

[[unit]]
id = "mg:arc-agi-2/high"
desc = "Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["abstract_reasoning"] }
reason = "MG stores 1 row per model (its peak tier), placing claude-opus-5-5=93.3 in high and gpt-6.1-sol=94.2 in max; see mg:arc-agi-2/max note"
meaningful_gap = 9.2
trust_grade = "B"

[[unit]]
id = "mg:arc-agi-2/xhigh"
desc = "Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["abstract_reasoning"] }
reason = "No score for any current profile model (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon) in this variant"
meaningful_gap = 9.2
trust_grade = "B"

[[unit]]
id = "mg:arc-agi-2/untiered"
desc = "Fluid, compositional visual reasoning: inferring a hidden transformation rule from a handful of example input/output grids and applying it exactly to a new one."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["abstract_reasoning"] }
reason = "No score for any current profile model (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon) in this variant"
meaningful_gap = 9.2
trust_grade = "B"
```

## Facets

- [[concepts/facets/task|task]]: abstract_reasoning

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://arcprize.org/leaderboard>
