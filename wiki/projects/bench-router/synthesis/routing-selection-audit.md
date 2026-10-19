---
title: >-
  Bench-router routing criteria and uncalibrated constants
category: synthesis
tags: [agentic, coding, reasoning]
sources: ["repo:bench-router@d1a94b1c0164f9a129f37206812a077f70053a8b"]
created: 2026-10-19T01:52:29Z
updated: 2026-10-19T01:52:29Z
as_of: 2026-10-19
summary: >-
  Current automatic and external-choice paths, exact legacy scoring rules, optional cost constraints, and the limits of their empirical grounding.
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-routing-code-evidence.json|2026-10-19-routing-code-evidence.json]]"
---

# Bench-router routing criteria and uncalibrated constants

This audit describes commit `d1a94b1c0164f9a129f37206812a077f70053a8b`. The captured repository sections are the authority for the implementation findings below.

## Two selection paths

| Path | Responsibility |
|---|---|
| Plain `route` | Apply constraints, compute legacy benchmark/cost-tier scores, and select automatically |
| `evaluate` then `route --selection` | Return facts and eligibility; accept a recorded external choice and recheck eligibility |

The bundled skill recommends a cheap semantic decision provider for the second path. The decision workflow passes task requirements, relevant benchmark evidence, effort conditions, missing/stale flags, computed costs, and an explicit quality/cost preference. It has no universal composite-score formula.

## Legacy scoring

Let `a_b` be the benchmark weights after task-category mapping, `C` their observed weight, and `Q_obs` the weighted observed normalized score:

```text
C = sum(a_b for observed benchmarks)
Q_obs = sum(a_b * normalized_score_b for observed benchmarks) / C
Q = C * Q_obs + (1 - C) * 0.5 - 0.1 * (1 - C)
S = Q - lambda_cost * cost_proxy
```

No observation produces `quality=None`. A measured zero remains an observation. Only candidates with `C >= 0.5` receive a ranking score.

| Input | Current setting |
|---|---|
| Cost proxy | `low=0`, `medium=0.5`, `high=1` |
| `quality` priority | `lambda_cost=0` |
| `balanced` priority, the default | `lambda_cost=0.15` |
| `cost` priority | `lambda_cost=0.30` |
| Near tie for balanced/cost | Gap strictly below `0.02`; lower cost tier, then profile ID |
| Exact quality tie | Profile ID |
| No candidate with enough evidence | Eligible configured default, then configured fallback order |

`categories.toml` maps repository coding to 60% exact SWE evidence and 40% AA Coding; terminal work uses 70% exact Terminal evidence and 30% AA Coding. Other categories have their own mappings. Percentile normalization compares scores within a benchmark cohort; it does not yield task-success probabilities.

## Other inputs

| Input | Actual effect |
|---|---|
| Enabled state, exclusions, max cost tier, capabilities, locality, context capacity | Mandatory eligibility checks |
| Live availability | Additional eligibility check during live dispatch |
| Estimated USD cost | Optional per-call ceiling; unknown cost fails when the ceiling applies |
| `task.complexity` | Recorded as a fact; absent from legacy score and selection |
| Task facets, including difficulty | Retrieve relevant evidence; do not alter plain `route` scores |
| Latency or success-rate signals | No registered evaluator in the inspected implementation |

Cost comes from a supplied estimate first, otherwise `(input_tokens * input_price + output_tokens * output_price) / 1_000_000`. Missing or expired inputs are unusable. Prices are supplied externally; the router does not discover them. Cost tiers are independent of dollar estimates.

Benchmark evidence can become unusable when the configuration fingerprint changes or the source exceeds its maximum stale age. A TTL warning alone still permits last-good evidence. Exact-profile evidence weight is reported separately and does not introduce a further legacy bonus.

## Evidence behind the numbers

`03_ROUTING_AND_DATA_SPEC.md` labels the mappings, missing-value prior/penalty, and other constants as policy choices. Its example is synthetic. The inspected policy specification provides no calibration study establishing that these particular constants optimize real task outcomes. This finding is bounded to the inspected material; it does not assert that every numeric choice lacks a rationale.

Replacing these numbers with official starting recommendations still requires a project policy for cross-provider selection. ^[inferred]

## Related

- [[projects/bench-router/bench-router]]
- [[projects/bench-router/synthesis/vendor-guided-routing-proposal]]
- [[concepts/model-effort-selection]]
- [[concepts/facets/difficulty]]
- [[entities/benchmarks/swe-bench-verified-exact]]

## Sources

- [[_raw/_archived/2026-10-19-routing-code-evidence.json]] — immutable capture of relevant sections and complete-file hashes: `routing.py`, `cli.py`, `evidence.py`, `wiki.py`, `categories.toml`, the policy specification, and the decision workflow.
- [Routing implementation](../../../../bench_router/routing.py) — mutable working-tree view.
- [Policy specification](../../../../03_ROUTING_AND_DATA_SPEC.md) — mutable working-tree view.
