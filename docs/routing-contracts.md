# Multi-Criteria Routing Contracts

Updated: 2026-10-24. Implementation: `routing.py`, `decision.py`, `cli.py`, `herdr.py`, `parallel.py`. Preserves candidate evaluation, metrics, and constraint boundaries from the initial 2026-10-13 design; removed legacy automatic selection procedures are excluded from the current contract.

## 0. Goals and Responsibilities

The Router provides facts collation, hard constraint checking, official guide suitability, comparable evaluations, selection records, and execution dispatch. The upstream Orchestrator decides task decomposition, team formation, final selection, global budget allocation, and result adoption. There is no general-purpose plugin loader, rule engine, unit-conversion DSL, or workflow scheduler.

The default selection policy is [Vendor-guided Policy 6](vendor-guided-routing.md). Multiple viable candidates require upstream selection and are never reduced via weighted sums, near-tie logic, or default/fallback priorities.

## 1. Contract A — Separation of Candidate Assessment and Selection

### 1.1 Common Boundaries

| Function / CLI | Responsibility |
|---|---|
| `routing.assess()` | Facts, constraints, and optional benchmark evaluation for all profiles in ID order. Does not select. |
| `routing.evaluate()` / `evaluate --format 2` | Default schema 2.0 facts, constraints, and category benchmark quality/coverage. |
| `routing.evaluate_v1()` / `evaluate --format 1` | Schema 1.0 candidates/excluded compatibility format. |
| `decision.evaluate()` / `evaluate --format 3` | Schema 4.0 phased semantic judgments, candidate suitability, observations, comparisons, and diagnostics. |
| `decision.bind()` / `select` | Generates upstream selection record 6.0 from a completed format 3 assessment. |
| `routing.route()` → `decision.route()` | Policy 6 decision packets, bounded single-candidate selection 5.0, and selection replay. |
| `routing.apply_selection()` | Explicit override for selection 2.0 or `--profile`; checks current constraints. |

CLI `--format 3` is distinct from JSON schema version `4.0`. `select` does not accept format 1 or 2 results. All evaluate formats run offline without executing workers, writing files, or calling external decision APIs.

### 1.2 Default Benchmark Evaluation

`assess()` invokes `benchmark_evaluation()` directly only for candidates passing constraints. Evaluation results consist of `status: ok|insufficient|unavailable`, `quality`, `coverage`, `exact_evidence_weight`, and `evidence`. Output serialization attaches `coverage_band`. Candidates remain even when evidence is missing; disqualification is governed strictly by hard constraints.

Coverage indicates benchmark evidence completeness, not the overall confidence of the final decision. Category weights, percentiles, and quality formulas reside in [Data Specification](../03_ROUTING_AND_DATA_SPEC.md). `score`, `legacy_score`, and `cost_proxy` are omitted from output; candidate lists follow profile ID order. Adding a new evaluator requires appending its name and function call to `evaluations`. There is no separate `EVALUATORS` registry.

### 1.3 Evaluate Output 2.0

| Field | Meaning |
|---|---|
| `inputs`, `assessment_digest` | Static inputs (task/config/snapshot/context, default policy, metric registry version) and SHA-256 hex |
| `task_facts`, `max_estimated_cost_usd` | Task metrics and invocation cost allowance |
| `candidates` | All profiles in ID order: eligible, constraints, facts, unrecognized_metrics, evaluations |
| `classification`, `sources`, `warnings` | Default category classification, source timestamps, and warnings |
| `availability_verified` | false in evaluate; re-verified during live dispatch |

`evaluations` is `{}` for candidates failing constraints. `constraints` includes all evaluated passing and failing checks. Format 1 retains the candidates/excluded structure but provides no ranking or automatic selection.

### 1.4 Vendor-guided Candidate Assessment and Selection

Format 3 replays `analysis → eligible vendor guidance → benchmark (when comparisons exist)`. Incomplete decisions return `decision_required` (17); completed evaluations return `status: ok`. The final `assessment_digest` of pending responses is null, and the current request digest is `decision.request_digest`.

Completed schema 4.0 provides hard eligibility, suitability, facts, sparse observations/missing data, and candidate diagnostics across all profiles. Shared `evidence` contains unit definitions, comparisons, comparison_scopes, relevance, prefiltered_units, and auxiliary_units. Retrieval for selection is not subject to the 12-unit table display limit. `decision` contains replay data, while `recommendation` contains a bounded single-candidate recommendation or abstention. For detailed field specifications and response formatting, see [Upstream Integration](orchestrator.md#vendor-guided-candidate-assessments-and-upstream-choices).

## 2. Contract B — Facts Semantics and Validity

### 2.1 Metric Definitions Table

`routing.METRICS` defines targets, types, units, and maximum lifetimes for registered metrics: tokens.estimated_input/output, tokens.required_context, price.input/output_usd_per_mtok, cost.estimated_usd, and task.complexity. Other namespaced metrics (such as latency.p50_ms) are currently unregistered and passed through transparently.

The registry contains no preference directions or cross-metric weights. Mismatches in type or unit for registered metrics trigger input errors; automatic unit conversion is never performed. Unregistered namespaced metrics are validated for structural syntax and passed through, unused in constraints or evaluation.

### 2.2 Observation Format (Context 2.0)

```json
{"schema_version": "2.0",
 "task_metrics": {"task.complexity": {"value": "high", "source": "orch-classifier@3", "reason": "cross-file change"}},
 "max_estimated_cost_usd": 0.25,
 "profiles": {"my-codex": {"metrics": {
   "tokens.estimated_input": {"value": 40000, "unit": "tokens", "source": "orch-estimator@2"},
   "price.input_usd_per_mtok": {"value": 1.25, "unit": "usd/mtok", "source": "example-price",
                              "observed_at": "2026-10-24T00:00:00Z"},
   "latency.p50_ms": {"status": "missing", "reason": "not_measured", "source": "telemetry"},
   "acme.vibe": {"value": 3, "unit": "stars", "source": "experiment@1"}
 }}}}
```

The prices above serve as format examples. Profile keys must match configured profile IDs. All metrics are optional, and every observation requires a `source`. Recorded values must include `value` and defined `unit`; missing data must include `status: missing` and `reason`. `value: null` is rejected.

Metrics with finite validity require `observed_at`, and `expires_at` can impose shorter lifetimes. Price observations expire after 30 days. Computed facts annotate fresh/expired/missing status. Expired and missing values are not treated as zero and are excluded from computation. In the absence of constraints requiring a metric, missing data alone does not disqualify a candidate.

### 2.3 Context 1.0 Compatibility

`complexity`, `estimated_*_tokens`, `required_context_tokens`, `price{..., as_of}`, and `signals` are transformed into Context 2.0 and follow the same validation path. `context_hash` and `decision_context` operate on the converted structure. Historical 1.0 price entries also adhere to 30-day expiration.

## 3. Contract C — Constraints (Hard Requirements)

### 3.1 Constraints vs. Preferences

Constraint failures cannot be offset by high scores, upstream selection, or provisional acceptance. Cost-vs-latency trade-offs and global budgets are governed by upstream policy. The `priority` input is accepted for compatibility but is never used for automated cost discounting or near-tie sorting.

### 3.2 Named Checks

`routing.CONSTRAINTS` defines: enabled, task_exclusion, cost_tier, context_capacity, capabilities, local_only, availability, and estimated_cost. Check functions `(profile, task, x)` return a list of applied pass/fail results under the check name `constraint`.

```json
{"constraint": "estimated_cost", "passed": false, "code": "estimated_cost_exceeds_max",
 "metric": "cost.estimated_usd", "observed": 0.20, "limit": 0.05, "on_missing": "exclude"}
```

Context capacity is checked against the maximum of task minimum requirements and context requirements. Unknown capacity cannot satisfy positive requirements. When cost caps are specified, missing or expired estimates fail with `estimated_cost_unknown`. Unapplied constraints do not generate superfluous missing-value failures.

### 3.3 Tiers vs. Dollar Caps

`max_cost_tier` (low/medium/high) and `max_estimated_cost_usd` are independent; specifying both requires passing both. The default high tier permits all configured tiers. Specifying an estimated cost allowance does not bypass tier constraints.

### 3.4 Cost, Tokens, and Quota

1. Fresh `cost.estimated_usd` provider estimates take precedence.
2. If absent, cost is calculated as `(input tokens × input rate + output tokens × output rate) / 1,000,000` (`source: router:io2-v1`).
3. If inputs are missing or expired, missing status and cause are returned. Cache discounts and surcharges must be reflected in upstream estimates.

Estimated tokens represent cost inputs for this invocation, while profile.context_tokens represents static capacity. An invocation allowance must not be interpreted as a team budget or actual billing guarantee. In live mode, CodeBurn provider status and quota exhaustion across all windows are optionally checked. Antigravity checks the active model list via `agy models`. CodeBurn failures fall back to PATH checks while retaining agy model validation. No quota reservation is made for N workers.

## 4. Contract D — Binding Decision Records to Execution

### 4.1 Digest

The format 1/2 digest binds task_hash, config_hash, snapshot_id, context_hash, router_policy_version, and metric_registry_version. Timestamps, availability, and freshness are excluded from the digest and re-verified immediately prior to dispatch.

The format 3 schema 4.0 digest is `canonical_hash({"schema_version":"4.0", "decision":...})`. The decision encapsulates the task, static inputs, ordered request/digest/answers per stage, observations, relevance, and diagnostics. Stage request digests bind only the concrete dependencies of that stage. Historical elapsed time metrics are excluded, but freshness shifts due to expiration trigger re-verification. The contract does not hash raw file contents.

### 4.2 Selection Input

| Schema | Generation and Verification |
|---|---|
| 2.0 | Format 1/2 digest + profile, external policy, and reason. Overrides semantic decisions with a `selection_legacy` warning. |
| 5.0 | Policy 6 automated single candidate + full decision. Locked to recommended profile. |
| 6.0 | Produced via `select` from completed format 3 evaluation. External policy, reason, accept_provisional, and full decision. |

Schema 6.0 selects documented candidates or provisional/alternative candidates accompanied by explicit acceptance. Unsuitable, unassessed, or constraint-failed candidates are rejected. Acceptance does not resolve pending conditions. The output of `select` wraps the `selection` object inside a schema 1.0 envelope; store only the inner object in the `--selection` file.

`--selection` and `--profile` are mutually exclusive and cannot be combined with `--decision-response`. `--profile` constitutes an unrecorded override, emitting `selection_unrecorded`. Historical vendor-guided schema 3.0/4.0 and Policy 1–5 records cannot be reused for new decisions.

Executions using 5.0 or 6.0 replay stored stages without invoking providers, validating current constraints and availability. Altered evidence inputs trigger `stale_assessment` (14); malformed input formats or unsupported schemas trigger validation errors (2). Altering only the profile ID of a 5.0 record is rejected.

### 4.3 Idempotency

Identical canonical cwd, task_id, and round check for existing receipts first. Matching semantic hashes recover existing runs; mismatched contents constitute conflicts. Divergent profile specifications trigger `profile_round_conflict`; matching profiles with differing selection records trigger recovery with a `selection_differs_from_recorded` warning. Intentional new executions require upstream inspection of partial effects and submission under a new round. Timeouts do not grant permission for cancellation or resubmission.

### 4.4 decision.json

A run's `decision.json` augments the route response with selection and default evaluate 2.0 `assessment`. Raw vendor-guided evidence is preserved within `selection.decision`. There is no separate decision 2.0 wrapper. Full assessments are omitted from live execution responses. Output-only `selection.source` fields are stripped prior to re-submission.

## 5. Contract E — Parallel Execution

Group 1.0 repeats Policy 6 across task × fanout, excluding previously selected profiles from subsequent comparisons. Viable candidates trigger decision requests and upstream selection without defaulting to fallback profiles.

Group 2.0 accepts an ordered execution list of task-specific `context` and `selections`. Selections can use schema 2.0, 5.0, or 6.0 and may repeat identical profiles. Supports 1–8 tasks per group, up to 16 items total; the `fanout` key is prohibited. `max_parallel` ranges from 1 to 4, matching the shared pool of 4 active execution slots.

Upstream evaluators evaluate using group.cwd and original prompts. All selection digests are validated during the planning phase; a single stale item aborts execution of the entire group. Worktrees, group files, and workers are never created before all selections conclude. Because worker cwd and collaboration prompts vary at execution time, internal task hashes are adjusted while current constraints and availability are re-verified.

Identical groups are recovered using frozen plans and receipts. Altered inputs or reordered lists constitute conflicts. Member rounds preserve `delivery_state` and `reassignment`. Repeated selections receive separate labels, worktrees, receipts, and slot allocations. Team budgets, aggregation, adoption, and retries belong to upstream responsibility.

## 6. Versions and Documents

| Contract | Current Value |
|---|---|
| task / result / route envelope | 1.0 |
| context / group | 2.0 (accepts 1.0 input) |
| evaluate default / compatibility | schema 2.0 / 1.0 |
| evaluate `--format 3` | schema 4.0 |
| vendor-guided policy / selection | policy 6 / automatic 5.0, external 6.0 |
| default evaluation, snapshot policy / metric registry | routing.POLICY_VERSION 1.0 / METRIC_REGISTRY_VERSION 1 |

Policy versions, CLI format numbers, and JSON schema versions are independent. Official vendor guidelines are pinned to distinct versions and verbatim text in `guidelines.toml`. For operational examples, see [Reference](reference.md); for verification status, see [Implementation Status](implementation-status.md); for upstream usage, see [Orchestrator Integration](orchestrator.md).

## 7. Adding Metrics and Verification

Namespaced metrics passed through transparently require no registry modifications. Adding formal types, units, or lifetimes requires updating `METRICS`; adding filter constraints requires implementing functions, limits, and focused test fixtures in `CONSTRAINTS`. Illustrative latency caps must not be documented as active inputs. Ranking policies belong to upstream implementation.

The complete verification command is `python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn`. Verification standards for selection, staleness, replay, partial failure, and deduplication reside in [Validation Documentation](../06_VALIDATION_AND_OPEN_ITEMS.md). Live Projects dispatch, workflow quality, and team budget validation remain separate from offline contract testing.
