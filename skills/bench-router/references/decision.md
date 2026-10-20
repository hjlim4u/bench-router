# Vendor-guided decision provider

Use the host Orchestrator's native subagent tool for fallback. This helper does not launch a worker or delegate the coding task.

## Provider selection

- `TYPESAFE_API_KEY` (or `JEV_API_KEY`) present: `scripts/decide.py` calls the official Jev endpoint. `JEV_MODEL` overrides the pinned default `jev-1.13.0`. Keys stay in the environment; never include them in task files, prompts, or output. Besides real environment variables, `decide.py` and `refresh` read `JEV_API_KEY`, `TYPESAFE_API_KEY`, `JEV_MODEL`, `BENCH_ROUTER_DECISION_MODEL` and `ARTIFICIAL_ANALYSIS_API_KEY` from `./.env` in the working directory, then `~/.config/bench-router/env`; the process environment wins, and other variables in `.env` are ignored. Copy `.env.example` to `.env`, keep `.env` out of git (`chmod 600`), and carry it to each device through a secret manager or by hand.
- No key, or Jev fails: the helper returns `status: subagent_required` with a bounded decision request. Invoke one native subagent with that request, without inherited conversation history, file writes, tools, or further delegation. It must only return typed answers.
- Pass `--host antigravity`, `--host codex`, or `--host claude` on helper calls. Fallback packets identify the native `bench-decider` and its explicit model using the table below. `BENCH_ROUTER_DECISION_MODEL` overrides that model; apply the override with the host's per-invocation model selector when supported. If neither a named agent nor an explicit native model selector can honor it, report `decision_unavailable`. Do not inherit a more expensive parent model or silently execute a legacy automatic choice. Omitting `--host` retains the generic `cheapest_available` policy for other hosts; that value is a policy, not automatic price discovery.
- Respect host restrictions on subagents. A `subagent_required` packet is a handoff, not evidence that a subagent ran. No API key needs to be installed for fallback.

| Current host | Native agent definition (repository root) | Default model |
|---|---|---|
| Antigravity | `.agents/agents/bench-decider.md` | `flash` tier |
| Codex | `.codex/agents/bench-decider.toml` | `gpt-6-luna`, low effort |
| Claude Code | `.claude/agents/bench-decider.md` | `haiku` |

Invoke the named agent through the current host's native subagent tool, supplying the helper's `request` as its entire task. Codex model overrides require a fresh context (`fork_turns="none"` where supported); do not fork the parent's full conversation. For Claude Code, explicitly select the packet's model at invocation so a host-wide default cannot change it. Antigravity's agent definition fixes the `flash` tier. Confirm the actual model in host execution metadata; if the host substitutes a different model, report `decision_unavailable` rather than treating the requested model as the one used.

These definitions are project-scoped. When using the linked Skill from another workspace and `bench-decider` is not discovered, read the matching definition from this repository and invoke an equivalent fresh native subagent with its explicit model and instructions. Antigravity can use `define_subagent`; Codex and Claude Code can use their per-invocation model selector. If unsupported, stop at `decision_unavailable`. Do not create a separate CLI process, worktree, or recursively delegated Router task for this short decision.

## Decision flow

1. Create a task with its original requirements and any explicit facets from `wiki facets`. Request `route --task TASK.json --host HOST --dry-run`. The shared router now batches unresolved semantic facets and workload analysis itself; do not call a separate facet pass first. Analysis sees task requirements and known facets, without model IDs, benchmark scores or file bodies. Preserve uncertain facets as unresolved.
2. Resolve only the current `decision.request` using Jev or the native agent. The stages are `analysis`, then `fit`, then an optional `benchmark` relevance decision. Fit receives the preceding analysis, original requirements and exact model/effort guidance, without benchmark scores. Evaluation-only efforts remain conditional until code verifies a fresh exact workflow improvement against a lower effort of the same model/harness.
3. Save `{"stages": [<entries from decision.completed>, <new response>]}` and rerun with `--decision-response RESPONSE.json --dry-run` until selected. Each new response must echo its own request_digest and include every current question. Attach provider and actual model from host metadata. Never edit predecessor records or invent the next request. If the host cannot honor the requested model, return decision_unavailable.
4. The router retrieves evidence only for remaining candidates and task facets, preserving status, source, measurement conditions and missing data. It ranks comparable raw scores in code. Exact and model-proxy observations have separate comparison scopes; unrelated cohorts and percentiles cannot decide a winner. Conflicting evaluations trigger a score-blind benchmark relevance request. Missing measurements cause explicit uncertainty, not an extra model call to guess scores.
5. Execute with the completed response file without `--dry-run`, or extract the 3.0 selection record without its output-only `source` and use `--selection`. Policy version 2 binds all stages, inputs, observed evaluations and the resolved outcome. Older vendor-guided policy-1 records require a new decision. Execution rechecks constraints and availability; existing receipts are recovered first. A changed snapshot can reuse valid analysis/fit responses while generating a new final record.
6. Fanout reuses analysis and fit stages within the plan; picked profiles are removed from evidence retrieval and comparison. Unknown guidance remains provisional. Confidence is not measured success. Report the selected profile, evidence scope, unresolved conditions and recorded usage; reused stages are not additional provider calls.

Native response envelope (the caller attaches model metadata):

```json
{"request_digest": "<copied from decision packet>", "provider": "subagent", "model": "<actual host model>",
 "answers": {"<each supplied question ID>": {"type": "choice", "choice": "<supplied option>"}}}
```

`balanced` prefers a light configuration that plausibly meets the task, `cost` uses supplied estimated USD among suitable candidates, and `quality` prioritizes relevant evidence and documented task fit. Effort names are not shared vendor units. Unknown prices are not zero; missing guidance does not inherit from a similar model. Only registered model/effort combinations execute.

Request example (both backends use the same shape):

```json
{"state": "Implement a React dashboard with routing and shared state.",
 "questions": {"webdev_react": {
   "type": "noul",
   "instructions": "Does the requested deliverable require a multi-file React web application, including component structure or shared state?"
 }}}
```

For standalone bounded questions, `scripts/decide.py` retains the generic typed-answer interface. Routing stages and selection records come from the common CLI policy. Persist full evidence locally and give the parent the choice, provenance and unresolved issues. The same policy serves standalone CLI, copied Skill and parallel fanout. Use `--policy legacy` only for an explicitly requested old score-based choice.

Official Jev request/response reference: <https://docs.typesafe.ai/api>. Model IDs and prices: <https://docs.typesafe.ai/models>.
