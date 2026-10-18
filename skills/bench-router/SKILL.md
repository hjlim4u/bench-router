---
name: bench-router
description: Select and delegate a bounded task to a local coding agent through bench-router, then collect its result, or fan out several subtasks or best-of-N attempts to agents in isolated git worktrees that can share a scratchpad or deliberate. Use when an orchestrator wants a benchmark-informed agent handoff; do not invoke from inside a bench-router delegated run.
---

# Bench-router handoff

Use this skill only for a task the caller wants to hand off. The router validates the selected profile, owns dispatch receipts, and collects results. The caller still verifies the work and records feedback.

## Setup

- Run `scripts/cli.py` with Python 3.11+ from this skill's installed path. The script resolves the linked repository and forwards arguments to the existing CLI; it works from any current directory.
- Use the same runtime user's default config (`~/.config/bench-router`) and cache (`~/.cache/bench-router`) across agents, unless the operator has deliberately set shared `XDG_CONFIG_HOME` and `XDG_CACHE_HOME`. Keep all agents sharing a cache on one OS runtime; native Windows and WSL use different lock implementations and must not concurrently point at the same physical cache. Do not create agent-specific caches or copy snapshots.
- `profiles.toml`, Herdr, herdr-projects 1.2.1 and the target agent CLI must already be configured for live dispatch on Linux/WSL2. The task `cwd` must be the top level of a git repository with a commit. Profile `args` may only carry a model (`--model`/`-m`) and an effort; agent permissions follow the board's `worker.access` setting. See [Projects setup](../../docs/projects.md). Run `python scripts/cli.py status` to inspect snapshot health. See the [reference](../../docs/reference.md) for setup and command contracts.

## Delegate and recover

Use the [cheap decision workflow](references/decision.md) for semantic facets and final profile selection: Jev when `TYPESAFE_API_KEY` (or `JEV_API_KEY`) is set, otherwise the host's native `bench-decider` (Antigravity Flash, Codex GPT-6 Luna, Claude Code Haiku). Pass the current host through `scripts/decide.py --host antigravity|codex|claude`; `BENCH_ROUTER_DECISION_MODEL` overrides its model. Read that reference before choosing; the helper implements provider detection and response validation. Do not send these decisions through Router delegation or recursively invoke this Skill.

1. Create a temporary UTF-8 JSON task file with `schema_version: "1.0"`, a unique `task_id` (UUID hex is suitable), `round: 1`, `summary`, `prompt`, and an existing, trusted absolute `cwd`. Add only relevant optional task fields. Keep the task content and `(task_id, round)` stable for retries; use a new round only after checking the previous run's effects. Remove the temporary file once its CLI output is captured.
   Tag the task's nature in `facets` (`{axis: [value]}`) using only the values listed by `python scripts/cli.py wiki facets`; pick every value that fits the prompt and omit axes that do not apply. The output includes descriptions in `facets` and automatic detection rules in `detection`. Rules inspect language, file types and code blocks, but you can explicitly tag any listed value when a rule misses it (e.g. `task: webdev_react` for a React request without context files). `evidence --task TASK_FILE --format table` then shows matching benchmark results per profile, with task type matches first; an unknown value fails with the allowed list, so correct it from that list. This evidence table does not change the legacy automatic selection made by plain `route`; use `evaluate` and `route --selection` when making an Orchestrator choice from it.
2. Run `python scripts/cli.py route --task TASK_FILE --selection SELECTION_FILE` with the validated decision from the workflow above. Pass global options such as `--herdr-session` before `route` when needed. Read the JSON `status` even when the process exits nonzero, and retain `run_id` and `cwd` for recovery. Add `--dry-run` to validate selection without dispatch. Plain `route` still uses the legacy automatic policy when the caller explicitly requests it.
3. For `blocked`, address the reported approval or question through the normal caller workflow. For `timed_out` or `delivery_uncertain`, run `collect --run-id RUN_ID --cwd CWD --wait-ms N`; never generate a fresh task ID or resend the prompt to resolve uncertainty. For `conflict`, inspect the warning and existing receipt before another dispatch. A completed result means the artifact contract passed, not that the task succeeded.
4. A `completed` run's agent panes are closed automatically so finished agents stop holding resources (`release` in the output; agents still working or blocked are left open). To continue that agent's conversation, run `python scripts/cli.py resume --run-id RUN_ID --cwd CWD`; it reopens the board task's space and restarts the agent in the same session without sending anything.
5. Inspect the returned result and verify the requested work. Record the verified outcome with `feedback --run-id RUN_ID --cwd CWD --outcome success|partial|fail` when there is a run to assess.

## Parallel handoff

Default to `route`. Use `parallel` only when independent subtasks or a comparison of approaches is worth the cost: it starts tasks × fanout agents, and `deliberate` doubles that with a review round.

For several subtasks or a best-of-N attempt, write a group file (`group_id`, git top-level `cwd`, `tasks` without `cwd`, optional `fanout`, `max_parallel`, `isolation`) and run `python scripts/cli.py parallel --group GROUP_FILE` (`--dry-run` to preview profiles). Each agent works in its own git worktree. Choose `isolation`: `isolated` (no sharing), `shared` (agents share notes and intermediate results in a scratchpad), or `deliberate` (shared plus a review round with votes; read `consensus.winner`). Rerun the same group file to recover; it never resends prompts. Each member's `worktree`/`branch` is where the board committed the agent's work; compare and merge those branches yourself, then remove the worktrees.

- Worktrees start from `HEAD`; uncommitted changes in `cwd` are not included (`dirty_base` warning).
- The main repository must already be trusted in each agent CLI; otherwise agents report `blocked` at startup. Worktrees under a trusted repository were not asked again.
- A member that was `blocked` before its prompt is not resent by rerunning the same group. Resolve the cause, then use a new `group_id` or `round`.
- With two members, votes often tie (`consensus.winner` is `null`); use three or more members when a majority matters.

## Projects collaboration

Use ordinary `route` tasks for implementation, review and revision. Pass earlier artifacts explicitly in each new round. For blocked work use the returned board task ID (`thread_id`, e.g. `repo/12`) with `herdr-projects details`, and answer it on the board through the caller's normal approval workflow. Never delegate, retry or tell the task directly to recover a Router submission. All Router executions share durable task binding, the four-active limit and the overlapping-workspace guard. Verify results and record `coordination feedback` separately; do not delegate recursively. Shared/deliberate scratchpads sit outside each agent's worktree; with `worker.access ask` every write there needs approval.

## Shared data

Routing reads the shared snapshot; it does not refresh it. One user-level scheduled `refresh` can keep data current. Run `python scripts/cli.py refresh` manually only when explicitly requested or operating the shared schedule. Concurrent refreshes and dispatches to the same `cwd` return a busy/conflict result; do not work around their locks. See `status` and the JSON warnings for stale or missing evidence.
