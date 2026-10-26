# Projects Execution and Collaboration

The current execution pathway is `route` / `parallel` → herdr-projects 1.2.1 public CLI (board) → Herdr → Agent CLI.
The upstream agent decides task decomposition, profile selection, subsequent rounds, and result adoption.
bench-router maintains benchmark evaluations, hard constraints, execution logs, and result contract validation.

## Setup

- Live dispatch runs within the same user and Herdr session on Linux or WSL2.
- The certified contract version is Projects **1.2.1** (`herdr-projects version`). Other versions are rejected prior to submission; active runs are held as `delivery_uncertain` if the recorded version changes.
- Plugin installation and user configuration are managed by the operator. The router does not modify installations, credentials, or board configuration.
- The task `cwd` must be the root of a Git repository containing at least one commit. The board branches an agent-specific worktree from that HEAD (uncommitted changes are omitted, emitting a `dirty_base` warning).
- The router registers `.bench-router/` in the `cwd`'s `info/exclude` to prevent result files from polluting board commits.
- Receipts from version 0.2.34 (`backend: "projects"`) are not automatically migrated. Those workers must be inspected and cleaned up manually.

```bash
export PATH="$HOME/.local/bin:$PATH"
herdr --version                                   # herdr 0.9.3+ (https://herdr.dev)
herdr plugin install eliasstravik/herdr-projects  # Install Projects plugin
herdr-projects version                            # herdr-projects 1.2.1 (...)
# Optional: export BENCH_ROUTER_PROJECTS=/absolute/path/to/herdr-projects
python3 -m bench_router.cli route --task task.json
```

## Profiles and Permissions

Projects 1.2.1 has no named profiles. The router translates profile `kind/args` into task configuration arguments:

| Router args | board config |
|---|---|
| (none) | `--worker.agent KIND` (program default model) |
| `--model M` / `-m M` | `--worker.agent KIND/M` (name from `herdr-projects models KIND`) |
| `--effort E`, codex `-c model_reasoning_effort="E"` | `--worker.effort E` |

Other arguments (such as `--add-dir`) cannot be expressed and are rejected prior to submission (`execution_failed`, `not_attempted`).
Permissions directly follow board `worker.access` (`full` | `ask`). Modify via `herdr-projects set worker.access ask [--repo NAME]`.
Under `ask`, Claude prompts for approval on every edit, and Codex prompts on writes outside the worktree, transitioning to `blocked`.

Each receipt represents a single agent invocation. The router fixes the following parameters per task:
`--workspace.from here --workspace.cleanup false --review.when never --review.rounds 0 --merge.by you --merge.pr false --attempts.by 1 --plan.approve none --no-research`.

## Execution and Collection

The router atomically saves input and result contracts to `input.txt`, records submission intent, and invokes:
`add br-RUN_ID --desc PROMPT --repo CWD --delegate ... --json`. The returned task ID (`repo/N`) serves as `thread_id` in the output.
Because the prompt is passed as a single argv argument, the total size including result contracts is capped at 120 KiB.

Status is determined via `stage` / `state` from `list --all --json`; mismatched titles (`br-RUN_ID`) trigger a hold.

| board | Router status |
|---|---|
| stage `approval`/`done` | Checks result contract in `details` worktree → `completed` / `result_invalid` |
| state `blocked` (prompts, permissions, rate limits, etc.) | `blocked`, single-line summary from board in `diagnostic_tail` |
| stage `failed`/`nosummary`/`stopped`/`todo`, state `error` | `execution_failed` |
| stage `after`/`queued`/`starting` | `timed_out` (not yet started) |
| other (`working`, `checking`, etc.) | `timed_out` (in progress) |

- Result files are written to `.bench-router/runs/RUN_ID/` inside the agent worktree and copied to `<cwd>/.bench-router/runs/RUN_ID/` upon passing validation. The output `worktree`/`branch` identifies the agent's working location. Upon completion, the board commits changes to that branch and waits in `approval`. Merging (`approve`) is decided by a human operator.
- Resource cleanup: Upon reaching `completed`, the router closes the Herdr pane (agent) inside the task worktree (`herdr pane list` → `pane close`; closing the final pane removes the space). If the agent inside remains `working`/`blocked`, the pane is left open and retried during the next collection. Closed panes and agent sessions are recorded in `release` within receipt and output. Incomplete executions are not closed.
- Resuming work: `resume --cwd CWD --run-id RUN` invokes board `reopen ID` to reopen the space and restart the agent with the same conversation context (sending nothing). Resumed sessions are not closed by the router. Subsequent instructions are delivered via `tell --cwd CWD --run-id RUN --message "..."`.
- Lost responses: Identical task/round requests are never re-submitted. If a task ID is lost, verify effects in the board under the `br-RUN_ID` title and resolve explicitly.
- In-progress / waiting on prompts: Observe active executions via `collect --cwd CWD --run-id RUN --wait-ms N`. Questions and permissions are handled via the standard board approval interface (`herdr-projects details ID`).
- Follow-up review and modification: Upstream agents specify prior results and review notes in a new task round. Automated retries, tell loops, or recursive delegation are never performed.
- Non-blocking launch: `--wait-ms N` in `route`/`parallel` reduces wait time only after submission (`add`). Submission itself continues to use the task `timeout_ms` budget. If set to `0`, `timed_out` returns immediately after submission; collection is handled via `collect` or re-running the same group.
- Headless execution: Tasks with `execution: headless` do not use board agents. They execute one-shot CLIs in Herdr worktree panes and report status to the board as an agentless task. For details, see [Reference](reference.md#headless-execution).
- Cancellation: `stop --cwd CWD [--run-id RUN]` invokes board `stop ID` (or `herdr workspace close` for headless tasks) and appends to `messages.jsonl`. Stoppage occurs only when explicitly invoked by an upstream agent. When the board reports `stopped` or the headless workspace closes, agent termination is confirmed; the next `collect` records `execution_failed` and releases concurrency admission (no `coordination release` required).
- Waiting across multiple runs: `collect --run CWD RUN_ID --run … --until any|all --wait-ms N` polls each run, returning when one or all settle or become `blocked`. Result adoption is decided by upstream agents.
- Runtime guidance: `tell --cwd CWD [--run-id RUN] --message TEXT | --message-file F` delivers a message to the agent for that run via board `tell ID TEXT`. The router never sends messages autonomously; messages are sent strictly on explicit invocation. Pre- and post-send states are recorded in `runs/RUN_ID/messages.jsonl` (`attempted` → `sent`/`uncertain`). If a response is lost, verify status in the board before retransmitting. Settled runs start a new agent, so messages are accepted only after `resume`. Receipts update during `collect`; tasks that have already ended (approval, done, failed, etc.) are rejected before sending. Headless runs (`execution: headless`) reject messages. Dispatch locks are not held during `tell`, allowing messages to be sent while `collect` or `parallel` waits on the same cwd. Omitting `--run-id` targets the sole incomplete run in the cwd.
- `completed` denotes structural receipt compliance across run ID, nonce, profile fingerprint, result path, file size, and SHA-256 validation. Substantive task success is recorded in `task_outcome`, and result adoption is recorded via `coordination feedback`.
- When pre-submission failure is confirmed, the receipt settles and admission is returned immediately. Runs that have been submitted or whose delivery remains uncertain retain one of the 4 concurrent execution slots until worker stoppage and partial effects are verified. If necessary, release slots manually via `coordination release --key KEY --confirmed-stopped --note "..."`.
- Tasks created directly in the board do not count towards router execution limits.

## Parallel Dispatch

`parallel` stores each member's receipt at `<cwd>/.bench-router/groups/GROUP/members/LABEL`; this is `receipt_cwd` in the output and the value used with `collect`, `tell`, `stop`, `resume`, and `feedback`.
The board receives the original repository as `--repo` and creates the member's only worktree. Until the runner creates it, `worktree` and `branch` are `null`; the confirmed path and branch then replace them in the member output and receipt.
The `shared` scratchpad resides outside the agent worktree, requiring approval on each write under `worker.access ask`.
Comparing, merging, and pruning worktrees is managed by the upstream agent. Execution resources are never provisioned before all selections complete. Group 2.0 allows repeated selections with identical profiles, assigning distinct labels and receipts. Bounded by 8 tasks per group, 16 items per group total, and `max_parallel` 1–4. Preserves Policy 6, bulk rejection of stale assessments, replay of frozen plans, and partial failure retention, passing `delivery_state` and `reassignment` to member rounds. See [Routing Contracts](routing-contracts.md) for version specifications.

## Verification

```bash
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
```

The Projects CLI is substituted with a test double conforming to 1.2.1 source code (`brief`/`details` in `src/cli/tasks.rs`, stage→state mapping in `crates/flow/src/state.rs`), creating real `git worktree` instances for each task.
Actual model behavior, PTY terminal handling, and board ticker recovery are not certified by this test suite.
