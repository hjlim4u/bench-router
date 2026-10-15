"""P3 병렬 위임 V30–V34: worktree 격리, fanout, shared scratchpad, deliberate 투표, 재실행 멱등.
herdr는 workspace마다 test_p2.FakeProjects를 하나씩 두는 멀티 agent fake. 실행: python3 -m unittest -v test_p3"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path

from bench_router import parallel as pl
from bench_router import routing as r
from test_p0 import MAPPING, config, profile
from test_p2 import FakeProjects, which, write_result, projects_environment, cleanup_temp


class MultiProjects:
    def __init__(self, on_prompt):
        self.on_prompt, self.lock = on_prompt, threading.Lock()
        self.threads, self.starts, self.prompts, self.ws_cwds = {}, [], [], []
        self.profiles = {}

    def __call__(self, cmd, **kw):
        argv = cmd[3:]
        if argv == ["--version"]:
            return subprocess.CompletedProcess(cmd, 0, "herdr-projects 0.2.34+test", "")
        if argv[:2] == ["profile", "resolve"]:
            p = self.profiles[argv[2]]
            return subprocess.CompletedProcess(cmd, 0, json.dumps({"name": p["id"], "agent": p["kind"], "args": p["args"]}), "")
        with self.lock:
            if argv[:2] == ["thread", "start"]:
                tid = f"t-{len(self.threads) + 1:04}"
                fake = FakeProjects(on_prompt=self.on_prompt, profiles=self.profiles, pane=f"w{len(self.threads) + 1}:p1")
                self.threads[tid] = fake
                fake.updates["id"] = tid
                self.starts.append(argv)
                self.ws_cwds.append(argv[argv.index("--repo") + 1])
            else:
                fake = self.threads[argv[3]]
                tid = argv[3]
        out = fake(cmd, **kw)
        if argv[:2] == ["thread", "start"]:
            self.prompts.extend(fake.prompts)
            obj = json.loads(out.stdout)
            obj["id"] = tid
            out.stdout = json.dumps(obj)
        return out


def agent_act(vote="t1-1"):
    result = write_result()

    def act(fake, prompt):
        result(fake, prompt)
        m = re.search(r"(\S+\.vote\.json) 에", prompt)
        if m:
            Path(m.group(1)).write_text(json.dumps({"best": vote, "reason": "r"}), "utf-8")
    return act


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
        grant = ["--add-dir", str(Path(self.cwd) / ".bench-router/groups")]
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["-m", "a", *grant]),
                           profile("b", args=["-m", "b", *grant])], default="a")

    def tearDown(self):
        subprocess.run(["git", "-C", self.cwd, "worktree", "prune"], capture_output=True)
        cleanup_temp(self.tmp)

    def group(self, **kw):
        task = {"schema_version": "1.0", "round": 1, "summary": "s", "prompt": "do it",
                "categories": {"general": 1}, "category_confidence": 0.9}
        raw = {"schema_version": "1.0", "group_id": "g1", "cwd": self.cwd,
               "tasks": [{**task, "task_id": "t1"}, {**task, "task_id": "t2"}]}
        raw.update(kw)
        return pl.validate_group(raw)

    def run_(self, g, fake):
        fake.profiles = {p["id"]: p for p in self.cfg["profile"]}
        return pl.run_group(g, self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=which)

    def test_v40_group_v2_orchestrator_selections(self):
        task = {"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "do it",
                "categories": {"general": 1}, "category_confidence": 0.9}
        context = {"schema_version": "2.0", "profiles": {p: {"metrics": {
            "cost.estimated_usd": {"value": 0.01, "unit": "usd", "source": "quote@1"}}} for p in ("a", "b")}}
        # Orchestrator는 group 수준 task(cwd=group.cwd)로 evaluate해서 digest를 얻는다
        digest = r.evaluate(r.validate_task({**task, "cwd": self.cwd}), self.cfg, MAPPING, None, [],
                            pl.datetime.now(pl.timezone.utc), context=context)["assessment_digest"]
        sel = lambda pid: {"schema_version": "2.0", "profile": pid, "assessment_digest": digest,
                           "policy": {"id": "orch-diverse", "version": "1"}, "reason": f"{pid} for diversity"}
        raw = {"schema_version": "2.0", "group_id": "g2", "cwd": self.cwd, "isolation": "deliberate",
               "tasks": [{"task": task, "context": context, "selections": [sel("b"), sel("a")]}]}
        fake = MultiProjects(agent_act())
        out = self.run_(pl.validate_group(raw), fake)
        self.assertEqual((out["status"], out["schema_version"], out["fanout"]), ("completed", "2.0", 2), out)
        self.assertEqual([m["profile"] for m in out["members"]], ["b", "a"])  # router 순위가 아닌 Orchestrator 선택
        self.assertIn("estimate_round1_only", [w["code"] for w in out["warnings"]])
        decision = json.loads((Path(out["members"][0]["rounds"][0]["receipt_path"]).parent / "decision.json")
                              .read_text("utf-8"))
        self.assertEqual((decision["selection"]["reason"], decision["decision_context"]["profiles"]["b"]["metrics"]
                          ["cost.estimated_usd"]["value"]), ("b for diversity", 0.01))
        # 평가 후 설정 변경 → 그룹 전체 실행 안 함
        self.cfg = config([*self.cfg["profile"], profile("c")], default="a")
        stale_fake = MultiProjects(agent_act())
        stale = self.run_(pl.validate_group({**raw, "group_id": "g3"}), stale_fake)
        self.assertEqual((stale["status"], stale_fake.prompts), ("stale_assessment", []))
        for bad in ({**raw, "fanout": 2},
                    {**raw, "tasks": [{"task": task, "selections": [sel("a"), sel("a")]}]},
                    {**raw, "tasks": [{"task": task, "selections": []}]}):
            with self.subTest(bad=bad), self.assertRaises(r.InputError):
                pl.validate_group(bad)

    def test_v30_isolated_worktrees(self):
        fake = MultiProjects(agent_act())
        out = self.run_(self.group(), fake)
        self.assertEqual(out["status"], "completed", out)
        wts = sorted(m["worktree"] for m in out["members"])
        self.assertEqual(sorted(fake.ws_cwds), wts)  # 각 agent cwd = 자기 worktree
        self.assertTrue(all(Path(w, "a.txt").exists() for w in wts))
        self.assertFalse(any("--add-dir" in s for s in fake.starts))
        self.assertNotIn("공용 scratchpad", fake.prompts[0])
        self.assertEqual(subprocess.run(["git", "-C", self.cwd, "status", "--porcelain"], capture_output=True,
                                        text=True).stdout, "")  # .bench-router는 exclude

    def test_v31_fanout_distinct_profiles(self):
        one = [{"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "p"}]
        out = self.run_(self.group(fanout=2, tasks=one), MultiProjects(agent_act()))
        self.assertEqual(out["status"], "completed", out)
        self.assertEqual(sorted(m["profile"] for m in out["members"]), ["a", "b"])
        g = self.group(fanout=3)
        out = pl.run_group(g, self.cfg, MAPPING, None, [], dry_run=True)
        self.assertEqual(len(out["members"]), 4)
        self.assertIn("fanout_reduced", [w["code"] for w in out["warnings"]])

    def test_v32_shared_scratchpad(self):
        fake = MultiProjects(agent_act())
        out = self.run_(self.group(isolation="shared"), fake)
        self.assertEqual(out["status"], "completed", out)
        shared = out["shared_dir"]
        self.assertTrue(all("--add-dir" not in s for s in fake.starts))
        self.assertTrue(all(Path(shared).is_relative_to(Path(p["args"][-1])) for p in self.cfg["profile"]))
        self.assertTrue(any(f"{shared}/t1-1.md" in p for p in fake.prompts))

    def test_v33_deliberate_round_and_vote(self):
        fake = MultiProjects(agent_act(vote="t2-1"))
        out = self.run_(self.group(isolation="deliberate"), fake)
        self.assertEqual(out["status"], "completed", out)
        self.assertEqual([len(m["rounds"]) for m in out["members"]], [2, 2])
        self.assertEqual(out["members"][0]["rounds"][1]["round"], 2)
        self.assertTrue(Path(out["shared_dir"], "t1-1.result.md").exists())
        self.assertEqual(out["consensus"], {"votes": {"t1-1": 0, "t2-1": 2}, "winner": "t2-1"})

    def test_v34_rerun_does_not_resend(self):
        g = self.group(isolation="shared")
        fake = MultiProjects(agent_act())
        self.run_(g, fake)
        sent = len(fake.prompts)
        out = self.run_(g, fake)
        self.assertEqual(out["status"], "completed", out)
        self.assertEqual(len(fake.prompts), sent)

    def test_v61_shared_access_must_be_preconfigured(self):
        for p in self.cfg["profile"]:
            p["args"] = []
        fake = MultiProjects(agent_act())
        with self.assertRaises(r.InputError):
            self.run_(self.group(isolation="shared"), fake)
        self.assertEqual(fake.starts, [])

    def test_group_validation(self):
        for bad in ({"isolation": "open"}, {"fanout": 0},
                    {"tasks": [{"schema_version": "1.0", "task_id": "x", "round": 1, "summary": "s", "prompt": "p",
                                "cwd": self.cwd}]}):
            with self.assertRaises(r.InputError):
                self.group(**bad)
        t = {"schema_version": "1.0", "task_id": "x", "round": 1, "summary": "s", "prompt": "p"}
        with self.assertRaises(r.InputError):
            self.group(tasks=[t, t])


if __name__ == "__main__":
    unittest.main()
