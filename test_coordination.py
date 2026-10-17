"""Projects integration: admission, replay, uncertainty, identity and acceptance."""
import io
import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from bench_router import cli, coordination as co, herdr, routing as r
from test_p0 import MAPPING, config, profile
from test_p2 import FakeProjects, git_repo, which, write_result, projects_environment, cleanup_temp


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(cleanup_temp, self.tmp)
        self.base = Path(self.tmp.name)
        self.project = projects_environment(self, self.base)
        self.cwd = self.base / "work"
        self.cwd.mkdir()
        git_repo(self.cwd)
        self.cfg = config([profile("review")], default="review")

    def task(self, **kw):
        return r.validate_task({"schema_version": "1.0", "task_id": "one", "round": 1, "cwd": str(self.cwd),
                                "summary": "review", "prompt": "Review supplied content",
                                "constraints": {"timeout_ms": 5000}, **kw})

    def run_(self, fake, t=None):
        fake.profiles = {p["id"]: p for p in self.cfg["profile"]}
        return herdr.dispatch(t or self.task(), self.cfg, MAPPING, None, [], runner=fake, which=which)

    def test_v44_repeat_observes_and_backend_is_immutable(self):
        fake = FakeProjects(on_prompt=write_result())
        first = self.run_(fake)
        self.assertEqual(self.run_(fake)["run_id"], first["run_id"])
        self.assertEqual(len(fake.prompts), 1)
        self.assertEqual(self.run_(fake, self.task(prompt="changed"))["status"], "conflict")
        with self.assertRaises(co.Conflict):
            co.reserve(self.task(), "legacy", {})
        self.assertEqual(co.inspect()["records"][0]["backend"], herdr.BACKEND)

    def test_v46_uncertain_initial_submission_never_retries(self):
        fake = FakeProjects(prompt_error="lost response")
        first = self.run_(fake)
        self.assertEqual((first["status"], first["thread_id"]), ("delivery_uncertain", None))
        self.assertEqual(self.run_(fake)["status"], "delivery_uncertain")
        self.assertEqual(len(fake.prompts), 1)
        self.assertTrue(co.load(first["coordination_key"])["active"])

    def test_v47_configuration_change_keeps_submission_uncertain(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        fake.version = "herdr-projects 1.2.2 (/fake)"
        fake.status = "idle"
        write_result()(fake, fake.prompts[0])
        self.assertEqual(herdr.collect_run(str(self.cwd), out["run_id"], 0, runner=fake)["status"], "delivery_uncertain")
        self.assertTrue(co.load(out["coordination_key"])["active"])
        self.assertEqual(len(fake.prompts), 1)

    def test_v48_global_limit_and_workspace_writer_exclusion(self):
        for i in range(4):
            cwd = self.base / f"work-{i}"
            cwd.mkdir()
            git_repo(cwd)
            out = self.run_(FakeProjects(after_status="working"), self.task(cwd=str(cwd)))
            self.assertEqual(out["status"], "timed_out")
        self.assertEqual(co.inspect()["active"], 4)
        fake = FakeProjects()
        self.assertEqual(self.run_(fake)["status"], "conflict")
        self.assertEqual(fake.adds, [])  # binding check only

    def test_v49_completion_and_acceptance_are_separate(self):
        out = self.run_(FakeProjects(on_prompt=write_result()))
        rec = co.load(out["coordination_key"])
        self.assertEqual(rec["acceptance"]["decision"], "withheld")
        with self.assertRaises(co.Conflict):
            co.feedback(rec["key"], "0" * 64, "accepted", "verified")
        self.assertEqual(co.feedback(rec["key"], rec["request_hash"], "accepted", "verified")["acceptance"]["decision"], "accepted")

    def test_v50_failed_worker_holds_slot_until_inspected(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        fake.gone = True
        self.assertEqual(herdr.collect_run(str(self.cwd), out["run_id"], 0, runner=fake)["status"], "execution_failed")
        self.assertTrue(co.load(out["coordination_key"])["active"])
        co.resolve(out["coordination_key"], "worker stopped; partial effects inspected")
        self.assertEqual(co.inspect()["active"], 0)

    def test_v51_crash_before_receipt_does_not_launch(self):
        co.reserve(self.task(), herdr.BACKEND, herdr.project_binding(runner=FakeProjects()))
        fake = FakeProjects()
        self.assertEqual(self.run_(fake)["status"], "conflict")
        self.assertEqual(fake.calls, [["version"]])  # binding only; nothing added

    def test_v52_same_key_lock_and_parent_workspace_exclusion(self):
        with co.operation(co.key_for(self.task())):
            self.assertEqual(self.run_(FakeProjects())["status"], "conflict")
        self.run_(FakeProjects(after_status="working"))
        child = self.cwd / "child"
        child.mkdir()
        fake = FakeProjects()
        self.assertEqual(self.run_(fake, self.task(cwd=str(child)))["status"], "conflict")
        self.assertEqual(fake.adds, [])  # binding check only

    def test_v53_cli_status_and_release_require_confirmation(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(cli.main(["coordination", "status"]), 0)
        self.assertEqual(json.loads(output.getvalue())["active"], 0)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["coordination", "release", "--key", "0" * 64, "--note", "inspect"]), 2)

    def test_v54_concurrent_admission_is_bounded(self):
        tasks = []
        for i in range(8):
            cwd = self.base / f"independent-{i}"
            cwd.mkdir()
            tasks.append(self.task(cwd=str(cwd)))
        def admit(t):
            try:
                co.reserve(t, "projects", {})
                return True
            except co.Conflict:
                return False
        with ThreadPoolExecutor(8) as pool:
            self.assertEqual(sum(pool.map(admit, tasks)), 4)
        self.assertEqual(co.inspect()["active"], 4)

    def test_v55_identity_and_stale_state_fail_closed(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        write_result()(fake, fake.prompts[0])
        fake.status = "idle"
        for rows, details in (({"title": "br-other"}, {}), ({"id": "repo/9"}, {}), ({}, {"agent": "other"}),
                              ({}, {"worktree": None}), ({}, {"task": {"id": "repo/9"}})):
            fake.updates, fake.detail_updates = rows, details
            self.assertEqual(herdr.collect_run(str(self.cwd), out["run_id"], 0, runner=fake)["status"], "delivery_uncertain")
            self.assertTrue(co.load(out["coordination_key"])["active"])
        fake.updates, fake.detail_updates = {}, {}
        self.assertEqual(herdr.collect_run(str(self.cwd), out["run_id"], 0, runner=fake)["status"], "completed")

    def test_v57_collect_uses_recorded_session(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        with self.assertRaises(r.InputError):
            herdr.collect_run(str(self.cwd), out["run_id"], 0, "other-session", runner=fake)
        fake.status = "idle"
        write_result()(fake, fake.prompts[0])
        self.assertEqual(herdr.collect_run(str(self.cwd), out["run_id"], 0, runner=fake)["status"], "completed")

    def test_v58_pending_brief_cannot_complete_from_a_report(self):
        fake = FakeProjects(on_prompt=write_result())
        fake.updates = {"stage": "queued", "state": "working"}
        out = self.run_(fake)
        self.assertEqual(out["status"], "timed_out")
        self.assertIsNone(out["result_path"])
        fake.updates = {}
        self.assertEqual(herdr.collect_run(str(self.cwd), out["run_id"], 0, runner=fake)["status"], "completed")

    def test_v59_cli_route_and_collect_use_projects(self):
        task_file = self.base / "task.json"
        task_file.write_text(json.dumps({"schema_version": "1.0", **self.task()}), "utf-8")
        fake = FakeProjects(on_prompt=write_result(), profiles={"review": self.cfg["profile"][0]})
        call = herdr.project_call
        with patch.object(cli, "_config", return_value=(self.cfg, MAPPING)), \
             patch.object(r, "load_snapshot", return_value=(None, [])), \
             patch.object(herdr, "project_call", side_effect=lambda argv, runner=None, raw=False, **kw: call(argv, fake, raw, **kw)):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(cli.main(["route", "--task", str(task_file)]), 0, output.getvalue())
            run = json.loads(output.getvalue())
            self.assertEqual(run["thread_id"], "repo/1")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["collect", "--cwd", str(self.cwd), "--run-id", run["run_id"]]), 0)


if __name__ == "__main__":
    unittest.main()
