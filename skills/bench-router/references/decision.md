# Vendor-guided decision provider

Use the host Orchestrator's native subagent tool for fallback. This helper does not launch a worker or delegate the coding task.

## Provider selection

- `TYPESAFE_API_KEY` (or `JEV_API_KEY`) present: `scripts/decide.py` calls the official Jev endpoint. `JEV_MODEL` overrides the pinned default `jev-1.13.0`. Keys stay in the environment; never include them in task files, prompts, or output. Besides real environment variables, `decide.py` and `refresh` read `JEV_API_KEY`, `TYPESAFE_API_KEY`, `JEV_MODEL`, `BENCH_ROUTER_DECISION_MODEL` and `ARTIFICIAL_ANALYSIS_API_KEY` from `./.env` in the working directory, then `~/.config/bench-router/env`; the process environment wins, and other variables in `.env` are ignored. Copy `.env.example` to `.env`, keep `.env` out of git (`chmod 600`), and carry it to each device through a secret manager or by hand.
- No key, or Jev fails: the helper returns `status: subagent_required` with a bounded decision request. Invoke one native subagent with that request, without inherited conversation history, file writes, tools, or further delegation. It must only return typed answers.
- Pass `--host antigravity`, `--host codex`, or `--host claude` on helper calls. Fallback packets identify the native `bench-decider` and its explicit model using the table below. `BENCH_ROUTER_DECISION_MODEL` overrides that model; apply the override with the host's per-invocation model selector when supported. If neither a named agent nor an explicit native model selector can honor it, report `decision_unavailable`. Do not inherit a more expensive parent model or silently execute a legacy automatic choice. Omitting `--host` retains the generic `cheapest_available` policy for other hosts; that value is a policy, not automatic price discovery.
- Respect host restrictions on subagents. A `subagent_required` packet is a handoff, not evidence that a subagent ran. No API key needs to be installed for fallback.

| Current host | Native agent definition (repository root) | Bundled copy (this skill) | Default model |
|---|---|---|---|
| Antigravity | `.agents/agents/bench-decider.md` | `references/agents/antigravity.md` | `flash` tier |
| Codex | `.codex/agents/bench-decider.toml` | `references/agents/codex.toml` | `gpt-6-luna`, low effort |
| Claude Code | `.claude/agents/bench-decider.md` | `references/agents/claude.md` | `haiku` |

Invoke the named agent through the current host's native subagent tool, supplying the helper's `request` as its entire task. Codex model overrides require a fresh context (`fork_turns="none"` where supported); do not fork the parent's full conversation. For Claude Code, explicitly select the packet's model at invocation so a host-wide default cannot change it. Antigravity's agent definition fixes the `flash` tier. Confirm the actual model in host execution metadata; if the host substitutes a different model, report `decision_unavailable` rather than treating the requested model as the one used.

The repository definitions are project-scoped. When using the installed Skill from another workspace and `bench-decider` is not discovered, read the matching bundled copy under this skill's `references/agents/` and invoke an equivalent fresh native subagent with its explicit model and instructions. Antigravity can use `define_subagent`; Codex and Claude Code can use their per-invocation model selector. If unsupported, stop at `decision_unavailable`. Do not create a separate CLI process, worktree, or recursively delegated Router task for this short decision.

## Decision flow

Before the initial assessment, check source health with `status`; use `evaluate --refresh --format 3 --task TASK.json --host HOST` when a source check is needed. Inspect the refresh report to distinguish collection failure from successful collection with an absent/null metric. Never add `--refresh` to response replay. Policy 7 preserves last-good observations until max_stale, explicitly labels nearest same-vendor measured proxies, and exposes participating profiles per compatible comparison. Task priority and interactive guide conditions must remain visible to the guidance decision.

1. Create a task with its original requirements and any explicit facets from `wiki facets`. Request `route --task TASK.json --host HOST --dry-run`. The shared router batches semantic facets and workload analysis itself; do not call a separate facet pass first. Keyword, code-fence and extension task tags are tentative `rule_hints`: reject them when they do not describe the requested work. Rejected rules do not reappear in retrieval. Analysis sees task requirements and known facets, without model IDs, benchmark scores or file bodies. Preserve uncertain facets as unresolved.
2. Resolve only the current `decision.request` using Jev or the native agent. Stages are `analysis`, then one `guidance` request for each vendor represented by the eligible profiles (in vendor ID order), then one batched `benchmark` review whenever comparable task evidence survives the prefilter. A guidance request contains only that vendor's dated guide, quoted verbatim from its own pages in its own shape, and official sources, with no profile IDs; never apply one vendor's rules to another. Choose the one starting point the guide assigns to the requirements (`guidance:<vendor>`, a model+effort row); for Gemini choose the model role and the workload class, which code maps to that model's level. Follow that vendor's own strategy text when several rows cover the requirements, `__none__` when none does, `__unknown__` when information is insufficient. Profiles matching the chosen model+effort are `documented`; the vendor's other profiles are `alternative`; models without guidance need no request and stay `provisional` with `guidance_missing`. Return both `relevance:<unit>` (0..1) and `basis:<unit>` (a directly measured primary requirement facet or a supplied supporting/unrelated/unknown reason). Acceptance requires at least 0.8 plus a primary-requirement basis; this is a policy threshold, not calibrated confidence. The router reports per-unit results without votes or aggregation. Alternatives are not searched, compared or auto-selected; evaluation-gated (`escalation`) efforts also carry `workflow_gain_unverified`. The caller owns workflow validation and explicit acceptance.
3. Save `{"stages": [<entries from decision.completed>, <new response>]}` and rerun with `--decision-response RESPONSE.json --dry-run` while status is `decision_required`. Each new response must echo its own request_digest and include every current question. Attach provider and actual model from host metadata. Never edit predecessor records or invent the next request. If the host cannot honor the requested model, return decision_unavailable.
4. The router retrieves evidence only for remaining candidates and reviewed facets, without the evidence table's display cap. `prefiltered_units` records noncurrent, noncomparable or generic-only evidence; `auxiliary_units` retains common agent reliability without task-quality votes. All observations and missing data remain available for diagnostics. The compact benchmark request groups definitions by suite and omits models, scores and provenance details. Exact and model-proxy observations have separate comparison scopes; unrelated cohorts and percentiles cannot decide a winner. Missing measurements cause explicit uncertainty, not a model call to guess scores.
5. Policy 7 automatically selects only a sole suitable (`documented` or `provisional`) profile without pending conditions. With multiple suitable profiles, `route` returns `decision_unavailable` (exit 17), `selected: null` and `upstream_selection_required`. Reuse the completed response file with `evaluate --format 3`, save the assessment, choose a profile in the caller, and run `select --assessment ASSESSMENT.json --profile PROFILE --policy-id POLICY --policy-version VERSION --reason REASON` (add `--accept-provisional` for a `provisional` or `alternative` profile). Save the returned `selection` object and execute `route --task TASK.json --selection SELECTION.json`. Existing records require reassessment for new execution; existing receipts are recovered first. Changed snapshots can reuse valid semantic responses while generating a new final record.
6. Fanout reuses analysis and guidance stages within the plan; picked profiles are removed from evidence retrieval and comparison. Unknown guidance remains provisional. Confidence is not measured success. Report the selected profile, evidence scope, unresolved conditions and recorded usage; reused stages are not additional provider calls.

Native response envelope (the caller attaches model metadata):

```json
{"request_digest": "<copied from decision packet>", "provider": "subagent", "model": "<actual host model>",
 "answers": {"<each supplied question ID>": {"type": "choice", "choice": "<supplied option>"}}}
```

The caller applies `quality`, `balanced` or `cost` preferences using the reported evidence and estimates. The router does not choose among suitable profiles using cost tiers, default/fallback order or ID. Effort names are not shared vendor units. Unknown prices are not zero; missing guidance does not inherit from a similar model. Only registered model/effort combinations execute.

Request example (both backends use the same shape):

```json
{"state": "Implement a React dashboard with routing and shared state.",
 "questions": {"webdev_react": {
   "type": "noul",
   "instructions": "Does the requested deliverable require a multi-file React web application, including component structure or shared state?"
 }}}
```

For standalone bounded questions, `scripts/decide.py` retains the generic typed-answer interface. Routing stages and selection records come from the common CLI policy. Persist full evidence locally and give the parent the choice, provenance and unresolved issues. The same policy serves standalone CLI, copied Skill and parallel fanout.

Upstream allocation can inspect `evaluate --format 3` → `evidence.relevance[unit]`: raw `score`, `accepted`, selected `basis`, `task_requirement`, short `reason`, matched facets, comparison scope, source page and benchmark request digest. The original task and shared unit descriptions remain in `decision.task` and `evidence.units`; per-candidate observations supply the measured conditions. `benchmark_relevance` contains accepted relevance values without voting. Rejected and auxiliary evidence remains visible. These are bounded evaluator judgments, not verified task success. All fields are replayed and digest-bound when an upstream policy selects a model using selection 4.0.

Official Jev request/response reference: <https://docs.typesafe.ai/api>. Model IDs and prices: <https://docs.typesafe.ai/models>.
