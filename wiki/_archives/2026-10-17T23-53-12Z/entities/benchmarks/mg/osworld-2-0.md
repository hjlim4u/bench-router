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
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# OSWorld 2.0

Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly.

## Key Ideas

- 분류: agentic / Long-horizon computer use
- 상태: current, 신뢰 등급 C, 의미 있는 점수 차 9.7점, 문항 108개
- 변형: v2026_06_24_full, v2026_08_08_full, v2026_08_08_offline, v2026_08_08_full_modified, v2_1_full, v2_1_offline
- 과제 형태: One task drops an agent into a fresh Ubuntu virtual machine, preloaded with the files, accounts, and self-hosted mock web apps the scenario needs, and hands it a goal a working professional would recognize: reconcile records scattered across mail, chat, spreadsheets, and a legacy web portal, then produce the correct final artifact. The agent sees the screen only through screenshots and acts only through mouse and keyboard, under a default budget of 500 action steps at 1080p resolution. The suite is long-horizon by design: median skilled-human completion time is about 1.6 hours, and many tasks deliver new information mid-task — a late email that changes the requirements, or a record the agent must recover from an earlier report — so success requires revising plans rather than executing a fixed script. Grading checks a fixed set of weighted checkpoints against the machine's final state, about 27 per task on average, reported two ways: partial reward (mean checkpoint credit earned) and a strict or binary pass (every checkpoint met). No task's actual instructions are reproduced here.

관련: [[entities/benchmarks/mg/agents-last-exam]], [[entities/benchmarks/mg/toolathlon-verified]]

## Index

```toml
[[unit]]
id = "mg:osworld-2-0/v2026_06_24_full"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2026_08_08_full"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2026_08_08_offline"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2026_08_08_full_modified"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2_1_full"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.7
trust_grade = "C"

[[unit]]
id = "mg:osworld-2-0/v2_1_offline"
desc = "Whether an AI agent can carry out long, multi-app computer workflows on a real Ubuntu desktop and finish them correctly."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["computer_use"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 9.7
trust_grade = "C"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://osworld-v2.xlang.ai/>
