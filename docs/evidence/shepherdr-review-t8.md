# T8 independent review — supervisor verdicts

Reviewer: codex-gpt-6-2-sol-xhigh (bench-router run 522fdcf9), on `70f2afc`. All snippets below were re-run by the
supervisor against `70f2afc`: 9 tests, 8 failures + 1 error, i.e. every finding reproduces.

| # | Finding | Verdict |
|---|---|---|
| 1 | Misrouted core connection lets `stop` kill another session's `t1` (core.json alone is taken as proof of the connected core) | **valid, severe**: violates "never control another session's terminal" |
| 2 | Partial headless stop releases admission while a second terminal is live | **valid, severe**: violates the four-active limit |
| 3 | 3.2→3.1 swap mid-run holds collection as uncertain | **dropped**: the plan routes work whose core moved to manual reconciliation |
| 4 | Running pre-port receipts (no `core_id`) cannot be collected | **valid**: observe-only should be allowed when session and task identity match |
| 5 | Headless lost start response / terminal finished before verification strands a valid result | **valid** (both cases) |
| 6 | Memory board lost start crashes collect with `Path(None)` | **valid** |
| 7 | Interactive finished terminal with a valid result settles as `execution_failed` | **valid** |
| 8 | Native collect never uses the lost-create run-title lookup | **valid** |

Also open (T6 worker): `resume_run` does not persist `resume_attempted` before calling resume (board.PERSISTENCE).

Gate G2 is **held** until findings 1 and 2 are fixed (wrong terminal control, false admission release).

---

# T8 independent review

Reviewed `git diff da31d4c..HEAD -- bench_router/ 'test_*.py'` at `70f2afc`, the connected CLI, routing, receipt, coordination and lifecycle paths, and the checked-in Shepherdr captures.

## Findings

The snippets are methods for a temporary `class Review(P2)` run from the repository root. They use the existing local Git and board fakes. The common imports are:

```python
import os
from pathlib import Path
from subprocess import CompletedProcess
from types import SimpleNamespace
from unittest.mock import patch

from bench_router import coordination, herdr as hd
from test_board import WorktreeMemoryBoard
from test_p2 import P2, SPIKE, FakeSessionProjects, headless_cli, write_result
```

### 1. High · A misrouted core connection can kill another session's terminal

[bench_router/shepherdr.py:89](../../../bench_router/shepherdr.py#L89), [bench_router/shepherdr.py:222](../../../bench_router/shepherdr.py#L222), [bench_router/shepherdr.py:258](../../../bench_router/shepherdr.py#L258). Violates terminal isolation. If `core.json` exists, binding uses that file as proof of the connected core's identity. The stop path then accepts the address and task label. An independent core can have both `t1` and `repo#1`. In the repro, the runner routes hc to `default` after the run starts in `shepherdr`. A server query would report a different core ID using the checked-in status fixture.

```python
    def test_foreign_core(self):
        fake = FakeSessionProjects(board_session="shepherdr", after_status="working")
        path = Path(os.environ["XDG_STATE_HOME"]) / "herdr-core/shepherdr/core.json"
        path.parent.mkdir(parents=True)
        path.write_bytes((SPIKE / "session/core_json_after_shepherdr.out").read_bytes())
        out = self.run_(fake, wait_ms=0)
        key = out["thread_id"]
        foreign = fake.add_unrelated_terminal("default")
        foreign.update(task=key, labels={"herdr.task": key}, cwd="/another/worktree")
        fake.hc_session = "default"
        fake.commands.clear()

        def runner(cmd, **kw):
            if cmd[:3] == [hd.HERDR_BIN, "server", "status"]:
                return CompletedProcess(cmd, 0, (SPIKE / "session/status_default.out").read_text(), "")
            return fake(cmd, **kw)

        response = hd.stop_run(self.cwd, out["run_id"], runner=runner)
        self.assertEqual((response["status"], "other#1" in fake.sessions["default"], fake.closed),
                         ("delivery_uncertain", True, []))
```

Observed `('stop_sent', False, ['t1'])`. The router killed the foreign terminal. The check expected it to remain live. This reproduces the router's behavior under a misrouted connection.

### 2. High · A partial headless stop releases admission with a live terminal

[bench_router/herdr.py:642](../../../bench_router/herdr.py#L642), [bench_router/herdr.py:648](../../../bench_router/herdr.py#L648). Violates the four-active limit. Stop records both targets, but headless collection looks only at the receipt's primary terminal. After `t1` goes away, it frees the slot even when `t2` failed to stop and remains live.

```python
    def test_headless_partial_stop(self):
        fake = FakeSessionProjects(after_status="working")
        out = self.run_(fake, self.task(execution="headless"), wait_ms=0)
        key = out["thread_id"]
        fake.panes["second"] = {"address": "t2", "task": key, "labels": {"herdr.task": key}, "state": "live"}

        def runner(cmd, **kw):
            if cmd[:3] == [hd.HERDR_BIN, "kill", "t2"]:
                return CompletedProcess(cmd, 1, "", "synthetic kill failure")
            return fake(cmd, **kw)

        self.assertEqual(hd.stop_run(self.cwd, out["run_id"], runner=runner)["status"], "delivery_uncertain")
        done = hd.collect_run(self.cwd, out["run_id"], 0, runner=runner)
        rc = self.receipt(done)
        active = coordination.load(done["coordination_key"])["active"]
        self.assertEqual((rc["process_exited"], active, fake.panes["second"]["state"]), (False, True, "live"))
```

Observed `(process_exited, active, t2_state) == (True, False, 'live')`, expected `(False, True, 'live')`.

### 3. High · A 3.2 to 3.1 swap blocks collection before the card can be inspected

[bench_router/shepherdr.py:66](../../../bench_router/shepherdr.py#L66), [bench_router/herdr.py:693](../../../bench_router/herdr.py#L693). Violates mid-run version swap recovery. When the installed CLI switches to the 3.1 command set, binding compares its launch session `default` with the recorded 3.2 session `shepherdr`. Collection refuses before reading the card or its already-written result, even when both remain available in the fake.

```python
    def test_version_swap(self):
        fake = FakeSessionProjects(board_session="shepherdr", on_prompt=write_result())
        fake.core_version = "hc 0.1.20"
        out = self.run_(fake, wait_ms=0)
        fake.commands.clear()

        def old_cli(cmd, **kw):
            if cmd[:2] == [hd.PROJECTS_BIN, "--help"]:
                return CompletedProcess(cmd, 0, "usage: herdr-task [-h] {add,start}\n", "")
            return fake(cmd, **kw)

        done = hd.collect_run(self.cwd, out["run_id"], 0, runner=old_cli)
        self.assertEqual((done["status"], done["last_observation"]["note"]), ("completed", None))
```

Observed `delivery_uncertain` with `Shepherdr session 'default' differs from recorded/configured 'shepherdr'`.

### 4. High · Pre-port running receipts cannot be collected after upgrading the router

[bench_router/shepherdr.py:133](../../../bench_router/shepherdr.py#L133), [bench_router/herdr.py:693](../../../bench_router/herdr.py#L693). Violates continuity for running work during the port. The pre-port binding never stored `core_id`. A current binding always has one, so equality fails even with the same CLI and core. The compatibility return only covers receipts that are already completed.

```python
    def test_old_running(self):
        fake = FakeSessionProjects(on_prompt=write_result())
        fake.core_version = "hc 0.1.20"
        out = self.run_(fake, wait_ms=0)
        rc = self.receipt(out)
        del rc["project_binding"]["core_id"]
        hd.save(rc)
        done = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((done["status"], done["last_observation"]["note"]), ("completed", None))
```

Observed `delivery_uncertain` with `Shepherdr session or core binding differs from the receipt`.

### 5. High · Headless collection strands valid results after a lost start response or an early terminal exit

[bench_router/herdr.py:640](../../../bench_router/herdr.py#L640), [bench_router/herdr.py:727](../../../bench_router/herdr.py#L727), [bench_router/shepherdr.py:222](../../../bench_router/shepherdr.py#L222). Violates run and collect recovery. After a lost start response, the card is known and shows a live worker, but collection requires an already persisted terminal ID before checking the exit marker and result. After a confirmed start, if the terminal finishes before verification, plain `hc ls` hides it. Collection repeats that same verification and never reaches `hc get`.

```python
    def test_headless_lost_start(self):
        fake = FakeSessionProjects(after_status="working")
        fake.core_version = "hc 0.1.20"
        fake.on_run = headless_cli()
        fake.start_error = True
        out = self.run_(fake, self.task(execution="headless"), wait_ms=0)
        self.assertIsNone(self.receipt(out).get("terminal_id"))
        self.assertEqual(fake.panes[out["thread_id"]]["address"], "t1")
        fake.commands.clear()
        done = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((done["status"], done["last_observation"]["note"]), ("completed", None))
```

Observed `delivery_uncertain` with `hc run response was lost; inspect the recorded run label before resolving`.

```python
    def test_headless_fast_exit(self):
        fake = FakeSessionProjects(after_status="working")
        fake.core_version = "hc 0.1.20"

        def finish(board, cmd):
            headless_cli()(board, cmd)
            next(iter(board.panes.values()))["state"] = "finished"

        fake.on_run = finish
        core = fake._core
        empty = (SPIKE / "stop/ls_live_t0.out").read_text()
        def core_hides_finished(argv):
            if argv[0] == "ls" and "--all" not in argv and fake.panes:
                return CompletedProcess(argv, 0, empty, "")
            return core(argv)
        fake._core = core_hides_finished
        out = self.run_(fake, self.task(execution="headless"), wait_ms=0)
        rc = self.receipt(out)
        self.assertTrue(Path(rc["run_dir"], "exit_code").exists())
        done = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((done["status"], done["last_observation"]["note"]), ("completed", None))
```

Observed `delivery_uncertain` with `recorded terminal is absent from the task's core session`. This uses the captured `{"hidden_finished":1,"terminals":[]}` response for plain `ls` while the fake retains the finished record for `get`.

### 6. High · The alternate board crashes collection after a lost start response

[bench_router/herdr.py:669](../../../bench_router/herdr.py#L669), [bench_router/herdr.py:415](../../../bench_router/herdr.py#L415), [bench_router/board.py:38](../../../bench_router/board.py#L38). Violates alternate-provider recovery through the router. The shared contract test observes a lost start, but the router has no worktree path from the lost response. The adapter reports that the turn ended and the valid manifest is on disk, then collection tries to construct `Path(None)`.

```python
    def test_memory_lost_start(self):
        board = WorktreeMemoryBoard(Path(self.cwd) / "wt")
        board.lose.add("start")
        def offline_runner(cmd, **kw):
            self.fail(f"unexpected CLI command {cmd}")
        with patch.dict(hd.BOARDS, {board.backend: lambda runner: board}):
            out = self.run_(offline_runner, backend=board.backend, wait_ms=0)
            rc = self.receipt(out)
            self.assertEqual((out["status"], rc["worktree"]), ("delivery_uncertain", None))
            key = out["thread_id"]
            prompt = Path(rc["run_dir"], "input.txt").read_text()
            write_result()(SimpleNamespace(worktree_of=lambda _: board.root / key), prompt)
            board.cards[key].update(raw="finished", proc="ended")
            done = hd.collect_run(self.cwd, out["run_id"], 0, runner=offline_runner)
            self.assertEqual((done["status"], board.calls["start"]), ("completed", 1))
```

Observed `TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'`.

### 7. Medium · A finished interactive terminal can leave a valid result uncollected

[bench_router/herdr.py:754](../../../bench_router/herdr.py#L754). Violates collect recovery. The captured board behavior allows `status="working"`, `live=[]` and a finished terminal at the same time. The new stopped branch settles the receipt as failed before checking the result already on disk.

```python
    def test_interactive_finished_result(self):
        fake = FakeSessionProjects(after_status="working", on_prompt=write_result())
        fake.core_version = "hc 0.1.20"
        out = self.run_(fake, wait_ms=0)
        fake.panes[out["thread_id"]]["state"] = "finished"
        fake.detail_updates["live"] = []
        done = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((done["status"], done["task_outcome"], done["last_observation"]["note"]),
                         ("completed", "success", None))
```

Observed `('execution_failed', None, 'task agent stopped')`, expected `('completed', 'success', None)`.

### 8. Medium · Native collection skips the lost-create identity lookup

[bench_router/herdr.py:715](../../../bench_router/herdr.py#L715), [bench_router/shepherdr.py:340](../../../bench_router/shepherdr.py#L340). Violates the Board contract for identifying a card after an uncertain create. The adapter implements run-title lookup, but the native collect path exits before calling it. The fake creates one card and loses the add response. A list response makes the existing card available for lookup.

```python
    def test_lost_create_lookup(self):
        fake = FakeSessionProjects(after_status="working")
        fake.add_error = True
        out = self.run_(fake, wait_ms=0)
        fake.commands.clear()

        def runner(cmd, **kw):
            if cmd[:2] == [hd.PROJECTS_BIN, "list"]:
                return fake._ok({"tasks": list(fake.tasks.values())})
            return fake(cmd, **kw)

        done = hd.collect_run(self.cwd, out["run_id"], 0, runner=runner)
        self.assertEqual((done["thread_id"], fake.mutations()), ("repo#1", []))
```

Observed `(thread_id, mutations) == (None, [])`, expected `('repo#1', [])`. No task was resubmitted.

## Checked and correct

- The documented offline suite ran 305 tests with one skip on Python 3.15.0.
- Separate run, collect, Ready and terminal cleanup flows passed with both fake release profiles at hc 0.1.20. Each fake had a second core with its own `t1`. With the connection correctly routed, only the recorded run's terminal closed.
- The unchanged CLI parser, backend identifiers and existing JSON assertions passed. Completed Shepherdr receipts without `core_id` stayed byte-for-byte readable in the compatibility test.
- Same-round recovery did not replay an uncertain add or start. Existing coverage for lost send and Ready responses passed. The successful handoff kept the merge decision with the human.
- The standard admission tests still reject a fifth active dispatch. The interactive multi-terminal stop test kept admission until its second terminal exited.
- The in-memory board passed the shared adapter contract and the ordinary router dispatch, collect, handoff and cleanup integration with zero Shepherdr calls.
- `git diff --check` passed. The review left tracked files untouched.

## Could not check

- Real end-to-end flows, replacement or migration of a live board, or whether a live installation can produce the misrouted core connection injected in finding 1. The review used the captured CLI evidence and offline fakes.
- Live agent idle and turn reporting, real observer scheduling, and the actual human merge and worktree removal after acceptance.
- Python 3.11 specifically. It was unavailable as `python3.11` in the review environment.
