# bench-router Documentation & Current State

Updated: 2026-10-24 · Python 3.11+ · Selection Policy: `vendor-guided` version `6`

bench-router **provides benchmark evidence for matching CLI Agent profiles to delegated tasks and bridges selection with execution**. The runnable implementation lives in `bench_router/`. The Orchestrator handles delegation decisions, task decomposition, team formation, final selection, and result adoption, while the router checks hard constraints, official guidance, comparable benchmarks, and selection history. Actual execution is delegated to herdr-projects 1.2.1 and Herdr.

## Run First

Run from the repository root. No extra installation is needed for the offline CLI.

```bash
python3 -m bench_router.cli --help
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
python3 -m bench_router.cli wiki compile --check
```

Configuration defaults to `~/.config/bench-router/profiles.toml`, and cache defaults to `~/.cache/bench-router`. `examples/profiles.example.toml` contains disabled placeholders. Edit manually or generate via `profiles discover`. Overwriting an existing config requires `--force`. Arena refresh requires `pyarrow`, so run `mise install` followed by `mise run setup`.

## Current Selection and Execution Flow

1. Receive an offline decision packet via `route --task task.json --host codex --dry-run`. Match the host to your actual environment. `decision_required` and exit code 17 indicate an incomplete decision.
2. Collect responses in the order of `analysis` → eligible vendor `guidance` → `benchmark` (if needed), and supply them via `--decision-response`. Neither dry-run nor `evaluate` performs network access, Herdr invocation, or file writes.
3. When multiple viable candidates remain, no automatic ranking is generated. Based on completed evaluation (schema 4.0) from `evaluate --format 3`, the upstream Orchestrator produces selection 6.0 via `select`. When there is a single viable candidate and no unverified conditions, automatic selection 5.0 is possible. The CLI format number differs from the JSON schema version.
4. Revalidate with `route --selection selection.json --dry-run`, and drop `--dry-run` for live execution. Current constraints and availability are re-checked. For a previously submitted identical task/round, recovering an existing receipt takes precedence over making a new decision.
5. Inspect the result contract with `collect`, and upstream reviews actual success to submit `feedback`. Note: `completed` represents receipt reception status, not a quality pass verdict.

Weighted sum, near-tie, default/fallback automatic selection, and `--policy legacy` have been removed. `evaluate` default output is facts/constraints inquiry in 2.0; vendor-guided candidate suitability is provided under `--format 3`. Legacy selection 2.0 and `--profile` are preserved as explicit overrides.

## Documentation Map

| Document | Description |
|---|---|
| [README](README.md) | Installation, quick start, overall overview |
| [01 Intent and Decisions](01_INTENT_AND_DECISIONS.md) | Responsibility boundaries and architectural rationale |
| [02 External Evidence](02_EVIDENCE_AND_DEPENDENCIES.md) | Verification scope for external dependencies and past research evidence |
| [03 Routing and Data Spec](03_ROUTING_AND_DATA_SPEC.md) | Collection, matching, freshness, and selection pathways |
| [04 Interface and Herdr](04_INTERFACE_AND_HERDR.md) | CLI, task, profile, result, and recovery contracts |
| [05 Implementation Playbook](05_IMPLEMENTATION_PLAYBOOK.md) | Module structure, change procedures, operational commands |
| [06 Validation and Open Items](06_VALIDATION_AND_OPEN_ITEMS.md) | Current validation coverage and remaining verification |
| [Vendor-guided Policy](docs/vendor-guided-routing.md) | Policy 6 phases, decision responses, selection replay |
| [Routing Contracts](docs/routing-contracts.md) · [Upstream Integration](docs/orchestrator.md) | Versions and usage for context, assessment, selection, and group |
| [Projects Execution](docs/projects.md) · [Detailed Reference](docs/reference.md) | Execution backend, permissions, complete CLI commands |
| [Orchestration Boundary](docs/orchestration-boundary.md) | Distinguishing upstream pattern policies from single-task routing |
| [Implementation Status](docs/implementation-status.md) | Current capabilities, verification results, historical measurement records |

## Standards for Reading Documentation and Evidence

Follow user requirements and repository `AGENTS.md` first. Cross-reference current behavior against code and tests; refer to vendor-guided docs for detailed selection contracts and Projects docs for execution. Do not interpret early design weights or past eval results as current selection policy. Research and analysis documents represent records as of their respective verification dates.

Fixture passing, external live data calls, live Agent smoke tests, and batch task quality/cost evaluations are distinct forms of evidence. Past direct Herdr smoke tests and legacy batch comparisons do not validate current Projects execution or Policy 6. API keys, logins, and specific model access must be confirmed in each operational environment.
