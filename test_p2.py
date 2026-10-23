"""P2 검증 V19–V29 (06 문서). herdr는 0.9.3 실측 응답 형식을 따르는 fake.
실행: python3 -m unittest -v test_p2"""
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace

from bench_router import herdr as hd
from bench_router import routing as r
from test_p0 import MAPPING, config, profile, guided_reply, guided_responses, NOW


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


def git_repo(path):
    """Projects 1.2.1 works on git repositories: a top-level repo with one commit."""
    git = ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git[:3] + ["init", "-q"], check=True)
    subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "init"], check=True)


def projects_environment(case, base):
    case.enterContext(patch.dict(os.environ, {"BENCH_ROUTER_HERDR_SESSION": "brtest",
                                            "BENCH_ROUTER_COORDINATION_DIR": str(Path(base) / "admission")}))
    case.enterContext(patch.object(hd, "probe_profiles", side_effect=lambda profiles, which=hd.shutil.which:
                                  {p["id"]: hd.probe(p, which) for p in profiles}))
    # No real waiting in offline state-transition tests.
    import itertools
    from types import SimpleNamespace
    ticks = itertools.count()
    case.enterContext(patch.object(hd, "time", SimpleNamespace(monotonic=lambda: next(ticks), sleep=lambda _: None)))


class FakeProjects:
    """Projects 1.2.1 CLI JSON shapes (src/cli/tasks.rs brief/details); every task gets a real git worktree."""

    def __init__(self, prompt_error=None, after_status="idle", on_prompt=None, profiles=None):
        self.calls, self.prompts, self.kwargs, self.adds, self.ws_cwds = [], [], [], [], []
        self.prompt_error, self.on_prompt, self.status = prompt_error, on_prompt, after_status
        self.profiles = profiles or {}
        self.version = "herdr-projects 1.2.1 (/fake/bin/herdr-projects)"
        self.tasks, self.gone, self.pending, self.updates, self.detail_updates = {}, False, False, {}, {}
        self.panes, self.closed, self.pane_error = {}, [], None
        self.tells, self.tell_error = [], None
        self.runs, self.reports, self.on_run = [], [], None  # headless: herdr pane run, board report
        self.stopped = set()
        self.lock = __import__("threading").Lock()

    def _ok(self, obj):
        return subprocess.CompletedProcess([], 0, json.dumps(obj), "")

    def worktree_of(self, prompt):
        return next(t["worktree"] for t in self.tasks.values() if t["prompt"] == prompt)

    def _row(self, t):
        stage, state, msg = {"idle": ("approval", "blocked", "Approve to merge?"), "working": ("working", "working", ""),
                             "blocked": ("asks", "blocked", "approval or question: command not found")}[self.status]
        if self.pending:
            stage, state, msg = "starting", "working", "Starting"
        if self.gone:
            stage, state, msg = "failed", "error", "The agent has exited"
        if t["id"] in self.stopped:
            stage, state, msg = "stopped", "idle", "Stopped"
        return {"id": t["id"], "state": state, "app": t["agent"], "title": t["title"], "msg": msg, "stage": stage,
                **self.updates}

    def _pane(self, t):
        self.panes[t["id"]] = {"pane_id": f"w{t['id'].split('/')[1]}:p1", "cwd": t["worktree"], "agent": t["agent"],
                               "agent_session": {"value": f"sess-{t['id']}"}}

    def _herdr(self, argv):
        """herdr 0.9.x `pane list` / `pane close` shapes; each task's agent pane sits in its worktree."""
        self.calls.append(["herdr", *argv[:2]])
        if self.pane_error:
            return subprocess.CompletedProcess([], 1, "", self.pane_error)
        if argv == ["pane", "list"]:
            status = {"idle": "idle", "working": "working", "blocked": "blocked"}[self.status]
            return self._ok({"result": {"panes": [{**p, "agent_status": status} for p in self.panes.values()]}})
        if argv[:2] == ["worktree", "create"]:
            path, branch, repo = (argv[argv.index(f) + 1] for f in ("--path", "--branch", "--cwd"))
            subprocess.run(["git", "-C", repo, "worktree", "add", "-q", "-b", branch, path, "HEAD"],
                           check=True, capture_output=True)
            pane = {"pane_id": f"h{len(self.panes) + 1}:p1", "workspace_id": f"h{len(self.panes) + 1}", "cwd": path,
                    "agent": None, "agent_session": None}
            self.panes[path] = pane
            return self._ok({"result": {"root_pane": pane, "workspace": {"workspace_id": pane["pane_id"][:-3]},
                                        "worktree": {"path": path, "branch": branch}}})
        if argv[:2] == ["pane", "run"]:
            self.runs.append(argv[3])
            if self.on_run:
                self.on_run(self, argv[3])
            return self._ok({"result": {"type": "ok"}})
        if argv[:2] == ["pane", "get"]:
            if any(p["pane_id"] == argv[2] for p in self.panes.values()):
                return self._ok({"result": {"pane": {"pane_id": argv[2]}}})
            return subprocess.CompletedProcess([], 1, json.dumps({"error": {"code": "pane_not_found"}}), "")
        if argv[:2] == ["workspace", "close"]:
            self.panes = {k: p for k, p in self.panes.items() if p.get("workspace_id") != argv[2]}
            return self._ok({"result": {"type": "ok"}})
        if argv[:2] == ["pane", "close"]:
            self.closed.append(argv[2])
            self.panes = {k: p for k, p in self.panes.items() if p["pane_id"] != argv[2]}
            return self._ok({"result": {"type": "ok"}})
        raise AssertionError(argv)

    def __call__(self, cmd, **kw):
        assert kw["shell"] is False
        if cmd[0] == hd.HERDR_BIN:
            return self._herdr(cmd[1:])
        assert cmd[0] == hd.PROJECTS_BIN
        argv = cmd[1:]
        self.kwargs.append((argv[0], kw))
        self.calls.append(argv[:2])
        if argv == ["version"]:
            return subprocess.CompletedProcess(cmd, 0, self.version + "\n", "")
        if argv[0] == "add" and "--delegate" not in argv:  # headless: an agent-less board task, nothing starts
            with self.lock:
                tid = f"repo/{len(self.tasks) + 1}"
                self.tasks[tid] = {"id": tid, "title": argv[1], "prompt": argv[argv.index("--desc") + 1],
                                   "worktree": None, "branch": None, "agent": None}
                self.adds.append(argv)
            return self._ok({"id": tid, "state": "idle", "title": argv[1], "stage": "todo"})
        if argv[0] == "stop":
            self.stopped.add(argv[1])
            return subprocess.CompletedProcess(cmd, 0, "stopped\n", "")
        if argv[0] == "report":
            self.reports.append(argv[argv.index("--state") + 1])
            return subprocess.CompletedProcess(cmd, 0, "ok\n", "")
        if argv[0] == "add":
            title, prompt, repo = argv[1], argv[argv.index("--desc") + 1], argv[argv.index("--repo") + 1]
            wt = Path(repo) / ".bench-router" / "wt" / title
            subprocess.run(["git", "-C", repo, "worktree", "add", "-q", "-b", f"work/{title}", str(wt), "HEAD"],
                           check=True, capture_output=True)
            with self.lock:
                tid = f"repo/{len(self.tasks) + 1}"
                self.tasks[tid] = {"id": tid, "title": title, "prompt": prompt, "worktree": str(wt),
                                   "branch": f"work/{title}", "agent": argv[argv.index("--worker.agent") + 1].split("/")[0]}
                self._pane(self.tasks[tid])
                self.prompts.append(prompt)
                self.adds.append(argv)
                self.ws_cwds.append(repo)
            if self.on_prompt:
                self.on_prompt(self, prompt)
            if self.prompt_error:
                raise subprocess.TimeoutExpired(cmd, 15)
            return self._ok({"id": tid, "state": "working", "title": title, "stage": "starting"})
        if argv[:1] == ["list"]:
            return self._ok([self._row(t) for t in self.tasks.values()])
        if argv[0] == "reopen":
            self._pane(self.tasks[argv[1]])
            return self._ok({"pane": self.panes[argv[1]]["pane_id"], "hasAgent": True})
        if argv[0] == "tell":
            if self.tell_error:
                raise subprocess.TimeoutExpired(cmd, 15)
            self.tells.append((argv[1], argv[2]))
            return self._ok({"id": argv[1]})
        if argv[0] == "details":
            t = self.tasks[argv[1]]
            return self._ok({"task": {"id": t["id"], "title": t["title"], "stage": self._row(t)["stage"]},
                             "agent": t["agent"], "worktree": t["worktree"], "branch": t["branch"], **self.detail_updates})
        raise AssertionError(argv)


def result_dir(fake, prompt):
    rel = re.search(r"결과 디렉터리\(현재 worktree 기준 상대 경로\): (.+)", prompt).group(1)
    return Path(fake.worktree_of(prompt)) / rel


def headless_cli(exit_code=0, result=True):
    """Stand-in for `herdr pane run`: what the typed one-shot CLI would leave behind."""
    def act(fake, cmd):
        script = shlex.split(cmd)[2]
        wt = shlex.split(script.split(" && ")[0])[1]
        rd = Path(re.search(r"cat (\S+)/input\.txt", script).group(1))
        if result:
            write_result()(SimpleNamespace(worktree_of=lambda prompt: wt), (rd / "input.txt").read_text("utf-8"))
        (rd / "exit_code").write_text(f"{exit_code}\n", "utf-8")
    return act


def write_result(status="success", nonce=None, body="# 결과\n작업 완료\n", sha=None, run_id=None):
    def act(fake, prompt):
        rd = result_dir(fake, prompt)
        rd.mkdir(parents=True, exist_ok=True)
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
        git_repo(self.cwd)
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["--model", "m", "--effort", "high"])],
                          default="a")

    def tearDown(self):
        cleanup_temp(self.tmp)

    def task(self, **kw):
        raw = {"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "do the thing",
               "cwd": self.cwd,
               "constraints": {"timeout_ms": 5000}}
        raw.update(kw)
        return r.validate_task(raw)

    def run_(self, fake, t=None, w=which, **kw):
        fake.profiles = {p["id"]: p for p in self.cfg["profile"]}
        return hd.dispatch(t or self.task(), self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=w,
                           decision_options={"policy": "legacy"}, **kw)

    def receipt(self, out):
        return json.loads(Path(out["receipt_path"]).read_text("utf-8"))

    def test_v98_external_selection_dispatch_and_receipt_first_recovery(self):
        from bench_router import decision
        self.cfg = config([*self.cfg["profile"], profile("b")], default="a")
        t = self.task()
        def evaluate(response=None):
            return decision.evaluate(t, self.cfg, MAPPING, None, [], NOW, host="codex", env={}, response=response)
        assessment = evaluate(guided_responses(evaluate(), evaluate, "__tie__"))
        self.assertEqual(assessment["recommendation"]["profile"], "a")
        selection = decision.bind(assessment, "b", {"id": "team", "version": "1"}, "specialist", True)
        fake = FakeProjects(on_prompt=write_result(), profiles={p["id"]: p for p in self.cfg["profile"]})
        def dispatch():
            return hd.dispatch(t, self.cfg, MAPPING, None, [], session="brtest", runner=fake, which=which,
                               selection=selection, decision_options={"host": "codex", "env": {}})
        out = dispatch()
        self.assertEqual((out["status"], out["selected"]["profile"], out["selection"]["schema_version"]),
                         ("completed", "b", "4.0"))
        with patch.object(decision, "load_guidelines", side_effect=AssertionError("must collect saved run")):
            again = dispatch()
        self.assertEqual((again["run_id"], len(fake.prompts)), (out["run_id"], 1))

    def test_v76_guided_live_preflight_and_receipt_first_recovery(self):
        from bench_router import decision
        fake = FakeProjects(on_prompt=write_result())
        fake.profiles = {p["id"]: p for p in self.cfg["profile"]}
        opts = {"host": "codex", "env": {}}
        pending = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], session="brtest", runner=fake,
                              which=which, decision_options=opts)
        self.assertEqual((pending["status"], fake.calls), ("decision_required", []))
        self.assertFalse((Path(self.cwd) / ".bench-router").exists())
        response = guided_responses(pending, lambda response: r.route(
            self.task(), self.cfg, MAPPING, None, [], NOW, host="codex", env={}, response=response), "a")
        first = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], session="brtest", runner=fake,
                            which=which, decision_options={**opts, "response": response})
        self.assertEqual((first["status"], first["selection"]["schema_version"]), ("completed", "3.0"))
        with patch.object(decision, "load_guidelines", side_effect=AssertionError("must recover without new choice")):
            again = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], session="brtest", runner=fake,
                                which=which, decision_options=opts)
        self.assertEqual((again["reused_receipt"], len(fake.prompts)), (True, 1))

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
        self.assertTrue(all(k["shell"] is False for _, k in fake.kwargs))

    def test_v20_uses_returned_ids_and_one_run_settings(self):
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(fake)
        t = fake.tasks["repo/1"]
        self.assertEqual((out["thread_id"], out["worktree"], out["branch"]), ("repo/1", t["worktree"], t["branch"]))
        add = fake.adds[0]
        self.assertEqual(add[1], "br-" + out["run_id"])
        self.assertEqual(add[add.index("--worker.agent") + 1:add.index("--worker.agent") + 4],
                         ["claude/m", "--worker.effort", "high"])
        self.assertIn("--delegate", add)
        self.assertEqual(add[add.index("--review.when") + 1], "never")
        self.assertNotIn("--worker.access", add)  # the board's own access setting applies
        self.assertTrue(Path(out["result_path"]).is_relative_to(self.cwd))  # copied next to the receipt

    def test_completed_agent_is_released_then_resumed(self):
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(fake)
        self.assertEqual((out["status"], fake.closed), ("completed", ["w1:p1"]))
        self.assertEqual(out["release"]["panes"], [{"pane_id": "w1:p1", "agent": "claude", "session": "sess-repo/1"}])
        res = hd.resume_run(self.cwd, out["run_id"], runner=fake)
        self.assertEqual((res["resumed"]["pane_id"], res["resumed"]["has_agent"]), ("w1:p1", True))
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "completed")
        self.assertEqual(fake.closed, ["w1:p1"])  # a resumed session is never closed again by the router
        self.assertEqual(len(fake.prompts), 1)  # resume sends nothing

    def test_poll_near_deadline_keeps_call_budget(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        fake.kwargs.clear()
        res = hd.collect_run(self.cwd, out["run_id"], 1, runner=fake)  # the wait ends before the poll returns
        self.assertEqual(res["status"], "timed_out")  # still working, not delivery_uncertain
        self.assertEqual({kw["timeout"] for cmd, kw in fake.kwargs if cmd == "list"}, {hd.OBSERVE_FLOOR_S})

    def test_wait_zero_returns_after_submission(self):
        fake = FakeProjects(after_status="working", on_prompt=write_result())
        out = self.run_(fake, wait_ms=0)
        self.assertEqual((out["status"], len(fake.adds), out["thread_id"]), ("timed_out", 1, "repo/1"))
        self.assertFalse([c for c in fake.calls if c[:1] == ["list"]])  # returned without waiting on the board
        fake.status = "idle"
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "completed")

    def test_tell_refuses_task_finished_on_board(self):
        fake = FakeProjects(after_status="working", on_prompt=write_result())
        out = self.run_(fake, wait_ms=0)
        fake.status = "idle"  # the agent finished (approval) but nobody collected yet: the receipt still says timed_out
        with self.assertRaisesRegex(r.InputError, "finished on the board"):
            hd.tell_run(self.cwd, out["run_id"], "late", runner=fake)
        self.assertEqual(fake.tells, [])

    def test_headless_runs_one_shot_cli_in_a_pane(self):
        fake = FakeProjects()
        fake.on_run = headless_cli()
        out = self.run_(fake, self.task(execution="headless"))
        self.assertEqual((out["status"], out["task_outcome"]), ("completed", "success"), out)
        self.assertNotIn("--delegate", fake.adds[0])  # the board task is a view; no board agent
        cmd = shlex.split(fake.runs[0])[2]
        self.assertIn("claude -p --model m --effort high --dangerously-skip-permissions", cmd)
        self.assertNotIn("do the thing", cmd)  # the prompt reaches the CLI from input.txt only
        self.assertEqual((fake.reports, len(fake.closed)), (["working", "done"], 1))
        with self.assertRaisesRegex(r.InputError, "headless"):
            hd.tell_run(self.cwd, out["run_id"], "hi", runner=fake)

    def test_headless_running_then_pane_closed_is_failure(self):
        fake = FakeProjects()  # no exit_code yet: the CLI is still running
        out = self.run_(fake, self.task(execution="headless"), wait_ms=0)
        self.assertEqual(out["status"], "timed_out")
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "timed_out")
        fake.panes.clear()  # closed by hand = stopped
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "execution_failed")
        self.assertEqual(fake.reports[-1], "error")

    def test_headless_failing_cli_without_result(self):
        fake = FakeProjects()
        fake.on_run = headless_cli(exit_code=1, result=False)
        self.assertEqual(self.run_(fake, self.task(execution="headless"))["status"], "execution_failed")
        self.cfg["profile"][0]["args"] = ["--weird"]  # nothing headless can express
        out = self.run_(fake, self.task(task_id="t2", execution="headless"))
        self.assertEqual((out["status"], len(fake.runs)), ("execution_failed", 1))
        agy = hd.headless_argv(profile("g", kind="agy", args=["--model", "gemini-3.8-flash-low"]))
        self.assertEqual(agy[-1], "-p")  # agy -p consumes the next argument as the prompt

    def test_stop_ends_live_runs_and_frees_the_workspace(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake, wait_ms=0)
        self.assertEqual(hd.stop_run(self.cwd, None, runner=fake)["status"], "stop_sent")  # board stop
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "execution_failed")
        with self.assertRaisesRegex(r.InputError, "already settled"):
            hd.stop_run(self.cwd, out["run_id"], runner=fake)
        hl = self.run_(fake, self.task(task_id="t2", execution="headless"), wait_ms=0)  # the stop freed the cwd
        self.assertEqual(hl["status"], "timed_out", hl)
        hd.stop_run(self.cwd, hl["run_id"], runner=fake)  # headless: closes its whole workspace
        self.assertEqual(hd.collect_run(self.cwd, hl["run_id"], 0, runner=fake)["status"], "execution_failed")
        log = [json.loads(x)["state"] for x in Path(hl["receipt_path"]).with_name("messages.jsonl").read_text().splitlines()]
        self.assertEqual(log, ["stop_attempted", "stop_sent"])

    def test_collect_many_any_then_all(self):
        other = tempfile.TemporaryDirectory()
        self.addCleanup(cleanup_temp, other)
        cwd2 = os.path.realpath(other.name)
        git_repo(cwd2)
        fake = FakeProjects(after_status="working", on_prompt=write_result())
        a = self.run_(fake, wait_ms=0)
        b = self.run_(fake, self.task(cwd=cwd2, execution="headless"), wait_ms=0)  # no exit_code: still running
        runs = [(self.cwd, a["run_id"]), (cwd2, b["run_id"])]
        self.assertEqual(hd.collect_many(runs, 0, "any", runner=fake)["status"], "timed_out")
        fake.status = "idle"  # a finishes on the board
        res = hd.collect_many(runs, 0, "any", runner=fake)
        self.assertEqual((res["status"], res["ready"]), ("ok", [a["run_id"]]))
        self.assertEqual([x["status"] for x in res["runs"]], ["completed", "timed_out"])
        self.assertEqual(hd.collect_many(runs, 0, "all", runner=fake)["status"], "timed_out")  # b still running

    def test_tell_relays_explicit_message(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        self.assertEqual(out["status"], "timed_out")
        res = hd.tell_run(self.cwd, None, "use the v2 API", runner=fake)  # the only live run under cwd
        self.assertEqual((res["status"], fake.tells), ("sent", [("repo/1", "use the v2 API")]))
        log = [json.loads(x) for x in Path(res["messages_path"]).read_text("utf-8").splitlines()]
        self.assertEqual([x["state"] for x in log], ["attempted", "sent"])
        self.assertEqual(log[0]["text"], "use the v2 API")
        fake.tell_error = True
        self.assertEqual(hd.tell_run(self.cwd, out["run_id"], "again", runner=fake)["status"], "delivery_uncertain")
        with self.assertRaises(r.InputError):
            hd.tell_run(self.cwd, out["run_id"], "x" * (hd.MAX_PROMPT_ARG_BYTES + 1), runner=fake)
        rc = self.receipt(out)
        rc["status"] = "completed"
        hd.save(rc)
        with self.assertRaisesRegex(r.InputError, "settled"):  # tell on a finished task would start a new agent
            hd.tell_run(self.cwd, out["run_id"], "late", runner=fake)
        with self.assertRaisesRegex(r.InputError, "0 unsettled"):
            hd.tell_run(self.cwd, None, "late", runner=fake)
        rc["resumed"] = {"at": "t"}
        hd.save(rc)
        fake.tell_error = None
        self.assertEqual(hd.tell_run(self.cwd, out["run_id"], "after resume", runner=fake)["status"], "sent")

    def test_only_settled_completed_agents_are_released(self):
        for i, (status, kw) in enumerate((("working", {}), ("blocked", {}), ("idle", {"on_prompt": None}))):
            fake = FakeProjects(after_status=status, **kw)
            out = self.run_(fake, self.task(task_id=f"r{i}"))
            self.assertNotEqual(out["status"], "completed")
            self.assertEqual(fake.closed, [], status)
            from bench_router import coordination
            coordination.resolve(out["coordination_key"], "inspected")
            for rc in hd.receipts(self.cwd):  # settle the cwd for the next case
                rc["status"] = "execution_failed"
                hd.save(rc)

    def test_release_failure_keeps_result_and_retries(self):
        fake = FakeProjects(on_prompt=write_result())
        fake.pane_error = "herdr server not running"
        out = self.run_(fake)
        self.assertEqual((out["status"], out["release"], fake.closed), ("completed", None, []))
        fake.pane_error = None
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["release"]["panes"][0]["pane_id"], "w1:p1")

    def test_v21_inexpressible_profile_sends_nothing(self):
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["--add-dir", "/x"])], default="a")
        fake = FakeProjects()
        out = self.run_(fake)
        self.assertEqual((out["status"], out["delivery_state"], fake.prompts), ("execution_failed", "not_attempted", []))
        missing = self.run_(FakeProjects(), self.task(task_id="missing"), w=lambda _: None)
        self.assertEqual(missing["excluded"], [{"profile": "a", "reasons": ["executable_not_found"]}])

    def test_worker_settings(self):
        p = lambda kind, args: {"kind": kind, "args": args}
        self.assertEqual(hd.worker_settings(p("claude", [])), ["--worker.agent", "claude"])
        self.assertEqual(hd.worker_settings(p("codex", ["-m", "x", "-c", 'model_reasoning_effort="high"'])),
                         ["--worker.agent", "codex/x", "--worker.effort", "high"])
        for bad in (["--add-dir", "/x"], ["-m"], ["-c", "sandbox=x"]):
            self.assertIsNone(hd.worker_settings(p("codex", bad)), bad)

    def test_v22_not_started_cannot_complete(self):
        fake = FakeProjects(on_prompt=write_result())
        fake.pending = True
        out = self.run_(fake)
        self.assertEqual((out["status"], out["delivery_state"]), ("timed_out", "submission_attempted"))
        self.assertIsNone(out["result_path"])
        fake.pending = False
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
            (result_dir(fake, prompt) / "result.json").write_bytes(b" " * (hd.RESULT_JSON_MAX + 1))
        for i, act in enumerate((huge, write_result(body="  \n"))):
            self.assertEqual(self.run_(FakeProjects(on_prompt=act), self.task(task_id=f"p{i}"))["status"], "result_invalid")
        outside = Path(self.cwd) / "secret.md"
        outside.write_text("secret", "utf-8")
        def symlinked(fake, prompt):
            write_result()(fake, prompt)
            rd = result_dir(fake, prompt)
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
        self.assertTrue(all(0 < kw["timeout"] <= 5 for cmd, kw in fake.kwargs if cmd != "version"))
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
        fake.version = "herdr-projects 1.3.0 (/fake)"
        with self.assertRaises(r.InputError):
            self.run_(fake)
        self.assertEqual((fake.prompts, hd.receipts(self.cwd)), ([], []))

    def test_prompt_size_limit(self):
        with self.assertRaises(r.InputError):
            self.run_(FakeProjects(), self.task(prompt="x" * hd.MAX_PROMPT_ARG_BYTES))


if __name__ == "__main__":
    unittest.main()
