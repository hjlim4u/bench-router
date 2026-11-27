"""Board port contract tests. BoardContract runs against any adapter; MemoryBoard is the reference fake."""
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from bench_router import herdr as hd, routing as r, shepherdr
from bench_router.board import CAPABILITIES, PERSISTENCE, PROCESS_STATES, TASK_STATES, Board, observation
from bench_router.routing import InputError

# Raw names deliberately unlike Shepherdr's (todo/queued/running/needs/ready/stopped).
RAW_TASK = {"fresh": "not_started", "waiting": "queued", "busy": "working",
            "asks_human": "blocked", "finished": "turn_done", "halted": "stopped"}
RAW_PROC = {"up": "live", "ended": "exited", "none": "gone", "?": "unknown"}
TO_RAW_TASK = {v: k for k, v in RAW_TASK.items()}
TO_RAW_PROC = {v: k for k, v in RAW_PROC.items()}


class MemoryBoard:
    backend = "memory"
    PROTOCOL = "mem/2"

    def __init__(self, capabilities=CAPABILITIES):
        self.capabilities = frozenset(capabilities)
        self.protocol = self.PROTOCOL
        self.cards = {}
        self.calls = Counter()  # side effects actually applied
        self.lose = set()       # ops whose response is lost after the side effect
        self.flaky = self.stubborn = False

    def _done(self, op):
        self.calls[op] += 1
        if op in self.lose:
            self.lose.discard(op)
            raise TimeoutError(f"{op}: response lost")

    def _need(self, cap):
        if cap not in self.capabilities:
            raise InputError(f"memory board does not support {cap}")

    def bind(self, session, cwd):
        if self.protocol != self.PROTOCOL:
            raise InputError(f"unsupported board protocol {self.protocol}")
        return {"backend": self.backend, "protocol": self.protocol, "session": session}

    def create(self, rc):
        n = len(self.cards) + 1
        key = f"m-{n:04x}"
        self.cards[key] = {"title": rc["run_id"], "uid": f"uid/{n}", "raw": "fresh", "proc": "none",
                           "terminal": None, "session": None, "inbox": []}
        self._done("create")
        return {"thread_id": key, "task_id_on_board": f"uid/{n}"}

    def start(self, rc):
        if self.bind(rc["binding"]["session"], None) != rc["binding"]:
            raise InputError("board binding changed since bind")
        card = self.cards[rc["thread_id"]]
        card.update(raw="busy", proc="up", terminal=f"tty-{rc['thread_id']}", session=f"s-{rc['thread_id']}")
        self._done("start")
        return {"terminal_id": card["terminal"], "worktree": f"/mem/{rc['thread_id']}", "branch": f"mem/{rc['thread_id']}"}

    def observe(self, rc):
        if self.flaky:
            return observation(None, "unknown", retryable=True, why="board busy")
        extra = {}
        key = rc.get("thread_id")
        if not key:  # lost create: look up by run-id title only
            found = [k for k, c in self.cards.items() if c["title"] == rc["run_id"]]
            if len(found) != 1:
                raise InputError(f"{len(found)} cards titled {rc['run_id']}")
            key = found[0]
            extra["ids"] = {"thread_id": key, "task_id_on_board": self.cards[key]["uid"]}
        card = self.cards.get(key)
        if card is None:
            raise InputError(f"card {key} not found")
        ok = (not rc.get("task_id_on_board") or card["uid"] == rc["task_id_on_board"]) and \
             (not rc.get("terminal_id") or card["terminal"] == rc["terminal_id"])
        return observation(RAW_TASK[card["raw"]], RAW_PROC[card["proc"]], "ok" if ok else "mismatch", **extra)

    def stop(self, rc):
        card = self.cards[rc["thread_id"]]
        card["raw"] = "halted"
        if not self.stubborn:
            card["proc"] = "ended"
        self._done("stop")
        return self.observe(rc)

    def handoff(self, rc):
        self.cards[rc["thread_id"]]["raw"] = "finished"
        self._done("handoff")
        return "handed_off"

    def cleanup(self, rc):
        card = self.cards[rc["thread_id"]]
        if card["proc"] == "up" and card["raw"] == "busy":
            return {"closed": [], "left_open": "agent still working"}
        closed = [card["terminal"]] if card["terminal"] else []
        card["proc"] = "none"
        return {"closed": closed, "left_open": None}

    def tell(self, rc, text):
        self._need("tell")
        self.cards[rc["thread_id"]]["inbox"].append(text)
        self._done("tell")

    def resume(self, rc):
        self._need("resume")
        card = self.cards[rc["thread_id"]]
        resumed = card["session"] is not None
        card.update(terminal=f"tty-{rc['thread_id']}-r{self.calls['resume'] + 1}", proc="up", raw="busy")
        self._done("resume")
        return {"terminal_id": card["terminal"], "resumed": resumed}


def call(rc, op, fn, *args):
    """Reference router side of PERSISTENCE: record before, store on success, never re-call after a lost response."""
    assert rc["ops"].get(op) != "uncertain", f"{op} re-called after lost response"
    rc["events"].append({"op": op, "state": "attempted"})
    if op == "create":
        rc["delivery_state"] = "submission_attempted"
    rc["ops"][op] = "attempted"
    try:
        out = fn(rc, *args)
    except InputError:
        raise
    except Exception:
        rc["ops"][op] = "uncertain"
        if op in ("create", "start"):
            rc["delivery_state"] = "uncertain"
        return None
    rc["ops"][op] = "confirmed"
    if isinstance(out, dict) and op in ("create", "start", "resume"):
        rc.update({k: v for k, v in out.items() if k != "resumed"})
    return out


class BoardContract:
    """Mixin. Subclasses provide make_board(capabilities) and force(board, rc, task, process)."""

    def make_board(self, capabilities=CAPABILITIES): raise NotImplementedError
    def force(self, board, rc, task, process): raise NotImplementedError
    def lose_next(self, board, op): raise NotImplementedError
    def side_effects(self, board, op): raise NotImplementedError
    def set_flaky(self, board): raise NotImplementedError
    def set_stubborn(self, board): raise NotImplementedError
    def set_unsupported(self, board): raise NotImplementedError

    def started(self, capabilities=CAPABILITIES):
        board = self.make_board(capabilities)
        rc = {"run_id": "run-1", "events": [], "ops": {}, "delivery_state": "not_attempted"}
        rc["binding"] = board.bind("sess", "/repo")
        call(rc, "create", board.create)
        call(rc, "start", board.start)
        return board, rc

    def test_v01_lifecycle(self):
        board, rc = self.started()
        self.assertIsInstance(board, Board)
        self.assertLessEqual(board.capabilities, CAPABILITIES)
        for k in ("thread_id", "task_id_on_board", "terminal_id", "worktree", "branch"):
            self.assertTrue(rc.get(k), k)
        self.assertEqual(board.observe(rc)["task"], "working")
        self.assertEqual(board.cleanup(rc)["closed"], [])  # working agent is left open, with a reason
        self.force(board, rc, "turn_done", "live")
        self.assertIsInstance(call(rc, "handoff", board.handoff), str)
        self.force(board, rc, "turn_done", "exited")
        out = board.cleanup(rc)
        self.assertEqual((out["closed"], out["left_open"]), ([rc["terminal_id"]], None))

    def test_v02_task_and_process_axes(self):
        board, rc = self.started()
        for task in sorted(TASK_STATES):
            for process in sorted(PROCESS_STATES):
                self.force(board, rc, task, process)
                obs = board.observe(rc)
                self.assertEqual((obs["task"], obs["process"], obs["identity"], obs["retryable"]),
                                 (task, process, "ok", False))
                self.assertIn("why", obs)

    def test_v03_identity_mismatch(self):
        board, rc = self.started()
        self.assertEqual(board.observe(dict(rc, terminal_id="someone-else"))["identity"], "mismatch")

    def test_v04_transient_error_is_retryable(self):
        board, rc = self.started()
        self.set_flaky(board)
        obs = board.observe(rc)
        self.assertEqual((obs["task"], obs["retryable"]), (None, True))

    def test_v05_unsupported(self):
        board, rc = self.started(capabilities=frozenset())
        with self.assertRaises(InputError):
            board.tell(rc, "hi")
        with self.assertRaises(InputError):
            board.resume(rc)
        self.set_unsupported(board)
        with self.assertRaises(InputError):
            board.bind("sess", "/repo")

    def test_v06_start_revalidates_binding(self):
        board = self.make_board()
        rc = {"run_id": "run-1", "events": [], "ops": {}, "delivery_state": "not_attempted",
              "binding": board.bind("sess", "/repo")}
        call(rc, "create", board.create)
        self.set_unsupported(board)
        with self.assertRaises(InputError):
            board.start(rc)
        self.assertEqual(self.side_effects(board, "start"), 0)

    def test_v07_create_lost_lookup_by_title(self):
        board = self.make_board()
        rc = {"run_id": "run-1", "events": [], "ops": {}, "delivery_state": "not_attempted",
              "binding": board.bind("sess", "/repo")}
        self.lose_next(board, "create")
        self.assertIsNone(call(rc, "create", board.create))
        self.assertEqual((rc["delivery_state"], rc.get("thread_id")), ("uncertain", None))
        with self.assertRaises(AssertionError):
            call(rc, "create", board.create)
        ids = board.observe(rc)["ids"]
        self.assertTrue(ids["thread_id"] and ids["task_id_on_board"])
        self.assertEqual(self.side_effects(board, "create"), 1)

    def test_v08_start_lost_observe_stored_card(self):
        board = self.make_board()
        rc = {"run_id": "run-1", "events": [], "ops": {}, "delivery_state": "not_attempted",
              "binding": board.bind("sess", "/repo")}
        call(rc, "create", board.create)
        self.lose_next(board, "start")
        self.assertIsNone(call(rc, "start", board.start))
        self.assertEqual((rc["delivery_state"], rc.get("terminal_id")), ("uncertain", None))
        obs = board.observe(rc)
        self.assertEqual((obs["task"], obs["identity"]), ("working", "ok"))
        self.assertEqual(self.side_effects(board, "start"), 1)

    def test_v09_resume_lost_identity_mismatch(self):
        board, rc = self.started()
        self.force(board, rc, "stopped", "exited")
        self.lose_next(board, "resume")
        self.assertIsNone(call(rc, "resume", board.resume))
        self.assertEqual(rc["ops"]["resume"], "uncertain")
        self.assertEqual(board.observe(rc)["identity"], "mismatch")  # -> manual reconciliation
        self.assertEqual(self.side_effects(board, "resume"), 1)

    def test_v10_resume_returns_new_terminal(self):
        board, rc = self.started()
        old = rc["terminal_id"]
        out = call(rc, "resume", board.resume)
        self.assertTrue(out["resumed"])
        self.assertNotEqual(rc["terminal_id"], old)
        self.assertEqual(board.observe(rc)["identity"], "ok")

    def test_v11_tell_lost_no_resend(self):
        board, rc = self.started()
        self.lose_next(board, "tell")
        self.assertIsNone(call(rc, "tell", board.tell, "hi"))
        self.assertEqual(rc["events"][-1], {"op": "tell", "state": "attempted"})
        self.assertEqual(self.side_effects(board, "tell"), 1)

    def test_v12_stop_needs_exit_evidence(self):
        board, rc = self.started()
        self.set_stubborn(board)
        obs = call(rc, "stop", board.stop)
        self.assertEqual(obs["task"], "stopped")
        self.assertNotEqual(obs["process"], "exited")  # request accepted is not termination: keep admission
        board2, rc2 = self.started()
        self.assertEqual(call(rc2, "stop", board2.stop)["process"], "exited")

    def test_v13_handoff_lost_no_recall(self):
        board, rc = self.started()
        self.force(board, rc, "turn_done", "live")
        self.lose_next(board, "handoff")
        self.assertIsNone(call(rc, "handoff", board.handoff))
        self.assertEqual(rc["ops"]["handoff"], "uncertain")
        with self.assertRaises(AssertionError):
            call(rc, "handoff", board.handoff)
        self.assertEqual(self.side_effects(board, "handoff"), 1)

    def test_v14_persistence_table_covered(self):
        self.assertEqual(set(PERSISTENCE), {"create", "start", "resume", "tell", "stop", "handoff"})


class MemoryBoardContract(BoardContract, unittest.TestCase):
    def make_board(self, capabilities=CAPABILITIES):
        return MemoryBoard(capabilities)

    def force(self, board, rc, task, process):
        board.cards[rc["thread_id"]].update(raw=TO_RAW_TASK[task], proc=TO_RAW_PROC[process])

    def lose_next(self, board, op):
        board.lose.add(op)

    def side_effects(self, board, op):
        return board.calls[op]

    def set_flaky(self, board):
        board.flaky = True

    def set_stubborn(self, board):
        board.stubborn = True

    def set_unsupported(self, board):
        board.protocol = "mem/1"


class FakeShepherdr:
    """herdr-task and hc argv -> JSON shaped like docs/evidence/shepherdr-cli (3.2.19), in memory. Never runs a CLI."""
    OPS = {"create": "add", "start": "start", "resume": "resume", "tell": "send", "stop": "kill", "handoff": "ready"}

    def __init__(self):
        self.version, self.cards, self.terms = "1", {}, {}
        self.calls, self.lose = Counter(), set()
        self.flaky = self.stubborn = False

    def __call__(self, cmd, **kw):
        assert kw["shell"] is False
        out = self._core(cmd[1], cmd[2:]) if cmd[0] == shepherdr.HERDR_BIN else self._tasks(cmd[1], cmd[2:])
        code, body = out if isinstance(out, tuple) else (0, out)
        text = body if isinstance(body, str) else json.dumps(body)
        if cmd[1] in self.lose:
            self.lose.discard(cmd[1])
            raise subprocess.TimeoutExpired(cmd, 15)
        return subprocess.CompletedProcess(cmd, code, text if code == 0 else "", "" if code == 0 else text)

    def _terminal(self, card):
        address = f"t{len(self.terms) + 1}"
        self.terms[address] = {"address": address, "state": "live", "labels": {"herdr.task": card["key"]}}
        card.update(state="running", status="working", needs=None, live=[{"address": address, "status": "working"}],
                    worktree=f"{card['folder']}/.wt/{card['title']}")
        return address

    def _tasks(self, op, a):
        arg = lambda flag: a[a.index(flag) + 1] if flag in a else None
        self.calls[op] += 1
        if op == "--version":
            return self.version + "\n"
        if op == "--help":
            return "{add,start,stop}"
        if op == "add":
            n = len(self.cards) + 1
            card = {"id": n, "key": f"repo#{n}", "ref": f"REPO-{n}", "title": a[0], "folder": arg("--folder"),
                    "agent": arg("--agent"), "mode": "worktree", "state": "todo", "status": "todo", "needs": None,
                    "why": None, "live": [], "worktree": None, "branch": arg("--branch")}
            self.cards[card["key"]] = card
            return card
        if op == "list":
            return {"folder": "/repo", "tasks": list(self.cards.values())}
        if op == "show":
            return (1, '{"error": "core busy"}') if self.flaky else self.cards[a[0]]
        if op in ("start", "resume"):
            card = self.cards[a[0]]
            terminal = self._terminal(card)
            return {**card, "terminal": terminal, **({"resumed": True} if op == "resume" else {})}
        if op == "ready":
            self.cards[a[0]]["status"] = "ready"
            return {**self.cards[a[0]], "state": "ready"}
        raise AssertionError(op)

    def _core(self, op, a):
        if op == "--version":
            return "hc 0.1.20\n"
        if op == "server":
            return {"core": {"id": "fake-core"}}
        if op == "get":
            t = self.terms.get(a[0])
            if t is None:
                return 3, '{"error": {"kind": "not_found"}}'
            return (5, '{"error": {"kind": "unavailable"}}') if t.get("unknown") else t
        if op == "ls":
            key = a[a.index("--label") + 1].split("=", 1)[1]
            card = self.cards[key]
            status = {x["address"]: x["status"] for x in card["live"]}
            return {"terminals": [{"address": t["address"], "state": t["state"], "status": status.get(t["address"], "done")}
                                  for t in self.terms.values() if t["labels"]["herdr.task"] == key]}
        self.calls[op] += 1
        if op == "kill":
            t = self.terms[a[0]]
            self.cards[t["labels"]["herdr.task"]].update(status="needs", needs="stopped", why="Agent stopped", live=[])
            if not self.stubborn:
                t["state"] = "finished"
            return {"ok": True}
        if op == "send":
            return {"ok": True}
        raise AssertionError(op)


# Board state -> a Shepherdr card (state, status, needs, live worker status or None).
SHEPHERDR_ROWS = {"not_started": ("todo", "todo", None, None), "queued": ("queued", "queued", None, None),
                  "working": ("running", "working", None, "working"), "blocked": ("running", "needs", "input", "working"),
                  "turn_done": ("running", "ready", None, "idle"), "stopped": ("running", "needs", "stopped", None)}


class ShepherdrBoardContract(BoardContract, unittest.TestCase):
    def make_board(self, capabilities=CAPABILITIES):
        board = shepherdr.ShepherdrBoard(FakeShepherdr(), capabilities=capabilities)
        board.fake = board.runner
        return board

    def force(self, board, rc, task, process):
        state, status, needs, worker = SHEPHERDR_ROWS[task]
        t = rc["terminal_id"]
        board.fake.cards[rc["thread_id"]].update(state=state, status=status, needs=needs,
                                                 live=[{"address": t, "status": worker}] if worker else [])
        board.fake.terms.pop(t, None)
        if process != "gone":
            board.fake.terms[t] = {"address": t, "state": {"live": "live", "exited": "finished"}.get(process, "live"),
                                   "labels": {"herdr.task": rc["thread_id"]}, "unknown": process == "unknown"}

    def lose_next(self, board, op):
        board.fake.lose.add(FakeShepherdr.OPS[op])

    def side_effects(self, board, op):
        return board.fake.calls[FakeShepherdr.OPS[op]]

    def set_flaky(self, board):
        board.fake.flaky = True

    def set_stubborn(self, board):
        board.fake.stubborn = True

    def set_unsupported(self, board):
        board.fake.version = "2"


class WorktreeMemoryBoard(MemoryBoard):
    """MemoryBoard registered as a router backend; its agent works in a real directory."""
    backend = "memory-1"

    def __init__(self, root):
        super().__init__()
        self.root = root

    def start(self, rc):
        return {**super().start(rc), "worktree": str(self.root / rc["thread_id"])}


class RouterBoardIntegration(unittest.TestCase):
    def test_v16_memory_board_through_router(self):
        from test_p0 import MAPPING, config, profile
        from test_p2 import cleanup_temp, git_repo, projects_environment, which
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(cleanup_temp, tmp)
        projects_environment(self, tmp.name)
        cwd = Path(os.path.realpath(tmp.name)) / "repo"
        cwd.mkdir()
        git_repo(cwd)
        cfg = config([profile("a", kind="claude", executable="claude", args=["--model", "m"])])
        task = r.validate_task({"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "do it",
                                "cwd": str(cwd), "constraints": {"timeout_ms": 60000}})
        board, picked, commands = WorktreeMemoryBoard(Path(tmp.name) / "wt"), [], []
        def runner(cmd, **kw):
            commands.append(cmd)
            raise AssertionError(f"no CLI may run for a memory board: {cmd}")
        with patch.dict(hd.BOARDS, {"memory-1": lambda runner: picked.append(runner) or board}):
            out = hd.dispatch(task, cfg, MAPPING, None, [], runner=runner, which=which, profile_id="a",
                              selection_mode="orchestrator_pinned", wait_ms=0, backend="memory-1")
            self.assertEqual(out["status"], "timed_out", out)
            rc = json.loads(Path(out["receipt_path"]).read_text("utf-8"))  # recovery starts from the receipt on disk
            self.assertEqual((rc["backend"], rc["delivery_state"]), ("memory-1", "submission_attempted"))
            self.assertTrue(rc["thread_id"] and rc["task_id_on_board"] and rc["terminal_id"])
            # the agent writes its result and ends the turn
            body = b"# result\n"
            res = Path(rc["worktree"]) / hd.RESULT_REL / rc["run_id"]
            res.mkdir(parents=True)
            (res / "result.md").write_bytes(body)
            (res / "result.json").write_text(json.dumps({
                "schema_version": "1.0", "run_id": rc["run_id"], "nonce": rc["nonce"],
                "profile_fingerprint": rc["profile_fingerprint"], "status": "success", "result_file": "result.md",
                "result_sha256": hashlib.sha256(body).hexdigest(), "checks": []}), "utf-8")
            board.cards[rc["thread_id"]]["raw"] = "finished"
            picked.clear()
            done = hd.collect_run(str(cwd), rc["run_id"], 0, runner=runner)
        self.assertTrue(picked)  # collect, handoff and cleanup chose the adapter from rc["backend"]
        self.assertEqual((done["status"], done["task_outcome"]), ("completed", "success"))
        self.assertEqual(done["ready"], {"state": "handed_off", "error": None})
        self.assertEqual(done["release"]["terminals"], [{"terminal_id": rc["terminal_id"]}])
        self.assertEqual(+board.calls, Counter(create=1, start=1, handoff=1))
        self.assertEqual([c for c in commands if c[0] in (shepherdr.HERDR_BIN, shepherdr.PROJECTS_BIN)], [])
        self.assertEqual(commands, [])


class ObservationTest(unittest.TestCase):
    def test_v15_rejects_unknown_values(self):
        with self.assertRaises(ValueError):
            observation("running", "live")  # Shepherdr raw names never leak through the port
        with self.assertRaises(ValueError):
            observation("working", "alive")


if __name__ == "__main__":
    unittest.main()
