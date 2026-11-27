# Shepherdr 3.1/3.2 switch matrix (T9)

Captured 2026-11-27 with the bench-router CLI from this checkout (`--runner herdr --herdr-space demo`) against
Shepherdr 3.1.26 and 3.2.19 with herdr-core (hc) 0.1.20. Everything ran inside throwaway `shepherdr-env:<tag>`
containers (`eval/shepherdr-env`). Only this checkout (read-only, `/src`) and, for T9c, one named volume
(`/carry`, removed afterwards) were mounted. No host HOME, XDG dir or socket was mounted. No model, paid decision
or network routing call was made.

Reproduce: `sh eval/shepherdr_matrix.sh [TAG...]` (default `v3.1.26 v3.2.19`; T9c runs when both tags are given).
It takes about 4 minutes. Raw evidence is in `shepherdr-matrix/<tag>/<path>/`: CLI `NAME.out|.err|.rc`, `receipt.json`,
`observed.json` (every check and its inputs), and `calls.json` (the router's and observer's herdr-task/hc calls for that run).
Each container also leaves `calls.jsonl` (the full call log), `hc_ls_all.json`, `coordination.json`, `stub-log.jsonl`
(each agent's argv tail and HC_/HERDR env), `told.log` and `run.log`. `shepherdr-matrix/summary.tsv` holds the rows below.
Only `summary.tsv` is tracked in git; the per-tag directories linked below exist after a local run of the script.

## Setup inside each container

- The repo is copied to `~/br` (`PYTHONPATH`). Each path gets its own Git repo `~/w/<path>` with one commit and no remote.
  A path needs its own cwd because the router refuses a new dispatch while a cwd has an unsettled run.
- `profiles.toml` has one profile, `claude-opus-medium` (`claude --model claude-opus-5-5 --effort medium`).
  `claude` on PATH is a synthetic Python stub. It reads the router contract (run id, nonce, fingerprint, result dir)
  from its argv, writes `result.md`/`result.json` into the run's result dir, and commits `agent.txt`. Interactive
  runs report `working`/`idle` to hc with OSC 7501 (`ESC ] 7501 ; state=idle BEL`; hc's only status source, see
  `hc --skill`). The stub then idles and reads stdin, which receives `hc send` messages. Headless (`-p`) runs exit 0.
  The task prompt selects a behaviour: `MODE=complete|tell|hang|slow` (slow: results after 25 s).
- `codexbar` is a synthetic stub that returns fresh 10 % usage. Without it the live preflight excludes the profile
  (`codexbar_quota_unverified`).
- Selection: every task has `profile_filter` with one model and one effort. `evaluate --preflight --format 3 --host claude`
  is followed by `select`, and the resulting `selection` object is passed as `--selection` (route) or in group schema 2.0
  `selections` (parallel). No decision stage was requested.
- Call log: `/tmp/shim/herdr-task` and `/tmp/shim/hc` come first on PATH, also for the core and its terminals.
  They log every call as `{t, by, exe, rc, argv}`. `by` is the caller's process: `router` (`bench_router.cli`),
  `observer` (`bench_router.lifecycle`) or `other` (herdr-task's own hc calls).
- Checks (`/tmp/check.py`, in the script) use the real binaries directly, so they do not appear in the call log.
  They observe separately: (1) the **result copied beside the receipt**, meaning `run_dir/result.{json,md}` exist,
  the nonce and run id match, and the SHA-256 is correct; (2) the **terminal end state**, from `hc get` of every
  `herdr.task=<key>` terminal, read with `hc ls --all` in the tag's session; (3) **admission**, the record's `active`
  in `bench-router coordination status`; (4) the receipt's `ready`/`release` and `herdr-task show`.

## Paths

| path | what runs |
|---|---|
| route-interactive | `route --selection … --wait-ms 90000`, agent completes in its first turn |
| route-headless | same, `execution: headless` (one-shot `claude -p` through `start --argv`) |
| observer | `route --wait-ms 0` and no collect; the core observer (`hc run --bg … bench_router.lifecycle`) must collect, call ready and release. Checked: `ready` came from `by=observer` |
| tell | `MODE=tell`: `route --wait-ms 0`, wait until hc reports `idle`, `tell --message`, `collect --wait-ms 60000`. The result exists only if the message reached the agent |
| stop | `MODE=hang` (agent stays `working`): `route --wait-ms 0`, `stop`, `collect --wait-ms 30000` |
| resume | `resume` of route-interactive's completed run, then `tell` to the resumed agent |
| parallel-sm-par-i-1 / -h-1 | `parallel --group` schema 2.0 with one interactive and one headless member, `--wait-ms 90000` |
| restart | `MODE=slow`: `route --wait-ms 0`, `hc server restart` 2 s later while the agent works, then `collect --wait-ms 90000` |
| T9c | see below |

Ready and release are checked on every completed path: the receipt's `ready.state == "ready"`, `herdr-task show`
`state == "ready"`, `release` recorded, and every task terminal `finished/killed`.

## Matrix

| tag | hc | core session | run id | path | expected | observed | result | evidence |
|---|---|---|---|---|---|---|---|---|
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `e6e35542` | route-interactive | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t1:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.1.26/route-interactive/observed.json](shepherdr-matrix/v3.1.26/route-interactive/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `7ba1e6b8` | route-headless | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t4:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.1.26/route-headless/observed.json](shepherdr-matrix/v3.1.26/route-headless/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `9db1e509` | observer | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t6:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.1.26/observer/observed.json](shepherdr-matrix/v3.1.26/observer/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `01fae190` | tell | completed; result copied; Ready; released; terminals finished; admission released; message delivered | status=completed; result_copied=True; terminals=t8:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.1.26/tell/observed.json](shepherdr-matrix/v3.1.26/tell/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `24669f47` | stop | execution_failed; process exited; terminals finished; admission released | status=execution_failed; result_copied=False; terminals=t10:finished/killed; admission_active=False; ready=None; release=no | **PASS** | [shepherdr-matrix/v3.1.26/stop/observed.json](shepherdr-matrix/v3.1.26/stop/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `e6e35542` | resume | resumed terminal live and labelled; completed record kept; admission released; message delivered | status=completed; result_copied=True; terminals=t1:finished/killed,t12:live/None; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.1.26/resume/observed.json](shepherdr-matrix/v3.1.26/resume/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `6fd44fce` | parallel-sm-par-i-1 | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t13:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.1.26/parallel-sm-par-i-1/observed.json](shepherdr-matrix/v3.1.26/parallel-sm-par-i-1/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `322d9a5e` | parallel-sm-par-h-1 | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t15:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.1.26/parallel-sm-par-h-1/observed.json](shepherdr-matrix/v3.1.26/parallel-sm-par-h-1/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (d3de2a6a) | `6a339184` | restart | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t17:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.1.26/restart/observed.json](shepherdr-matrix/v3.1.26/restart/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `2c962dae` | route-interactive | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t1:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.2.19/route-interactive/observed.json](shepherdr-matrix/v3.2.19/route-interactive/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `082aec6a` | route-headless | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t4:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.2.19/route-headless/observed.json](shepherdr-matrix/v3.2.19/route-headless/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `a57d9fa0` | observer | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t6:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.2.19/observer/observed.json](shepherdr-matrix/v3.2.19/observer/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `b8706ce0` | tell | completed; result copied; Ready; released; terminals finished; admission released; message delivered | status=completed; result_copied=True; terminals=t8:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.2.19/tell/observed.json](shepherdr-matrix/v3.2.19/tell/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `4241d13a` | stop | execution_failed; process exited; terminals finished; admission released | status=execution_failed; result_copied=False; terminals=t10:finished/killed; admission_active=False; ready=None; release=no | **PASS** | [shepherdr-matrix/v3.2.19/stop/observed.json](shepherdr-matrix/v3.2.19/stop/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `2c962dae` | resume | resumed terminal live and labelled; completed record kept; admission released; message delivered | status=completed; result_copied=True; terminals=t1:finished/killed,t12:live/None; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.2.19/resume/observed.json](shepherdr-matrix/v3.2.19/resume/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `fd0fba2f` | parallel-sm-par-i-1 | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t13:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.2.19/parallel-sm-par-i-1/observed.json](shepherdr-matrix/v3.2.19/parallel-sm-par-i-1/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `380c6ac7` | parallel-sm-par-h-1 | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t15:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.2.19/parallel-sm-par-h-1/observed.json](shepherdr-matrix/v3.2.19/parallel-sm-par-h-1/observed.json) |
| v3.2.19 | hc 0.1.20 | `shepherdr` (bea90bf8) | `3915723b` | restart | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t17:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/v3.2.19/restart/observed.json](shepherdr-matrix/v3.2.19/restart/observed.json) |
| v3.1.26 | hc 0.1.20 | `default` (416e90ad) | `9347de05` | T9c make: t9c-completed | completed; result copied; Ready; released; terminals finished; admission released | status=completed; result_copied=True; terminals=t1:finished/killed; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/t9c/make-v3.1.26/t9c-completed/observed.json](shepherdr-matrix/t9c/make-v3.1.26/t9c-completed/observed.json) |
| v3.2.19 | hc 0.1.20 | `default` (416e90ad) | `9347de05` | T9c collect: t9c-completed | completed receipt bytes unchanged; result readable; no control calls | status=completed; result_copied=True; terminals=t1:live/None; admission_active=False; ready=ready; release=yes | **PASS** | [shepherdr-matrix/t9c/check-v3.2.19/t9c-completed/observed.json](shepherdr-matrix/t9c/check-v3.2.19/t9c-completed/observed.json) |
| v3.2.19 | hc 0.1.20 | `default` (416e90ad) | `2127a17c` | T9c collect: t9c-unfinished | delivery_uncertain; admission held; 0 start/send/kill/ready calls | status=delivery_uncertain; result_copied=False; terminals=t4:None/None; admission_active=True; ready=None; release=no | **PASS** | [shepherdr-matrix/t9c/check-v3.2.19/t9c-unfinished/observed.json](shepherdr-matrix/t9c/check-v3.2.19/t9c-unfinished/observed.json) |

**Summary: 21 rows, 21 pass, 0 fail.** v3.1.26 has 10 pass and 0 fail (9 paths plus the T9c receipt creation).
v3.2.19 has 11 pass and 0 fail (9 paths plus the two T9c collects). No router failure was observed, so no
router code was changed.

## T9c: receipts carried from 3.1.26 to 3.2.19

1. In a 3.1.26 container, the script created run `9347de05` (completed, Ready, released) and run `2127a17c`
   (`MODE=hang`, `route --wait-ms 0`, receipt `timed_out`, terminal `t4` in session `default`). It wrote `~/w`
   (repos and receipts) and `~/.local/state/bench-router` (admission records) to the named volume, plus the
   receipts' SHA-256 (`t9c/make-v3.1.26/sha256`).
2. In a 3.2.19 container, before restoring them, `hc run --bg sleep 3600` took address **t1** in both the
   `shepherdr` and the `default` session (`t9c/check-v3.2.19/t9c-occupy/t1_*.out`). The receipts were then restored
   at the same paths, and `collect --wait-ms 10000` ran for each run. The check counts every call in the collect's
   time window, by any caller.
   - **Completed** (`9347de05`): the receipt bytes are unchanged (SHA-256 equal), the status is `completed`, and
     the copied result validates. The calls were only `herdr-task --version`, `herdr-task --help` and `hc --version`.
     There was no start, send, kill, ready or resume. The row's `t1:live` is the occupying `sleep` in the 3.2
     `shepherdr` session, read by the checker. The router did not touch it.
   - **Unfinished** (`2127a17c`): the status is `delivery_uncertain` with the note "Shepherdr session or core binding
     differs from the receipt". The receipt's `default` core id `416e90ad…` does not match the new container's
     `default` core.json. Admission is still `active: true`. The calls were the same three probes, so there were
     **0 start, send, kill and ready calls**. Task identity could not be confirmed, so the run stays held.

## Failures

None. Every check in every row passed (`observed.json` → `checks`).

## Observations (not failures)

- **Core session and identity.** 3.1.26 receipts record `session: default` and 3.2.19 receipts `session: shepherdr`.
  The core id was unchanged across `hc server restart` on both tags. A live agent keeps running across the restart
  (`restart/server_restart.out` shows the same `core.id`). After the restart, `collect` completed the run.
- **The observer yields to a foreground collect.** In route-interactive, stop, tell and restart, the foreground
  `route`/`collect` held the dispatch lock, so the observer made one poll and the router did ready and kill.
  In the observer path, the observer made every call (`ready` and `kill` by `observer`).
  Observer terminals are `--rm`. Except for the last one (restart, `t18`, still live a few seconds after its run
  settled), they were gone by container end (`hc_ls_all.json`).
- **Stop.** After `stop` (`hc kill`), `collect` gave `execution_failed` with `process_exited: true`, the terminal
  `finished/killed`, and admission released. `herdr-task show` still read `state: running, needs: null` when it was
  checked, a few seconds after the kill (spike: it turns `needs: stopped` 2–5 s after a kill). The router did not
  depend on it.
- **Resume.** `herdr-task resume` returned a new terminal (`t12`), `session_resumed: false` (stub, no recorded
  session) and identity `ok`. `tell` to it was `sent` and the agent logged the message. As documented, the resumed
  terminal stays live and is not released again. The completed record and its admission (inactive) are unchanged.

## Not exercised

- A real agent CLI, login, model access, permission prompts (`blocked`) and Shepherdr's `needs: reply`. The stub
  never asks for anything.
- Exact-session resume (`resumed: true`). The stub has no recorded session.
- Queued or scheduled starts and router `stop` through `reopen`, because the router never schedules.
- A real host reboot, `hc server stop` and later start, and a systemd-managed core. Only `hc server restart` was
  exercised; the container has no systemd user manager.
- T9c for an unfinished run whose identity is confirmed. A 3.1 → 3.2 switch always changes the core session, so this
  case cannot arise here. The same-tag observe-only behaviour is covered by the stop and restart paths.
- The Shepherdr web service and app (`--no-build` install), and 3.1 card data. The 3.1 board (`~/.herdr`) was not
  carried, so 3.2 has no 3.1 cards. The router never got as far as reading the board.
