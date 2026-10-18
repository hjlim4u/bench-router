---
title: >-
    Terminal-Bench 4.0
category: entities
tags: [benchmark, themodelgap, agentic]
relationships:
  - target: "[[entities/benchmarks/mg/terminal-bench-2-1]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/deepswe]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://hub.harborframework.com/datasets/terminal-bench/terminal-bench/4"]
summary: >-
    Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Terminal-Bench 4.0

Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments.

## Key Ideas

- 분류: agentic / Terminal ops
- 상태: current, 신뢰 등급 B, 의미 있는 점수 차 12.4점, 문항 66개
- 변형: max, high, xhigh, default
- 과제 형태: One task spins up a fresh, isolated machine environment and hands the agent a single natural-language objective drawn from an unusually wide spread of domains — the 66 items cover software engineering, machine learning, science, operations, hardware, security, and media work, so a task may ask the agent to repair a broken system, produce a correct data artifact, or harden a misconfigured setup. The agent acts only through a terminal: it issues shell commands, inspects results, and iterates the way a human engineer would, under a flat eight-hour timeout as of 4.0 calibrated so frontier models rarely hit it. Nothing in the goal statement names the steps; working them out is the task. When the agent stops, grading runs that task's hidden automated test suite against the final state of the machine — files written, services running, data produced — and passes only if every test clears. There is no partial credit, no LLM judging transcripts, and no multiple-choice floor. This describes the task format the maintainers document, not any single item's actual instructions.

관련: [[entities/benchmarks/mg/terminal-bench-2-1]], [[entities/benchmarks/mg/deepswe]]

## Index

```toml
[[unit]]
id = "mg:terminal-bench-4-0/max"
desc = "Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 12.4
trust_grade = "B"

[[unit]]
id = "mg:terminal-bench-4-0/high"
desc = "Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 12.4
trust_grade = "B"

[[unit]]
id = "mg:terminal-bench-4-0/xhigh"
desc = "Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 12.4
trust_grade = "B"

[[unit]]
id = "mg:terminal-bench-4-0/default"
desc = "Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 12.4
trust_grade = "B"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://hub.harborframework.com/datasets/terminal-bench/terminal-bench/4>
