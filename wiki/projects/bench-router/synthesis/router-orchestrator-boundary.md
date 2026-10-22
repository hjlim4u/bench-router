---
title: >-
  Router and orchestration-layer responsibility boundary
category: synthesis
tags: [agentic, coding]
sources:
  - "conversation:2026-10-22"
  - "conversation:2026-10-23"
  - "repo:bench-router@2d879cd"
  - "repo:docs/orchestration-boundary.md"
created: 2026-10-22T22:22:22Z
updated: 2026-10-22T22:49:39Z
as_of: 2026-10-23
summary: >-
  Original proposal for a pattern-agnostic router, with a 2026-10-23 cross-check linking the consolidated design and corrections.
provenance:
  extracted: 0.55
  inferred: 0.45
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-22
tier: supporting
relationships:
  - target: "[[projects/bench-router/synthesis/multi-agent-pattern-selection]]"
    type: related_to
  - target: "[[projects/bench-router/bench-router]]"
    type: related_to
---

# Router and orchestration-layer responsibility boundary

## Cross-check — 2026-10-23

The [consolidated design](../../../../docs/orchestration-boundary.md) compares this proposal with the earlier design in `docs/orchestration-boundary.md` against repository commit `2d879cd`. It is the current design recommendation, not an implemented contract or human review approval. The original proposal below is retained for provenance. ^[inferred]

- The boundary concerns ownership of workflow decisions, not whether role words appear in task descriptions or fit evidence.
- Current uncertainty is decision-level; a missing benchmark majority can trigger the relevance stage. A public candidate assessment needs explicit diagnostic scopes and an external-selection binding contract because selection 3.0 is bound to the router's resolved profile.
- Repeated selections are still rejected by the current validator. Hypothetical normalized groups using repeated 2.0 and 3.0 selections passed fake execution, separate worktree/run identity, asynchronous collection, replay without resubmission, and stale-input rejection. This supports a small follow-up change; it is not live validation.
- Resource observations/admission belong to the execution adapter; topology and budget allocation remain upstream. Current CodeBurn preflight does not reserve capacity for N runs.
- Static call compilation generalizes to an upstream state-and-observation policy for dynamic workflows. Group schema 1.0 compatibility does not require switching its default routing policy to `legacy`.

## Context

Decomposing a request into subtasks, analysing their dependencies, and choosing a multi-agent pattern belong to the layer that calls bench-router. Benchmark evidence can influence that choice, which is why [[projects/bench-router/synthesis/multi-agent-pattern-selection]] was researched. Making the router own the pattern decision would make its responsibility too broad.

**Status: unimplemented design proposal.** It has not been reviewed or approved. ^[inferred]

## Decision

The router is a pattern-agnostic **single-task profile assignment service**. A pattern is a composition of router calls made by the calling layer, so adding or changing a pattern needs no router change. ^[inferred]

Boundary test: if a pattern name or role name appears in router input or output, the boundary has been crossed. ^[inferred]

| Question | Owner |
|---|---|
| Subtask decomposition, dependency graph, shared state | Calling layer |
| Candidate patterns, final pattern, roles, aggregation, iteration limits | Calling layer (needs workflow evidence) |
| Splitting total budget, deadline, and quota across agents | Calling layer (`docs/orchestrator.md` already assigns group totals to the Orchestrator) |
| Which profiles fit **one** task, with what evidence and uncertainty | Router (analysis → fit → benchmark → resolve in `bench_router/decision.py`) |
| Whether a fixed assignment can run now (constraints, availability, digest, quota) | Router (`apply_record`, `herdr.probe_profiles`, CodeBurn preflight) |

## Reasoning

### Earlier integration proposals that cross the boundary

The "Proposed integration" steps in [[projects/bench-router/synthesis/multi-agent-pattern-selection]] would put pattern decisions into the router. ^[inferred]

- Step 1 adds decomposition and dependency facts to `analysis_request()`.
- Step 4 adds an outer plan-selection step inside the router.
- Step 5 uses `resolve()` ties or a missing `_majority()` winner to trigger a collaboration check.

Under this boundary, ties and missing majorities stay **uncertainty codes that are only reported**. The calling layer decides whether they justify collaboration. Step 3 (role-specific fit) needs no router change: when each role is submitted as its own task, the fit stage already judges that role's actual work. ^[inferred]

### Pattern policies already inside the router

- Group schema 1.0 fanout in `parallel.plan()` picks k *different* profiles through `omit_profiles=picked`. That is a "diverse fanout" pattern built into the router.
- Group schema 2.0 `validate_group()` rejects duplicate profiles in `selections`, which encodes "diversity is better". This prevents repeated calls to the strongest profile (Self-MoA), which the pattern research supports when there is a capability gap.

Proposed treatment: keep 1.0 as legacy with no new extensions, and remove the duplicate-profile check from 2.0. Member labels are index-based (`t1-1`, `t1-2`) and each label gets its own worktree, so repeated profiles probably do not collide. This has not been tested. ^[inferred]

## Router primitives (pattern-agnostic)

1. **One role = one ordinary task.** No `role` field is added. A checker or synthesizer is expressed through the task's summary, prompt, acceptance criteria, and facets. ^[inferred]
2. **Candidate-pool output as a contract.** `decision.evaluation` already holds `fits`, `comparisons`, `comparison_scopes`, and `uncertainty` for each candidate, but only as internal structure. Documenting these fields as a versioned output lets the calling layer build pools from them. Examples: repeat the strongest profile when the gap is large, or consider a mixed pool on a near-tie. Uncertainty codes such as `tie_resolved_by_configuration`, `comparable_evaluation_missing`, and `model_proxy_comparison` should be stable contract values. ^[inferred]
3. **Execution by stage.** Group 2.0 is the substrate for a single parallel stage. Sequential and iterative patterns (maker-checker, pipelines, orchestrator-workers) are built by the calling layer, which issues one `route`/`dispatch` per step with a new round. The router gets no DAG executor. ^[inferred]
4. **Preflight for N concurrent agents.** Whether k concurrent runs of one profile fit within quota is an executability question, so it can legitimately belong to the router. The simpler split has the router report quota facts and the calling layer sum them and reduce the plan. Whether CodeBurn exposes concurrency-relevant quota data has not been checked. ^[inferred]
5. **Roles whose inputs arrive later.** A checker or synthesizer prompt contains other roles' outputs, so its digest cannot be bound at plan time. Recommended: call `route` when the inputs exist. The frozen upstream plan records the role specification and assignment policy, and any changed selection is recorded with a traceable reason. Making the internal `check_digest=False` bypass public is not recommended, because it blurs the validation boundary. ^[inferred]

## Calling-layer extension point

Each pattern is a compiler from an upstream plan to a sequence of router calls. ^[inferred]

```
task analysis → candidate patterns (including a single-agent baseline)
  → per pattern: role nodes → route each node (read evaluation output)
  → compare plans (quality evidence, cost, latency, quota)  ← workflow evidence store (calling layer)
  → freeze plan → run stages (group 2.0 / route+dispatch) → aggregate and apply stop conditions
```

- Adding a pattern adds one compiler entry. The router, `guidelines.toml`, and the wiki index stay unchanged.
- Workflow evaluation records (pattern, role assignments, per-item outcomes, end-to-end quality and cost) belong to a store owned by the calling layer. Router benchmark units keep holding per-profile capability evidence. Judge reliability that can be measured per profile can still use the existing unit and facet scheme. ^[inferred]

## Implications

- Candidate next steps: allow repeated profiles in group 2.0 with a `test_p3.py` case, and document the candidate-pool and uncertainty-code contract in `docs/routing-contracts.md`.
- Every role node runs its own analysis stage. `decision_cache` reuses identical requests by digest, but distinct role tasks each cost a decision call. ^[inferred]
- If this boundary is accepted, rewrite the "Proposed integration" section of [[projects/bench-router/synthesis/multi-agent-pattern-selection]] to match it.

## Related

- [[projects/bench-router/bench-router]]
- [[projects/bench-router/synthesis/multi-agent-pattern-selection]]
- [[projects/bench-router/synthesis/vendor-guided-routing-proposal]]
- [[concepts/model-effort-selection]]

## Sources

- Conversation on 2026-10-22 exploring how to separate the calling layer's pattern decisions from router responsibilities.
- Repository observations at commit `2d879cd`: [decision stages](../../../../bench_router/decision.py), [parallel planning](../../../../bench_router/parallel.py), and [Orchestrator integration](../../../../docs/orchestrator.md). These files can change.
