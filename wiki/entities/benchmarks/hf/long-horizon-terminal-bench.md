---
title: >-
    Long-Horizon Terminal-Bench
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/IntelligenceLab/Long-Horizon-Terminal-Bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Whether LLM agents sustain useful work in a containerized terminal over hundreds of steps
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Long-Horizon Terminal-Bench

Whether LLM agents sustain useful work in a containerized terminal over hundreds of steps.

From the dataset card (`IntelligenceLab/Long-Horizon-Terminal-Bench`):

> Long-Horizon Terminal-Bench (LHTB) Leaderboard: the panel at the top of this page has two views. Use the Task menu in its top-right corner to switch between Lhtb2 Solved (LHTB 2.0, out of 77 tasks) and Lhtb Solved (LHTB 1.0, out of 46). Both count soft solves (tasks with reward ≥ 0.95), not hard solves (reward = 1.0).

## Index

```toml
[[unit]]
id = "hf:IntelligenceLab/Long-Horizon-Terminal-Bench"
desc = "Whether LLM agents sustain useful work in a containerized terminal over hundreds of steps"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"], shape = ["long_horizon"] }
reason = "Leaderboard API (2026-10-18): 9 rows, 9 models, 0 verified, 9 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/shape|shape]]: long_horizon
- [[concepts/facets/task|task]]: terminal_ops

## Related benchmarks

- [[entities/benchmarks/hf/terminal-bench-2-0]] — Terminal-Bench 2.0
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/mg/terminal-bench-2-1]] — Terminal-Bench 2.1
- [[entities/benchmarks/mg/terminal-bench-4-0]] — Terminal-Bench 4.0
- [[entities/benchmarks/terminal-bench-exact]] — Terminal-Bench 4.0 (exact import)

## Sources

- <https://huggingface.co/datasets/IntelligenceLab/Long-Horizon-Terminal-Bench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
