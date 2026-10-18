---
title: >-
    Terminal-Bench-Science
category: entities
tags: [benchmark, hf-official, agentic, reasoning]
sources: ["url:https://huggingface.co/datasets/harborframework/terminal-bench-science", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Real-world computational research workflows across the sciences, run in a terminal
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Terminal-Bench-Science

Real-world computational research workflows across the sciences, run in a terminal.

From the dataset card (`harborframework/terminal-bench-science`):

> Terminal-Bench-Science The primary source is hosted on GitHub, please open issues and pull requests there, not here. Terminal-Bench-Science is a benchmark of real-world computational research workflows across the life, physical, earth, mathematical, and engineering sciences. Like Terminal-Bench, it's a continuous benchmark: releases are published as tags on the source repo.

## Index

```toml
[[unit]]
id = "hf:harborframework/terminal-bench-science"
desc = "Real-world computational research workflows across the sciences, run in a terminal"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops", "science_reasoning"] }
reason = "Leaderboard API (2026-10-18) returned no rows; no model scores are published yet. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: science_reasoning, terminal_ops

## Related benchmarks

- [[entities/benchmarks/hf/long-horizon-terminal-bench]] — Long-Horizon Terminal-Bench
- [[entities/benchmarks/hf/mmmu-pro]] — MMMU-Pro
- [[entities/benchmarks/hf/researchclawbench]] — ResearchClawBench
- [[entities/benchmarks/hf/terminal-bench-2-0]] — Terminal-Bench 2.0
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/mg/gpqa-diamond]] — GPQA Diamond

## Sources

- <https://huggingface.co/datasets/harborframework/terminal-bench-science>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
