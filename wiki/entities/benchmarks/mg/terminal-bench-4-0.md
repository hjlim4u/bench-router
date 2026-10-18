---
title: >-
    Terminal-Bench 4.0
category: entities
tags: [benchmark, themodelgap, agentic]
relationships:
  - target: "[[entities/benchmarks/terminal-bench-exact]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/terminal-bench-2-1]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/deepswe]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://huggingface.co/datasets/harborframework/terminal-bench", "url:https://hub.harborframework.com/datasets/terminal-bench/terminal-bench/4"]
summary: >-
    Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Terminal-Bench 4.0

Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments.

## Key Ideas

- Category: agentic / Terminal ops
- Lifecycle: current, trust grade B, meaningful gap 12.4 points, 66 items
- Variants: max, high, xhigh, default
- Task shape: One task spins up a fresh, isolated machine environment and hands the agent a single natural-language objective drawn from an unusually wide spread of domains — the 66 items cover software engineering, machine learning, science, operations, hardware, security, and media work, so a task may ask the agent to repair a broken system, produce a correct data artifact, or harden a misconfigured setup. The agent acts only through a terminal: it issues shell commands, inspects results, and iterates the way a human engineer would, under a flat eight-hour timeout as of 4.0 calibrated so frontier models rarely hit it. Nothing in the goal statement names the steps; working them out is the task. When the agent stops, grading runs that task's hidden automated test suite against the final state of the machine — files written, services running, data produced — and passes only if every test clears. There is no partial credit, no LLM judging transcripts, and no multiple-choice floor. This describes the task format the maintainers document, not any single item's actual instructions.

Related: [[entities/benchmarks/mg/terminal-bench-2-1]], [[entities/benchmarks/mg/deepswe]]

## Index

```toml
[[unit]]
id = "mg:terminal-bench-4-0/max"
desc = "Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments."
metric = "pass_pct"
status = "current"
adoption = "active"
facets = { task = ["terminal_ops"] }
reason = "Independent vals-ai runs under identical mini-swe-agent harness (single bash tool, pass@1 over 3 passes, max effort): claude-opus-5-5=65.15, gpt-6.1-sol=55.05"
meaningful_gap = 12.4
trust_grade = "B"

[[unit]]
id = "mg:terminal-bench-4-0/high"
desc = "Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "Only 1 profile model in this tier (gemini-4-argon=57.58 via vals-ai mini-swe-agent at high effort); claude-opus-5-5 and gpt-6.1-sol are recorded in the max tier"
meaningful_gap = 12.4
trust_grade = "B"

[[unit]]
id = "mg:terminal-bench-4-0/xhigh"
desc = "Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "No score for any current profile model (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon) in this variant"
meaningful_gap = 12.4
trust_grade = "B"

[[unit]]
id = "mg:terminal-bench-4-0/default"
desc = "Whether an AI agent can finish hard, frontier-grade terminal work — debugging, systems administration, science, security — inside live machine environments."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "No score for any current profile model (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon) in this variant"
meaningful_gap = 12.4
trust_grade = "B"
```

## Facets

- [[concepts/facets/task|task]]: terminal_ops

## Related benchmarks

- [[entities/benchmarks/hf/long-horizon-terminal-bench]] — Long-Horizon Terminal-Bench
- [[entities/benchmarks/hf/terminal-bench-2-0]] — Terminal-Bench 2.0
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/mg/terminal-bench-2-1]] — Terminal-Bench 2.1
- [[entities/benchmarks/terminal-bench-exact]] — Terminal-Bench 4.0 (exact import)

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://hub.harborframework.com/datasets/terminal-bench/terminal-bench/4>
- <https://huggingface.co/datasets/harborframework/terminal-bench> — HF official mirror of the continuous Terminal-Bench (one repo, one tag per version; `main` tracks the latest). Pin the 4.0 tag before using its scores; score rows are `verified=false`.
