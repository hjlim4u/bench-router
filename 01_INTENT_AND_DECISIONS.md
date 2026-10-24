# User Intent and Design Decisions

Updated: 2026-10-24. Current behavior and contracts follow [Documentation Guide](00_START_HERE.md), [Vendor-guided Policy](docs/vendor-guided-routing.md), and [Projects Execution](docs/projects.md).

## Starting Point

The user requested an investigation into whether existing OSS/tools could be utilized, and a design objectively cross-verified against other AI responses prior to implementation. Early documents were written as handoffs for other CLI Agents to continue implementation, and now serve as design decision records for the implemented router.

The user requirements below preserve the original goals. During implementation, weighted-sum automatic selection was removed, replaced with official guideline-based evaluation and upstream final selection. Past external tool surveys represent point-in-time records and are not comprehensive head-to-head comparisons of current versions.

## User Requirements

1. The Orchestrator determines prompt complexity and delegation necessity.
2. When delegating, it constructs the context and subagent prompt and invokes the script.
3. The script retrieves relevant leaderboards and benchmarks from API/cache to select an appropriate Agent.
4. Delivers the prompt to the selected Agent.
5. Returns results to the Orchestrator upon completion so it can decide whether to proceed with additional rounds or terminate.
6. Minimizes frequent data API calls and prompt-to-benchmark retrieval costs.
7. Maximizes herdr capabilities for subagent invocation, results, and state tracking to minimize custom implementation scope.
8. Avoids unnecessary standalone implementation if existing tools satisfy requirements.

## Core Boundaries

| Subject | Responsibility |
| --- | --- |
| Orchestrator | Delegation decision, task decomposition & team formation, task/facets & context, final selection among multiple candidates, result review / additional rounds / budget |
| bench-router | Snapshot collection & normalization, hard constraints, official guidance suitability & comparative evidence & selection history, execution dispatch & result contract validation |
| herdr-projects / herdr | Worktree & pane management, Agent execution, input delivery, actual state observation & recovery |
| Subagent | Task execution, per-run result file generation, reporting completed / unexecuted / error information |
| Periodic Execution Tool | Runs periodic refresh; uses whatever is present locally among cron/systemd/launchd |

Validating result files and maintaining a small local receipt to prevent duplicate submission is essential glue code. This does not mean building a separate worker queue, heartbeat, custom terminal detector, or lifecycle server.

## Design Decision Record

| ID | Decision | Rationale | Status |
| --- | --- | --- | --- |
| D01 | Routing unit is a Profile (Agent CLI + Model + Configuration) | Even with identical models, harness, reasoning effort, tools, and versions differ | Established principle |
| D02 | `route` never calls benchmark APIs | Eliminates user request latency and external API load | Established principle |
| D03 | `refresh` is a separate command and OS periodic task | Sufficient without continuous services or Redis | v1 default |
| D04 | SQLite history + small JSON snapshot | Standard library, simplified read path, reproducible evidence | v1 default |
| D05 | Basic evaluation uses L1 rules → general; vendor-guided uses semantic analysis | Early L0 categories input removed; explicit task characteristics use `task.facets` | Implemented |
| D06 | Bounded phased decisions via Jev or native bench-decider, no embeddings | Structures task analysis, vendor guide starting points, and evaluation relevance | Implemented |
| D07 | Invoke herdr-projects public CLI via subprocess argv (2026-10-15) | Reuses project execution layer. Router maintains result contract and admission | Established principle |
| D08 | Verify Projects approval/done or headless termination + per-run result contract | Process exit is not proof of task success | Established principle |
| D09 | Single-machine, fresh workers, support wait-ms/collect and explicit resume | Remote execution and automated session pooling are not implemented | Implemented |
| D10 | Separate selection, collection, and execution into distinct functions | Enables dry-run and fixture testing without building a plugin framework | v1 default |
| D11 | Validate result optimality through real-task comparative evaluation | External rankings do not equate to individual task success probability | Established principle |
| D12 | Pin and record API responses and CLI schemas by version | Controls divergence across dynamic data, docs, and installed versions | Established principle |
| D13 | Final selection, metric trade-offs, and budget belong to Orchestrator; Router provides factual summary, hard constraints, selection records, and execution (2026-10-13) | Adding metrics will not alter Router policy, avoiding nonsensical blends of USD and percentiles. Evidence: `docs/routing-extensibility-review.md` | Established principle |
| D14 | New metric = one line in `METRICS` (+ one `CONSTRAINTS` function only when filtering), unregistered metrics passed through (2026-10-13) | Extends without plugin framework or rule engine. Contract: `docs/routing-contracts.md` | v1 default |
| D15 | Policy 6: analysis → vendor guidance → benchmark if needed; multiple viable candidates deferred to upstream selection | Avoids generalizing guidance principles across vendors or aggregating disparate evaluations | Implemented |
| D16 | Candidate evaluation schema 4.0 (`--format 3`), automatic selection 5.0, external selection 6.0 | Decouples CLI format numbers, JSON schemas, and selection policy versions | Implemented |
| D17 | Group 2.0 allows repeated selections, `max_parallel` 1–4, aggregate admission 4 | Maintains per-instance worktrees and receipts | Implemented |

## Elements Preserved from Other AI Drafts

- Request/refresh path separation, local cache, last-known-good snapshot, atomic JSON replacement.
- Closed categories and Orchestrator hints, deterministic selection applying hard constraints first.
- Model alias normalization and distinguishing agent+model results.
- Leveraging `herdr start/prompt/wait/read` and returning result files.
- `dry-run`/`explain`, recording selection evidence, baseline dates, and feedback.
- Keeping embeddings and decision models as optional future enhancements.

## Early Draft Review Record (As of Review Date)

The coverage shrinkage, default fallback, and determinism notes below reflect early design comparisons. Currently, quality/coverage remains only for basic diagnostic evaluation; cost deductions, default/fallback, and near-tie automatic selections have been removed. Semantic decisions are replayed via stored phase responses and digests.

| Draft Assumption | Handoff Baseline |
| --- | --- |
| Single call for complete AA list + math index | Paginate through actual API; do not assume math index on current Free schema |
| LMArena code = general coding | webdev is a web development proxy; not used as direct score for repo edits or all code generation |
| Automatic mixing of Terminal-Bench 2.0 / latest | Pin benchmark versions; official site currently shows 4.0, do not mix with 2.0 rows |
| Missing harness penalty of model score × 0.9 | Not an empirical harness adjustment; cross-substituting scores from different evals forbidden in MVP |
| Only reweighting missing score weights | Combine coverage with shrinkage on missing data; partial data should not gain an unfair advantage |
| 7-day stale route triggers automatic refresh | v1 `route` only emits a warning; `refresh` handled by separate timer or explicit command |
| Missing cache → unconditionally delegate to default | Apply identical hard constraints to default; terminate with no candidates if missing or ineligible |
| Idle Agent reused if name matches | MVP does not reuse; future reuse must verify cwd, config fingerprint, ownership, and lock |
| Idle/done + result file exists = completed | Verify run ID, nonce, profile, result hash, path, and manifest state |
| Same input always yields same output | Deterministic when task + snapshot + config + explicit availability snapshot are identical |
| 70% match with human-selected Agent = success | Reference metric only; evaluate by real success rate, cost per success, and latency against baseline |
| Switchyard 0.2 baseline only | Verified official README mentions 0.3.0 and sub-agent strategies; avoid asserting hard bounds |
| L0 cost exactly 0, embeddings guaranteed 5–20ms | Eliminate extra calls by reusing analysis; measure actual token costs and latencies |
| Jev pricing and English-centricity assumed fixed | Confirm official accessibility, contracts, pricing, and multilingual suitability locally; disabled by default |

## Rationale for Implementation

Reviewed tools (RouteLLM, Switchyard, semantic-router) provide reusable routing components. Based solely on provided materials and verified official documentation, no off-the-shelf setup was found that immediately replaces the entire pipeline: **external benchmark collection → real CLI profile matching → herdr delegation**. This does not prove no alternative exists in the broader ecosystem.

Therefore, minimal collection, selection, and herdr glue code is implemented. If existing repositories/tools are verified to satisfy these contracts during implementation, replace with them and record which capabilities and verifications were reused.

## Out of Scope

Custom Agent runtimes, intra-agent per-turn model swapping, automated weight training, vector databases, web dashboards, Kubernetes, automated remote file synchronization, and automatic herdr plugin installation are out of scope. The implemented parallel execution adapter is not a general pattern, DAG, voting, or budget scheduler. Benchmark tasks themselves are not re-executed daily.

Python is the recommended default. If a local repository is already adequately implemented in another language, prioritizing contract compliance over rewriting is preferred.
