"""P2 검증 V19–V29 (06 문서). herdr는 0.9.3 실측 응답 형식을 따르는 fake.
실행: python3 -m unittest -v test_p2"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from bench_router import herdr as hd
from bench_router import routing as r
from test_p0 import MAPPING, config, profile


def which(name):
    return f"/usr/bin/{name}"


REAL_SLEEP = __import__("time").sleep


def cleanup_temp(tmp):
    for attempt in range(5):
        try:
            tmp.cleanup()
            return
        except OSError as e:
            if getattr(e, "winerror", None) != 145 or attempt == 4:
                raise
            REAL_SLEEP(0.05)


def projects_environment(case, base):
    home = Path(base) / "home"
    project = home / "projects/test"
    (project / ".state").mkdir(parents=True)
    (project / "PROJECT.md").write_text("+++\nname = 'test'\n+++\n", "utf-8")
    (project / ".state/coordinator.json").write_text(json.dumps({"socket": "/test.sock", "session": "brtest"}), "utf-8")
    cfg = home / ".config/herdr-projects"
    cfg.mkdir(parents=True)
    (cfg / "config.toml").write_text("[safety.default]\nyolo = false\nthread_agent_args = []\n", "utf-8")
    case.enterContext(patch.dict(os.environ, {"HOME": str(home), "BENCH_ROUTER_PROJECT_DIR": str(project),
                                            "BENCH_ROUTER_HERDR_SESSION": "brtest",
                                            "BENCH_ROUTER_COORDINATION_DIR": str(Path(base) / "admission")}))
    # No real waiting in offline state-transition tests.
    import itertools
    from types import SimpleNamespace
    ticks = itertools.count()
    case.enterContext(patch.object(hd, "time", SimpleNamespace(monotonic=lambda: next(ticks), sleep=lambda _: None)))
    return project


class FakeProjects:
    """Stock Projects JSON shapes; no invented server endpoints."""

    def __init__(self, start_error=None, pre_prompt_status="idle", prompt_error=None, after_status="idle",
                 on_prompt=None, pane="w7:p3", profiles=None):
        self.calls, self.prompts, self.kwargs = [], [], []
        self.start_error, self.pre_prompt_status = start_error, pre_prompt_status
        self.prompt_error, self.after_status, self.on_prompt = prompt_error, after_status, on_prompt
        self.pane, self.status, self.gone = pane, after_status, False
        self.profiles = profiles or {"a": profile("a", kind="claude", executable="claude",
                                               args=["--model", "m", "--effort", "high"]), "b": profile("b")}
        self.cwd, self.selected, self.updates, self.show_error = None, None, {}, False

    def _ok(self, obj):
        return subprocess.CompletedProcess([], 0, json.dumps(obj), "")

    def __call__(self, cmd, **kw):
        assert cmd[0] == hd.PROJECTS_BIN and kw["shell"] is False and cmd[1] == "--root"
        self.kwargs.append(kw)
        argv = cmd[3:]
        self.calls.append(argv[:2])
        if argv == ["--version"]:
            return subprocess.CompletedProcess(cmd, 0, getattr(self, "version", "herdr-projects 0.2.34+test"), "")
        if argv[:2] == ["profile", "resolve"]:
            if self.start_error:
                return subprocess.CompletedProcess(cmd, 1, "", self.start_error)
            p = self.profiles[argv[2]]
            return self._ok({"name": p["id"], "agent": p["kind"], "args": p["args"]})
        if argv[:2] == ["thread", "start"]:
            self.selected = argv[argv.index("--profile") + 1]
            self.cwd = argv[argv.index("--repo") + 1]
            prompt = Path(argv[argv.index("--task-file") + 1]).read_text("utf-8")
            self.prompts.append(prompt)
            if self.on_prompt and self.pre_prompt_status == "idle":
                self.on_prompt(self, prompt)
            if self.prompt_error:
                raise subprocess.TimeoutExpired(cmd, 15)
            return self._ok({"id": "t-0001", "kind": "checkout", "profile": self.selected,
                             "agent": self.profiles[self.selected]["kind"], "branch": "", "pane_id": self.pane})
        if argv[:2] == ["thread", "read"]:
            return subprocess.CompletedProcess(cmd, 0, "approval or question: command not found", "")
        if argv[:2] == ["thread", "show"]:
            if self.show_error:
                raise subprocess.TimeoutExpired(cmd, 15)
            return self._ok({"id": "t-0001", "kind": "checkout", "profile": self.selected,
                             "agent": self.profiles[self.selected]["kind"], "cwd": self.cwd, "machine": "",
                             "workspace_id": "w7", "pane_id": self.pane,
                             "status": "failed" if self.gone else "open",
                             "note": "no agent" if self.gone else self.status,
                             "group_token": "waiting-on-you" if self.status == "blocked" else "idle",
                             "prompt_pending": self.pre_prompt_status != "idle", **self.updates})
        raise AssertionError(argv)


def write_result(status="success", nonce=None, body="# 결과\n작업 완료\n", sha=None, run_id=None):
    def act(fake, prompt):
        rd = Path(re.search(r"결과 디렉터리\(절대 경로\): (.+)", prompt).group(1))
        m = {"schema_version": "1.0", "run_id": run_id or re.search(r"실행 식별자: (\S+)", prompt).group(1),
             "nonce": nonce or re.search(r"검증 토큰: (\S+)", prompt).group(1),
             "profile_fingerprint": re.search(r"프로필 지문: (\S+)", prompt).group(1), "status": status,
             "result_file": "result.md", "checks": [{"command": "true", "outcome": "passed", "notes": ""}]}
        (rd / "result.md").write_bytes(body.encode("utf-8"))
        m["result_sha256"] = sha or hashlib.sha256(body.encode()).hexdigest()
        (rd / "result.json").write_text(json.dumps(m), "utf-8")
    return act


class P2(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        state = tempfile.TemporaryDirectory()
        self.addCleanup(cleanup_temp, state)
        env = patch.dict(os.environ, {"BENCH_ROUTER_COORDINATION_DIR": state.name})
        env.start()
        self.addCleanup(env.stop)
        projects_environment(self, state.name)
        self.cwd = os.path.realpath(self.tmp.name)
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["--model", "m", "--effort", "high"])],
                          default="a")

    def tearDown(self):
        cleanup_temp(self.tmp)

    def task(self, **kw):
        raw = {"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "do the thing",
               "cwd": self.cwd, "categories": {"general": 1}, "category_confidence": 0.9,
               "constraints": {"timeout_ms": 5000}}
        raw.update(kw)
        return r.validate_task(raw)

    def run_(self, fake, t=None, w=which):
        fake.profiles = {p["id"]: p for p in self.cfg["profile"]}
        return hd.dispatch(t or self.task(), self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=w)

    def receipt(self, out):
        return json.loads(Path(out["receipt_path"]).read_text("utf-8"))

    def test_v35_pinned_profile_replay_and_retry_guidance(self):
        self.cfg = config([*self.cfg["profile"], profile("b", kind="claude", executable="claude")], default="a")
        fake = FakeProjects(on_prompt=write_result())
        context = {"schema_version": "1.0", "profiles": {"a": {
            "estimated_input_tokens": 1000, "estimated_output_tokens": 1000,
            "price": {"input_usd_per_million_tokens": 1, "output_usd_per_million_tokens": 2,
                      "source": "test", "as_of": "2026-10-13T00:00:00+00:00"}}}}
        first = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], runner=fake, which=which,
                            profile_id="a", context=context, selection_mode="orchestrator_pinned")
        self.assertEqual((first["status"], first["selection_mode"], first["reassignment"]),
                         ("completed", "orchestrator_pinned", "review_result"))
        self.assertEqual((first["selection"], first["warnings"][-1]["code"]),
                         ({"source": "unrecorded"}, "selection_unrecorded"))
        repriced = {**context, "profiles": {"a": {**context["profiles"]["a"],
                    "price": {**context["profiles"]["a"]["price"], "output_usd_per_million_tokens": 4}}}}
        replay = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], runner=fake, which=which,
                             profile_id="a", context=repriced, selection_mode="orchestrator_pinned")
        self.assertEqual(replay["context_hash"], first["context_hash"])
        self.assertEqual(replay["candidates"][0]["context_facts"]["estimated_cost_usd"], 0.003)
        conflict = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], runner=fake, which=which,
                               profile_id="b", selection_mode="orchestrator_pinned")
        self.assertEqual((conflict["status"], len(fake.prompts)), ("conflict", 1))
        self.assertEqual(conflict["warnings"][-1]["code"], "profile_round_conflict")

    def test_v39_selection_record_digest_and_round_reuse(self):
        fake = FakeProjects(on_prompt=write_result())
        context = {"schema_version": "2.0", "profiles": {"a": {"metrics": {
            "cost.estimated_usd": {"value": 0.01, "unit": "usd", "source": "quote@1"}}}}}
        digest = r.evaluate(self.task(), self.cfg, MAPPING, None, [], hd._now(), context=context)["assessment_digest"]
        sel = r.validate_selection({"schema_version": "2.0", "profile": "a", "assessment_digest": digest,
                                    "policy": {"id": "orch-cheapest", "version": "4"}, "reason": "lowest quote"})
        go = lambda t, s, cfg=None: hd.dispatch(t, cfg or self.cfg, MAPPING, None, [], runner=fake, which=which,
                                                context=context, selection=s, selection_mode="orchestrator_pinned")
        first = go(self.task(), sel)
        self.assertEqual((first["status"], first["selection"]["policy"]["id"]), ("completed", "orch-cheapest"))
        self.assertNotIn("assessment", first)
        decision = json.loads((Path(first["receipt_path"]).parent / "decision.json").read_text("utf-8"))
        self.assertEqual((decision["selection"], decision["assessment"]["assessment_digest"]),
                         (first["selection"], digest))
        self.assertTrue(all(x["passed"] for x in decision["assessment"]["candidates"][0]["constraints"]))
        # 같은 round: 다른 선택 근거여도 최초 실행 회수, 재전송 없음
        again = go(self.task(), {**sel, "reason": "changed my mind"})
        self.assertEqual((again["reused_receipt"], len(fake.prompts)), (True, 1))
        self.assertEqual(again["warnings"][-1]["code"], "selection_differs_from_recorded")
        # 평가 후 설정 변경: 새 round라도 옛 digest로는 실행 안 함
        changed = config([*self.cfg["profile"], profile("b", kind="claude", executable="claude")], default="a")
        stale = go(self.task(round=2), sel, changed)
        self.assertEqual((stale["status"], stale["selected"], len(fake.prompts)), ("stale_assessment", None, 1))
        self.assertNotEqual(stale["assessment_digest"], digest)
        for bad in ({**sel, "assessment_digest": "x"}, {**sel, "policy": {"id": "p"}}, {k: sel[k] for k in sel if k != "reason"}):
            with self.subTest(bad=bad), self.assertRaises(r.InputError):
                r.validate_selection(bad)

    def test_v19_prompt_is_argv_not_shell(self):
        evil = "x $(touch /tmp/pwned) `id`; rm -rf ~\n\"quoted\" 'single' \\ & | > <"
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(fake, self.task(prompt=evil))
        self.assertEqual(out["status"], "completed")
        self.assertTrue(fake.prompts[0].startswith(evil))
        self.assertFalse(Path("/tmp/pwned").exists())
        self.assertTrue(all(k["shell"] is False for k in fake.kwargs))

    def test_v20_uses_returned_ids(self):
        fake = FakeProjects(on_prompt=write_result(), pane="w42:p9")
        out = self.run_(fake)
        self.assertEqual((out["workspace_id"], out["thread_id"]), ("w7", "t-0001"))
        self.assertEqual(self.receipt(out)["pane_id"], "w42:p9")
        self.assertNotIn(["agent", "start"], fake.calls)

    def test_v21_start_failures_send_nothing(self):
        fake = FakeProjects(start_error="profile unavailable")
        out = self.run_(fake)
        self.assertEqual((out["status"], out["delivery_state"], fake.prompts), ("execution_failed", "not_attempted", []))
        missing = self.run_(FakeProjects(), self.task(task_id="missing"), w=lambda _: None)
        self.assertEqual(missing["excluded"], [{"profile": "a", "reasons": ["executable_not_found"]}])

    def test_projects_profile_identity_must_match(self):
        fake = FakeProjects(on_prompt=write_result())
        fake.profiles["a"] = profile("a")
        out = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], runner=fake, which=which)
        self.assertEqual((out["status"], fake.prompts), ("execution_failed", []))

    def test_v22_not_idle_before_prompt(self):
        fake = FakeProjects(pre_prompt_status="starting")
        fake.updates = {"status": "starting", "note": "no agent"}
        out = self.run_(fake)
        self.assertEqual((out["status"], out["delivery_state"]), ("timed_out", "submission_attempted"))
        self.assertIsNone(out["result_path"])
        fake.pre_prompt_status, fake.updates = "idle", {}
        write_result()(fake, fake.prompts[0])
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "completed")

    def test_v23_completed_with_contract(self):
        out = self.run_(FakeProjects(on_prompt=write_result(status="partial")))
        self.assertEqual((out["status"], out["task_outcome"], out["delivery_state"]),
                         ("completed", "partial", "activity_observed"))
        self.assertTrue(os.path.isabs(out["result_path"]) and Path(out["manifest_path"]).is_file())
        self.assertTrue(out["selected"]["profile_fingerprint"])

    def test_v24_settled_but_invalid_result(self):
        cases = {"missing": None, "old_run": write_result(run_id="00000000-0000-0000-0000-000000000000"),
                 "nonce": write_result(nonce="f" * 32), "hash": write_result(sha="0" * 64)}
        for i, (name, act) in enumerate(cases.items()):
            with self.subTest(name):
                out = self.run_(FakeProjects(on_prompt=act), self.task(task_id=f"t{i}"))
                self.assertEqual(out["status"], "result_invalid")
                self.assertIsNone(out["result_path"])

    def test_v25_path_and_size_attacks(self):
        def huge(fake, prompt):
            write_result()(fake, prompt)
            rd = Path(re.search(r"결과 디렉터리\(절대 경로\): (.+)", prompt).group(1))
            (rd / "result.json").write_bytes(b" " * (hd.RESULT_JSON_MAX + 1))
        for i, act in enumerate((huge, write_result(body="  \n"))):
            self.assertEqual(self.run_(FakeProjects(on_prompt=act), self.task(task_id=f"p{i}"))["status"], "result_invalid")
        outside = Path(self.cwd) / "secret.md"
        outside.write_text("secret", "utf-8")
        def symlinked(fake, prompt):
            write_result()(fake, prompt)
            rd = Path(re.search(r"결과 디렉터리\(절대 경로\): (.+)", prompt).group(1))
            (rd / "result.md").unlink()
            (rd / "result.md").symlink_to(outside)
        if os.name == "nt":
            original = Path.is_symlink
            with patch.object(Path, "is_symlink", lambda p: p.name == "result.md" or original(p)):
                out = self.run_(FakeProjects(on_prompt=write_result()), self.task(task_id="link"))
        else:
            out = self.run_(FakeProjects(on_prompt=symlinked), self.task(task_id="link"))
        self.assertEqual(out["status"], "result_invalid")

    def test_v26_timeout_no_resend_then_collect(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        self.assertEqual(out["status"], "timed_out")
        self.assertTrue(all(0 < kw["timeout"] <= 5 for kw in fake.kwargs))
        again = self.run_(fake)
        self.assertEqual((len(fake.prompts), again["reused_receipt"], again["run_id"]), (1, True, out["run_id"]))
        write_result()(fake, fake.prompts[0])
        fake.status = "idle"
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "completed")

    def test_v27_crash_after_submission_attempted(self):
        class Crash(Exception):
            pass

        fake = FakeProjects()

        def crash(f, prompt):
            raise Crash()
        fake.on_prompt = crash
        with self.assertRaises(Crash):
            self.run_(fake)
        rc = hd.receipts(self.cwd)[0]
        self.assertEqual((rc["status"], rc["delivery_state"]), ("dispatching", "submission_attempted"))
        fake.on_prompt, fake.status = None, "idle"
        out = self.run_(fake)  # 재실행: 재전송 없이 collect
        self.assertEqual((len(fake.prompts), out["status"], out["reused_receipt"]), (1, "delivery_uncertain", True))

    def test_v28_conflicts_and_locks(self):
        fake = FakeProjects(on_prompt=write_result())
        first = self.run_(fake)
        self.assertEqual(self.run_(fake)["status"], "completed")  # 같은 hash: 기록 재사용
        self.assertEqual(len(fake.prompts), 1)
        self.assertEqual(self.run_(fake, self.task(prompt="different"))["status"], "conflict")
        with hd.dispatch_lock(self.cwd):
            self.assertEqual(self.run_(fake, self.task(task_id="t2"))["status"], "conflict")
            child = subprocess.run([sys.executable, "-c",
                                    "import sys\nfrom bench_router import herdr as h\n"
                                    "try:\n with h.dispatch_lock(sys.argv[1]): print('acquired')\n"
                                    "except h.Busy: print('busy')",
                                    self.cwd], capture_output=True, text=True, check=True)
            self.assertEqual(child.stdout.strip(), "busy")
        stuck = FakeProjects(after_status="working")
        self.run_(stuck, self.task(task_id="t3"))
        blocked = self.run_(fake, self.task(task_id="t4"))
        self.assertEqual(blocked["status"], "conflict")
        self.assertEqual(blocked["warnings"][-1]["code"], "coordination")
        self.assertEqual(first["status"], "completed")

    def test_v29_agent_gone_or_partial(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        write_result()(fake, fake.prompts[0])
        fake.gone = True  # Agent 종료: 파일만으로 성공 선언 금지
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "execution_failed")
        fb = hd.feedback(self.cwd, out["run_id"], "fail", "orchestrator", "agent exited")
        self.assertEqual((fb["status"], fb["receipt_status"]), ("recorded", "execution_failed"))
        from bench_router import coordination
        coordination.resolve(out["coordination_key"], "worker gone; partial effects inspected")
        out = self.run_(FakeProjects(on_prompt=write_result(status="fail")), self.task(task_id="t9"))
        self.assertEqual((out["status"], out["task_outcome"]), ("completed", "fail"))  # 수신 성공 ≠ 작업 성공

    def test_blocked_after_prompt_returns_screen(self):
        out = self.run_(FakeProjects(after_status="blocked"))  # live smoke: mv 권한 승인 대기
        self.assertEqual((out["status"], out["delivery_state"]), ("blocked", "activity_observed"))
        self.assertIn("command not found", out["diagnostic_tail"])
        self.assertNotIn("원자적", hd.contract_text(hd.load_receipt(self.cwd, out["run_id"])))

    def test_v60_version_drift_blocks_submission(self):
        fake = FakeProjects(on_prompt=write_result())
        fake.version = "herdr-projects 0.2.35+new"
        out = self.run_(fake)
        self.assertEqual((out["status"], out["delivery_state"], fake.prompts), ("execution_failed", "not_attempted", []))

    def test_prompt_size_limit(self):
        with self.assertRaises(r.InputError):
            self.run_(FakeProjects(), self.task(prompt="x" * hd.MAX_PROMPT_ARG_BYTES))


if __name__ == "__main__":
    unittest.main()
