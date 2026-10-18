---
title: >-
    Terminal-Bench 2.1
category: entities
tags: [benchmark, themodelgap, agentic]
relationships:
  - target: "[[entities/benchmarks/mg/deepswe]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/toolathlon-verified]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://hub.harborframework.com/datasets/terminal-bench/terminal-bench-2-1/6", "url:https://huggingface.co/datasets/harborframework/terminal-bench-2.1"]
summary: >-
    Whether an AI agent can actually operate a real command line to debug code, administer systems, and fix security issues.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Terminal-Bench 2.1

Whether an AI agent can actually operate a real command line to debug code, administer systems, and fix security issues.

## Key Ideas

- 분류: agentic / Terminal ops
- 상태: current, 신뢰 등급 B, 의미 있는 점수 차 10.6점, 문항 89개
- 변형: default
- 과제 형태: One task instantiates a fresh, isolated container/VM environment and gives the agent a single natural-language objective — for example, get a broken build compiling, close off a mis-configured service's known vulnerability, or stand up and wire together a small data-processing or model-training pipeline — with no further hand-holding. The agent works purely through a terminal: it can run arbitrary multi-turn shell commands, inspect output, and iterate, the same way a human sysadmin or engineer would. When it finishes (or times out), grading runs a hidden, task-specific automated test suite against the resulting state of the environment — files written, services running, data produced — rather than against anything the agent said; there is no reference answer to text-match and no credit for output that merely looks right. This describes the general task format the maintainers themselves describe (compiling code, configuring servers, training models, debugging systems, fixing security issues) — not any single specific item's actual instructions.

관련: [[entities/benchmarks/mg/deepswe]], [[entities/benchmarks/mg/toolathlon-verified]]

## Index

```toml
[[unit]]
id = "mg:terminal-bench-2-1/default"
desc = "Whether an AI agent can actually operate a real command line to debug code, administer systems, and fix security issues."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "수집기 미구현, 프로필 커버리지 미확인"
meaningful_gap = 10.6
trust_grade = "B"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://hub.harborframework.com/datasets/terminal-bench/terminal-bench-2-1/6>
- <https://huggingface.co/datasets/harborframework/terminal-bench-2.1> — HF 공식 미러 (점수 행 `verified=false`)
