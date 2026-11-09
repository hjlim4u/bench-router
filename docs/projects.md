# Shepherdr Execution and Collaboration

The live pathway is `route` / `parallel` → Shepherdr 3.x `herdr-task` → herdr-core (`hc`) → Agent CLI.
The caller chooses decomposition, profiles, review rounds and result adoption. bench-router keeps durable receipts,
admission limits and result validation. The certified upstream contracts are Shepherdr **3.1.14**, herdr-task
protocol **1**, and herdr-core **0.1.17+**. Core version or space changes hold an active run as `delivery_uncertain`.

## Setup

Use the official [upgrading guide](https://github.com/eliasstravik/shepherdr/blob/main/docs/upgrading.md) and
[install guide](https://github.com/eliasstravik/shepherdr/blob/main/docs/install.md). The old terminal
`herdr-projects` plugin and Shepherdr are separate installations. Keep the old installation and data when upgrading;
the documented 2.x transition does not establish a migration path for 1.2.x data. Do not update the old plugin
checkout from the new main branch.

For a web-only Linux/WSL2 installation, install herdr-core and have Tailscale signed in, then:

```bash
git clone https://github.com/eliasstravik/shepherdr
cd shepherdr
./install.sh --web --dry-run
./install.sh --web
shepherdr doctor
shepherdr web status
```

The web service is private to the tailnet and listens locally on 127.0.0.1. On WSL an existing Windows Tailscale
installation can be reused through a `tailscale` command forwarding to its executable; verify the HTTPS API,
including authentication, after installation. No desktop app is required for this mode.

Create a space for the repository in the web app. Select it using the global `--herdr-space SPACE` option,
`BENCH_ROUTER_SPACE`, or a local `<repo>/.bench-router/shepherdr.json` containing `{"space":"SPACE"}`.
A caller already inside herdr-core can inherit its terminal's space. `--herdr-session` and
`BENCH_ROUTER_HERDR_SESSION` remain aliases for the space selection; these no longer select a terminal-Herdr
session. Shepherdr uses the default core session. Recorded runs recover with their recorded space.

```bash
hc --version                         # hc >= 0.1.17
herdr-task --version                  # task protocol: 1 (not the Shepherdr release)
bench-router --herdr-space SPACE --runner herdr route --task task.json --selection selection.json
```

`BENCH_ROUTER_TASKS` and `BENCH_ROUTER_HC` can override executable paths. `auto` selects `herdr` only when both
`herdr-task` and `hc` are available. The task cwd must be the root of a committed Git repository. Uncommitted
changes are excluded from the new worktree, with a `dirty_base` warning. `.bench-router/` is excluded from commits.

## App and companion TUI

From this repository, use `mise run herdr-app` for the primary desktop window and
`mise run herdr-tui` in another terminal for a plugin-free companion. Without mise:

```bash
sh scripts/herdr.sh app
sh scripts/herdr.sh tui
```

The companion uses session `app-companion`, configuration `examples/herdr-tui.toml`, and
separate config/state directories under `.bench-router/tui/`. Existing user plugins and their
startup hooks are not loaded into this environment; no plugin installation or removal is needed.
Use this launcher rather than bare `herdr`, which still uses the user's existing configuration.
The shell wrapper restores the original XDG directories so `hc`, Shepherdr and bench-router
inside ordinary TUI panes use the same user environment as the app.

In the TUI, press **Ctrl+B, H** to select and attach to a live core terminal, or
**Ctrl+B, Shift+H** to observe without typing or resizing. **Ctrl+backslash** detaches from
core while leaving its program running. Close/detach this viewer before closing its TUI pane.
Tasks continue to be created through Shepherdr/bench-router, in the default core session.
The TUI has its own server: attaching is a terminal view, not synchronization of the two
agent sidebars. A task whose worker was released can be reopened through router `resume`.
No extra agent or duplicate task is started by the attach shortcuts.

The app requires a working desktop session (WSLg on this WSL2 installation). An existing
web-only Shepherdr installation does not automatically add the desktop layout; follow the
[Shepherdr install guide](https://github.com/eliasstravik/shepherdr/blob/main/docs/install.md)
if the layout is missing. `python3 scripts/check-herdr-launch.py` checks launch isolation
without starting servers. `sh scripts/herdr.sh tui config check` validates the native config.

References: [TUI custom commands](https://herdr.dev/tui/docs/configuration/#custom-command-keybindings),
[core attach](https://github.com/herdrdev/herdr-core/blob/master/docs/commands.md#hc-attach).

## Profiles and Permissions

| Router profile | herdr-task setting |
|---|---|
| kind | `--agent KIND` |
| `--model M` / `-m M` | `--model M` |
| no model | `--model default` (the CLI's default) |
| `--effort E`, Codex `-c model_reasoning_effort="E"` | `--effort E` |

For interactive Antigravity (`agy`) tasks, start uses herdr-task’s public `--argv` override to pass the validated executable/model/effort flags and `--prompt-interactive` directly. Shepherdr saves that argv for queued execution and subsequent resume/handoff; its default model/effort builder only handles Claude/Codex.

Interactive Codex tasks also start through `--argv`, with the profile flags plus
`--dangerously-bypass-approvals-and-sandbox`: Codex's workspace-write sandbox cannot write the lock files a git
worktree keeps in the main repository's `.git`, so a sandboxed worker can never commit.

Other profile arguments are rejected before submission. Interactive Claude and agy workers inherit the user's CLI
permissions and Shepherdr settings. The old `worker.access` setting does not exist on this platform. A permission or question
appears as `blocked`; answer through Shepherdr's cards or normal approval workflow.

Each task gets `--worktree --set review=off --set "merge=ask me first" --set proof=off` and branches from the
caller's exact HEAD commit, on `br/RUN_ID`. A private `br-base/RUN_ID` branch pins that commit because the upstream base option accepts branch names only; retain it with the worktree until the caller prunes the run. If Shepherdr's folder setting disables worktrees, the router adds the
task but refuses to start it in the user's checkout.

## Execution and Collection

The prompt is written to `runs/RUN_ID/input.txt` and passed using `--prompt-file`. For compatibility the router
retains its 120 KiB prompt limit. Creation and start are separate calls:

```text
herdr-task add br-RUN_ID --folder REPO --prompt-file FILE ... --json
herdr-task start KEY --folder REPO --space SPACE --json
herdr-task show KEY --folder REPO --json
```

The task's durable `key` (`repo#12`, distinct from its numeric id and display ref) becomes `thread_id`.
Submission intent is saved before add; identity is saved before start. A lost response or process crash never
causes automatic add/start retries. An added task without a confirmed start is held for inspection, not started
by collect. The result is validated against the task's key, numeric id, title, folder, agent, worktree and branch.

| Shepherdr observation | Router status |
|---|---|
| queued / scheduled | `timed_out` |
| working | `timed_out` |
| needs a permission, answer or provider action | `blocked` |
| idle/done worker with result.json after its turn | validate result → `completed` / `result_invalid` |
| ready / done | validate result → `completed` / `result_invalid` |
| stopped worker | `execution_failed`; unexpected exits retain admission until inspected |
| missing or changed task identity | `delivery_uncertain` |

After a successful result is validated and copied beside its receipt, the router calls `herdr-task ready`.
Workers commit requested code changes and end their turn without calling ready/done/accept themselves.
Ready can open a GitHub PR; the person accepts the task before merging (`merge=ask me first`). Shepherdr
owns subsequent merge and worktree/branch cleanup. Router `completed` still means result delivery, not merge.
Partial/failed results are collected without marking the task Ready. A `ready` receipt records the handoff;
an attempted or uncertain handoff is never automatically repeated: inspect the board before acting manually.
The target is the repository's checked-out branch; detached HEAD is refused. Shepherdr manages the starting
revision, so execution no longer pins the caller's HEAD with a private base branch. Existing receipts with
private base branches are not handed to Ready automatically; finish those runs manually.

Results live at `.bench-router/runs/RUN_ID/` in the task worktree, and are copied beside the receipt after
run id, nonce, fingerprint, file path, size, encoding and SHA-256 checks. `task_outcome` records reported success,
partial or failure; `completed` alone does not establish substantive success.

On completion, only idle/done core terminals with this task's label are ended (`release`). Working or blocked
terminals remain. `resume` uses `herdr-task resume` in the recorded space: Shepherdr resumes a known Claude/Codex
session, otherwise it starts with a handoff (`resumed.session_resumed` reports which). A resumed session is not
automatically released again. `tell` uses `hc send` to the sole live worker and logs attempted/sent/uncertain
message delivery. It never starts a new worker. These commands act only on explicit caller invocation.

`stop` ends the observed live core terminal(s). The next collect confirms the stopped worker and releases
admission. For a queued/scheduled task, stop uses `herdr-task reopen` to return it to todo and verifies that the queue was cancelled before reporting stop_sent. If the scheduler already started it, stop reports uncertainty instead of claiming cancellation. A failure with unverified partial effects retains its slot until
`coordination release --confirmed-stopped` after inspection.

`collect --run CWD RUN_ID --run ... --until any|all --wait-ms N` observes multiple runs. `--wait-ms 0` returns
immediately after submission; the task timeout still bounds add/start. Neither collect nor re-dispatch sends a
new prompt. Receipts from `projects` / `projects-1.2` are deliberately not converted to `shepherdr-3`: inspect and
control those workers using the retained old installation. Legacy control commands never target the new core.

## Headless Execution

Headless Herdr runs now create a normal Shepherdr card and worktree, then start a one-shot CLI through the
public task `start --argv` option. The CLI reads input.txt and records its exit code beside the durable receipt.
Its terminal and the card are linked by Shepherdr's own task labels. Headless tell/resume remain unsupported.

Every new Herdr run starts a separate core observer (`monitor` in the output). It collects and validates results
and exits after collection and the Ready handoff. It does not watch for merge or remove Git resources.
Callers can still collect whenever they need the result. An observer launch error is reported in
`monitor.error`. The observer retries transient Git/core errors every five seconds until collection completes.
Results and receipts remain outside the worktree so Shepherdr can clean it up after acceptance.

## Parallel Dispatch

Receipts live at `<cwd>/.bench-router/groups/GROUP/members/LABEL` (`receipt_cwd`). Interactive members each get a
Shepherdr task and worktree; headless members each get a router worktree and core terminal. The shared scratchpad
is outside these worktrees, so writes may require approval under the user's CLI settings. The caller compares,
merges and prunes worktrees. The shared four-active admission limit and overlapping-workspace guard still apply.

## Verification

```bash
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codexbar test_evidence_policy
```

Tests use synthetic herdr-task/hc responses and real temporary Git worktrees. They cover split add/start recovery,
identity drift, permissions, result validation, worktrees-off refusal, legacy receipt isolation and local/external
runner compatibility. Historical Herdr TUI evidence remains in docs/evidence and does not certify this platform.

Manual web-only smoke on 2026-11-07 used upstream commit `4552191829b5e67dee60a1c780f41224575ef685`,
Shepherdr 3.1.14 and hc 0.1.18 on WSL2. `shepherdr doctor`, the authenticated Tailscale HTTPS API, and
interactive start/collect/release, resume with a handoff, explicit send, and headless completion passed.
The smoke used a synthetic Python worker and real herdr-task/hc commands; it made no paid model request and
does not certify a provider's login, model access or exact-session recovery. The offline suite ran 218 tests
with 2 skipped. Existing TUI installations and the two pre-existing untracked wiki notes were preserved.

## User plugin migration

`python3 scripts/migrate-herdr-app.py` checks the installed sources and runs the official
Shepherdr desktop installation dry run. `--apply` backs up affected user configuration,
installs the desktop layout while preserving existing keys and agent hooks, unregisters
Annotate/terminal-browser when present, removes their TUI keybindings, and switches Ovis
to herdr-core using its existing configuration and state. Ovis is stopped and restarted
through its own launcher, without stopping Herdr or core. Reviewr and Plugin Manager
are not copied into the app. The script preserves plugin data and standalone binaries.

Apply requires write access to the user's home and access to the running services.
After installation select Shepherdr with Ctrl+Shift+L in the app. Existing TUI clients
load removed keybindings on the next config reload or launch. Ovis remains installed
as a TUI-managed package; its launcher now serves core terminals, not the TUI server.
`python3 scripts/check-herdr-migration.py` checks binding removal offline.
