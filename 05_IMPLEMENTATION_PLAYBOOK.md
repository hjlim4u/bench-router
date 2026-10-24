# Development and Operational Playbook

Updated: 2026-10-24. Initial P0–P3 implementation is complete. Reuse existing modules and contracts rather than initiating duplicate implementations.

## Module Structure

| File | Responsibility |
|---|---|
| `bench_router/cli.py` | argparse, config loading, per-command formatting, exit codes |
| `routing.py` | task/profile/context validation, facts, hard constraints, basic benchmark quality/coverage, selection compatibility |
| `decision.py` / `decision_provider.py` | Policy 6 phased decisions, suitability, evaluation comparison, digests, selection replay / Jev and native response contracts |
| `guidelines.toml` | Version-pinned vendor guide excerpts, starting points, post-evaluation escalation paths |
| `data.py` | AA/Arena/MG collection, manual imports, SQLite persistence, snapshot publishing |
| `wiki.py` / `evidence.py` | Reviewed wiki compilation / Per-facet evidence querying |
| `herdr.py` | Profile discovery, availability probing, Projects interactive / Herdr headless execution, receipt, collect, tell, stop, resume, result contract validation |
| `parallel.py` | Group validation, selection pre-flight checks, worktrees, frozen execution plans, parallel dispatch and collection |
| `coordination.py` / `locking.py` | Shared user admission, path overlap prevention / OS-specific file locking |
| `eval/` | Comparative task benchmarks, token/cost analysis, CodeBurn auxiliary utilities |
| `skills/bench-router/` | Installable Skill and CLI / decision entrypoint scripts |

## When Starting Changes

1. Check `git status` and applicable `AGENTS.md` files; preserve user modifications.
2. Verify touched contracts and callers directly in code. Cross-reference selection against [Vendor-guided Routing](docs/vendor-guided-routing.md), context/selection against [Routing Contracts](docs/routing-contracts.md), and execution against [Projects](docs/projects.md).
3. For behavioral changes, add synthetic fixtures to the corresponding `test_p*.py`, coordination, or codeburn tests. Never run unit tests against live external services.
4. Update documentation, CLI examples, and schema version impacts simultaneously. Do not reinterpret prior selection versions or alter receipt recovery precedence for task/round.
5. Ensure the entire offline test suite and relevant documentation checks pass. Explicitly distinguish test suite passes, real data runs, and live smoke tests in reports.

```bash
python3 -m bench_router.cli --help
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
python3 -m bench_router.cli wiki compile --check
```

## Installation and Setup

The core CLI runs entirely on the Python 3.11+ standard library. Arena refresh requires `pyarrow`, and the CodeBurn CLI is an optional utility for availability and quota monitoring.

```bash
mise install
mise run setup   # uv sync --extra arena
mise run test
# Run only when live network collection is needed:
mise run refresh # refreshes all sources with --force
```

User configuration and API credentials must never be committed to the repository. Copy and activate `examples/profiles.example.toml`, or generate via `profiles discover`. Discovery inspects installed CLI models, Codex caches, guidelines, and CodeBurn models, but cannot guarantee successful live account calls. Use `--force` explicitly when replacing an existing configuration file.

## From Selection to Collection

```bash
BR="python3 -m bench_router.cli"
$BR status
$BR route --task task.json --host codex --dry-run
$BR evaluate --format 3 --task task.json --host codex --decision-response responses.json
$BR select --assessment assessment.json --profile PROFILE \
  --policy-id team-policy --policy-version 1 --reason "Candidate review outcome for task"
```

`responses.json` contains the array of verified phase responses up to the current stage. Incomplete responses exit with code 17; inspect `status` to resolve the next packet. Save the complete output of `evaluate --format 3` as the assessment file, and extract only the inner `selection` object from the `select` output. For detailed response schemas, refer to [Upstream Integration](docs/orchestrator.md).

Live execution requires Linux or WSL2, Projects 1.2.1, Herdr, and authenticated target CLIs. `cwd` must be a clean Git repository root with at least one commit. Uncommitted changes are not transferred to the worker.

```bash
$BR route --task task.json --selection selection.json --dry-run
$BR --herdr-session work route --task task.json --selection selection.json --wait-ms 0
$BR collect --run-id RUN --cwd /abs/project --wait-ms 60000
$BR feedback --run-id RUN --cwd /abs/project --outcome success --evaluator orchestrator
```

`--wait-ms 0` still performs task submission before returning immediately. A returned status of `timed_out` is not an abort; monitor it via `collect`. Resubmissions recover existing receipts for the same task/round without sending a new prompt. Intentional re-runs must be dispatched as an explicit new round after confirming quiescence and reviewing partial side effects.

## Parallel Execution and Resource Management

The `selections` list in upstream group 2.0 represents an ordered execution sequence. Repeated profiles are launched as distinct workers and count toward limits of 8 tasks per group, 16 items per group, and `max_parallel` 1–4. Shared admission enforces an overall limit of 4 active concurrent runs. No worktrees, group manifests, or workers are created until all selections pass pre-flight validation.

Execution plans are frozen to disk; identical groups recover the existing plan. Check `delivery_state` and `reassignment`, following the `collect_first` protocol. Never auto-retry merely upon observing `partial_failure`. Patterns, DAGs, voting consensus, final result adoption, and overall budget remain the sole responsibility of the upstream Orchestrator.

When `completed`, managed panes are returned; `resume` reopens the existing session. `tell` and `stop` execute only upon explicit instruction. Pre-submission failures settle receipts and release admission slots. If execution delivery is uncertain, slots are not automatically released prior to quiescence verification. When necessary, record manual releases with `coordination release --confirmed-stopped --note ...`.

## Data Operations and Checkpoints

Run refresh manually or via operator-configured system timers. Adjust keys, absolute binary paths, config/cache directories, and timezones to the local environment, and avoid placing API keys directly in schedule files. The request path never populates an empty cache. Refer to [Timer Examples in Reference](docs/reference.md#정기-실행-예시-설치하지-않음).

Status documentation must record implementation revision, modified files, verification commands/results, source baseline dates and revisions, unresolved runs/receipts, contract versions, and remaining verification items. Never copy secrets or proprietary prompts. The current checkpoint is maintained in [Implementation Status](docs/implementation-status.md).
