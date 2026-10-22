# Orchestrator integration

Default profile decisions now use the shared [vendor-guided policy](vendor-guided-routing.md), including offline native handoff packets and 3.0 selection records. The manual 2.0 selection workflow below remains an explicit override; it is not vendor-guidance validation. Use `--policy legacy` only to request the old weighted automatic policy.

The router reports benchmark evidence and checks whether a chosen profile can run. The Orchestrator owns task complexity, estimates, final selection, and fallback order.

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
- `evaluations.benchmark` (eligible profiles only): `status ok|insufficient|unavailable`, `quality`, `coverage`, `evidence`, and `legacy_score`. `legacy_score` is the old automatic-route score, not an overall ranking.

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

Schema 1.0 groups keep the legacy behaviour: the router's own `route` choice plus the next candidates, up to `fanout`.
