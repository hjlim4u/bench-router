# bench-router Implementation Status

Updated: 2026-10-24 · Corroborated implementation commit: `67d90a9` · This update is a documentation synchronization.

## Current Implementation

| Area | Implementation & Contracts |
|---|---|
| Selection | Vendor-guided Policy 6: analysis → vendor guidance → benchmark (if needed). Multiple viable candidates require upstream selection. |
| Public Assessment | `evaluate` default schema 2.0, `--format 1` compatibility, `--format 3` schema 4.0 semantic suitability, observations, and diagnostics. |
| Selection Records | Automated single-candidate 5.0 / `select` upstream choice 6.0. Legacy 2.0 and `--profile` serve as explicit overrides. |
| Guidelines | `guidelines.toml` pins official verbatim text, starting points per vendor, supported efforts, and escalation rules. No runtime web lookups. |
| Evidence | Wiki compiled index and facet lookups; retrieval for model selection is not bounded by the 12-unit table display limit; differentiates exact/proxy, freshness, and comparison conditions. |
| Data | AA pagination, Arena revision-pinned Parquet (`pyarrow`), The Model Gap JSON, and manual SWE/TB import. |
| Storage | SQLite sources/snapshots/observations, per-source last-good state, atomic publishing, recent 3 payloads, and 30-day snapshot reproducibility. |
| Live Dispatch | Projects 1.2.1 board interactive mode / Herdr worktree headless one-shot mode. Model and effort flag translation, receipts, and result contracts. |
| Recovery & Control | `collect`, multi-run waiting, explicit `tell`/`stop`, session `resume` for completed runs, and `feedback`. |
| Parallel Dispatch | Group 1.0/2.0, repeated selections, separate worktrees, frozen plans, receipt recovery, and member delivery state. 8 tasks, 16 items per group, max_parallel 1–4. |
| Admission | Max 4 shared active slots, path overlap prevention, ownership tracking, and adoption records. Pre-submission confirmed failure settles receipts and returns slots. |
| Availability & Discovery | PATH checks, `agy models`, optional CodeBurn quota, `profiles discover` (Claude guide/CLI effort flags, Codex cache, CodeBurn, agy models). |
| Environment | Core CLI uses Python 3.11+ stdlib. Arena refresh (`pyarrow`) and optional CodeBurn use uv/mise. |

Weighted sum scoring, cost discounts, near-tie logic, default/fallback auto-selection, and `--policy legacy` have been removed. Category quality/coverage metrics remain as evaluate 1/2 diagnostics. Historical vendor-guided selection 3.0/4.0 records are not accepted as current inputs and require re-evaluation. Replaying previously submitted receipts takes precedence over new policies.

## Validation Status (2026-10-24)

```bash
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
```

165 test executions: **163 passed, 2 skipped**. Skipped tests cover Windows-specific file sharing checks and real Parquet decoding in environments without pyarrow. Under Python 3.14, a single SQLite connection `ResourceWarning` is emitted with zero test failures. Tests use fake sources/CLIs and real temporary Git worktrees.

Checked 147 local links across 18 documents, 14 JSON examples, fenced code block pairs, and terminal-demo.svg XML. CLI smoke testing under temporary configurations verified default evaluate (schema 2.0, exit 0), evaluate --format 3 (schema 4.0, decision_required, exit 17), and route dry-run (schema 1.0, decision_required, exit 17). `wiki compile --check` and `git diff --check` also pass cleanly.

Actual Projects model execution, PTY handling, board ticker recovery, and Policy 6 real-world workflow quality and cost were not verified live in this pass. No external API refresh, paid inference calls, or live Agent submissions were executed during this documentation update.

## Historical Measurements and Interpretation Boundaries

| Record | Verified Scope |
|---|---|
| AA (2026-10-12) | Free API v4.3, 4 pages, 697 models collected. Verified coding null values and effort-specific alias differences at the time. |
| Arena (2026-10-12) | Revision `e16f9023…` fetched, verifying retries, TTL skips, error deadlines, and last-good cache fallback. |
| Arena Parquet Migration (2026-10-21) | Improved historical 26 requests / 600s / 47 missing wiki units down to 14 requests / 14s / 0 missing units. |
| Direct Herdr 0.9.3 Smoke (2026-10-12) | Verified Claude/Codex execution, blocked states, result hashes, identical task/round receipt recovery, and duplicate suppression. Does not certify current Projects execution. |
| Prior Parallel Smoke (2026-10-13) | Verified two worktrees, two rounds, and shared scratchpad. The deliberate mode of that era has since been removed. |
| Benchmark Suite v1 | 20 tasks × 2 profiles: fixed default 20/20, low-cost-first 19/20, legacy router 20/20. |

The API-equivalent cost per success in v1 was $0.234 / $0.070 / $0.217. These represent token counts converted to API list prices, not actual subscription expenditures. Constrained by 1 attempt per task and ceiling effects on simpler tasks, where the legacy router selected the default profile in 18 of 20 cases. Do not interpret these as evidence of quality or cost gains under the current policy. Detailed results: [v1](../eval/results/v1.md) and [v1-cost](../eval/results/v1-cost.md). External CLI evidence resides in [evidence/herdr-0.9.3](evidence/herdr-0.9.3/skill.md).

Historical permission flags, configuration paths, and incomplete checklists from earlier environments must not be applied to current operations. Current interactive permissions follow Projects `worker.access`; headless permissions follow [Reference](reference.md#headless-execution).

## Remaining Work and Operational Limits

- Real-world Agent smoke testing and error recovery validation across Projects interactive and headless modes.
- Evaluating held-out task quality, inference cost, and runtime for Policy 6 and upstream selection policies. Empirical workflow effort gains must be compared in upstream environments.
- Confirming account-level CLI/model/effort availability and quota windows, and supplementing comparable exact observations. Profile discovery does not guarantee successful API invocations.
- No automated OS timer installation. Configuration files, API credentials, and snapshot retention policies must be managed by the operator.
- CLI fingerprint versions remain `unknown`. Decisions and feedback are recorded per run without logging aggregate execution tokens in the router.
- Remote worker execution, automated agent pools, global team budget reservation/settlement, DAG execution graphs, voting schemes, and multi-agent pattern selection remain outside the implementation scope.

For current usage instructions, consult [README](../README.md), [Policy](vendor-guided-routing.md), [Orchestrator Integration](orchestrator.md), [Projects](projects.md), and [Validation Criteria](../06_VALIDATION_AND_OPEN_ITEMS.md).
