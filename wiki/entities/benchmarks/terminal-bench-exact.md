---
title: >-
    Terminal-Bench 4.0 (exact import)
category: entities
tags: [benchmark, exact, agentic]
relationships:
  - target: "[[entities/benchmarks/mg/terminal-bench-4-0]]"
    type: related_to
sources: ["repo:bench_router/data.py"]
summary: >-
    Manual exact import and official public-leaderboard model-proxy evidence for Terminal-Bench 4.0.
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Terminal-Bench 4.0 (exact import)

Manual Terminal-Bench 4.0 import matched to the profile's harness and effort. The import contract is `EXACT_PINS` in `bench_router/data.py`.

The automatic public leaderboard preserves its published model, agent and effort, but has no installed profile harness/version proof. It is model-proxy evidence; the manual import remains the only exact-profile path.

Related: [[entities/benchmarks/mg/terminal-bench-4-0]]

## Index

```toml
[[unit]]
id = "terminal_exact"
desc = "Completion rate of multi-step tasks in real terminal environments"
metric = "pass_pct"
status = "current"
adoption = "active"
reason = "Collected and matched per profile harness and effort; complements mg:terminal-bench-4-0/max (vals-ai mini-swe-agent model-proxy)"
facets = { task = ["terminal_ops"] }

[[unit]]
id = "terminal_proxy"
desc = "Official Terminal-Bench 4.0 public leaderboard completion rate, compared only within the published agent scaffold"
metric = "pass_pct"
status = "current"
adoption = "active"
reason = "Automatic source preserves model, effort, agent label and trial count but does not claim installed harness equivalence"
facets = { task = ["terminal_ops"] }
```

## Facets

- [[concepts/facets/task|task]]: terminal_ops

## Related benchmarks

- [[entities/benchmarks/hf/long-horizon-terminal-bench]] — Long-Horizon Terminal-Bench
- [[entities/benchmarks/hf/terminal-bench-2-0]] — Terminal-Bench 2.0
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/mg/terminal-bench-2-1]] — Terminal-Bench 2.1
- [[entities/benchmarks/mg/terminal-bench-4-0]] — Terminal-Bench 4.0
- [[entities/benchmarks/swe-bench-verified-exact]] — SWE-bench Verified (exact import)

## Sources

- `bench_router/data.py` `EXACT_PINS`, `validate_import`
