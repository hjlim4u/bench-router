"""P2 검증 V19–V29 (06 문서). herdr는 0.9.3 실측 응답 형식을 따르는 fake. WSL/Linux에서 실행(fcntl).
실행: python3 -m unittest -v test_p2"""
import hashlib
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from bench_router import herdr as hd
from bench_router import routing as r
from test_p0 import MAPPING, config, profile


def which(name):
    return f"/usr/bin/{name}"


class FakeHerdr:
    """herdr CLI 흉내. on_prompt(fake, rc_text)로 Agent 동작(결과 파일 작성 등)을 주입한다."""

    def __init__(self, start_error=None, pre_prompt_status="idle", prompt_error=None, after_status="idle",
                 on_prompt=None, pane="w7:p3"):
        self.calls, self.prompts, self.kwargs = [], [], []
        self.start_error, self.pre_prompt_status = start_error, pre_prompt_status
        self.prompt_error, self.after_status, self.on_prompt = prompt_error, after_status, on_prompt
        self.pane, self.agent, self.status, self.gone = pane, None, None, False

    def _ok(self, result):
        return subprocess.CompletedProcess([], 0, json.dumps({"id": "cli", "result": result}), "")

    def _err(self, code):
        return subprocess.CompletedProcess([], 1, "", json.dumps({"error": {"code": code, "message": code}, "id": "cli"}))

    def info(self):
        return {"agent": {"name": self.agent, "pane_id": self.pane, "agent_status": self.status,
                          "workspace_id": "w7", "tab_id": "w7:t1", "terminal_id": "t", "focused": False, "revision": 1}}

    def __call__(self, cmd, **kw):
        assert cmd[0] == hd.HERDR_BIN and kw.get("shell") is False and isinstance(cmd, list)
        self.kwargs.append(kw)
        argv = cmd[1:]
        if argv[0] == "--session":
            argv = argv[2:]
        self.calls.append(argv[:2])
        group, verb = argv[0], argv[1]
        if (group, verb) == ("workspace", "create"):
            return self._ok({"type": "workspace_created", "workspace": {"workspace_id": "w7"},
                             "tab": {"tab_id": "w7:t1"}, "root_pane": {"pane_id": self.pane, "cwd": argv[3]}})
        if (group, verb) == ("pane", "read"):  # 0.9.3 실측: JSON이 아닌 터미널 텍스트
            return subprocess.CompletedProcess([], 0, "$ claude\nclaude: command not found\n", "")
        if group != "agent":
            raise AssertionError(argv)
        if verb == "start":
            if self.start_error:
                return self._err(self.start_error)
            self.agent, self.status = argv[2], self.pre_prompt_status
            return self._ok({"type": "agent_started", "argv": argv[argv.index("--") + 1:], **self.info()})
        if self.agent is None or self.gone or argv[2] != self.agent:
            return self._err("agent_not_found")
        if verb == "get":
            return self._ok({"type": "agent_info", **self.info()})
        if verb == "prompt":
            self.prompts.append(argv[3])
            if self.prompt_error:
                return self._err(self.prompt_error)
            if self.on_prompt:
                self.on_prompt(self, argv[3])
            self.status = self.after_status
            return self._ok({"type": "agent_prompted", **self.info()})
        if verb == "wait":
            self.status = self.after_status
            return self._ok({"type": "agent_info", **self.info()})
        raise AssertionError(argv)


def write_result(status="success", nonce=None, body="# 결과\n작업 완료\n", sha=None, run_id=None):
    def act(fake, prompt):
        rd = Path(re.search(r"결과 디렉터리\(절대 경로\): (.+)", prompt).group(1))
        m = {"schema_version": "1.0", "run_id": run_id or re.search(r"실행 식별자: (\S+)", prompt).group(1),
             "nonce": nonce or re.search(r"검증 토큰: (\S+)", prompt).group(1),
             "profile_fingerprint": re.search(r"프로필 지문: (\S+)", prompt).group(1), "status": status,
             "result_file": "result.md", "checks": [{"command": "true", "outcome": "passed", "notes": ""}]}
        (rd / "result.md").write_text(body, "utf-8")
        m["result_sha256"] = sha or hashlib.sha256(body.encode()).hexdigest()
        (rd / "result.json").write_text(json.dumps(m), "utf-8")
    return act


class P2(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = os.path.realpath(self.tmp.name)
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["--model", "m", "--effort", "high"])],
                          default="a")

    def tearDown(self):
        self.tmp.cleanup()

    def task(self, **kw):
        raw = {"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "do the thing",
               "cwd": self.cwd, "categories": {"general": 1}, "category_confidence": 0.9}
        raw.update(kw)
        return r.validate_task(raw)

    def run_(self, fake, t=None, w=which):
        return hd.dispatch(t or self.task(), self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=w)

    def receipt(self, out):
        return json.loads(Path(out["receipt_path"]).read_text("utf-8"))

    def test_v19_prompt_is_argv_not_shell(self):
        evil = "x $(touch /tmp/pwned) `id`; rm -rf ~\n\"quoted\" 'single' \\ & | > <"
        fake = FakeHerdr(on_prompt=write_result())
        out = self.run_(fake, self.task(prompt=evil))
        self.assertEqual(out["status"], "completed")
        self.assertTrue(fake.prompts[0].startswith(evil))
        self.assertFalse(Path("/tmp/pwned").exists())
        self.assertTrue(all(k["shell"] is False for k in fake.kwargs))

    def test_v20_uses_returned_ids(self):
        fake = FakeHerdr(on_prompt=write_result(), pane="w42:p9")
        out = self.run_(fake)
        self.assertEqual((out["selected"]["pane_id"], out["workspace_id"]), ("w42:p9", "w7"))
        self.assertTrue(re.fullmatch(r"br-[0-9a-f]{12}", out["selected"]["agent_name"]))

    def test_v21_start_failures_send_nothing(self):
        for code, status in (("timeout", "execution_failed"), ("agent_not_ready", "blocked")):
            with self.subTest(code=code):
                fake = FakeHerdr(start_error=code)
                out = self.run_(fake, self.task(task_id=f"t-{code.replace('_', '-')}"))
                self.assertEqual((out["status"], out["delivery_state"], fake.prompts), (status, "not_attempted", []))
                self.assertIn("command not found", out["diagnostic_tail"])
                self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "execution_failed")
                rc = hd.load_receipt(self.cwd, out["run_id"])  # 원래 실패 원인 보존
                obs = rc["pre_prompt_failure"]["observation"] if status == "blocked" else rc["last_observation"]
                self.assertEqual(obs["error"]["code"], code)
        out = self.run_(FakeHerdr(), self.task(task_id="t-missing"), w=lambda _: None)
        self.assertEqual(out["status"], "no_eligible_profile")
        self.assertEqual(out["excluded"], [{"profile": "a", "reasons": ["executable_not_found"]}])

    def test_v22_not_idle_before_prompt(self):
        for st in ("working", "blocked", "unknown"):
            fake = FakeHerdr(pre_prompt_status=st)
            out = self.run_(fake, self.task(task_id=f"t-{st}"))
            self.assertEqual((fake.prompts, out["delivery_state"]), ([], "not_attempted"))
            self.assertIn(out["status"], ("blocked", "execution_failed"))
            hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)  # 다음 dispatch를 위해 정리

    def test_v23_completed_with_contract(self):
        out = self.run_(FakeHerdr(on_prompt=write_result(status="partial")))
        self.assertEqual((out["status"], out["task_outcome"], out["delivery_state"]),
                         ("completed", "partial", "activity_observed"))
        self.assertTrue(os.path.isabs(out["result_path"]) and Path(out["manifest_path"]).is_file())
        self.assertTrue(out["selected"]["profile_fingerprint"])

    def test_v24_settled_but_invalid_result(self):
        cases = {"missing": None, "old_run": write_result(run_id="00000000-0000-0000-0000-000000000000"),
                 "nonce": write_result(nonce="f" * 32), "hash": write_result(sha="0" * 64)}
        for i, (name, act) in enumerate(cases.items()):
            with self.subTest(name):
                out = self.run_(FakeHerdr(on_prompt=act), self.task(task_id=f"t{i}"))
                self.assertEqual(out["status"], "result_invalid")
                self.assertIsNone(out["result_path"])

    def test_v25_path_and_size_attacks(self):
        outside = Path(self.cwd) / "secret.md"
        outside.write_text("secret", "utf-8")

        def symlinked(fake, prompt):
            write_result()(fake, prompt)
            rd = Path(re.search(r"결과 디렉터리\(절대 경로\): (.+)", prompt).group(1))
            (rd / "result.md").unlink()
            (rd / "result.md").symlink_to(outside)

        def huge(fake, prompt):
            write_result()(fake, prompt)
            rd = Path(re.search(r"결과 디렉터리\(절대 경로\): (.+)", prompt).group(1))
            (rd / "result.json").write_bytes(b" " * (hd.RESULT_JSON_MAX + 1))

        for i, act in enumerate((symlinked, huge, write_result(body="  \n"))):
            out = self.run_(FakeHerdr(on_prompt=act), self.task(task_id=f"p{i}"))
            self.assertEqual(out["status"], "result_invalid", i)

    def test_v26_timeout_no_resend_then_collect(self):
        fake = FakeHerdr(prompt_error="timeout", after_status="working")
        out = self.run_(fake)
        self.assertEqual((out["status"], out["delivery_state"]), ("timed_out", "uncertain"))
        again = self.run_(fake)  # 같은 task/round → collect, 재전송 없음
        self.assertEqual((len(fake.prompts), again["reused_receipt"], again["run_id"]), (1, True, out["run_id"]))
        write_result()(fake, fake.prompts[0])  # Agent가 뒤늦게 결과 작성
        fake.status = "idle"
        done = hd.collect_run(self.cwd, out["run_id"], 1000, runner=fake)
        self.assertEqual((done["status"], len(fake.prompts)), ("completed", 1))
        for code in ("agent_prompt_stalled", "weird_error"):
            f = FakeHerdr(prompt_error=code)
            o = self.run_(f, self.task(task_id=f"s-{code.replace('_', '-')}"))
            self.assertEqual((o["status"], o["delivery_state"]), ("delivery_uncertain", "uncertain"))
            f.status = "idle"
            self.assertEqual(hd.collect_run(self.cwd, o["run_id"], 0, runner=f)["status"], "delivery_uncertain")
            Path(o["receipt_path"]).unlink()  # 테스트 정리: 미해결 receipt 제거

    def test_v27_crash_after_submission_attempted(self):
        class Crash(Exception):
            pass

        fake = FakeHerdr()

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
        fake = FakeHerdr(on_prompt=write_result())
        first = self.run_(fake)
        self.assertEqual(self.run_(fake)["status"], "completed")  # 같은 hash: 기록 재사용
        self.assertEqual(len(fake.prompts), 1)
        self.assertEqual(self.run_(fake, self.task(prompt="different"))["status"], "conflict")
        with hd.dispatch_lock(self.cwd):
            self.assertEqual(self.run_(fake, self.task(task_id="t2"))["status"], "conflict")
        stuck = FakeHerdr(prompt_error="timeout", after_status="working")
        self.run_(stuck, self.task(task_id="t3"))
        blocked = self.run_(fake, self.task(task_id="t4"))
        self.assertEqual(blocked["status"], "conflict")
        self.assertEqual(blocked["warnings"][-1]["code"], "unresolved_run")
        self.assertEqual(first["status"], "completed")

    def test_v29_agent_gone_or_partial(self):
        fake = FakeHerdr(prompt_error="timeout", after_status="working")
        out = self.run_(fake)
        write_result()(fake, fake.prompts[0])
        fake.gone = True  # Agent 종료: 파일만으로 성공 선언 금지
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "execution_failed")
        fb = hd.feedback(self.cwd, out["run_id"], "fail", "orchestrator", "agent exited")
        self.assertEqual((fb["status"], fb["receipt_status"]), ("recorded", "execution_failed"))
        out = self.run_(FakeHerdr(on_prompt=write_result(status="fail")), self.task(task_id="t9"))
        self.assertEqual((out["status"], out["task_outcome"]), ("completed", "fail"))  # 수신 성공 ≠ 작업 성공

    def test_prompt_size_limit(self):
        with self.assertRaises(r.InputError):
            self.run_(FakeHerdr(), self.task(prompt="x" * hd.MAX_PROMPT_ARG_BYTES))


if __name__ == "__main__":
    unittest.main()
