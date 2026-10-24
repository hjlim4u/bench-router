# Validation Scope, Completion Criteria, and Open Items

Updated: 2026-10-24. Current test suites extend the original V01–V40 test scenarios; expected outputs from removed legacy selection rules are not used as current contracts.

## Offline Verification

```bash
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
python3 -m bench_router.cli wiki compile --check
```

| File | Current Verification Scope |
|---|---|
| `test_p0.py` | Input, context metrics, hard constraints, percentiles, quality/coverage, basic evaluation, facet rules, wiki/evidence, vendor-guided phases, guidelines, relevance, public evaluation, selection 6.0 |
| `test_p1.py` | AA pagination, Arena/MG fixtures, malformed payload isolation, partial failures & last-known-good, aliases, efforts, evaluation conditions, deadlines, locking, atomic publishing |
| `test_p2.py` | Projects and headless execution, argv, receipts, result paths/nonces/hashes, blocked, timeout, uncertain delivery, recovery, explicit controls, selection revalidation |
| `test_p3.py` | Worktree isolation, shared scratchpads, group selection, frozen plans, recovery, repeated selection, delivery states, limits |
| `test_coordination.py` | Shared admission (limit 4), path overlaps, ownership, quiescence checks, result adoption, Projects integration |
| `test_codeburn.py` | CodeBurn availability, quotas, usage tracking, profile discovery fixtures |

External CLIs are mocked/faked, while Git worktrees are created for real in temporary directories. Offline tests do not certify the behavior of live models, PTYs, board tickers, or account quotas. Execution outcomes and dates are recorded in [Implementation Status](docs/implementation-status.md).

## Key Verification Criteria for Current Selection Contracts

- Hard constraint failure prevents selection and execution. Benchmark data gaps do not trigger hard elimination and are distinguished from a score of zero.
- Default `evaluate` 2.0 outputs facts, constraints, and quality/coverage without making a selection. Does not output `score`, `legacy_score`, or `cost_proxy`.
- Policy 6 follows: analysis → eligible vendor guidance → benchmark relevance if needed. Follows official vendor guidelines and model ID / effort mappings without unifying distinct vendor principles onto a shared scale.
- Decision requests send only information required for that specific phase. Configurations absent from guidelines retain provisional states such as `guidance_missing`.
- Compares only comparable evaluation conditions and fresh raw values. Never mixes exact and proxy observations or percentiles from different cohorts into composite scores or plurality votes.
- Multiple viable candidates trigger `upstream_selection_required`. Even a single viable candidate is not selected automatically if unverified conditions or relevance abstentions exist.
- In completed format 3 evaluations (schema 4.0), `select` generates selection 6.0. Provisional and alternative classifications require explicit acceptance, and unsuitable or hard-failing candidates cannot be bypassed.
- Selection 5.0 is bound to a single router recommendation. Selection 6.0 allows selecting alternative viable candidates under upstream policy. Selection 2.0 overrides and `--profile` emit distinct warnings. Historical selection schemas 3.0 and 4.0 must be re-evaluated.
- Input, evidence, or policy alterations mandate re-evaluation. Phase digests bind only actual dependencies; historical Policy 1–5 records are never reused for new selections.
- `dry-run`, `evaluate`, `explain`, and `evidence` perform no network requests, Herdr calls, or file writes. Unresolved decision packets and abstentions exit with code 17 without falling back automatically to legacy modes.

## Key Criteria for Execution and Recovery

- Identical `task_id`/`round` and semantic hash recover the existing receipt. Differing task contents or profile collisions are not executed. Changes to policies or decision APIs do not justify resending already submitted prompts.
- Execution intent is persisted to disk prior to invocation. Following dropped responses, timeouts, or crashes, delivery state is preserved and `collect_first` protocol is followed.
- `completed` requires verifying run ID, nonce, fingerprint, status, UTF-8 validity, file size, path locality, and SHA-256 hash. `checks` represents the worker's claims and is not executed automatically by the router.
- Pre-submission failures clean up receipts and admission slots. Uncertain execution slots are not released automatically without confirming worker quiescence.
- Group 2.0 counts repeated profiles as distinct execution instances. Enforces limits of 8 tasks per group, 16 items per group, and `max_parallel` 1–4. A single stale selection prevents execution of the entire group; no execution resources are allocated until all selections are validated.
- Preserves partial failures after execution; group re-invocations recover the frozen plan and receipts. Propagates `delivery_state` and `reassignment` to member rounds.

## Live Smoke Tests and Efficacy Evaluations are Distinct

In operational environments, verify Projects version, Herdr session, CLI login, model arguments, and permissions within an approved small Git project and profile set. Verify offline selection first, followed sequentially by live dispatch, identical task/round receipt recovery, `collect`, result hash/branch inspection, and `feedback`. Verify that uncommitted local changes are not transferred to workers.

Live verification against the Projects 1.2.1 pathway and task batch quality/cost evaluations under Policy 6 were not conducted as part of this documentation update. Past direct Herdr smoke tests and 20-task benchmark runs are documented in [eval/results/v1.md](eval/results/v1.md) and [Cost Records](eval/results/v1-cost.md), and do not demonstrate current policy efficacy.

Efficacy evaluation must compare fixed profiles, low-cost priority, and current upstream selection policies under identical tasks, environments, budgets, and acceptance checks. Record verified success/partial/fail rates, elapsed time, decision call costs, distinguished token counts versus cost proxies, abstentions, data gaps, constraint violations, and duplicate transmissions. Never claim statistical superiority based on a single 20-task exploratory run.

## Open Items and Operational Decisions

| Item | Current Status / Action Required |
|---|---|
| Projects Interactive / Headless Live | Verified with fake CLIs and real temporary worktrees; live models, PTYs, and recovery smoke tests must be validated in operational environments |
| Task-level Quality & Cost under Policy 6 | Provides official guidance compliance and comparative evidence without guaranteeing success or lowest cost; held-out task cohort evaluation needed |
| Workflow Effort Improvements | Retains `workflow_gain_unverified`; upstream reviews and accepts based on real task comparative evaluations |
| Accounts, Models, Quotas | Discovery and CodeBurn provide preliminary data; do not guarantee execution viability or entire team remaining budget |
| Exact Benchmark Data | Recognizes only rows matching model, harness, effort, and evaluation conditions; never fills gaps with proxies |
| OS Timers & Retention Policies | No automated timer installation; 30-day snapshot and user log retention parameters adjusted by operator |
| Overall Team Budget & Pattern Selection | Upstream responsibility; router contains no reservation, billing, DAG, or voting engines |
| Standalone JSON Schema & format 1 Removal | Runtime validators enforce contracts; deprecation/removal timeline determined independently |

Reports must state modified files, contract versions, reproduction commands, fixture vs. live status, actual validation outcomes, and boundaries. Always distinguish `completed` from final substantive quality approval.
