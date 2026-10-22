---
title: >-
  Multi-agent pattern selection and benchmark evidence
category: synthesis
tags: [agentic, reasoning, coding]
sources:
  - "conversation:2026-10-21"
  - "conversation:2026-10-22"
  - "repo:bench-router"
  - "url:https://www.anthropic.com/research/building-effective-agents"
  - "url:https://www.anthropic.com/research/multi-agent-research-system"
  - "url:https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns"
  - "url:https://developers.openai.com/api/docs/guides/responses-multi-agent"
  - "url:https://developers.openai.com/api/docs/guides/evaluation-best-practices"
  - "url:https://arxiv.org/abs/2512.08296v3"
  - "url:https://arxiv.org/abs/2609.17306v1"
  - "url:https://arxiv.org/abs/2608.25937v2"
  - "url:https://proceedings.neurips.cc/paper_files/paper/2025/file/934252acd87f254d5d4672fbde283bd2-Paper-Conference.pdf"
  - "url:https://arxiv.org/html/2512.08296v2"
  - "url:https://arxiv.org/abs/2502.00674"
  - "url:https://arxiv.org/abs/2607.20768"
  - "url:https://arxiv.org/abs/2502.19130"
created: 2026-10-22T07:20:11Z
updated: 2026-10-22T07:40:27Z
as_of: 2026-10-22
summary: >-
  Propose pattern candidates after task analysis, then choose the pattern, role assignments, and aggregation together using workflow evidence before dispatch.
provenance:
  extracted: 0.47
  inferred: 0.5
  ambiguous: 0.03
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-22
tier: supporting
relationships:
  - target: "[[concepts/model-effort-selection]]"
    type: extends
  - target: "[[projects/bench-router/synthesis/vendor-guided-routing-proposal]]"
    type: related_to
---

# Multi-agent pattern selection and benchmark evidence

## Context

Bench-router needs to distinguish uncertainty about which agent to select from evidence that multiple agents improve a task. Near-equal individual benchmark scores do not establish that voting, debate, or synthesis will improve the result. ^[inferred]

**Status: research synthesis and unimplemented extension proposal.** The official sources describe patterns and evaluation principles. The placement and data-contract recommendations below are project-specific proposals, not an approved implementation plan or a universal vendor standard. ^[inferred]

## Finding

Generate possible patterns after analyzing the task. Finalize the pattern together with role-specific model/effort assignments, aggregation, and resource limits after retrieving relevant evidence and before freezing the execution plan. This refines the earlier pattern-first recommendation: early selection identifies candidates; it does not irrevocably select a topology before model and workflow evidence is available. ^[inferred]

OpenAI's evaluation guide explicitly states that the decision to use a multi-agent architecture should be driven by application evaluations. Anthropic recommends increasing complexity when justified and identifies task-dependent conditions for parallelization, orchestrator-workers, and evaluator-optimizer. Microsoft recommends the least complex architecture that reliably meets requirements. These are official engineering recommendations, not a common numerical switching rule.

## Task characteristics and candidate patterns

The following mapping combines the inspected guides. The task examples are applications of those criteria, rather than mandatory vendor classifications. ^[inferred]

| Task characteristics | Candidate pattern | Evidence and limits |
|---|---|---|
| Independent documents, code areas, or research directions | Parallel sectioning with synthesis | Anthropic parallelization; OpenAI independent workstreams. Combine distinct findings rather than treating each as a vote on one answer. |
| Repeated judgments with comparable discrete outputs | Independent voting or ensemble | Anthropic voting; Microsoft concurrent orchestration. Define answer equivalence, thresholds, abstention, and unresolved disagreement. |
| Alternative implementations or proposals with a common rubric | Parallel candidates followed by evaluation and selection | Project application of Microsoft's concurrent comparison/selection. Evaluate executable candidates with tests where possible. |
| A draft can improve through concrete feedback | Evaluator-optimizer or maker-checker | Anthropic and Microsoft require clear evaluation or acceptance criteria. Set an iteration limit and a defined outcome when it is reached. |
| Subtasks emerge during exploration | Orchestrator-workers | Anthropic describes dynamic decomposition for research and complex multi-file work. |
| Conflicting perspectives require interaction | Bounded group chat, debate, or council | Microsoft describes guided discussion and maker-checker workflows. Objective completion criteria and discussion overhead matter. |

OpenAI identifies sequential dependence, contention over shared mutable resources, and short tasks as reasons that additional subagents may provide limited benefit. Anthropic's research-system report identifies broad parallel investigations and separate context windows as useful cases, while noting coordination difficulties for tightly coupled work.

Anthropic's research-system report states that most coding tasks involve fewer truly parallelizable subtasks than research, and that its multi-agent system used about 15× the tokens of a chat interaction. That multi-agent system, with an Opus 4 lead and Sonnet 4 subagents, outperformed single-agent Opus 4 by 90.2% on Anthropic's internal research evaluation. The result is specific to breadth-first research and does not transfer to coding.

Microsoft's concurrent-orchestration guidance matches the aggregation method to the output type: majority rule for classification, weighted merging for scored recommendations, and a model-written synthesis for narrative results. It advises against concurrent orchestration when no conflict-resolution strategy exists or when model quota prevents parallel execution. It recommends three or fewer agents in group chat. A maker-checker loop needs an iteration cap and a defined fallback, such as human escalation or the best result returned with a quality warning.

Multiple calls to one model can instantiate these patterns; using different vendors is a separate composition choice. ^[inferred]

## Information required before choosing a pattern

| Input | Decision affected | Dependence on benchmark results |
|---|---|---|
| Subtask boundaries and dependency graph | Parallel, sequential, or dynamic decomposition | Structural analysis first; scores do not reveal the graph. |
| Deliverable and acceptance criteria | Vote, select, synthesize, or revise | Criteria are task inputs; evaluator reliability requires measurement. |
| Shared state and write footprint | Isolation and coordination | Environment inspection first; observed conflicts provide additional evidence. |
| Context, tools, permissions, and availability | Feasibility and specialization | Capability declarations first; actual tool-use reliability is empirical. |
| Quality target, total spending limit, and deadline | Feasible patterns, team size, and iteration limits | Limits are requirements; attainable cost and latency require estimates or measurements. |
| Relevant single-agent success and failure modes | Whether collaboration has improvement headroom | Direct dependence on representative task evaluations. |
| Item-level overlap of model errors | Whether independent voting adds information | Requires aligned per-item results, not just aggregate scores. |
| Checker, selector, and synthesizer performance | Whether generated good answers survive aggregation | Requires role- and generator-dependent evaluation. |
| End-to-end quality, cost, and elapsed time | Final pattern and composition | Requires complete workflow comparisons. |

This dependency table is a project synthesis. A task description can propose a structure without benchmark scores; proving that the structure improves quality needs stronger evidence. ^[inferred]

## How benchmarks can change the pattern

### Single-agent capability changes the benefit of coordination

*Towards a Science of Scaling Agent Systems*, v3 dated 2026-04-08, studies 260 configurations across six agentic benchmarks. It identifies capability saturation: stronger single-agent baselines can leave less benefit for collaboration. Its task-grounded capability measure improves the fitted model over a static intelligence composite. Reported thresholds, including approximately 45% single-agent performance, describe the study's conditions rather than a universal routing boundary. Small evaluation subsets and cross-domain prediction limits constrain transfer.

Earlier versions of the paper (180 configurations, four benchmarks) report three figures. Centralized coordination gained 80.9% on parallelizable tasks such as financial reasoning. Every multi-agent variant lost 39–70% on sequential reasoning tasks. Error amplification was 17.2× for independent agents and 4.4× for centralized coordination. The reported coefficients and R² values differ between versions. Use the parallelizable-versus-sequential direction as evidence and do not treat these figures as stable constants. ^[ambiguous]

### A capability gap among candidates favors repeating the strongest model

*Rethinking Mixture-of-Agents* (ICLR 2025) finds that proposer quality matters more than proposer diversity, and that mixing different LLMs often lowers average proposer quality. Self-MoA aggregates only outputs of the top-performing model and reports +6.6% over MoA on AlpacaEval 2.0, with an average gain of +3.8% across benchmarks including MMLU, CRUX, and MATH. The paper also identifies scenarios in which mixing models helps.

*Are Diversity Metrics Measuring Diversity?* (arXiv 2607.20768, 2026) audits majority-vote gain under capability controls. It reports that simple voting beats the strongest member in only 9.98% of canonical size-3 subsets, although oracle coverage is positive in every subset, and that the diversity measures it tested mostly track capability. Only the abstract was inspected.

Benchmark gaps therefore bear on pool composition: a large gap suggests repeated independent calls to the strongest profile, while a near-tie is a precondition for, not evidence of, useful heterogeneous composition. ^[inferred]

### Task type changes the aggregation protocol

*Voting or Consensus? Decision-Making in Multi-Agent Debate* (Findings of ACL 2025) holds the agents fixed and varies only the decision protocol. Voting improved reasoning tasks by 13.2%, and consensus improved knowledge tasks by 2.8%, relative to other protocols. More agents improved performance, while more discussion rounds before voting reduced it. The aggregation protocol is a task-structure choice; benchmark scores do not select it. ^[inferred]

### Equal aggregate scores conceal different ensemble behavior

In an illustrative 100-question binary task, three models can each score 80%. If all fail on the same 20 questions with the same wrong label, majority voting remains at 80%. If their 20-question error sets are disjoint, majority voting reaches 100%. These are constructed examples, not measured benchmark results. Aggregate near-ties alone cannot distinguish them. ^[inferred]

*Mo' Models, Mo' Problems*, submitted 2026-09-15, compares model-pool selection strategies on scientific reasoning benchmarks and reports that expanding a pool can underperform the strongest constituent model. Different model identities or families are not sufficient evidence of useful complementarity.

### Selection ability can change the aggregation policy

*Candidate supply and answer selection shape the value of LLM judging in multi-agent systems*, v2 dated 2026-08-30, separates candidate generation from final selection. It finds that judge reliability varies with the task, generator, and frequency of correct candidates. A pool can contain a correct answer while the system still selects an incorrect one.

*Debate or Vote* (NeurIPS 2025) finds that majority voting explains most of the studied debate gains across seven NLP benchmarks. Debate therefore needs comparison against independent sampling and voting, rather than an assumption that extra discussion improves answers. ^[inferred]

### Evidence levels must remain distinct

| Evidence | Supported use | Unsupported shortcut |
|---|---|---|
| Public model aggregate | A prior about relevant component capability | Treating a leaderboard gap as the expected gain from collaboration |
| Exact model/effort/harness evaluation | Performance under recorded component conditions | Assuming that the same profile is a good judge or coordinator |
| Aligned per-item outputs | Error overlap and candidate coverage | Claiming actual ensemble success from oracle coverage alone |
| Complete workflow comparison | Observed benefit of a recorded pattern and composition | Generalizing to other models, tools, tasks, or budgets without checking |
| Current execution's outputs and checks | A predeclared stop, retry, or escalation condition | Using post-run measurements as if they were known before dispatch |

These evidence boundaries are routing-design interpretations. ^[inferred]

## Proposed integration with bench-router

The inspected documentation on 2026-10-22 makes `vendor-guided` the default and retains weighted scoring under explicit `legacy` policy. The older [[projects/bench-router/synthesis/routing-selection-audit]] and [[projects/bench-router/synthesis/vendor-guided-routing-proposal]] retain their 2026-10-19 evidence scope; use the repository's current policy documentation for implemented behavior.

The proposed sequence is task/environment analysis, candidate patterns and roles, role-specific suitability and evidence retrieval, comparison of complete execution plans, plan freeze, dispatch, and bounded verification. It does not require running a new benchmark for every request: request-time selection can consume previously measured workflow evidence. ^[inferred]

1. Extend the facts produced around `decision.analysis_request()` and `_analysis()` with decomposition, dependencies, independent verification, and shared-state requirements. File paths and workload labels alone may not establish these facts; accept bounded inspection results and preserve unknowns. ^[inferred]
2. Generate a small set of candidate patterns, retaining a single-agent baseline when feasible. Decompose each pattern into explicit worker, checker, selector, or synthesis responsibilities. ^[inferred]
3. Apply `fit_request()` and relevant evidence retrieval to each role's actual task. Filtering every candidate solely against the original end-to-end task could discard a useful checker or specialist. ^[inferred]
4. Add an outer plan-selection step around the existing profile-selection boundaries. Compare pattern, role assignments, model/effort settings, aggregation, expected quality, and total resource use together. The existing conditional `benchmark` request rates relevance; it is not a general workflow evaluator. ^[inferred]
5. Finalize before `parallel.run_group()` freezes its plan and starts workers. Preserve the current all-members-before-execution validation boundary. Define any later expansion or refinement as a bounded policy with a resource ceiling and traceable reasons. ^[inferred]

The natural activation point is `decision.resolve()`. When several fit profiles remain in the final pool, it breaks the tie by `default_profile`, then `fallback_order`, then ID, and records `tie_resolved_by_configuration`. A missing majority winner in `_majority()` is a second signal. Either signal can trigger a collaboration check, but only when the analysis stage already permitted a pattern. After that check, the CodeBurn quota preflight should run for the full agent count and fall back to single-agent dispatch if quota is insufficient. ^[inferred]

The `bench_router/` code inspected on 2026-10-22 has no standard error, confidence interval, or per-item score field. A tie threshold therefore cannot yet be expressed in units of measurement noise. Some apparent near-ties may be noise, and others may be real differences hidden by coarse aggregates. ^[inferred]

The current `parallel.plan()` fanout path excludes already selected profiles. That is a profile-selection policy, not evidence that different profiles are always preferable to repeated independent calls to the same profile. A future pattern contract should express whether repeated profiles are permitted. ^[inferred]

## Evaluation data needed

The inspected manual benchmark import stores rows keyed by model, harness, and effort with one raw score. These rows do not themselves provide aligned item-level predictions, error overlap, or role-dependent aggregation outcomes.

Preserve existing model evidence and add a distinct workflow evaluation record with the following information. This is a proposed contract, not an implemented schema. ^[inferred]

- Task family, dataset revision, held-out split, scoring rubric, sample size, repetitions, and uncertainty.
- Pattern and policy versions; role-to-model/effort assignments; prompts, tools, context-sharing rules, and environment.
- Agent count, concurrency, iteration limits, answer aggregation, stopping conditions, and fallback behavior.
- Per-item outputs and correctness or rubric judgments, including generator, checker, and final-selection outcomes.
- Final quality, total usage and USD cost, wall-clock latency, failures, and the matched single-agent baseline.

For cross-pattern experiments, keep tasks, scoring, environment, and the declared resource comparison comparable while intentionally varying the pattern. Do not require the treatment itself to be identical. Benchmark score aggregation and the policy for combining agent answers are separate concepts. Compare both quality at a matched budget and cost/latency to reach a target quality where useful. ^[inferred]

Missing workflow evidence should remain explicit. Structural necessity or a user's explicit collaboration request can justify a pattern without establishing an empirical quality gain. A near-tie between model scores alone does not establish such a gain. ^[inferred]

## Open questions

- Which representative task families and acceptance rubrics should qualify each pattern?
- Which patterns and model combinations meet quality targets within total cost and latency limits?
- How should missing workflow measurements affect automatic selection and uncertainty reporting?
- How should live verification trigger bounded extra work without changing a frozen plan silently?

## Related

- [[projects/bench-router/bench-router]]
- [[concepts/model-effort-selection]]
- [[synthesis/vendor-guided-model-selection]]
- [[projects/bench-router/synthesis/vendor-guided-routing-proposal]]
- [[projects/bench-router/synthesis/routing-selection-audit]]
- [[concepts/facets/agent_signal]]

## Sources

The source claims and repository observations were inspected in the captured discussion on 2026-10-21 and 2026-10-22. This capture preserves that evidence scope; it does not claim a fresh fetch or a complete archived copy of each source.

- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents) — published 2024-12-19; workflow selection conditions.
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system) — published 2025-06-13; parallel research and coordination trade-offs.
- [Microsoft: AI agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) — concurrent aggregation, group chat, and maker-checker criteria.
- [OpenAI: Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent) — independent workstreams and limited-benefit cases.
- [OpenAI: Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) — evaluation-driven architecture choice and evaluator validation.
- [Towards a Science of Scaling Agent Systems, v3](https://arxiv.org/abs/2512.08296v3) — revised 2026-04-08; task/model/architecture interactions and limitations.
- [Mo' Models, Mo' Problems, v1](https://arxiv.org/abs/2609.17306v1) — submitted 2026-09-15; model-pool selection and achieved performance.
- [Candidate supply and answer selection, v2](https://arxiv.org/abs/2608.25937v2) — revised 2026-08-30; generator-dependent judge reliability.
- [Debate or Vote, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/file/934252acd87f254d5d4672fbde283bd2-Paper-Conference.pdf) — independent voting as a debate baseline.
- [Towards a Science of Scaling Agent Systems, v2](https://arxiv.org/html/2512.08296v2) — earlier version; parallelizable versus sequential figures and error amplification.
- [Rethinking Mixture-of-Agents](https://arxiv.org/abs/2502.00674) — ICLR 2025; quality-diversity trade-off and Self-MoA.
- [Are Diversity Metrics Measuring Diversity?](https://arxiv.org/abs/2607.20768) — 2026; capability-controlled majority-vote audit (abstract only).
- [Voting or Consensus?](https://arxiv.org/abs/2502.19130) — Findings of ACL 2025; decision protocol by task type.
- [Routing policy documentation](../../../../docs/vendor-guided-routing.md), [decision stages](../../../../bench_router/decision.py), [parallel planning](../../../../bench_router/parallel.py), and [benchmark import](../../../../bench_router/data.py) — mutable repository evidence; observations dated 2026-10-22.
