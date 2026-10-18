---
title: >-
    LiveBench
category: entities
tags: [benchmark, themodelgap, general]
relationships:
  - target: "[[entities/benchmarks/mg/hle]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/swe-bench-verified]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://livebench.ai/"]
summary: >-
    LiveBench's tracked "Overall" score is a composite average across seven independently-graded categories — reasoning, coding, agentic coding, math, data analysis, language, and instruction following...
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LiveBench

LiveBench's tracked "Overall" score is a composite average across seven independently-graded categories — reasoning, coding, agentic coding, math, data analysis, language, and instruction following — each scored against an objective, verifiable ground-truth answer rather than any single skill.

## Key Ideas

- Category: composite / Composite score across 7 domains
- Lifecycle: current, trust grade A, meaningful gap 2.7 points, 1436 items
- Variants: default
- Task shape: LiveBench is unlike every other benchmark tracked on this site in one specific way: the tracked "Overall" score isn't built from one uniform question type, because it averages seven separately-run categories, each with its own task format. Reasoning and Language items are closed-ended questions or short-answer puzzles graded against a single fixed correct answer. Math items are drawn from recent competition-style problems with a numeric or symbolic final answer. Coding items ask for a single-turn program that must pass hidden held-out test cases, while Agentic Coding items pose a similar goal but require the model to work iteratively inside a tool-using environment rather than emit one finished answer in one shot. Data Analysis items hand the model a real or synthetic dataset and ask it to compute or transform something checkable against a known result. Instruction Following items test whether a response obeys a set of stated constraints — length, format, required or forbidden content — that can be verified programmatically rather than judged by feel. Across all seven categories, source material is deliberately current: recent arXiv papers, news articles, Kaggle/Socrata datasets, IMDb synopses, and newly-published math-competition problems, refreshed periodically so older, possibly-memorized questions get retired. No example item is reproduced here — only the general shape of each category is described.

Related: [[entities/benchmarks/mg/hle]], [[entities/benchmarks/mg/swe-bench-verified]]

## Index

```toml
[[unit]]
id = "mg:livebench/default"
desc = "LiveBench's tracked \"Overall\" score is a composite average across seven independently-graded categories — reasoning, coding, agentic coding, math, data analysis, language, and instruction following — each scored against an objective, verifiable ground-truth answer rather than any single skill."
metric = "index"
status = "current"
adoption = "active"
facets = { task = ["general"] }
reason = "Independent livebench-official runs on the 2026-06-25 release at max effort: claude-opus-5-5=83.2, gpt-6.1-sol=81.6 (gemini-4-argon not yet evaluated)"
meaningful_gap = 2.7
trust_grade = "A"
```

## Facets

- [[concepts/facets/task|task]]: general

## Related benchmarks

- [[entities/benchmarks/artificial-analysis]] — Artificial Analysis indexes
- [[entities/benchmarks/hf/ace]] — ACE
- [[entities/benchmarks/hf/evasionbench]] — EvasionBench
- [[entities/benchmarks/hf/mmlu-pro]] — MMLU-Pro
- [[entities/benchmarks/hf/typed-decisions]] — Typed Decisions
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://livebench.ai/>
