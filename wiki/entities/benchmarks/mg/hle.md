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
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Humanity's Last Exam

Expert-written questions across dozens of subjects, built to be hard enough that today's best models still fail most of them.

## Key Ideas

- Category: reasoning / Reasoning
- Lifecycle: current, trust grade B, meaningful gap 2 points, 2500 items
- Variants: no_tools, with_tools
- Task shape: One HLE item is a single question written by a named subject-matter expert in one of dozens of academic fields — mathematics, physics, chemistry, biology, medicine, computer science, humanities, and more — and included specifically because the frontier models available when the dataset was built answered it wrong. About three-quarters of items are "exact-match": the model must output one specific short string (a number, a term, a formula) that an LLM judge checks against a fixed reference answer, tolerating equivalent formats. The remaining roughly one-quarter are multiple-choice, with several answer options rather than a fixed four-choice layout. A minority of items also pair the question text with an image the model has to interpret. HLE's own site (lastexam.ai) has published real sample questions publicly; one such public sample is a graduate-level biology question that asks for a single precise number as its answer, illustrating the level of domain specificity involved — its exact wording is not reproduced here.

Related: [[entities/benchmarks/mg/gpqa-diamond]], [[entities/benchmarks/mg/arc-agi-2]]

## Index

```toml
[[unit]]
id = "mg:hle/no_tools"
desc = "Expert-written questions across dozens of subjects, built to be hard enough that today's best models still fail most of them."
metric = "pass_pct"
status = "current"
adoption = "active"
facets = { task = ["science_reasoning"] }
reason = "Independent Artificial Analysis runs on the 2,158-question text-only subset: claude-opus-5-5=61.4 (max), gemini-4-argon=57.09 (high), gpt-6.1-sol=52.9 (max)"
meaningful_gap = 2
trust_grade = "B"

[[unit]]
id = "mg:hle/with_tools"
desc = "Expert-written questions across dozens of subjects, built to be hard enough that today's best models still fail most of them."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["science_reasoning"] }
reason = "No independently verified with_tools score exists per The Model Gap (2026-10-18), and 0 current profile models appear in this variant"
meaningful_gap = 2
trust_grade = "B"
```

## Facets

- [[concepts/facets/task|task]]: science_reasoning

## Related benchmarks

- [[entities/benchmarks/hf/mmmu-pro]] — MMMU-Pro
- [[entities/benchmarks/hf/researchclawbench]] — ResearchClawBench
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/mg/gpqa-diamond]] — GPQA Diamond

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://arxiv.org/abs/2501.14249>
- <https://huggingface.co/datasets/cais/hle> — HF official mirror (score rows `verified=false`)
