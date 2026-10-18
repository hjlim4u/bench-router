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
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Agents' Last Exam

Real, economically valuable professional work — video editing, CAD, manufacturing simulation — done end-to-end.

## Key Ideas

- 분류: agentic / Professional work
- 상태: current, 신뢰 등급 A, 의미 있는 점수 차 3.2점, 문항 1000개
- 변형: default
- 과제 형태: One ALE task reproduces a single real deliverable that a working professional was actually paid to produce, staged inside a real OS sandbox with the relevant professional software already installed. The agent is given an instruction plus starting files (for example: a CAD/CAE project, a video project with source footage, or a 3D character mesh) and must operate the real application end-to-end, not a toy API, to produce a finished artifact. Grading then compares that artifact against a reference answer that stays hidden until after the agent finishes, using tolerance/exact-match/geometry checks rather than a human or AI judge eyeballing the result. This description follows the general task format and the illustrative task categories (a manufacturing simulation task, a video-compositing task, a character-animation task) that the ALE paper itself publishes to explain its evaluation design — it does not reproduce any task's actual instruction text or reference answer.

관련: [[entities/benchmarks/mg/toolathlon-verified]], [[entities/benchmarks/mg/terminal-bench-2-1]]

## Index

```toml
[[unit]]
id = "mg:agents-last-exam/default"
desc = "Real, economically valuable professional work — video editing, CAD, manufacturing simulation — done end-to-end."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["professional_work"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 3.2
trust_grade = "A"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://arxiv.org/abs/2606.05405>
- <https://huggingface.co/datasets/agents-last-exam/agents-last-exam> — HF 공식 미러 (점수 행 `verified=false`)
