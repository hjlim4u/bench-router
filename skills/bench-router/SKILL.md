---
name: bench-router
description: Select and delegate a bounded task to a local coding agent through bench-router, then collect its result. Use when an orchestrator wants a benchmark-informed agent handoff; do not invoke from inside a bench-router delegated run.
---

# Bench-router handoff

Use this skill only for a task the caller wants to hand off. The router owns profile selection, dispatch receipts, and result collection. The caller still verifies the work and records feedback.

## Setup

- Run `scripts/cli.py` with Python 3.11+ from this skill's installed path. The script resolves the linked repository and forwards arguments to the existing CLI; it works from any current directory.
- Use the same runtime user's default config (`~/.config/bench-router`) and cache (`~/.cache/bench-router`) across agents, unless the operator has deliberately set shared `XDG_CONFIG_HOME` and `XDG_CACHE_HOME`. Keep all agents sharing a cache on one OS runtime; native Windows and WSL use different lock implementations and must not concurrently point at the same physical cache. Do not create agent-specific caches or copy snapshots.
- `profiles.toml`, herdr, and the target agent CLI must already be configured for live dispatch. Run `python scripts/cli.py status` to inspect snapshot health. See the repository [README](../../README.md) for setup and command contracts.

## Delegate and recover

1. Create a temporary UTF-8 JSON task file with `schema_version: "1.0"`, a unique `task_id` (UUID hex is suitable), `round: 1`, `summary`, `prompt`, and an existing, trusted absolute `cwd`. Add only relevant optional task fields. Keep the task content and `(task_id, round)` stable for retries; use a new round only after checking the previous run's effects. Remove the temporary file once its CLI output is captured.
2. Run `python scripts/cli.py route --task TASK_FILE`. Pass global options such as `--herdr-session` before `route` when needed. Read the JSON `status` even when the process exits nonzero, and retain `run_id` and `cwd` for recovery. `route --dry-run` selects without dispatch.
3. For `blocked`, address the reported approval or question through the normal caller workflow. For `timed_out` or `delivery_uncertain`, run `collect --run-id RUN_ID --cwd CWD --wait-ms N`; never generate a fresh task ID or resend the prompt to resolve uncertainty. For `conflict`, inspect the warning and existing receipt before another dispatch. A completed result means the artifact contract passed, not that the task succeeded.
4. Inspect the returned result and verify the requested work. Record the verified outcome with `feedback --run-id RUN_ID --cwd CWD --outcome success|partial|fail` when there is a run to assess.

## Shared data

Routing reads the shared snapshot; it does not refresh it. One user-level scheduled `refresh` can keep data current. Run `python scripts/cli.py refresh` manually only when explicitly requested or operating the shared schedule. Concurrent refreshes and dispatches to the same `cwd` return a busy/conflict result; do not work around their locks. See `status` and the JSON warnings for stale or missing evidence.
