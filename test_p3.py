"""P3 병렬 위임 V30–V34: worktree 격리, fanout, shared scratchpad, 재실행 멱등.
herdr-projects는 member마다 board task를 만드는 test_p2.FakeProjects. 실행: python3 -m unittest -v test_p3"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from bench_router import parallel as pl
from bench_router import routing as r
from test_p0 import MAPPING, config, profile, guided_reply, guided_responses, NOW
from test_p2 import FakeProjects, which, write_result, projects_environment, cleanup_temp


@unittest.skipUnless(shutil.which("git"), "git required")
class P3(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        state = tempfile.TemporaryDirectory()
        self.addCleanup(state.cleanup)
        env = patch.dict(os.environ, {"BENCH_ROUTER_COORDINATION_DIR": state.name})
        env.start()
        self.addCleanup(env.stop)
        projects_environment(self, state.name)
        self.cwd = os.path.realpath(self.tmp.name)
        git = ["git", "-C", self.cwd, "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git[:3] + ["init", "-q"], check=True)
        Path(self.cwd, "a.txt").write_text("a\n", "utf-8")
        subprocess.run(git + ["add", "a.txt"], check=True)
        subprocess.run(git + ["commit", "-qm", "init"], check=True)
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["-m", "a"]),
                           profile("b", args=["-m", "b"])])

    def tearDown(self):
        subprocess.run(["git", "-C", self.cwd, "worktree", "prune"], capture_output=True)
        cleanup_temp(self.tmp)

    def group(self, **kw):
        task = {"schema_version": "1.0", "round": 1, "summary": "s", "prompt": "do it"}
        raw = {"schema_version": "1.0", "group_id": "g1", "cwd": self.cwd,
               "tasks": [{**task, "task_id": "t1"}, {**task, "task_id": "t2"}]}
        raw.update(kw)
        return pl.validate_group(raw)

    def group2(self, fanout=1, tasks=None, profiles=("a", "b"), **kw):
        """2.0 group: each task carries one frozen selection per fanout slot, taken in `profiles` order."""
        base = {"schema_version": "1.0", "round": 1, "summary": "s", "prompt": "do it"}
        now, entries = pl.datetime.now(pl.timezone.utc), []
        for t in tasks or [{**base, "task_id": "t1"}, {**base, "task_id": "t2"}]:
            digest = r.evaluate(r.validate_task({**t, "cwd": self.cwd}), self.cfg, MAPPING, None, [], now)["assessment_digest"]
            entries.append({"task": t, "selections": [{
                "schema_version": "2.0", "profile": pid, "assessment_digest": digest,
                "policy": {"id": "test", "version": "1"}, "reason": "test"} for pid in profiles[:fanout]]})
        return pl.validate_group({"schema_version": "2.0", "group_id": "g1", "cwd": self.cwd, **kw, "tasks": entries})

    def run_(self, g, fake, **kw):
        fake.profiles = {p["id"]: p for p in self.cfg["profile"]}
        return pl.run_group(g, self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=which, **kw)

    def test_max_parallel_cannot_exceed_admission_limit(self):
        with self.assertRaises(r.InputError):
            self.group(max_parallel=5)
        self.assertEqual(self.group(max_parallel=4)["max_parallel"], 4)

    def test_v77_guided_fanout_preflight_and_frozen_recovery(self):
        from bench_router import decision
        g = self.group(fanout=2, tasks=[{"schema_version": "1.0", "task_id": "t1", "round": 1,
                                       "summary": "Fix typo", "prompt": "Fix a typo"}])
        opts = {"host": "codex", "env": {}}
        fake = FakeProjects(on_prompt=write_result())
        fake.profiles = {p["id"]: p for p in self.cfg["profile"]}
        first = pl.run_group(g, self.cfg, MAPPING, None, [], dry_run=True, decision_options=opts)
        self.assertEqual(first["status"], "decision_required")
        self.assertFalse((Path(self.cwd) / ".bench-router").exists())
        responses, next_ = {}, first
        for _ in range(6):
            member = next(m for m in next_["members"] if m["status"] == "decision_required")
            packet = {"decision_request": member["decision"]["request"], "decision": member["decision"],
                      "assessment_digest": member["decision"]["request_digest"]}
            responses[member["label"]] = guided_reply(packet, "__tie__")
            next_ = pl.run_group(g, self.cfg, MAPPING, None, [], dry_run=True, decision_options=opts, responses=responses)
            if next_["status"] != "decision_required":
                break
        self.assertEqual(next_["status"], "decision_unavailable", next_)
        self.assertIn("upstream_selection_required", next_["members"][0]["decision"]["uncertainty"])
        self.assertFalse((Path(self.cwd) / ".bench-router").exists())
        assessment = decision.evaluate(g["tasks"][0], self.cfg, MAPPING, None, [], NOW,
                                       response=responses["t1-1"], **opts)
        selections = [decision.bind(assessment, pid, {"id": "team", "version": "1"}, "explicit fanout", True)
                      for pid in ("a", "b")]
        g = self.group(schema_version="2.0", tasks=[{"task": g["raw_tasks"][0], "selections": selections}])
        self.assertEqual(pl.run_group(g, self.cfg, MAPPING, None, [], dry_run=True,
                                     decision_options=opts)["status"], "selected")
        out = pl.run_group(g, self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=which,
                           decision_options=opts)
        self.assertEqual((out["status"], [m["profile"] for m in out["members"]]), ("completed", ["a", "b"]), out)
        with patch.object(decision, "load_guidelines", side_effect=AssertionError("must reuse frozen choices")):
            again = pl.run_group(g, self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=which,
                                 decision_options=opts)
        self.assertEqual((again["status"], len(fake.prompts)), ("completed", 2), again)

        # Upstream 4.0 selections may repeat the same profile.
        repeated = self.group(schema_version="2.0", group_id="repeat",
                              tasks=[{"task": g["raw_tasks"][0],
                                      "selections": [out["members"][0]["selection"]] * 2}])
        out = pl.run_group(repeated, self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=which,
                           decision_options=opts)
        self.assertEqual((out["status"], [m["profile"] for m in out["members"]]), ("completed", ["a", "a"]))
        for key in ("label", "worktree"):
            self.assertEqual(len({m[key] for m in out["members"]}), 2)
        self.assertEqual(len({m["rounds"][0]["run_id"] for m in out["members"]}), 2)
        again = pl.run_group(repeated, self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=which,
                             decision_options=opts)
        self.assertEqual((again["status"], len(fake.prompts)), ("completed", 4))

    def test_v99_group_external_selection_repeats_and_stale_preflight(self):
        from bench_router import decision
        task = {"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "do it"}
        t = r.validate_task({**task, "cwd": self.cwd})
        def evaluate(response=None):
            return decision.evaluate(t, self.cfg, MAPPING, None, [], NOW, host="codex", env={}, response=response)
        assessment = evaluate(guided_responses(evaluate(), evaluate, "__tie__"))
        selection = decision.bind(assessment, "b", {"id": "team", "version": "1"}, "repeat specialist", True)
        raw = {"schema_version": "2.0", "group_id": "external", "cwd": self.cwd,
               "tasks": [{"task": task, "selections": [selection, selection]}]}
        fake = FakeProjects(on_prompt=write_result(), profiles={p["id"]: p for p in self.cfg["profile"]})
        def run(raw, runner):
            return pl.run_group(pl.validate_group(raw), self.cfg, MAPPING, None, [], session="brtest",
                                runner=runner, which=which, decision_options={"host": "codex", "env": {}})
        out = run(raw, fake)
        self.assertEqual((out["status"], [m["profile"] for m in out["members"]]), ("completed", ["b", "b"]))
        self.assertEqual(len({m["rounds"][0]["run_id"] for m in out["members"]}), 2)
        self.assertEqual((run(raw, fake)["status"], len(fake.prompts)), ("completed", 2))
        self.cfg = config([*self.cfg["profile"], profile("c")])
        stale_fake = FakeProjects()
        self.assertEqual(run({**raw, "group_id": "stale-external"}, stale_fake)["status"], "stale_assessment")
        self.assertEqual(stale_fake.prompts, [])

    def test_v40_group_v2_orchestrator_selections(self):
        task = {"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "do it"}
        context = {"schema_version": "2.0", "profiles": {p: {"metrics": {
            "cost.estimated_usd": {"value": 0.01, "unit": "usd", "source": "quote@1"}}} for p in ("a", "b")}}
        # Orchestrator는 group 수준 task(cwd=group.cwd)로 evaluate해서 digest를 얻는다
        digest = r.evaluate(r.validate_task({**task, "cwd": self.cwd}), self.cfg, MAPPING, None, [],
                            pl.datetime.now(pl.timezone.utc), context=context)["assessment_digest"]
        sel = lambda pid: {"schema_version": "2.0", "profile": pid, "assessment_digest": digest,
                           "policy": {"id": "orch-diverse", "version": "1"}, "reason": f"{pid} for diversity"}
        raw = {"schema_version": "2.0", "group_id": "g2", "cwd": self.cwd, "isolation": "shared",
               "tasks": [{"task": task, "context": context, "selections": [sel("b"), sel("a"), sel("b")]}]}
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(pl.validate_group(raw), fake)
        self.assertEqual((out["status"], out["schema_version"], out["fanout"]), ("completed", "2.0", 3), out)
        self.assertEqual([m["profile"] for m in out["members"]], ["b", "a", "b"])  # ordered execution instances
        for key in ("label", "worktree"):
            self.assertEqual(len({m[key] for m in out["members"]}), 3)
        self.assertEqual(len({m["rounds"][0]["run_id"] for m in out["members"]}), 3)
        for member in out["members"]:
            self.assertEqual((member["rounds"][0]["delivery_state"], member["rounds"][0]["reassignment"]),
                             ("activity_observed", "review_result"))
        again = self.run_(pl.validate_group(raw), fake)
        self.assertEqual((again["status"], len(fake.prompts)), ("completed", 3))
        reordered = {**raw, "tasks": [{**raw["tasks"][0], "selections": [sel("a"), sel("b"), sel("b")]}]}
        self.assertEqual(self.run_(pl.validate_group(reordered), fake)["status"], "conflict")
        self.assertEqual(len(fake.prompts), 3)
        stale_member = {**raw, "group_id": "stale-member", "tasks": [{**raw["tasks"][0],
                        "selections": [sel("b"), {**sel("b"), "assessment_digest": "0" * 64}]}]}
        stale_fake = FakeProjects(on_prompt=write_result())
        stale = self.run_(pl.validate_group(stale_member), stale_fake)
        self.assertEqual((stale["status"], stale_fake.prompts), ("stale_assessment", []))
        decision = json.loads((Path(out["members"][0]["rounds"][0]["receipt_path"]).parent / "decision.json")
                              .read_text("utf-8"))
        self.assertEqual((decision["selection"]["reason"], decision["decision_context"]["profiles"]["b"]["metrics"]
                          ["cost.estimated_usd"]["value"]), ("b for diversity", 0.01))
        # 평가 후 설정 변경 → 그룹 전체 실행 안 함
        self.cfg = config([*self.cfg["profile"], profile("c")])
        stale_fake = FakeProjects(on_prompt=write_result())
        stale = self.run_(pl.validate_group({**raw, "group_id": "g3"}), stale_fake)
        self.assertEqual((stale["status"], stale_fake.prompts), ("stale_assessment", []))
        for bad in ({**raw, "fanout": 2},
                    {**raw, "tasks": [{"task": task, "selections": [sel("a")] * 9}]},
                    {**raw, "tasks": [{"task": task, "selections":
                                       [sel("a"), {**sel("a"), "assessment_digest": "bad"}]}]},
                    {**raw, "tasks": [{"task": task, "selections": []}]}):
            with self.subTest(bad=bad), self.assertRaises(r.InputError):
                pl.validate_group(bad)

    def test_v41_partial_failure_preserves_reassignment(self):
        self.cfg["profile"][1]["args"] = ["--add-dir", "/unsupported"]
        fake = FakeProjects(on_prompt=write_result())
        g = self.group2(fanout=2, tasks=[{"schema_version": "1.0", "task_id": "t1", "round": 1,
                                        "summary": "s", "prompt": "do it"}])
        out = self.run_(g, fake)
        self.assertEqual(out["status"], "partial_failure")
        self.assertEqual([(m["status"], m["rounds"][0]["delivery_state"], m["rounds"][0]["reassignment"])
                          for m in out["members"]],
                         [("completed", "activity_observed", "review_result"),
                          ("execution_failed", "not_attempted", "safe_to_retry")])
        again = self.run_(g, fake)
        self.assertEqual((again["status"], len(fake.prompts)), ("partial_failure", 1))

    def test_v30_isolated_worktrees(self):
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(self.group2(), fake)
        self.assertEqual(out["status"], "completed", out)
        routed = sorted(str(Path(self.cwd, ".bench-router/worktrees/g1", m["label"])) for m in out["members"])
        self.assertEqual(sorted(fake.ws_cwds), routed)  # 각 board task의 repo = 자기 router worktree
        wts = [m["worktree"] for m in out["members"]]  # 보고되는 worktree는 board가 만든 agent 작업 위치
        self.assertEqual(sorted(wts), sorted(t["worktree"] for t in fake.tasks.values()))
        self.assertTrue(all(Path(w, "a.txt").exists() for w in wts))
        self.assertNotIn("공용 scratchpad", fake.prompts[0])
        self.assertEqual(subprocess.run(["git", "-C", self.cwd, "status", "--porcelain"], capture_output=True,
                                        text=True).stdout, "")  # .bench-router는 exclude

    def test_v31_fanout_distinct_profiles(self):
        one = [{"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "p"}]
        out = self.run_(self.group2(fanout=2, tasks=one), FakeProjects(on_prompt=write_result()))
        self.assertEqual(out["status"], "completed", out)
        self.assertEqual(sorted(m["profile"] for m in out["members"]), ["a", "b"])

    def test_v32_shared_scratchpad(self):
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(self.group2(isolation="shared"), fake)
        self.assertEqual(out["status"], "completed", out)
        shared = out["shared_dir"]
        self.assertTrue(any(f"{shared}/t1-1.md" in p for p in fake.prompts))

    def test_v34_rerun_does_not_resend(self):
        g = self.group2(isolation="shared")
        fake = FakeProjects(on_prompt=write_result())
        self.run_(g, fake)
        sent = len(fake.prompts)
        out = self.run_(g, fake)
        self.assertEqual(out["status"], "completed", out)
        self.assertEqual(len(fake.prompts), sent)

    def test_wait_zero_starts_members_then_rerun_collects(self):
        g = self.group2(isolation="shared")
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(g, fake, wait_ms=0)  # every member submitted, nobody waited on
        self.assertEqual([m["rounds"][0]["status"] for m in out["members"]], ["timed_out", "timed_out"], out)
        self.assertEqual(out["status"], "partial_failure")
        for member in out["members"]:
            self.assertEqual((member["rounds"][0]["delivery_state"], member["rounds"][0]["reassignment"]),
                             ("submission_attempted", "collect_first"))
        again = self.run_(g, fake)
        self.assertEqual((again["status"], len(fake.prompts)), ("completed", 2), again)

    def test_group_validation(self):
        for bad in ({"isolation": "open"}, {"fanout": 0},
                    {"tasks": [{"schema_version": "1.0", "task_id": "x", "round": 1, "summary": "s", "prompt": "p",
                                "cwd": self.cwd}]}):
            with self.assertRaises(r.InputError):
                self.group(**bad)
        t = {"schema_version": "1.0", "task_id": "x", "round": 1, "summary": "s", "prompt": "p"}
        with self.assertRaises(r.InputError):
            self.group(tasks=[t, t])
        sel = {"schema_version": "2.0", "profile": "a", "assessment_digest": "0" * 64,
               "policy": {"id": "repeat", "version": "1"}, "reason": "repeat one profile"}
        entries = [{"task": {**t, "task_id": f"t{i}"}, "selections": [sel] * n}
                   for i, n in enumerate((8, 8, 1))]
        self.assertEqual(self.group(schema_version="2.0", tasks=entries[:2])["fanout"], 8)
        with self.assertRaisesRegex(r.InputError, "total agents"):
            self.group(schema_version="2.0", tasks=entries)


if __name__ == "__main__":
    unittest.main()
