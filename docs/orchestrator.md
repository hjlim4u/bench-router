# Orchestrator integration

The router reports benchmark evidence and checks whether a chosen profile can run. The Orchestrator owns task complexity, estimates, final selection, and fallback order.

Create a normal `task.json`, then optionally supply `context.json`:

```json
{
  "schema_version": "1.0",
  "complexity": {"level": "high", "reason": "cross-file change and tests"},
  "max_estimated_cost_usd": 0.25,
  "profiles": {
    "my-codex": {
      "estimated_input_tokens": 12000,
      "estimated_output_tokens": 4000,
      "required_context_tokens": 24000,
      "price": {
        "input_usd_per_million_tokens": 1.5,
        "output_usd_per_million_tokens": 6,
        "source": "orchestrator price table",
        "as_of": "2026-10-13T00:00:00+00:00"
      },
      "signals": {
        "orchestrator.latency": {"value": 12, "unit": "seconds", "source": "recent runs"}
      }
    }
  }
}
```

`profiles` keys must match configured profile IDs. Every profile field is optional; absent price or token estimates produce `estimated_cost_usd: null` with a missing reason. With `max_estimated_cost_usd`, an unknown or over-budget estimate excludes that profile. Cost is `(input tokens × input rate + output tokens × output rate) / 1,000,000`. Estimates cover total billable tokens for this subtask. `required_context_tokens` checks the profile's configured context capacity separately. `complexity` and namespaced `signals` are reported as supplied; the router does not turn them into a score. Prices and estimates are supplied by the Orchestrator, not fetched or refreshed by the router.

```bash
python3 -m bench_router.cli evaluate --task task.json --context context.json
python3 -m bench_router.cli route --task task.json --context context.json --profile my-codex --dry-run
python3 -m bench_router.cli route --task task.json --context context.json --profile my-codex
```

`evaluate` returns `status: "ok"`, `selected: null`, every eligible candidate, and excluded profiles with reasons. Candidate `context_facts` includes cost, estimates, price source, context requirement, and signals. It does not probe live executable availability; live `route` probes again before dispatch. The Orchestrator chooses a profile from `candidates`. The normal `route` command without `--profile` continues to make the router's benchmark-based selection.

The run response includes `delivery_state` and `reassignment`. `safe_to_retry` means the prompt was not submitted. `collect_first` means delivery or completion remains uncertain; use `collect --run-id ID --cwd DIR` before deciding whether to reassign. `review_result` means the agent acted; inspect its result and workspace before sending the task elsewhere. A fallback execution uses a **new round** and normally excludes the previous profile in its new task. Reusing a task ID and round collects the existing receipt; choosing another profile for that same round returns `conflict`. These markers do not reserve a budget or guarantee that actual charges stay below estimated cost.
