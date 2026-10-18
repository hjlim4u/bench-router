---
title: >-
    Agents' Last Exam
category: entities
tags: [benchmark, themodelgap, agentic]
relationships:
  - target: "[[entities/benchmarks/mg/toolathlon-verified]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/terminal-bench-2-1]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://arxiv.org/abs/2606.05405", "url:https://huggingface.co/datasets/agents-last-exam/agents-last-exam"]
summary: >-
    Real, economically valuable professional work — video editing, CAD, manufacturing simulation — done end-to-end.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Agents' Last Exam

Real, economically valuable professional work — video editing, CAD, manufacturing simulation — done end-to-end.

## Key Ideas

- Category: agentic / Professional work
- Lifecycle: current, trust grade A, meaningful gap 3.2 points, 1000 items
- Variants: default
- Task shape: One ALE task reproduces a single real deliverable that a working professional was actually paid to produce, staged inside a real OS sandbox with the relevant professional software already installed. The agent is given an instruction plus starting files (for example: a CAD/CAE project, a video project with source footage, or a 3D character mesh) and must operate the real application end-to-end, not a toy API, to produce a finished artifact. Grading then compares that artifact against a reference answer that stays hidden until after the agent finishes, using tolerance/exact-match/geometry checks rather than a human or AI judge eyeballing the result. This description follows the general task format and the illustrative task categories (a manufacturing simulation task, a video-compositing task, a character-animation task) that the ALE paper itself publishes to explain its evaluation design — it does not reproduce any task's actual instruction text or reference answer.

Related: [[entities/benchmarks/mg/toolathlon-verified]], [[entities/benchmarks/mg/terminal-bench-2-1]]

## Index

```toml
[[unit]]
id = "mg:agents-last-exam/default"
desc = "Real, economically valuable professional work — video editing, CAD, manufacturing simulation — done end-to-end."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["professional_work"] }
reason = "Only 1 profile model on Snorkel's 2026-10-01 leaderboard (43 rows): claude-opus-5-5=38.2 pass rate (Claude Code Max, rank 1); gpt-6.1-sol and gemini-4-argon not yet evaluated"
meaningful_gap = 3.2
trust_grade = "A"
```

## Facets

- [[concepts/facets/task|task]]: professional_work

## Related benchmarks

- [[entities/benchmarks/hf/apex-agents]] — APEX-Agents
- [[entities/benchmarks/hf/apex-v1-extended]] — APEX-v1-extended
- [[entities/benchmarks/hf/chi-bench]] — χ-Bench (CHI-Bench)

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://arxiv.org/abs/2606.05405>
- <https://huggingface.co/datasets/agents-last-exam/agents-last-exam> — HF official mirror (score rows `verified=false`)
