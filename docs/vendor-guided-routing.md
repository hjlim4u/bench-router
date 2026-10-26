# Vendor-guided Routing Policy

The default selection policy for `route`, `explain`, `parallel`, and installed Skills is `vendor-guided`.
`evaluate` remains factual inquiry without selection.

## Selection Sequence

1. Determine executable profiles using hard constraints.
2. `analysis`: Jev or the native `bench-decider` jointly evaluates unconfirmed facets along with clarity, reasoning requirements, autonomy level, and completion criteria from the task summary and requirements. Task types derived from keywords, code blocks, or file extensions serve as `rule_hints` and can be rejected by semantic analysis. Rejected rules are never reapplied during retrieval. Explicit `task.facets` and structural facts such as language and prompt length are preserved. Ambiguous facets remain unconfirmed. Model names, benchmark scores, and file contents are never included in this request.
3. `guidance`: Sends a single request per vendor with eligible profiles to select one starting point assigned by that vendor's official documentation. Questions match the structure of the vendor guide, and all phrasing consists of verbatim quotes from official vendor pages. Principles from one vendor (e.g. OpenAI's "lightest setting") are never applied to another. OpenAI maps tasks to (model, effort) starting point rows (`guidance:openai`); Anthropic uses a model selection matrix (`state.models`) and per-model effort recommendation rows (`guidance:claude`); Gemini uses model roles (`guidance:gemini:model`) and model-agnostic thinking classes (`guidance:gemini:effort`: lookup/ordinary/advanced). The Gemini classification is mapped by code to the model's default and supported levels. If multiple rows cover the requirements, the verbatim `strategy` of that vendor is followed; if no rows cover the requirements, `__none__` is selected; if information is insufficient, `__unknown__` is selected. The request includes only that vendor's guide, sources, and task analysis—profile IDs, other vendors, and benchmark scores are excluded, so adding profiles or modifying other vendors' guides does not alter existing responses. Models without guidance or profiles with `unknown` effort are marked `provisional` and `guidance_missing` without sending a request.
   - Profiles matching the selected (model, effort) are marked `documented` regardless of harness.
   - Other profiles from the same vendor become `alternative` (`not_guided_starting_point`). If the selected starting point is not registered in configuration, `guided_configuration_not_registered` is flagged. Escalation efforts designated for use only after evaluation also receive `workflow_gain_unverified`.
   - `__none__` marks the entire vendor as `unsuitable`; `__unknown__` marks it as `provisional` (`guidance_fit_unresolved`).
4. Code retrieves reviewed facet evaluations strictly for the remaining candidates. Model selection retrieval is not subject to the top-12 display limit. Category evaluations are never arbitrarily recombined. Inactive units are excluded from the index; units that are incomparable, non-current, or only match general facets are recorded in `prefiltered_units` with stated rationale and excluded from semantic checks. Common agent reliability units are preserved as `auxiliary_units`. Missing values and observations per candidate are retained for diagnostic inspection.
5. Exact observations within max_stale sharing an identical measurement protocol are compared using raw values, preserving stale warnings after TTL. Model proxies (including explicitly marked nearest same-vendor measured proxies after a recent refresh check) are compared at the model level only under identical source, cohort, metric version, and protocol. If exact coverage is insufficient, exact observations can participate in this broader model comparison without retaining an exact comparison claim. `comparison_profiles` identifies the largest compatible cohort; other candidates remain missing or outside that comparison. Percentiles and separate protocols are never combined into rankings. See [freshness policy](../03_ROUTING_AND_DATA_SPEC.md#freshness-and-missing-data).
6. When comparisons pass prefiltering, a single `benchmark` request jointly determines relevance and basis. Only brief measurement descriptions, facets per suite, and original requirements are provided; candidate names, scores, source details, and Wiki bodies are omitted. `relevance:<unit>` is scored 0..1; `basis:<unit>` is either a facet of a directly measured core requirement or one of `__supporting__`, `__unrelated__`, or `__unknown__`. Units satisfying both a relevance score of 0.8+ and core requirement basis receive `accepted: true`. The 0.8 threshold is a policy cut-off, not a calibrated probability. Unit comparison results and relevance are provided to upstream layers without voting or summation. Missing data is never treated as a score of zero.
7. When multiple viable candidates remain, returns `decision_unavailable` (exit code 17) and `upstream_selection_required`. Candidates are never auto-narrowed by `quality`, `balanced`, `cost`, cost estimates, or default/fallback order. Upstream layers make the final choice via `evaluate --format 3` → `select` → `route --selection`. When exactly one viable candidate exists with no unverified conditions, single-candidate auto-routing (selection 5.0) can be used. If all comparison evidence is rejected, the router abstains from recommendation even in single-candidate cases. Constraints and availability are re-verified immediately prior to dispatch.

`alternative` profiles are excluded from evaluation retrieval, comparison, and automated selection, but upstream layers can explicitly select them via `select --accept-provisional` (the vendor guide's "escalation after evaluation" path). Efforts requiring evaluation retain `workflow_gain: null` and `workflow_gain_unverified` according to `escalation` rows in `guidelines.toml`. The router does not search lower-effort control groups or upgrade suitability based on benchmark superiority. Verifying and accepting improvements in real workflows is the responsibility of the upstream layer. `select --accept-provisional` explicitly accepts unverified conditions but does not resolve them.

Composite scores and cross-vendor effort scales are never synthesized. The decision agent evaluates semantic suitability, and code does not certify the truthfulness of that evaluation.
Resolving ties, benchmark conflicts, and cost-vs-quality trade-offs belongs to upstream policy. Models unlisted in official guides remain candidates flagged with `guidance_missing`. Neither quality nor minimum cost is guaranteed.
The router never alters registered profile execution arguments or synthesizes profiles dynamically.

## CLI and Offline Responses

```bash
python3 -m bench_router.cli route --task task.json --host codex --dry-run
python3 -m bench_router.cli route --task task.json --host codex --decision-response response.json --dry-run
python3 -m bench_router.cli route --task task.json --host codex --decision-response response.json
```

The first command outputs `decision_required` alongside the `decision` packet. Dry-run never invokes network calls or file writes, even if Jev keys are present.
The host forwards only the current packet's `request` to the native decision agent. The response file contains verified prior stages from `decision.completed` and the new response in sequence:

```json
{
  "stages": [
    {
      "request_digest": "<current decision.request_digest>",
      "provider": "subagent",
      "model": "<model from actual execution metadata>",
      "answers": {"<all question IDs in current stage>": {"type": "choice", "choice": "<allowed option>"}}
    }
  ]
}
```

Repeat the command with `--decision-response` to resolve subsequent stages. `decision.stage` proceeds through `analysis`, `guidance` per vendor (concurrent calls, recorded in vendor ID order), and `benchmark` if required. The initial stage can also be submitted as a single response object. Facet questions use `noul` responses. Separate facet decisions do not need to be invoked beforehand.

A matching `--host` argument is required. If the executing model differs from the requested model, `decision_unavailable` is returned.
`--decision-response` also accepts stored Jev responses (`provider: "jev"`).
Live `route` can invoke a configured Jev endpoint; if the key is missing or calls fail, it falls back to outputting native packets.
Both `decision_required` and `decision_unavailable` return exit code 17. The router never falls back to legacy selection upon abstention or failure.
If concrete dependencies of a stage change, responses for that stage must be re-acquired. When only the benchmark snapshot changes, task analysis and suitability responses can be reused, but the final selection record is regenerated. When upstream selection is required upon completing stages, invoke `evaluate --format 3` with the same response file to obtain the assessment. The returned `decision` includes reusable `stages` alongside candidate observations and relevance evidence.

## Selection Records and Compatibility

When upstream layers select a profile based on candidate assessment via their own policy, use `evaluate --format 3` → `select` → `route --selection`. Although the CLI format flag is 3, the returned assessment schema is **4.0** and the selection record is **6.0**. Profiles different from default recommendations can be chosen among viable candidates. Provisional (`provisional`) and alternative (`alternative`) profiles must be accepted using `--accept-provisional`; ineligible candidates or constraint failures cannot be bypassed. See [Orchestrator Integration](orchestrator.md#vendor-guided-candidate-assessments-and-upstream-choices). Legacy 2.0 overrides are preserved.

Single-candidate vendor-guided selection records are schema `5.0`, including `decision` within profile/digest/policy/reason. Upstream selections from format 3 assessments are schema `6.0`, adding `accept_provisional` to the same `decision`. Both formats preserve policy version `7` evaluation evidence; 5.0 is locked to the router's single candidate, while 6.0 records external policy selection and rationale. This does not imply quality certification of the external policy itself.
`decision` preserves `inputs`, the original `task`, ordered `stages`, `evaluation`, provider/model, and uncertainty. Each stage preserves request/digest/answers, actual provider/model, reported usage, and elapsed_ms (when present). `evaluation` contains shared unit definitions, sparse observations and missing data per candidate, conditional suitability checks, and actual comparison scopes.
The final digest binds this entire decision. Stage-level request digests bind only the contents of each request, preventing task analysis from being re-queried due to unrelated snapshot updates.
Historical elapsed time metrics are excluded, but expired evidence or estimates trigger re-evaluation due to freshness changes.
When passing recorded outputs to `route --selection`, output-only `source` annotations are removed.
Schema `2.0` selection records and `--profile` remain supported as explicit manual overrides, emitting warnings to distinguish them from new policy validation.
Schema `6.0` accepts only records produced by `evaluate --format 3` → `select`. Altering only the schema string of legacy records or changing the profile ID of a 5.0 record is rejected.
Historical vendor-guided selection schemas `3.0` and `4.0` are rejected as input. Policy version `1`–`6` selections cannot be reused and require re-evaluation. Replaying receipts for previously submitted executions retains priority over policy changes.
Replaying existing executions uses stored selections. Identical tasks are never re-dispatched due to new vendor guidelines or decision API outages.

### Relevance Evidence for Upstream Layers

`evidence.relevance[unit_id]` in `evaluate --format 3` and stored `decision.evaluation.relevance` provide identical evidence. Example:

```json
{"score": 0.9, "accepted": true, "basis": "task:repo_coding",
 "task_requirement": "Resolve an issue in an existing repository with a code patch",
 "reason": "The selected task requirement is judged directly measured by this unit.",
 "matched_facets": ["task:repo_coding"], "comparison_scope": "exact_profile",
 "source_page": "entities/benchmarks/swe-bench-verified-exact.md", "request_digest": "<benchmark request digest>"}
```

The original request is referenced in `decision.task`, measurement suite descriptions in `evidence.units[unit_id].desc`, and empirical measurement conditions in candidate `observations[unit_id]`. Descriptions are connected as structured evidence rather than re-synthesized per unit. `benchmark_relevance` represents relevance with rejected units marked as 0 and is not used for voting. `relevance.score` contains the original response. Upstream layers can apply independent agent/model allocation policies by inspecting supporting evidence, rejection reasons, auxiliary reliability, and proxy scopes. Decision contents reflect semantic assertions by evaluators, not execution success proofs. Tampered evidence fails digest or dispatch replay verification.

## Parallel Execution

`parallel --decision-response responses.json` accepts a map of member label → response object (e.g. `t1-1`).
When multiple viable candidates remain, this pathway also requires upstream selection. To allocate multiple models, generate selection 6.0 records from completed assessments and pass them via `selections` in group 2.0. Fan-out is never automatically completed using fallback profiles.
Task analysis and suitability evaluations are reused within the plan via request digests. Suitability is independent of fan-out order; subsequent selections exclude previously chosen profiles from evaluation retrieval and final comparison. Prior responses for each member are retained to resolve next packets. Caches persist only for the duration of the plan invocation without writing to disk. Stage records for each selection preserve original usage; summing fan-out records directly must not be interpreted as actual billing consumption.
Worktrees, group files, and workers are never created before all selections complete.
Upon launching execution, selections and group inputs are saved to `plan.json`. Re-running the same group recovers these selections and existing receipts.
Modified group inputs constitute conflicts, and stale selections for unexecuted members are rejected during holistic pre-validation.
`selections` in group 2.0 is an ordered list of execution instances, allowing repeated profiles. Repeated entries retain separate labels, worktrees, and receipts, counting towards limits of 8 tasks per group and 16 items per group. Member `rounds` preserve `delivery_state` and `reassignment`; uncertain or incomplete runs follow `collect_first` before reassignment.

## Guidelines Maintenance

`bench_router/guidelines.toml` contains version-pinned policy data extracted from official reference documents in the wiki.
Entries follow the verbatim format of vendor documentation. `start` contains task → (model, effort) starting point rows; Gemini contains model roles (`model`: including defaults and supported levels) and model-agnostic `effort_class`; `escalation` contains efforts designated strictly for post-evaluation use. Each vendor entry records revision, `strategy`, official URL, wiki path, and research date.
Model IDs are never matched via prefixes or fuzzy names. Other efforts for models present in the guide become `alternative`; models missing from the guide or `unknown` efforts become `guidance_missing`.
This represents a curated list of reviewed task-level recommendations, not an exhaustive inventory of supported efforts.
Guideline file versions and contents are updated and reviewed together; runtime web queries or automated promotion of draft wiki pages are never performed.
Because guidelines are bundled within the package, Skills installed via copy operate identically without the wiki folder.

## Prompt Guidance for the Selected Model

`bench-router prompt-guidance --profile <ID>` (or `--model <MODEL_ID>`) outputs verbatim official prompt guidance from the vendor of the selected model. It runs offline without writing files.
Items consist of `topic`, verbatim `when` (the context of the advice), recommended prompt `text` (if provided), and provenance (`url`, wiki reference note, verbatim capture). Models absent from the guide return `prompt_guidance: null` with a `prompt_guidance_missing` warning.
The router never alters prompts or rewrites prompts passed to `route`. Formulating improvements and presenting them to users is decided by upstream layers. Because vendor advice can conflict (e.g. adding vs. stripping instructions), only items from the selected model's vendor are shown, and applying them requires task-specific judgment.
These items reside in `[[vendor.*.prompt_guidance]]` in `guidelines.toml` and do not affect selections, digests, or hashes. `when` and `text` must match verbatim captures in `wiki/_raw/_archived/`, verified by unit tests. The effectiveness of guides is not verified by this project; reported numbers reflect vendor self-reported results.

## Concurrent vendor guidance

After analysis, independent vendor packets are issued together. Live Jev calls run in a bounded standard-library thread pool. Native handoff exposes all unresolved packets in `decision.requests`; the host launches one cheap `bench-decider` per packet concurrently and sends only that vendor request. The first packet remains mirrored in `decision_request` for older callers. Append all replies to `decision.completed` in the response envelope; guidance replies may arrive in any order and are canonicalized by vendor ID. A failed vendor does not discard successful siblings, which remain in `completed`; only missing packets are retried. Request digests, provider/model validation and per-call usage remain separate. No combined cross-vendor prompt is used.
