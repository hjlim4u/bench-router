"""Offline integration checks: shared native/A2A admission and stock CLI contracts."""
import hashlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from bench_router import a2a, cli, coordination as co, herdr, routing as r
from test_p0 import MAPPING, config, profile
from test_p2 import FakeHerdr, which, write_result


class FakeA2A:
    def __init__(self, agent, state=1, lose=None, runtime="codex"):
        self.agent, self.state, self.lose, self.runtime = agent, state, lose, runtime
        self.calls = []

    def __call__(self, cmd, **kw):
        assert kw["shell"] is False and "--wait" not in cmd and "--model" not in cmd
        self.calls.append(cmd)
        action = cmd[1]
        if action == self.lose:
            raise subprocess.TimeoutExpired(cmd, 30)
        obj = ({"agents": [{"name": self.agent, "runtime": self.runtime, "available": True}]}
               if action == "discover" else {"id": "task-1", "status": {"state": self.state},
                   "metadata": {"target": self.agent, "runtime": self.runtime, "instance": "worker-1"}, "artifacts": []})
        return subprocess.CompletedProcess(cmd, 1 if self.state == 4 and action != "discover" else 0,
                                           json.dumps(obj), "")


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        env = patch.dict(os.environ, {"BENCH_ROUTER_COORDINATION_DIR": str(self.base / "state")})
        env.start()
        self.addCleanup(env.stop)
        self.cwd = self.base / "work"
        self.cwd.mkdir()
        self.cfg = config([profile("review", kind="codex", executable="codex")], default="review")
        p = self.cfg["profile"][0]
        config_file = self.base / "gateway.yaml"
        config_file.write_text("operator-attested review profile", "utf-8")
        fp = r.profile_fingerprint(p)
        self.b = {"profile": p["id"], "profile_fingerprint": fp, "agent": f"review-{fp[:12]}",
                  "gateway": "http://127.0.0.1:9999", "model": p["model_id"],
                  "config_file": str(config_file), "config_sha256": hashlib.sha256(config_file.read_bytes()).hexdigest(),
                  "review_only": True}
        self.bindings = self.base / "a2a-bindings.json"
        self.write_binding()

    def write_binding(self):
        self.bindings.write_text(json.dumps({"schema_version": "1.0", "bindings": [self.b]}), "utf-8")

    def task(self, **kw):
        return r.validate_task({"schema_version": "1.0", "task_id": "one", "round": 1, "cwd": str(self.cwd),
                                "summary": "review", "prompt": "Review this explicit diff: + return 1", **kw})

    def review(self, fake, t=None):
        return a2a.delegate(t or self.task(), self.cfg, MAPPING, None, [], "review", self.bindings, runner=fake)

    def native(self, fake, t=None):
        return herdr.dispatch(t or self.task(), self.cfg, MAPPING, None, [], runner=fake, which=which)

    def test_v44a_cli_prefix_stays_argv_and_shell_free(self):
        prefix = ["C:/node.exe", "C:/cli.js"]
        self.assertEqual(a2a._argv(["discover"], "http://127.0.0.1:9999", prefix),
                         [*prefix, "discover", "--base-url", "http://127.0.0.1:9999", "--json"])

    def test_v44_repeat_observes_and_backend_is_immutable(self):
        fake = FakeA2A(self.b["agent"])
        first = self.review(fake)
        self.assertEqual(first["status"], "waiting")
        self.assertEqual(self.review(fake)["reference"], first["reference"])
        self.assertEqual([x[1] for x in fake.calls], ["discover", "delegate", "get"])
        native = FakeHerdr(on_prompt=write_result())
        self.assertEqual(self.native(native)["status"], "conflict")
        self.assertFalse(native.calls)
        other = FakeA2A(self.b["agent"])
        self.assertEqual(self.review(other, self.task(prompt="changed"))["status"], "conflict")
        self.assertFalse(other.calls)

    def test_v45_native_record_blocks_a2a_and_replays_receipt(self):
        fake = FakeHerdr(on_prompt=write_result())
        out = self.native(fake)
        self.assertEqual(out["status"], "completed")
        self.assertEqual(self.native(fake)["run_id"], out["run_id"])
        self.assertEqual(len(fake.prompts), 1)
        a = FakeA2A(self.b["agent"])
        self.assertEqual(self.review(a)["status"], "conflict")
        self.assertFalse(a.calls)

    def test_v46_uncertain_initial_submission_never_retries(self):
        fake = FakeA2A(self.b["agent"], lose="delegate")
        out = self.review(fake)
        self.assertEqual(out["status"], "delivery_uncertain")
        self.assertTrue(out["active"])
        self.review(fake)
        a2a.control(out["coordination_key"], "get", runner=fake)
        self.assertEqual([x[1] for x in fake.calls], ["discover", "delegate"])
        with self.assertRaises(co.Conflict):
            a2a.control(out["coordination_key"], "continue", "answer", runner=fake)

    def test_v47_profile_binding_and_catalog_fail_closed(self):
        fake = FakeA2A(self.b["agent"])
        Path(self.b["config_file"]).write_text("changed", "utf-8")
        with self.assertRaises(r.InputError):
            self.review(fake)
        self.assertFalse(fake.calls)
        Path(self.b["config_file"]).write_text("operator-attested review profile", "utf-8")
        fake.runtime = "claude"
        with self.assertRaises(r.InputError):
            self.review(fake)
        self.assertEqual(co.inspect()["active"], 0)
        self.b["agent"] = "unversioned-reviewer"
        self.write_binding()
        with self.assertRaises(r.InputError):
            self.review(fake)

    def test_v48_global_limit_and_workspace_writer_exclusion(self):
        fake = FakeA2A(self.b["agent"])
        for i in range(3):
            self.assertEqual(self.review(fake, self.task(task_id=f"r{i}"))["status"], "waiting")
        isolated = self.base / "isolated"
        isolated.mkdir()
        native = FakeHerdr(after_status="working", on_prompt=write_result())
        self.assertEqual(self.native(native, self.task(cwd=str(isolated)))["status"], "timed_out")
        self.assertEqual(co.inspect()["active"], 4)
        self.assertEqual(self.review(fake, self.task(task_id="fifth"))["status"], "conflict")
        self.assertEqual(self.native(FakeHerdr(), self.task(task_id="writer"))["status"], "conflict")
        native.after_status = "idle"
        native.status = "idle"
        receipt = next(x for x in co.inspect()["records"] if x["backend"] == "herdr")["reference"]
        herdr.collect_run(receipt["cwd"], receipt["run_id"], 0, runner=native)
        self.assertEqual(co.inspect()["active"], 3)

    def test_v49_continuation_lost_response_and_completion_acceptance(self):
        fake = FakeA2A(self.b["agent"], state=6)
        out = self.review(fake)
        key = out["coordination_key"]
        fake.lose = "continue"
        self.assertTrue(a2a.control(key, "continue", "Python 3.11", runner=fake)["continuation_uncertain"])
        fake.lose = None
        a2a.control(key, "get", runner=fake)
        with self.assertRaises(co.Conflict):
            a2a.control(key, "continue", "Python 3.11", runner=fake)
        fake.state = 3
        completed = a2a.control(key, "get", runner=fake)
        self.assertFalse(completed["active"])
        self.assertEqual(completed["acceptance"]["decision"], "withheld")
        with self.assertRaises(co.Conflict):
            co.feedback(key, "0" * 64, "accepted", "verified")
        self.assertEqual(co.feedback(key, out["input_hash"], "accepted", "independently verified")["acceptance"]["decision"], "accepted")

    def test_v50_failed_task_holds_slot_until_explicit_resolution(self):
        out = self.review(FakeA2A(self.b["agent"], state=4))
        self.assertEqual(out["status"], "execution_failed")
        self.assertTrue(out["active"])
        rec = co.resolve(out["coordination_key"], "Worker stopped; partial effects inspected")
        self.assertFalse(rec["active"])
        self.assertEqual(self.native(FakeHerdr())["status"], "conflict")

    def test_v51_crash_before_native_receipt_does_not_launch(self):
        co.reserve(self.task(), "herdr", {"session": None})
        fake = FakeHerdr()
        self.assertEqual(self.native(fake)["status"], "conflict")
        self.assertFalse(fake.calls)

    def test_v52_same_key_lock_and_parent_workspace_exclusion(self):
        with co.operation(co.key_for(self.task())):
            self.assertEqual(self.review(FakeA2A(self.b["agent"]))["status"], "conflict")
        self.review(FakeA2A(self.b["agent"]))
        child = self.cwd / "child"
        child.mkdir()
        fake = FakeHerdr()
        self.assertEqual(self.native(fake, self.task(cwd=str(child)))["status"], "conflict")
        self.assertFalse(fake.calls)

    def test_v53_cli_status_and_release_require_explicit_confirmation(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = cli.main(["coordination", "status"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["active"], 0)
        with redirect_stdout(io.StringIO()):
            code = cli.main(["coordination", "release", "--key", "0" * 64, "--note", "inspect"])
        self.assertEqual(code, 2)

    def test_v54_concurrent_admission_is_bounded(self):
        tasks = []
        for i in range(8):
            cwd = self.base / f"independent-{i}"
            cwd.mkdir()
            tasks.append(self.task(cwd=str(cwd)))
        def admit(t):
            try:
                co.reserve(t, "herdr", {"session": None})
                return True
            except co.Conflict:
                return False
        with ThreadPoolExecutor(8) as pool:
            self.assertEqual(sum(pool.map(admit, tasks)), 4)
        self.assertEqual(co.inspect()["active"], 4)

    def test_v55_identity_mismatch_and_unrecognized_response_remain_uncertain(self):
        fake = FakeA2A(self.b["agent"])
        out = self.review(fake)
        key = out["coordination_key"]
        original_response = Path(out["response_path"]).read_bytes()
        fake.agent = "another-agent"
        self.assertEqual(a2a.control(key, "get", runner=fake)["status"], "delivery_uncertain")
        self.assertEqual(Path(out["response_path"]).read_bytes(), original_response)
        self.assertTrue(co.load(key)["active"])
        fake.agent, fake.state = self.b["agent"], 999
        self.assertEqual(a2a.control(key, "get", runner=fake)["status"], "delivery_uncertain")
        fake.state = "TASK_STATE_COMPLETED"
        self.assertEqual(a2a.control(key, "get", runner=fake)["status"], "completed")

    def test_v56_preflight_failure_and_unsupported_work_do_not_submit(self):
        fake = FakeA2A(self.b["agent"], lose="discover")
        self.assertEqual(self.review(fake)["status"], "execution_failed")
        self.assertEqual(co.inspect()["records"], [])
        with self.assertRaises(r.InputError):
            self.review(fake, self.task(context_files=["file.py"]))
        with self.assertRaises(r.InputError):
            a2a._argv(["delegate", "agent", "x" * (121 * 1024)], self.b["gateway"])
        self.assertEqual([x[1] for x in fake.calls], ["discover"])

    def test_v57_native_collect_uses_recorded_session(self):
        fake = FakeHerdr(after_status="working", on_prompt=write_result())
        out = herdr.dispatch(self.task(), self.cfg, MAPPING, None, [], session="original", runner=fake, which=which)
        with self.assertRaises(r.InputError):
            herdr.collect_run(str(self.cwd), out["run_id"], 0, "another", runner=fake)
        fake.status = "idle"
        self.assertEqual(herdr.collect_run(str(self.cwd), out["run_id"], 0, runner=fake)["status"], "completed")

    def test_v58_cancel_keeps_slot_and_auth_is_not_auto_answered(self):
        fake = FakeA2A(self.b["agent"], state=8)
        out = self.review(fake)
        key = out["coordination_key"]
        with self.assertRaises(co.Conflict):
            a2a.control(key, "continue", "approve", runner=fake)
        fake.state = 5
        self.assertTrue(a2a.control(key, "cancel", runner=fake)["active"])
        self.assertTrue(a2a.control(key, "close", runner=fake)["active"])
        co.resolve(key, "closed worker and inspected effects")
        self.assertEqual(co.inspect()["active"], 0)

    def test_v59_cli_review_and_get_use_shared_adapter(self):
        task_file = self.base / "review.json"
        task_file.write_text(json.dumps({"schema_version": "1.0", **self.task()}), "utf-8")
        fake = FakeA2A(self.b["agent"])
        call = a2a._call
        with patch.object(cli, "_config", return_value=(self.cfg, MAPPING)), \
             patch.object(r, "load_snapshot", return_value=(None, [])), \
             patch.object(a2a, "_call", side_effect=lambda cmd, runner: call(cmd, fake)):
            output = io.StringIO()
            with redirect_stdout(output):
                code = cli.main(["--config-dir", str(self.base), "review", "--task", str(task_file), "--profile", "review"])
            self.assertEqual(code, 11)
            key = json.loads(output.getvalue())["coordination_key"]
            fake.state = 3
            output = io.StringIO()
            with redirect_stdout(output):
                code = cli.main(["a2a", "get", "--key", key])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue())["acceptance"]["decision"], "withheld")


if __name__ == "__main__":
    unittest.main()
