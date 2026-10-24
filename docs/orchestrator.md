# Orchestrator integration

Default profile assessments use the shared [vendor-guided policy](vendor-guided-routing.md). Policy 4 returns evidence for upstream selection whenever multiple suitable profiles remain or an effort requires workflow evaluation. Only a sole suitable profile without pending conditions can use the automatic 3.0 selection path. The manual 2.0 selection workflow below remains an explicit override; it is not vendor-guidance validation. Use `--policy legacy` only to request the old weighted automatic policy.

For the consolidated design cross-checked against both proposals and the implementation on 2026-10-23, see [orchestration boundary design](orchestration-boundary.md). It covers task decomposition, multi-agent patterns, per-task routing, and execution, distinguishing current contracts from proposed extensions.

The router reports benchmark evidence and checks whether a chosen profile can run. The Orchestrator owns task complexity, estimates, final selection, and fallback order.

## Vendor-guided candidate assessments and upstream choices

`evaluate --format 3` reports a versioned candidate assessment using the same staged analysis, suitability rules, and comparable evidence as automatic routing. Formats 1 and 2 retain their existing meaning; the default remains 2. Format 3 is offline: it never dispatches workers, makes network calls, or writes files, even when Jev credentials are configured.

```bash
python3 -m bench_router.cli evaluate --format 3 --task task.json --host codex
python3 -m bench_router.cli evaluate --format 3 --task task.json --host codex --decision-response responses.json
python3 -m bench_router.cli select --assessment assessment.json --profile specialist \
  --policy-id team-policy --policy-version 1 --reason "assign this specialist to the review step" --accept-provisional
python3 -m bench_router.cli route --task task.json --selection selection.json --dry-run
```

Use the same `--context` for assessment and execution when supplying metrics. Resolve each `decision_required` packet using the [existing stage response contract](vendor-guided-routing.md#cli와-오프라인-응답), preserving `decision.completed`. Pending responses use `decision.request_digest`; their final `assessment_digest` is null. Save the completed `status: "ok"` result as `assessment.json`. `select` returns `{"status":"ok", "schema_version":"1.0", "selection":{...}}`; save only its `selection` object as `selection.json`. Removing `--dry-run` from the last command requests live execution.

Assessment schema 3.0 exposes the following fields:

| Field | Contract |
|---|---|
| `candidates` | All configured profiles in ID order, with hard `eligible`/`constraints`, metric `facts`, semantic `suitability`, sparse `observations`/`missing`, and candidate-local `diagnostics`. Order is not a ranking. Hard-excluded or not-yet-assessed profiles have suitability `not_evaluated`. |
| `evidence` | Shared unit definitions, comparable-unit winners and exact/model-proxy scopes. `relevance` records score, acceptance, primary-requirement basis and description, reason, source page and request digest; `benchmark_relevance` records accepted relevance values without voting or aggregation. `prefiltered_units` records prefilter reasons, and `auxiliary_units` retains common reliability. Selection retrieval is uncapped (`omitted_units: 0`); semantic review only receives comparable task evidence. `inputs.index_hash` identifies the index. |
| `compared_profiles` | The candidate set used to check comparability; a unit enters `evidence.comparisons` only when its measurements are comparable for that set. |
| `diagnostics` | Assessment-wide `comparable_evaluation_missing` and `workload_unresolved` where applicable. |
| `recommendation` | A sole suitable profile without pending conditions, or `status: "abstained"` with a null profile and `upstream_selection_required`. No cross-unit votes, cost ranking or configuration tie breaks run. Unsuitable candidates remain unselectable. Before judgments complete, the whole field is null. |
| `decision` / `assessment_digest` | Replayable staged evidence and a hash of `{"schema_version":"3.0","decision":...}`. Inputs bind task/context, configuration, guidance, snapshot, index, exclusions, and selection policy. Projections are informational; execution revalidates the embedded decision. |

`select` creates selection schema **4.0** with `profile`, `assessment_digest`, external `policy: {id, version}`, `reason`, `decision`, and the boolean `accept_provisional`. It accepts any hard-eligible candidate whose recorded fit is documented, or provisional with explicit acceptance. It rejects unsuitable and unassessed candidates. A provisional candidate's pending conditions remain visible; acceptance does not establish measured quality. An upstream policy can use its own criterion even when the router abstains from a recommendation, provided the chosen candidate passed suitability assessment.

`route --selection` and group 2.0 accept 4.0 records, replay the same evidence without new judgment-provider calls, and check current constraints and availability. The chosen profile need not equal the router's recommendation. Changed decision inputs return `stale_assessment`; an already submitted run is collected first. Selection 2.0 remains an explicit semantic override, and 3.0 still requires the router's resolved profile. No existing selection version is reinterpreted.

Candidate diagnostics include `provisional_suitability`, `guidance_missing`, `guidance_fit_unresolved`, `workflow_gain_unverified`, `cost_unknown`, `model_proxy_comparison`, `task_quality_unverified`, and `task_specific_evaluation_missing`. Conditional efforts stay provisional even when benchmark results favor them; accepting them requires `accept_provisional=true` and does not clear the pending condition. Completed `route` calls needing an upstream choice return `decision_unavailable` (exit 17), `selected: null` and `decision.uncertainty` containing `upstream_selection_required`. Reuse their stage responses with `evaluate --format 3`, then `select` and `route --selection`; groups use these selections in schema 2.0. Preserve unknown diagnostic codes without triggering extra workers or retries; reject unsupported contract versions and required states. Policy-1/2/3 records require reassessment for new execution; existing receipts are recovered first. Workflow evaluation evidence and team budgets remain upstream.

## Existing facts and override workflow

Create a normal `task.json`, then optionally supply `context.json` (schema 2.0; contract in [routing-contracts.md](routing-contracts.md) §2):

```json
{
  "schema_version": "2.0",
  "task_metrics": {
    "task.complexity": {"value": "high", "reason": "cross-file change and tests", "source": "orch-classifier@3"}
  },
  "max_estimated_cost_usd": 0.25,
  "profiles": {
    "my-codex": {"metrics": {
      "tokens.estimated_input":    {"value": 12000, "unit": "tokens", "source": "orch-estimator@2"},
      "tokens.estimated_output":   {"value": 4000,  "unit": "tokens", "source": "orch-estimator@2"},
      "tokens.required_context":   {"value": 24000, "unit": "tokens", "source": "orch-estimator@2"},
      "price.input_usd_per_mtok":  {"value": 1.5, "unit": "usd/mtok", "source": "price table", "observed_at": "2026-10-13T00:00:00+00:00"},
      "price.output_usd_per_mtok": {"value": 6,   "unit": "usd/mtok", "source": "price table", "observed_at": "2026-10-13T00:00:00+00:00"},
      "latency.p50_ms":            {"status": "missing", "reason": "not_measured", "source": "telemetry"},
      "orchestrator.latency":      {"value": 12, "unit": "seconds", "source": "recent runs"}
    }}
  }
}
```

`profiles` keys must match configured profile IDs. Every metric is optional. Each observation needs a `source`; an absent value is `{"status": "missing", "reason": ...}`, never `null` or `0`.

Registered metrics (`METRICS` in `bench_router/routing.py`) are checked for target (task vs profile), type, and exact unit (no conversion). Some also expire: prices need `observed_at` and expire after 30 days, and any metric may carry an earlier `expires_at`. Expired or missing values are not used in calculations. Unregistered namespaced metrics are passed through in `context_facts.signals` and are never used by constraints.

Cost precedence:

1. A fresh `cost.estimated_usd` (Orchestrator's own quote, may include cache/extra charges) is used as is.
2. Otherwise the router computes `(input tokens × input rate + output tokens × output rate) / 1,000,000`.
3. If an input is missing, the cost is `null` with reason `estimate_or_price_missing`. If an input has expired, the reason is `price_expired`.

With `max_estimated_cost_usd`, an unknown or over-budget estimate excludes that profile. This is a per-call allowance; it is not a task budget. `tokens.required_context` checks the profile's configured context capacity. Metrics are reported as supplied; the router does not turn them into a score. Prices and estimates are supplied by the Orchestrator, not fetched or refreshed by the router.

Schema 1.0 context (`complexity`, `estimated_*_tokens`, `required_context_tokens`, `price{…, as_of}`, `signals`) is still accepted and converted to 2.0. `decision_context` and `context_hash` always use the 2.0 form. A 1.0 price older than 30 days now counts as expired.

```bash
python3 -m bench_router.cli evaluate --task task.json --context context.json
python3 -m bench_router.cli route --task task.json --context context.json --profile my-codex --dry-run
python3 -m bench_router.cli route --task task.json --context context.json --profile my-codex
```

`evaluate` returns schema `2.0`: `inputs` (task/config/context hashes, snapshot, router policy and metric registry versions), `task_facts`, and one entry per configured profile in profile-ID order. The order carries no ranking. Each entry has:

- `eligible`;
- `constraints`: every applied required check, with `passed`, `code` on failure, `metric`, `observed`, `limit`;
- `facts`: registered metrics with `freshness`, including `cost.estimated_usd` (the router's computed cost uses source `router:io2-v1`);
- `unrecognized_metrics`;
- `evaluations.benchmark` (eligible profiles only): `status ok|insufficient|unavailable`, `quality`, `coverage`, and `evidence`. There is no combined score; candidates are listed by profile ID.

`evaluate --format 1` keeps the previous candidate/excluded shape for one release.

`evaluate` does not probe live availability; live `route` probes again before dispatch. When `codeburn` is installed, the probe also rejects a configured Claude, Codex, or Antigravity profile whose CodeBurn provider is unavailable or has every reported quota window exhausted; otherwise it falls back to the executable PATH probe. The Orchestrator chooses a profile from the eligible entries. The normal `route` command without `--profile` continues to make the router's benchmark-based selection. `explain` prints that selection plus the same constraint results and facts.

To record why a profile was chosen, pass a selection instead of `--profile`:

```json
{"schema_version": "2.0", "profile": "my-codex",
 "assessment_digest": "<assessment_digest from evaluate>",
 "policy": {"id": "orch-cost-latency", "version": "4"},
 "reason": "lowest estimated cost among candidates with benchmark coverage >= 0.5"}
```

```bash
python3 -m bench_router.cli route --task task.json --context context.json --selection selection.json
```

`assessment_digest` is a hash of the static inputs: task, profile config, snapshot, context, router policy and metric registry versions. Time-dependent facts are not part of it; freshness and live availability are re-checked at dispatch.

If any of those inputs changed since `evaluate` (for example a refresh, a config edit, or a new context), the router does not execute. It returns `status: "stale_assessment"` (exit 14) with the current digest. Re-run `evaluate` and select again.

A recorded run is written to `decision.json` together with the selection and the full `evaluate` 2.0 assessment, including constraint values and limits. `route --profile` alone still works, but warns `selection_unrecorded`.

A repeated task ID and round returns the recorded run even if the selection differs, with warning `selection_differs_from_recorded`. Use a new round to act on a new decision.

The run response includes `delivery_state` and `reassignment`. `safe_to_retry` means the prompt was not submitted. `collect_first` means delivery or completion remains uncertain; use `collect --run-id ID --cwd DIR` before deciding whether to reassign. `review_result` means the agent acted; inspect its result and workspace before sending the task elsewhere. A fallback execution uses a **new round** and normally excludes the previous profile in its new task. Reusing a task ID and round collects the existing receipt; choosing another profile for that same round returns `conflict`. These markers do not reserve a budget or guarantee that actual charges stay below estimated cost.

## Parallel groups with Orchestrator selections

`parallel --group group.json` accepts schema 2.0. Each task carries its own context and the profiles the Orchestrator chose; fanout is the number of selections:

```json
{"schema_version": "2.0", "group_id": "g1", "cwd": "/repo", "isolation": "shared", "max_parallel": 4,
 "tasks": [{"task": {"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "...", "prompt": "..."},
            "context": {"schema_version": "2.0", "profiles": {"...": {"metrics": {}}}},
            "selections": [{"schema_version": "2.0", "profile": "b", "assessment_digest": "...",
                            "policy": {"id": "orch-diverse", "version": "1"}, "reason": "..."}]}]}
```

- Obtain each `assessment_digest` by running `evaluate` on the task with `cwd` set to the group `cwd` and the original prompt. Workers run in their own worktrees with collaboration text appended, so their tasks differ by design. The digest is checked once at planning time. Each worker dispatch re-checks context, constraints, and availability.
- If any selection is stale, the whole group returns `stale_assessment` and nothing runs.
- Each worker's `max_estimated_cost_usd` is a per-call allowance. The group total, and how a remaining budget is split across workers, are the Orchestrator's responsibility.
- `selections` is an ordered list of execution instances, so the same profile may appear more than once (with 2.0, 3.0, or 4.0 selection records). Each entry gets its own label, worktree, and receipt; repeats count toward the per-task limit of 8 and group limit of 16. Reusing the same group input collects those runs without resubmitting them.
- Each member's `rounds` carries `delivery_state` and `reassignment` from the single-run response, including `collect_first` for an uncertain or unfinished delivery. These fields may be absent or null when dispatch produced no receipt; inspect the returned status, warnings, and errors before choosing a next action.

Schema 1.0 groups keep the legacy behaviour: the router's own `route` choice plus the next candidates, up to `fanout`.
