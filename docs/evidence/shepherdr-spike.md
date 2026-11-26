# Shepherdr 3.1.26 / 3.2.19 CLI contract spike (T1)

Captured 2026-11-26 with herdr-core (hc) 0.1.20, only inside throwaway `shepherdr-env:<tag>` containers
(`eval/shepherdr-env`), nothing mounted. The agent is a synthetic `claude` stub (answers `claude auth status`,
commits `agent.txt`, then idles in `sleep`); see `shepherdr-cli/scripts/lib.sh`.

Reproduce: `sh docs/evidence/shepherdr-cli/scripts/capture.sh [TAG...]` (`SCENARIOS="stop"` for a subset).
Fixtures: `docs/evidence/shepherdr-cli/<tag>/<scenario>/<name>.out|.err|.rc`, `index.tsv` (name, exit code,
exact argv), `run.log` (scenario stderr), `agent_env.txt` (the HC_*/HERDR_* env the agent saw).

| scenario | script | covers |
|---|---|---|
| contract | `scripts/contract.sh` | `--version` (both CLIs), where, add (router argv, `--json` and plain), list, start, show, `hc ls --label`, `hc get` (default and shepherdr session), `hc run --bg --rm`, `hc send`, ready, release kill, state after kill |
| stop | `scripts/stop.sh` | `herdr-task stop` (3.2), router stop (`hc kill`), get / `ls --all` / `ls` / show at 0, 5, 30, 120, 300 s, kill again, `hc server restart`, resume, `hc rm`, reopen on a to-do card |
| session | `scripts/session.sh` | core.json and `hc server status` per session; hc precedence of HC_SOCKET / HC_SESSION / HC_TERMINAL_SOCKET; add+start under 10 environments and where each terminal landed |
| kill_only | `scripts/kill_only.sh` | show at 0, 2, 5, 15 s after killing a running worker; the card after a refused start |

## The three questions

### 1. Confirming the core before the first submission

No herdr-task command reports which core it will use (`where --json` has no session), and `--version` is `1`
on both tags (`contract/task_version.out`), so the protocol does not tell 3.1 from 3.2 either. What the
captures establish:

- **The core is fixed by the tag, not by the caller.** 3.1 runs only in the `default` session: every other
  `HC_SESSION`, and every `HC_SOCKET` (even the real `default.sock`), makes `start` fail with rc 1 and
  `{"error": "refusing to run hc: …"}` on stdout (`v3.1.26/session/start_*`). 3.2 runs in
  `$SHEPHERDR_SESSION`, else `shepherdr`. It rewrites an unset, empty, `default` or `shepherdr` HC_SESSION to
  that session (`v3.2.19/session/ls_session_default_in_shepherdr.out`). It refuses any other session, and any
  HC_SOCKET that is not that session's socket.
- **A refused start submits nothing.** The card stays `todo` with no worktree, and add never calls hc, so it
  succeeds under any environment (`*/kill_only/start_refused`, `show_refused`).
- **Each session has a stable identity.** `~/.local/state/herdr-core/<session>/core.json` holds `{"id","name"}`.
  `HC_SESSION=<s> hc server status --json` returns the same `core.id` (`*/session/status_*`, `core_json_after_*`),
  and 3.2 kept it across `hc server restart` (`v3.2.19/stop/server_restart.out`). Reading core.json is passive.
  **Any hc call (`status`, `ls`) starts a core when none is running** (`session/core_json_before_default.err`,
  `run.log`'s "no systemd user manager" warning), so an hc probe is never read-only.
- So before submitting, the router can derive the session from the tag (3.1 → `default`;
  3.2 → `$SHEPHERDR_SESSION` or `shepherdr`), check that HC_SOCKET is unset or that session's socket, and compare
  `HC_SESSION=<s> hc server status --json`.core.id with that session's core.json. After start, `hc get <terminal>`
  in that session must show `labels."herdr.task" == key` (`contract/get_*.out`).

### 2. Pinned socket vs inherited session

For **hc 0.1.20 itself** (same binary in both images), **HC_SOCKET wins over HC_SESSION**
(`session/hc_session_default_socket_other` reaches the `other` core, `hc_session_other_socket_default` the
`default` core). HC_TERMINAL_SOCKET alone is ignored (`hc_terminal_socket_other_only` → default). A missing
socket gives rc 5, `{"error":{"kind":"unavailable",…}}`.

For **herdr-task**, neither wins. The guard decides first:

| caller env | 3.1.26 start | 3.2.19 start |
|---|---|---|
| unset | ok → default | ok → shepherdr |
| HC_SESSION=default | ok → default | ok → **shepherdr** (rewritten) |
| HC_SESSION=shepherdr | refused | ok → shepherdr |
| HC_SESSION=other | refused | refused |
| HC_SESSION=other SHEPHERDR_SESSION=other | refused | ok → other |
| HC_SOCKET=default.sock | refused | refused |
| HC_SOCKET=shepherdr.sock | refused | ok → shepherdr |
| HC_SOCKET=other.sock | refused | refused |
| HC_SESSION=default HC_SOCKET=shepherdr.sock | refused | ok → shepherdr |
| foreign HC_TERMINAL_SOCKET/ID (other.sock, t1) | ok → default | ok → shepherdr (dropped) |

On 3.1, HC_SOCKET is refused unless it equals HC_TERMINAL_SOCKET or `/run/user/<uid>/herdr-core/default.sock`.
The container has no XDG_RUNTIME_DIR, so its real socket is under `~/.local/state` and is refused. The agent
terminal inherits the core's session: 3.2 sets `HC_SESSION=shepherdr`, `HC_TERMINAL_SOCKET=…/shepherdr.sock`
and `HERDR_GUARD_SESSION=shepherdr`. 3.1 sets no HC_SESSION unless the caller had one (`agent_env.txt`).

### 3. Observing the end state after kill/stop

Yes, and it did not expire in this test. `hc kill <t> --json` returns the terminal synchronously with
`state:"finished", reason:"killed", signal:1, finished_ms` (`contract/kill.out`). `hc get`, `hc ls --all` and
`hc ls --all --label herdr.task=<key>` show the same record, unchanged, at 0, 5, 30, 120 and 300 s and after
`hc server restart` (`stop/get_t*`, `ls_all_t*`, `get_after_restart`). Plain `hc ls` hides it and counts it
(`"hidden_finished":1`). Only `hc rm` removes it, after which `get` returns rc 3 `not_found` (`stop/get_after_rm`).
A second kill is rc 0 and idempotent. On the board, `show` drops the worker from `live` at once but keeps
`state:"running", status:"working"` for 2–5 s. It then reads `status:"needs", needs:"stopped", why:"Agent stopped"`
on both tags (`kill_only/show_t*`). A Ready card stays `ready` after its terminal is killed
(`contract/show_after_kill`). 3.2's `herdr-task stop` sets `needs:"stopped", why:"Stopped by you."` while the
terminal stays **live** (`v3.2.19/stop/task_stop.out`, `get_after_task_stop`).

## Contract differences between 3.1.26 and 3.2.19

1. **Core session**: 3.1 uses `default` only. 3.2 uses `shepherdr` (or `$SHEPHERDR_SESSION`) and rewrites
   HC_SESSION=default (see Q2).
2. **Guard wording**: 3.1 says `refusing to run hc: HC_SESSION is X. Run herdr-task with the real HOME, …`.
   3.2 says `… HC_SESSION is X, not Shepherdr's own (shepherdr). This shell's environment is wrong: …`.
   Both use rc 1, JSON on stdout and empty stderr.
3. **Plain `add` (no --json)**: 3.1 prints only `REPO-3`. 3.2 prints `"plain-title" added (its key, for commands only: REPO-3)`.
4. **Worktree location**: 3.1 uses `~/.herdr/worktrees/<repo>/<branch-slug>`. 3.2 uses `~/.local/share/shepherdr/worktrees/<repo>/<branch-slug>`.
5. **show/start JSON**: 3.2 adds `brief_review` and `pr_looked`. All other keys the router reads are the same:
   `key` (`repo#N`), `id`, `title`, `folder`, `agent`, `mode`, `state`, `worktree`, `branch`, `live[].address`,
   `terminal` (start/resume), `needs`, `why`, plus `ref` (`REPO-N`).
6. **Subcommands**: 3.2 adds `stop`, `reply`, `archive`, `flags`, `carry-over`, `sandbox`, `update-shepherdr`,
   `analytics`. 3.1 only has `backup`, `restore-spaces`, `autopilot`, `progress`, `star`, `complete`.
   `herdr-task stop` on 3.1 is rc 2 (argparse usage).
7. **add/start flags**: 3.2 adds `add --speed --permission --flags --pr` and `start --model --effort --speed --permission --pr`.
8. **Agent terminal env/argv**: 3.2 adds `HERDR_BROWSER_SPACE`, `HERDR_GUARD_SESSION` and a `.guard/bin` PATH
   wrapper in argv. Labels are identical: `herdr.task=<key>`, `herdr.task.space=<space>`, `herdr.agent=<agent>`.
9. **Title help**: 3.2 says "at most 30 characters", but the router's 39-character `br-<uuid>` title was
   accepted unchanged on both tags (`contract/add_router_title.out`).

Same on both: `herdr-task --version` = `1`, `hc --version` = `hc 0.1.20`, the ready response (`state:"ready"`),
reopen on a to-do card (`state:"todo"`), resume (`terminal`, `resumed:false` for the stub), the `hc send`
response `{"started":null,"status":null,"turn":0}`, the `hc run --bg --rm --json` row (`address`, `agent`,
`cwd`, `state`, `turn`; no labels), and `hc ls` rows, which carry no labels (filter only).

## Contradictions with the router (board.py / herdr.py)

- **herdr.py session binding breaks on 3.2.** `bound_runner` sets HC_SESSION to the receipt's `core_session`,
  which defaults to the caller's HC_SESSION or `"default"`. herdr-task 3.2 still runs in `shepherdr`, so the
  router's own hc calls look at a different core. `hc ls --label herdr.task=<key>` comes back empty and
  `hc get` returns rc 3 (`v3.2.19/contract/ls_label_default.out`, `get_default.err`). `_verify_terminal` would
  then mark a successful start `delivery_uncertain`. It works only if `core_session=shepherdr` (shepherdr.json),
  and that value is exactly what 3.1 refuses. The session must come from the tag, and `--version` cannot tell
  the tags apart.
- **herdr.py expects `state:"exited"`; hc reports `"finished"`.** `_poll_headless` accepts only `live|exited`, so a
  finished headless terminal raises "unexpected hc terminal response". `release()`'s `!= "exited"` test treats
  finished terminals as active.
- **board.py** stays consistent if the adapter maps hc `finished` → `exited` and `needs:"stopped"` → `stopped`.
  Two caveats from the captures. (a) For 2–5 s after a kill, `show` says `status:"working"` with an empty
  `live`. `working` must need a live worker, as the docstring says, or the adapter should fall back to the hc
  terminal state. (b) 3.2 `herdr-task stop` gives `stopped` with process `live`, so `stop()` must not treat
  `needs=stopped` as termination evidence. board.py already requires `process=exited` for that.
  `bind()`'s "protocol" alone cannot carry the session; it must also record the tag-derived session.

## Not verified

- Live worker `status` (`idle`/`working`/`done`) and `turn`. The stub is `sh`, so hc reports `status:null`,
  `turn:0`. The board's `turn_done` and `working` mappings need a real agent CLI.
- A terminal whose program exits by itself (`exit_code` set). Only kill was observed, and the state name for a
  natural exit is assumed to be `finished` too.
- Retention beyond 300 s, after `hc server stop` or a reboot, and with a systemd-managed core. Also the
  `/run/user/<uid>` socket layout, since the container has no XDG_RUNTIME_DIR.
- Resume of a real recorded session (`resumed:true`). After resume, `show` had `live:[]` immediately
  (`stop/show_after_resume`); it was not followed further.
- The Herdr app / web service, scheduled or queued starts (`--at`, `--after`), and `hc run --bg` for the real
  `bench_router.lifecycle` observer (a `sleep` stood in for it).
