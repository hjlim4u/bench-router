---
title: >-
    Terminal-Bench 2.0
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/harborframework/terminal-bench-2.0", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Read-only mirror of Terminal-Bench 2.0; the HF leaderboard is unofficial, the official one is tbench.ai
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Terminal-Bench 2.0

Read-only mirror of Terminal-Bench 2.0; the HF leaderboard is unofficial, the official one is tbench.ai.

From the dataset card (`harborframework/terminal-bench-2.0`):

> Warning: The leaderboard above is unofficial. The official leaderboard is https://www.tbench.ai/leaderboard/terminal-bench/2.0, in which entires are audited for correct configuration, results show which agent harness is used, and verified trajectories are publicly viewable. Warning: The dataset is a read-only mirror.

## Index

```toml
[[unit]]
id = "hf:harborframework/terminal-bench-2.0"
desc = "Read-only mirror of Terminal-Bench 2.0; the HF leaderboard is unofficial, the official one is tbench.ai"
metric = "pass_pct"
status = "current"
adoption = "archive"
facets = { task = ["terminal_ops"] }
reason = "Superseded by Terminal-Bench 4.0 (mg:terminal-bench-4-0/max and terminal_exact); unofficial read-only HF mirror (40 rows, 0 verified, 0 profile models)"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: terminal_ops

## Related benchmarks

- [[entities/benchmarks/hf/long-horizon-terminal-bench]] — Long-Horizon Terminal-Bench
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/mg/terminal-bench-2-1]] — Terminal-Bench 2.1
- [[entities/benchmarks/mg/terminal-bench-4-0]] — Terminal-Bench 4.0
- [[entities/benchmarks/terminal-bench-exact]] — Terminal-Bench 4.0 (exact import)

## Sources

- <https://huggingface.co/datasets/harborframework/terminal-bench-2.0>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
