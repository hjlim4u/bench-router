---
title: >-
    OSWorld 2.0
category: entities
tags: [benchmark, themodelgap, agentic]
relationships:
  - target: "[[entities/benchmarks/mg/agents-last-exam]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/toolathlon-verified]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://osworld-v2.xlang.ai/"]
summary: >-
    Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# OSWorld 2.0

Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly.

## Key Ideas

- Category: agentic / Long-horizon computer use
- Lifecycle: current, trust grade C, meaningful gap 9.7 points, 108 items
- Variants: v2026_06_24_full, v2026_08_08_full, v2026_08_08_offline, v2026_08_08_full_modified, v2_1_full, v2_1_offline
- Task shape: One task drops an agent into a fresh Ubuntu virtual machine, preloaded with the files, accounts, and self-hosted mock web apps the scenario needs, and hands it a goal a working professional would recognize: reconcile records scattered across mail, chat, spreadsheets, and a legacy web portal, then produce the correct final artifact. The agent sees the screen only through screenshots and acts only through mouse and keyboard, under a default budget of 500 action steps at 1080p resolution. The suite is long-horizon by design: median skilled-human completion time is about 1.6 hours, and many tasks deliver new information mid-task — a late email that changes the requirements, or a record the agent must recover from an earlier report — so success requires revising plans rather than executing a fixed script. Grading checks a fixed set of weighted checkpoints against the machine's final state, about 27 per task on average, reported two ways: partial reward (mean checkpoint credit earned) and a strict or binary pass (every checkpoint met). No task's actual instructions are reproduced here.

Related: [[entities/benchmarks/mg/agents-last-exam]], [[entities/benchmarks/mg/toolathlon-verified]]

## Index

```toml
[[unit]]
id = "mg:osworld-2-0/v2026_06_24_full"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "No score for any current profile model (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon) in this variant"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2026_08_08_full"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "No score for any current profile model (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon) in this variant"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2026_08_08_offline"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "Protocol mismatch (2026-10-18): both scores are vendor self-reports with incompatible protocols — gpt-6.1-sol=71.42 (OpenAI single-attempt, max effort) vs gemini-4-argon=69.2 (DeepMind best-of-3 test-set selection with CUA+compaction, untiered)"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2026_08_08_full_modified"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "No score for any current profile model (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon) in this variant"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2_1_full"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "Only 1 profile model (claude-opus-5-5=81.8 partial / 48.7 strict, Anthropic self-report with modified task/grading scripts and Opus 4.8 grader, §8.13.3 'not directly comparable')"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2_1_offline"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "No score for any current profile model (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon) in this variant"
meaningful_gap = 9.7
trust_grade = "C"
```

## Facets

- [[concepts/facets/task|task]]: computer_use

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://osworld-v2.xlang.ai/>
