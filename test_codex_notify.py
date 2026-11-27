import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import uuid

from bench_router import codex_notify as n


class CodexNotifications(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cwd = str(Path(self.temp.name).resolve())
        self.thread, self.run_id, self.queue_id = (str(uuid.uuid4()) for _ in range(3))
        self.enterContext(patch.dict(os.environ, CODEX_HOME=self.cwd, CODEX_THREAD_ID=self.thread))
        self.directory = n.h.run_dir(self.cwd, self.run_id)
        self.directory.mkdir(parents=True)
        self.state = self.directory / "codex-notification.json"
        self.rc = dict(cwd=self.cwd, run_dir=str(self.directory), run_id=self.run_id, backend=n.h.LOCAL_BACKEND,
                       codex_notify_home=n.daemon_home(), codex_notify_thread=n.caller_binding(),
                       status="completed", settled_contract=True, task_outcome="partial")
        self.ack = subprocess.CompletedProcess([], 0, f"Queued message {self.queue_id} for thread {self.thread}.",
                                               "warning: resume unavailable")

    def test_binding_and_terminal_gate(self):
        with patch.dict(os.environ, CODEX_THREAD_ID="latest"), self.assertRaises(n.r.InputError):
            n.caller_binding()
        statuses = [("delivery_uncertain", False), ("waiting", False), ("timed_out", False),
                    ("execution_failed", False), ("execution_failed", True), ("result_invalid", True)]
        for status, confirmed in statuses:
            with self.subTest(status=status, confirmed=confirmed):
                rc = {**self.rc, "status": status, "process_exited": confirmed, "delivery_state": "activity_observed"}
                n.h.save(rc)
                with patch.object(subprocess, "run", return_value=self.ack) as send:
                    self.assertEqual(confirmed, n.notify_final(rc))
                    self.assertEqual(int(confirmed), send.call_count)
                self.state.unlink(missing_ok=True)
        n.h.save({**self.rc, "status": "waiting"})
        self.assertFalse(n.notify_final(self.rc))  # In-memory status alone cannot send.
        n.h.save(self.rc)
        with patch.dict(os.environ, CODEX_HOME=self.cwd + "/elsewhere"):
            self.assertFalse(n.notify_final(self.rc))
        self.assertFalse(self.state.exists())

    def test_repeat_and_concurrent_collect_use_one_queue_item(self):
        self.rc.update(result_path="untrusted worker path", diagnostic_tail="untrusted output")
        n.h.save(self.rc)
        with patch.object(subprocess, "run", return_value=self.ack) as send:
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                self.assertEqual(sum(pool.map(n.notify_final, [self.rc] * 12)), 1)
            send.assert_called_once()
            self.assertFalse(n.notify_final(self.rc))
        args = send.call_args.args[0]
        self.assertEqual(args[:6], ["codex", "queue", "--thread", self.thread, "--resume", "--message"])
        self.assertNotIn("untrusted", args[6])
        self.assertIn('"task_outcome":"partial"', args[6])
        payload = json.loads(args[6].removeprefix("bench-router completion "))
        self.assertEqual((payload["receipt"], payload["result"]),
                         (str(self.directory / "receipt.json"), str(self.directory / "result.md")))
        self.assertTrue(Path(payload["receipt"]).is_absolute() and Path(payload["receipt"]).is_file())
        self.assertEqual(json.loads(self.state.read_text()), {"state": "queued", "returncode": 0,
                         "queue_id": self.queue_id, "warning": "warning: resume unavailable"})

    def test_ambiguous_send_keeps_claim(self):
        n.h.save(self.rc)
        with patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("codex", 10)) as send:
            self.assertFalse(n.notify_final(self.rc))
            self.assertFalse(n.notify_final(self.rc))
            send.assert_called_once()
        self.assertEqual(json.loads(self.state.read_text())["state"], "uncertain")

    def test_spawn_failure_keeps_receipt_collectable(self):
        rc = {**self.rc, "status": "waiting"}
        n.h.save(rc)
        with patch.object(subprocess, "Popen", side_effect=OSError("process limit")):
            self.assertFalse(n.spawn_local_observer(rc))
        self.assertIn("process limit", (self.directory / "codex-observer.log").read_text())
        self.assertEqual(n.h.load_receipt(self.cwd, self.run_id)["status"], "waiting")
