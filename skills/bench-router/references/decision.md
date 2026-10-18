# Cheap decision provider

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

1. Get the task and `wiki facets` vocabulary. Reuse the vocabulary within the conversation while `wiki_hash` is unchanged. Automatic rules and explicit tags take precedence; ask the decision provider only about facets still requiring semantic judgment. Send the existing task summary, relevant requirements and context filenames; if insufficient, include the needed original prompt rather than guessing from a truncated summary. Finalize task facet tags before `evaluate`; preserve the original prompt and requirements.
2. For facets, create a request with one `noul` question per relevant allowed facet. Multiple facets may fit. Include short descriptions and boundary cases in the questions; model IDs and benchmark IDs alone do not explain their meaning. Treat uncertain answers as unresolved, not absent. Retain baseline candidates or ask the caller when a required facet cannot be established.
   - Ask in one batched call. Skip `rule:always` facets, facets a rule already set, and `rule:script(...)` language facets (script detection is decisive). Still ask other rule facets, because file-extension and keyword rules miss cases such as a React request without context files.
   - Tag a facet when its `noul` is at least 0.8. Append these boundary cases to the matching questions; without them, a cheap model tags almost every prompt as instruction following:
     - `task:instruction_following`: 1 only if the main challenge is obeying explicit output constraints (exact length, count, ordering, format, forbidden words); 0 for ordinary tasks that merely state requirements.
     - `difficulty:hard_prompts`: most routine coding, writing, or lookup tasks are 0, even when well specified.
     - `domain:software_it`: 1 only if the subject matter is software or IT itself; 0 when code is merely a tool for another subject.
     - `task:math`: 1 only if the main work is mathematical derivation or calculation, not incidental arithmetic. `domain:mathematical`: 1 only if the subject matter is mathematics.
     - `task:ocr_parse`: 1 only if the input is a scanned or photographed document whose text must be converted to structured output. `task:vision_ocr`: 1 only if an image is attached and the answer comes from text inside that image.
   - Measured on 60 labeled prompts with Jev (`eval/retrieval.py`, `eval/results/retrieval-jev1.md`): facet F1 0.89 and hallucinated-facet rate 0.12, against F1 0.53 for rules alone. About 2.4k input tokens per task.
3. Obtain `evaluate` and `evidence --format table` results. Only `eligible` profile IDs can be choices. With none, return `no_eligible_profile`; a single eligible profile needs no selection call. For several candidates, give the provider the task, relevant benchmark results, measured effort, missing/stale flags, and code-computed cost estimates. Ask one `choice` question with profile IDs plus `abstain`; express the task's quality/cost preference explicitly. Do not ask the model to calculate budgets, compare timestamps, invent missing scores, or treat a model's different-effort result as an exact profile measurement.
4. Invoke `python scripts/decide.py --host HOST --request REQUEST.json` using the current host from the table above. For `subagent_required`, invoke that host's native `bench-decider` as described above. Require `{"answers": {"QUESTION_ID": {"type": "choice", "choice": "ALLOWED_ID"}}}` or `{"type": "noul", "noul": 0.0}` for each answer. The IDs, types, and values must correspond to the request. Validate its saved reply with `python scripts/decide.py --host HOST --request REQUEST.json --response REPLY.json` before using it. The helper's `model` identifies the requested model; record the actual model from host metadata separately.
5. A confidence value is a signal, not an observed success rate. Subagent confidence is self-reported. For abstention, uncertain answers, or insufficient benchmark evidence, return to the caller rather than guessing a profile. Choose thresholds from representative task results; never use a probability as a new benchmark score.
6. Build the existing selection record from the validated profile ID and current `assessment_digest`, with policy ID `bench-router-jev` or `bench-router-cheap-subagent`. Generate a short factual `reason` from selected evidence IDs and policy; neither Jev nor a cheap subagent needs to write an essay. Record model/version, facets, wiki/snapshot hashes, selected unit IDs and supplied answers alongside the selection. Recheck this evidence provenance before dispatch: the existing assessment digest does not include Wiki/facet evidence. If it changed, repeat the decision. Run normal `route --selection` with the same task/context; Router rechecks constraints and availability.

Request example (both backends use the same shape):

```json
{"state": "Implement a React dashboard with routing and shared state.",
 "questions": {"webdev_react": {
   "type": "noul",
   "instructions": "Does the requested deliverable require a multi-file React web application, including component structure or shared state?"
 }}}
```

Batch independent facet questions into one call. The final profile choice follows local evidence retrieval, so it may need a second call. Keep common benchmark details and all-missing rows summarized; expand them when relevant. Persist full evidence locally and give the parent only the decision, provenance, and unresolved issues. These provider calls belong to this Skill workflow; plain `route` keeps its existing offline automatic policy.

Official Jev request/response reference: <https://docs.typesafe.ai/api>. Model IDs and prices: <https://docs.typesafe.ai/models>.
