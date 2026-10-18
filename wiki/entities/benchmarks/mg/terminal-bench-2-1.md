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
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Terminal-Bench 2.1

Whether an AI agent can actually operate a real command line to debug code, administer systems, and fix security issues.

## Key Ideas

- Category: agentic / Terminal ops
- Lifecycle: current, trust grade B, meaningful gap 10.6 points, 89 items
- Variants: default
- Task shape: One task instantiates a fresh, isolated container/VM environment and gives the agent a single natural-language objective — for example, get a broken build compiling, close off a mis-configured service's known vulnerability, or stand up and wire together a small data-processing or model-training pipeline — with no further hand-holding. The agent works purely through a terminal: it can run arbitrary multi-turn shell commands, inspect output, and iterate, the same way a human sysadmin or engineer would. When it finishes (or times out), grading runs a hidden, task-specific automated test suite against the resulting state of the environment — files written, services running, data produced — rather than against anything the agent said; there is no reference answer to text-match and no credit for output that merely looks right. This describes the general task format the maintainers themselves describe (compiling code, configuring servers, training models, debugging systems, fixing security issues) — not any single specific item's actual instructions.

Related: [[entities/benchmarks/mg/deepswe]], [[entities/benchmarks/mg/toolathlon-verified]]

## Index

```toml
[[unit]]
id = "mg:terminal-bench-2-1/default"
desc = "Whether an AI agent can actually operate a real command line to debug code, administer systems, and fix security issues."
metric = "pass_pct"
status = "current"
adoption = "archive"
facets = { task = ["terminal_ops"] }
reason = "Superseded by Terminal-Bench 4.0 (mg:terminal-bench-4-0/max and terminal_exact): vals.ai archived its 2.1 board (checked 2026-09-30) and neither tbench.ai nor AA evaluates gpt-6.1-sol or gemini-4-argon on 2.1"
meaningful_gap = 10.6
trust_grade = "B"
```

## Facets

- [[concepts/facets/task|task]]: terminal_ops

## Related benchmarks

- [[entities/benchmarks/hf/long-horizon-terminal-bench]] — Long-Horizon Terminal-Bench
- [[entities/benchmarks/hf/terminal-bench-2-0]] — Terminal-Bench 2.0
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/mg/terminal-bench-4-0]] — Terminal-Bench 4.0
- [[entities/benchmarks/terminal-bench-exact]] — Terminal-Bench 4.0 (exact import)

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://hub.harborframework.com/datasets/terminal-bench/terminal-bench-2-1/6>
- <https://huggingface.co/datasets/harborframework/terminal-bench-2.1> — HF official mirror (score rows `verified=false`)
