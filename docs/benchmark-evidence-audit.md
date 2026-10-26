# Benchmark freshness, missing evidence and source audit

Checked 2026-10-26 against official pages in the Windows-installed Ego browser. The implementation is in the original bench-router repository, on `fix/benchmark-evidence-policy`. Existing unrelated work was preserved.

## Result

The saved selection passages were authentic, but incomplete coverage and interpretation prevented them from establishing an optimal model/effort for the earlier task. The stored OpenAI table omitted its interactive recommender. A strict deliverable was also described as demanding reasoning, and task priority disappeared before vendor guidance. The earlier Astra/xhigh choice was an upstream choice after router abstention, not a benchmark-proven optimum.

Policy 7 retains task priority, adds the verified conditional Luna starting points, uses one freshness policy, permits explicit same-vendor measured proxies and compares compatible subsets. It does not guarantee minimum cost or task success. Existing policy 6 selections require reassessment for new dispatch; existing execution receipts remain recoverable.

## Freshness and missing values

| State | Treatment |
|---|---|
| Age <= source TTL | Fresh; refresh can skip network |
| TTL < age <= max_stale | Last-good observations remain usable and comparable, marked stale |
| Age > max_stale | Observations excluded |
| Failed refresh | Keep last-good; record attempt/error; never reset successful measurement age |
| Missing/null after a recent source check | Use an explicitly marked nearest same-vendor measured proxy where available |
| No recent check or no eligible same-vendor observation | Retain missing value and request a check; never treat it as zero |

`evaluate --refresh` checks due automatic sources before loading the assessment snapshot and returns `benchmark_refresh`. Run it only for the initial assessment; it is rejected with `--decision-response` so a replay cannot silently change evidence. Normal evaluation remains offline. Manual SWE/TB sources still require explicit imports. A successful refresh with missing/null cells is different from a failed collection. The report and retained source attempt/error metadata expose that distinction.

Proxy preference is the same model, then the same name-derived family, then name similarity and measured effort proximity, with stable profile ID ties. Only enabled, non-excluded, fingerprint-valid registered donors from the same known vendor are eligible. The source must have been checked within its TTL; a failed recent check permits last-good data only within max_stale. Unknown vendors remain missing. The donor score, conditions, model/profile/effort, stale flag, refresh outcome and original missing reason are preserved. The proxy is never an exact measurement of the requested profile. Name similarity is a heuristic, not a calibrated prediction.

Comparisons expose `comparison_profiles`. A missing candidate no longer blocks an otherwise compatible cohort. The largest compatible group is used, preferring exact comparisons when there is sufficient exact coverage; separate datasets/protocols are not merged. Other candidates remain visible with their missing evidence. Equal proxy donors do not create independent measurements. Diagnostics now distinguish accepted task evidence from actual missing task evaluations.

Model Gap previously stored `effort` inside display conditions but set the matching field to null. Adapter 5 retains both. `refresh --force` reparses unchanged payloads immediately after upgrading; without force a still-fresh source waits until it is due.

## Direct vendor-source comparison

Evidence is under [the dated capture directory](evidence/2026-10-26-source-audit/manifest.json). HTML captures are gzip-compressed without changing their decoded bytes. Browser text and Defuddle Markdown are separate artifacts. Original archived wiki captures were left intact.

| Check | Finding |
|---|---|
| Existing `guidelines.toml` selection rows | All 29 stored workload/role/escalation/thinking-rule rows matched official text at sentence level after ignoring case, punctuation and layout |
| Existing wiki reference and archived quoted lines for these sources | All 127 nonempty quote lines matched after removing Markdown links/list numbering/code fences and ignoring layout/punctuation |
| Claude selection and effort | Confirmed model-specific defaults and conditional escalation; several extra constraints came from the separate model prompting pages, which were also opened directly |
| Google model and thinking selection | Confirmed model roles and model-specific supported/default thinking levels |
| OpenAI static starting table | Seven stored rows matched, including Astra/xhigh for demanding analysis; the table alone was incomplete |

The row-level [guideline comparison](evidence/2026-10-26-source-audit/guideline-comparison.json) records the pre-change guide version and fragments. The [wiki quote comparison](evidence/2026-10-26-source-audit/wiki-quote-comparison.json) records source file/line and match result. These are bounded substring checks, not proof that every original page section was captured or that a semantic choice was optimal. This audit covers selection-related pages and the four Claude prompting pages used in selection; it does not claim a fresh audit of every output-only OpenAI/Google prompt snippet.

The [OpenAI interactive capture](evidence/2026-10-26-source-audit/openai-interactive.json) records the actual browser results for `Software engineering → Fix a well-scoped bug`:

| Priority input | Recommended model | Effort |
|---|---|---|
| Lower latency & costs | Luna | Low |
| Balanced | Luna | Medium |
| Higher quality outputs | Luna | High |

The missing Medium/High options were added with their task and priority context, rather than generalized to all engineering tasks. The earlier setup task is not literally a bug fix, so this observation does not prove Luna/Medium is its optimum. It proves the saved static table did not represent all official recommendations, and that high precision requirements alone do not justify Astra/xhigh. The original page itself calls for testing alternatives against actual quality needs.

Official sources: [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection), [Claude model selection](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model), [Claude effort](https://platform.claude.com/docs/en/build-with-claude/effort), [Gemini models](https://ai.google.dev/gemini-api/docs/models), [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking). Individual prompting URLs and capture hashes are in the manifest.

## Defuddle and Windows Ego collection review

Ego was invoked through the Windows executable from WSL, using one task space and reusing one page. It successfully rendered the official pages and changed the OpenAI work category and priority through browser actions. This exposed recommendations unavailable in a static table-only capture.

Defuddle successfully converted every captured HTML document to Markdown. It is useful for readable prose and tables and remains an audit tool, with no new router runtime dependency. It does not certify that interactive states or hidden rows have been covered.

The [Terminal-Bench original](https://www.tbench.ai/) renders 23 representative model rows. Its page hydration data contains **35** leaderboard rows, including Astra/Codex at max, xhigh, high, medium and low, each with 330 trials. A text-only representative table therefore loses effort coverage. The decoded primary data is saved as [terminal-leaderboard-data.json](evidence/2026-10-26-source-audit/terminal-leaderboard-data.json), preserving effort, agent, trials, scores, confidence intervals and costs. This is a real collection coverage gap, not evidence that the missing effort was unpublished.

For better collection, use the primary structured response/page data when it exists, retain raw payloads and schema/protocol fields, and use Ego plus Defuddle to verify rendered content and contextual recommendations. The `tb_auto` source now parses the public hydration data into `terminal_proxy`, retaining its published agent, effort and trial count. It remains model-proxy evidence because the public agent label does not establish the installed CLI version/scaffold configuration required for an exact-profile claim. Manual imports still enforce the existing dataset/protocol contract.

## Validation

Run the standard repository suite plus `test_evidence_policy`. Regression coverage includes TTL boundaries, refresh failure and last-good retention, snapshot/status agreement, missing-source status, same-model effort and nearby-model proxies, cross-vendor exclusion, measured zero, partial protocol coverage, priority propagation, interactive recommendation conditions, explicit refresh/replay isolation and Model Gap effort matching.

Initial freshness change: **192 tests run, OK, 2 skipped**. `git diff --check` passed and all 34 capture artifact hashes were verified. Existing subprocess/SQLite ResourceWarnings also occurred on the pre-change baseline; they are outside this change. Existing unrelated diffs were checked against the saved baseline and preserved.

The follow-up implements independent concurrent vendor calls: Jev uses a bounded thread pool; native handoff returns every unresolved vendor packet under `decision.requests` for concurrent host subagents. Each call sees only its vendor guide and preserves its own digest/provider/model/usage. Out-of-order replies are stored canonically; successful siblings survive a partial failure. A barrier-based regression fails if the vendor calls become sequential.

## Follow-up collection verification

`refresh --source tb_auto --force` succeeded against the public site with one HTTP request: 35 published rows, 34 observations, and one explicit `none` effort row retained in the raw payload but excluded from supported-effort observations. HTTP retry, size, request budget, deadline and last-good handling reuse the existing collector path. Fragmented Flight records are reassembled as data without executing scripts. Version/package, dataset revision, model/agent, effort, duplicate row, score and trial-count checks fail closed.

The shared snapshot linked Terminal-Bench observations to 59 of 73 configured profiles (including labeled effort proxies); the evidence table supplied 14 additional same-vendor nearby proxies, with zero missing cells in this smoke task. All cells remained `model_proxy`. Agent cohorts stay separate, so that table coverage does not imply a comparable cross-vendor ranking. [Recorded smoke result](evidence/2026-10-26-followup-smoke.json).

The live source exposed two mapping hazards: Anthropic display labels omit the Claude prefix, while a Fable 5.1 link slug names another release. Matching now retains the display version and adds the missing vendor prefix only for official Anthropic links; it does not substitute the link slug as the model ID. The release-date field is preserved as `model_release_date`, not misreported as `evaluated_at`. Published metrics (confidence intervals, cost and tokens included) remain in measurement conditions.

The bundled facet index now includes `terminal_proxy`; runtime code and the installed-skill source use the same collector and concurrent guidance implementation. No new runtime dependency was added.

Follow-up validation: **198 tests run, OK, 2 skipped**; `wiki compile --check` and `git diff --check` passed. Unrelated pre-existing diffs were verified unchanged. The live collection smoke used the shared cache and completed without worker dispatch or paid decision API calls.
