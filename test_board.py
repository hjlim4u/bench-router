"""Board port contract tests. BoardContract runs against any adapter; MemoryBoard is the reference fake."""
import unittest
from collections import Counter

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


class ObservationTest(unittest.TestCase):
    def test_v15_rejects_unknown_values(self):
        with self.assertRaises(ValueError):
            observation("running", "live")  # Shepherdr raw names never leak through the port
        with self.assertRaises(ValueError):
            observation("working", "alive")


if __name__ == "__main__":
    unittest.main()
