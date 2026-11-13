"""P2 검증 V19–V29 (06 문서). Shepherdr 3.1.14 / hc CLI 형식을 따르는 fake.
실행: python3 -m unittest -v test_p2"""
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
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
    """Shepherdr worktrees need git repositories: a top-level repo with one commit."""
    git = ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git[:3] + ["init", "-q"], check=True)
    subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "init"], check=True)


def projects_environment(case, base):
    case.enterContext(patch.dict(os.environ, {"BENCH_ROUTER_HERDR_SESSION": "default",
                                            "BENCH_ROUTER_COORDINATION_DIR": str(Path(base) / "admission")}))
    case.enterContext(patch.object(hd, "probe_profiles", side_effect=lambda profiles, which=hd.shutil.which:
                                  {p["id"]: hd.probe(p, which) for p in profiles}))
    # No real waiting in offline state-transition tests.
    import itertools
    from types import SimpleNamespace
    ticks = itertools.count()
    case.enterContext(patch.object(hd, "time", SimpleNamespace(monotonic=lambda: next(ticks), sleep=lambda _: None)))


class FakeProjects:
    """Shepherdr 3.1.14 herdr-task and hc JSON contracts, with real isolated git worktrees."""

    def __init__(self, prompt_error=None, after_status="idle", on_prompt=None, profiles=None):
        self.calls, self.prompts, self.kwargs, self.adds, self.ws_cwds = [], [], [], [], []
        self.prompt_error, self.on_prompt, self.status = prompt_error, on_prompt, after_status
        self.profiles = profiles or {}
        self.version, self.core_version = "1", "hc 0.1.18"
        self.tasks, self.gone, self.pending, self.updates, self.detail_updates = {}, False, False, {}, {}
        self.panes, self.closed, self.pane_error = {}, [], None
        self.tells, self.tell_error = [], None
        self.runs, self.reports, self.on_run = [], [], None
        self.stopped = set()
        self.add_error, self.start_error, self.mode = None, None, "worktree"
        self.lock = __import__("threading").Lock()

    def _ok(self, obj):
        return subprocess.CompletedProcess([], 0, json.dumps(obj), "")

    def worktree_of(self, prompt):
        return next(t["worktree"] for t in self.tasks.values() if t["prompt"] == prompt)

    def _row(self, t):
        state, status, needs, why = {"idle": ("ready", "ready", None, None),
            "working": ("running", "working", None, None),
            "blocked": ("running", "needs", "asks", "approval or question: command not found")}[self.status]
        if not t.get("started"):
            state, status, needs = "todo", "todo", None
        if self.pending:
            state, status, needs = "queued", "queued", None
        if self.gone or t["key"] in self.stopped:
            state, status, needs, why = "running", "needs", "stopped", "Agent stopped"
        live = [{"address": p["address"], "status": "idle" if self.status == "idle" else self.status}
                for p in self.panes.values() if p.get("task") == t["key"]]
        return {**t, "state": state, "status": status, "needs": needs, "why": why, "live": live,
                **self.updates, **self.detail_updates}

    def _pane(self, t):
        self.panes[t["key"]] = {"address": f"t{t['id']}", "cwd": t["worktree"], "agent": t["agent"],
                                "task": t["key"], "state": "live"}

    def _core(self, argv):
        self.calls.append(["hc", *argv[:2]])
        if argv == ["--version"]:
            return subprocess.CompletedProcess([], 0, self.core_version + "\n", "")
        if self.pane_error:
            return subprocess.CompletedProcess([], 1, "", self.pane_error)
        if argv[0] == "ls":
            label = argv[argv.index("--label") + 1]
            value = label.split("=", 1)[1]
            panes = [p for p in self.panes.values() if p.get("task") == value or p.get("run") == value]
            return self._ok({"terminals": [{**p, "status": {"state": self.status}} for p in panes]})
        if argv[0] == "run" and "bench_router.lifecycle" in argv:
            return self._ok({"address": "observer"})
        if argv[0] == "run":
            script = argv[-1]
            self.runs.append(shlex.join(["sh", "-c", script]))
            wt = argv[argv.index("--cwd") + 1]
            address = f"h{len(self.runs)}"
            self.panes[address] = {"address": address, "cwd": wt, "agent": None, "state": "live",
                                   "run": argv[argv.index("--label") + 1].split("=", 1)[1]}
            if self.on_run:
                self.on_run(self, self.runs[-1])
            return self._ok({"address": address})
        if argv[0] == "get":
            return self._ok(next((p for p in self.panes.values() if p["address"] == argv[1]),
                                 {"address": argv[1], "state": "exited"}))
        if argv[0] in ("keep", "rm"):
            return self._ok({"ok": True})
        if argv[0] == "kill":
            self.closed.append(argv[1])
            for key, p in list(self.panes.items()):
                if p["address"] == argv[1]:
                    if p.get("task"):
                        self.stopped.add(p["task"])
                    del self.panes[key]
            return self._ok({"ok": True})
        if argv[0] == "send":
            if self.tell_error:
                raise subprocess.TimeoutExpired(argv, 15)
            self.tells.append((argv[1], argv[2]))
            return self._ok({"ok": True})
        raise AssertionError(argv)

    def __call__(self, cmd, **kw):
        assert kw["shell"] is False
        if cmd[0] == hd.HERDR_BIN:
            return self._core(cmd[1:])
        assert cmd[0] == hd.PROJECTS_BIN
        argv = cmd[1:]
        self.kwargs.append((argv[0], kw))
        self.calls.append(argv[:2])
        if argv == ["--version"]:
            return subprocess.CompletedProcess(cmd, 0, self.version + "\n", "")
        if argv[0] == "add":
            with self.lock:
                n = len(self.tasks) + 1
                key = f"repo#{n}"
                self.tasks[key] = {"id": n, "key": key, "ref": f"REPO-{n}", "mode": self.mode,
                    "title": argv[1], "prompt": Path(argv[argv.index("--prompt-file") + 1]).read_text(),
                    "folder": argv[argv.index("--folder") + 1], "worktree": None,
                    "branch": argv[argv.index("--branch") + 1], "agent": argv[argv.index("--agent") + 1]}
                self.adds.append(argv)
            if self.add_error:
                raise subprocess.TimeoutExpired(cmd, 15)
            return self._ok(self._row(self.tasks[key]))
        if argv[0] == "start":
            t = self.tasks[argv[1]]
            t["argv"] = json.loads(argv[argv.index("--argv") + 1]) if "--argv" in argv else [t["agent"]]
            if self.pending and getattr(self, "queue_only", False):
                return self._ok(self._row(t))
            repo, branch = t["folder"], t["branch"]
            wt = Path(repo) / ".bench-router" / "wt" / t["title"]
            base = next(a[a.index("--base") + 1] for a in self.adds if a[1] == t["title"])
            subprocess.run(["git", "-C", repo, "worktree", "add", "-q", "-b", branch, str(wt), base],
                           check=True, capture_output=True)
            with self.lock:
                t.update(worktree=str(wt), started=True)
                self._pane(t)
                self.prompts.append(t["prompt"])
                self.ws_cwds.append(repo)
            if "--argv" in argv and t["argv"][:2] == ["sh", "-c"]:
                self.runs.append(shlex.join(t["argv"]))
                if self.on_run:
                    self.on_run(self, self.runs[-1])
            if self.on_prompt:
                self.on_prompt(self, t["prompt"])
            if self.prompt_error or self.start_error:
                raise subprocess.TimeoutExpired(cmd, 15)
            return self._ok({**self._row(t), "terminal": f"t{t['id']}"})
        if argv[0] == "resume":
            t = self.tasks[argv[1]]
            t["resumed_argv"] = list(t["argv"])
            self._pane(t)
            self.stopped.discard(t["key"])
            return self._ok({**self._row(t), "terminal": f"t{t['id']}", "resumed": True})
        if argv[0] in ("ready", "done"):
            return self._ok({**self._row(self.tasks[argv[1]]), "state": argv[0]})
        if argv[0] == "status":
            return self._ok({"ok": True})
        if argv[0] == "reopen":
            t = self.tasks[argv[1]]
            self.pending = False
            t["started"] = False
            return self._ok(self._row(t))
        if argv[0] == "show":
            return self._ok(self._row(self.tasks[argv[1]]))
        raise AssertionError(argv)


class FakeTui(FakeProjects):
    """herdr 0.9.5 TUI CLI shapes seen live (workspace create, pane run/get, workspace close), one real sh per pane.
    Like herdr, a pane outlives its CLI until its workspace closes, and closing it hangs up what still runs."""

    def __init__(self, run_error=None):
        super().__init__()
        self.procs, self.ws_closed, self.typed, self.run_error, self.close_fail = {}, [], [], run_error, 0
        self.socket = "/home/u/.config/herdr/herdr.sock"
        self.version, self.terminal = "0.9.5", "term_1"
        self.waits = []
        self.agents, self.agent_status, self.agent_prompts, self.prompt_calls = {}, "idle", [], 0
        self.completion_seq = None  # set by finish(): herdr marks an idle transition that ended real work
        self.start_error = self.prompt_error = self.on_agent_prompt = self.last_prompt_cmd = None
        self.screen = "Quick safety check: Is this a project you trust?"

    def restart(self):
        """herdr server restart: processes die, panes come back under the same ids as new shells (new terminal)."""
        for proc in self.procs.values():
            if proc:
                os.killpg(proc.pid, 9)
                proc.wait()
        self.procs = dict.fromkeys(self.procs)
        self.terminal += "-restored"
        self.agent_status, self.completion_seq = "idle", None  # a resumed conversation, no finished turn

    def finish(self, status="done"):
        self.agent_status, self.completion_seq = status, (self.completion_seq or 0) + 1

    def __call__(self, cmd, **kw):
        if cmd[0] != hd.TUI_BIN:
            return super().__call__(cmd, **kw)
        op, arg = cmd[1:3], (cmd[3] if len(cmd) > 3 else None)
        if op == ["status", "server"]:
            return subprocess.CompletedProcess(cmd, 0, f"status: running\nversion: {self.version}\nsocket: {self.socket}\n", "")
        if op == ["workspace", "create"]:
            w = f"w{len(self.ws_closed) + len(self.procs) + 1}x{len(self.runs)}"
            self.runs.append(cmd)
            return self._ok({"result": {"workspace": {"workspace_id": w},
                                        "root_pane": {"pane_id": f"{w}:p1", "terminal_id": self.terminal}}})
        if op == ["pane", "run"]:
            if self.run_error:
                return subprocess.CompletedProcess(cmd, 1, "", self.run_error)
            self.typed.append(cmd[4])
            self.procs[arg] = subprocess.Popen(["sh", "-c", cmd[4]], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL, start_new_session=True)
            return subprocess.CompletedProcess(cmd, 0, "", "")  # herdr 0.9.5 prints nothing here
        if op == ["agent", "start"]:
            if self.start_error:
                return subprocess.CompletedProcess(cmd, 1, "", self.start_error)
            self.agents[arg] = cmd
            return self._ok({"result": {"agent": {"name": arg, "agent_status": "idle"}}})
        if op == ["agent", "prompt"]:
            self.prompt_calls += 1
            self.last_prompt_cmd = cmd
            if self.on_agent_prompt:
                self.on_agent_prompt()
            if self.prompt_error or self.agent_status == "blocked":
                return subprocess.CompletedProcess(cmd, 1, "", self.prompt_error or '{"error":{"code":"agent_blocked"}}')
            self.agent_prompts.append((arg, cmd[4]))
            if "--wait" in cmd:  # herdr returns once it saw the turn; without --wait it still reads idle for a while
                self.agent_status = "working"
            return self._ok({"result": {"agent": {"name": arg, "agent_status": self.agent_status}}})
        if op == ["agent", "get"]:
            if arg not in self.agents:
                return subprocess.CompletedProcess(cmd, 1, "", '{"error":{"code":"agent_not_found"}}')
            agent = {"name": arg, "agent_status": self.agent_status, "terminal_id": self.terminal}
            if self.completion_seq is not None:
                agent["completion_seq"] = self.completion_seq
            return self._ok({"result": {"agent": agent}})
        if op == ["agent", "wait"]:
            self.waits.append(cmd)
            until = [cmd[i + 1] for i, a in enumerate(cmd) if a == "--until"]
            if arg in self.agents and self.agent_status in until:
                return self._ok({"result": {"agent": {"name": arg, "agent_status": self.agent_status,
                                                      "terminal_id": self.terminal,
                                                      **({"completion_seq": self.completion_seq}
                                                         if self.completion_seq is not None else {})}}})
            return subprocess.CompletedProcess(cmd, 1, "", '{"error":{"code":"timeout"}}')
        if op == ["pane", "wait-output"]:
            self.waits.append(cmd)
            proc = self.procs.get(arg)
            try:  # like herdr: returns once the CLI printed its end marker, or at the timeout
                proc.wait(timeout=int(cmd[cmd.index("--timeout") + 1]) / 1000)
                return self._ok({"result": {"matched_line": "bench-router-exited"}})
            except (AttributeError, subprocess.TimeoutExpired):
                return subprocess.CompletedProcess(cmd, 1, "", '{"error":{"code":"timeout"}}')
        if op == ["agent", "read"]:
            return subprocess.CompletedProcess(cmd, 0, self.screen, "")
        if op == ["pane", "get"]:
            if arg not in self.procs:
                return subprocess.CompletedProcess(cmd, 1, "", '{"error":{"code":"pane_not_found"}}')
            return self._ok({"result": {"pane": {"pane_id": arg, "terminal_id": self.terminal}}})
        if op == ["workspace", "close"]:
            if self.close_fail:
                self.close_fail -= 1
                return subprocess.CompletedProcess(cmd, 1, "", '{"error":{"code":"server_busy"}}')
            if arg in self.ws_closed:
                return subprocess.CompletedProcess(cmd, 1, "", '{"error":{"code":"workspace_not_found"}}')
            self.ws_closed.append(arg)
            self.agents = {n: c for n, c in self.agents.items() if f"{arg}:" not in " ".join(c)}
            for pane in [p for p in self.procs if p.startswith(arg + ":")]:
                proc = self.procs.pop(pane)
                if proc is None:
                    continue
                try:
                    os.killpg(proc.pid, 1)  # SIGHUP, as a closed terminal does
                except ProcessLookupError:
                    pass
                proc.wait()
            return self._ok({"result": {"type": "ok"}})
        raise AssertionError(cmd)


def result_dir(fake, prompt):
    rel = re.search(r"결과 디렉터리\(현재 worktree 기준 상대 경로\): (.+)", prompt).group(1)
    return Path(fake.worktree_of(prompt)) / rel


def headless_cli(exit_code=0, result=True):
    """Stand-in for `herdr pane run`: what the typed one-shot CLI would leave behind."""
    def act(fake, cmd):
        script = shlex.split(cmd)[2]
        wt = shlex.split(script.split(" && ")[0].removeprefix("{ "))[1]
        rd = Path(re.search(r"cat (\S+)/input\.txt", script).group(1))
        if wt == ".":
            wt = fake.worktree_of((rd / "input.txt").read_text("utf-8"))
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
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["--model", "m", "--effort", "high"])])

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
        return hd.dispatch(t or self.task(), self.cfg, MAPPING, None, [], session="default", runner=fake, which=w,
                           profile_id="a", selection_mode="orchestrator_pinned", **kw)

    def receipt(self, out):
        return json.loads(Path(out["receipt_path"]).read_text("utf-8"))

    def test_v99_discovery_uses_native_models_without_usage_queries(self):
        def runner(cmd, **kw):
            self.assertEqual(cmd, ["agy", "models"])
            return SimpleNamespace(returncode=0, stdout="gemini-4-argon-high\tGemini 4 Argon (High)\n", stderr="")
        profiles = hd.discover_profiles(which=lambda name: None if name == "claude" else "/usr/bin/tool", runner=runner,
                                        codex_cache=Path(self.tmp.name) / "missing.json", claude_models=[])
        self.assertEqual([p["id"] for p in profiles], ["agy-gemini-4-argon-high"])
        self.assertEqual(r.load_profiles(self._write_profiles(profiles))["profile"], profiles)

    def test_v108_discovers_unused_models_from_codex_cache_and_claude_guidance(self):
        cache = Path(self.tmp.name) / "models_cache.json"
        cache.write_text(json.dumps({"models": [
            {"slug": "gpt-6-astra", "visibility": "list", "supported_reasoning_levels": [{"effort": "low"}, {"effort": "ultra"}]},
            {"slug": "gpt-6.1-sol", "visibility": "list", "supported_reasoning_levels": [{"effort": "medium"}]},
            {"slug": "codex-auto-review", "visibility": "hide", "supported_reasoning_levels": [{"effort": "low"}]}]}), "utf-8")
        def runner(cmd, **kw):
            if cmd[0] == "claude":
                return SimpleNamespace(returncode=0, stdout="  --effort <level>  Effort level (low, max)\n", stderr="")
            rows = [{"provider": "codex", "model": "gpt-6.1-sol"}, {"provider": "claude", "model": "claude-opus-5-5"}]
            return SimpleNamespace(returncode=0 if cmd[0] != "agy" else 1, stdout=json.dumps(rows), stderr="")
        profiles = hd.discover_profiles(which=lambda name: "/usr/bin/tool", runner=runner, codex_cache=cache,
                                        claude_models=["claude-haiku-5-5", "claude-opus-5-5"])
        by_id = {p["id"]: p for p in profiles}
        self.assertEqual(sorted(by_id), ["claude-claude-haiku-5-5-low", "claude-claude-haiku-5-5-max",
                                         "claude-claude-opus-5-5-low", "claude-claude-opus-5-5-max",
                                         "codex-gpt-6-1-sol-medium", "codex-gpt-6-astra-low", "codex-gpt-6-astra-ultra"])
        # the cache's own efforts replace the default list; hidden internal models are not registered
        self.assertEqual(by_id["codex-gpt-6-1-sol-medium"]["config_revision"], "codex-models-cache")
        self.assertEqual(by_id["claude-claude-haiku-5-5-max"]["args"], ["--model", "claude-haiku-5-5", "--effort", "max"])
        self.assertEqual(by_id["claude-claude-opus-5-5-low"]["config_revision"], "claude-guidance")
        self.assertEqual(hd.codex_models(Path(self.tmp.name) / "missing.json"), {})

    def test_v97b_long_model_names_keep_distinct_effort_ids(self):
        runner = lambda cmd, **kw: SimpleNamespace(returncode=0 if cmd[0] == "claude" else 1, stderr="",
                                                   stdout="  --effort <level>  Effort level (low, medium, max)\n")
        profiles = hd.discover_profiles(which=lambda name: "/usr/bin/tool", runner=runner,
                                        codex_cache=Path(self.tmp.name) / "none.json", claude_models=["claude-" + "x" * 45])
        ids = [p["id"] for p in profiles]
        self.assertEqual((len(ids), len(set(ids))), (len(profiles), len(profiles)))
        self.assertTrue(len(profiles) > 1 and all(len(i) <= 48 for i in ids))

    def _write_profiles(self, profiles):
        path = Path(self.tmp.name) / "profiles.toml"
        path.write_text(hd.profiles_toml(profiles), "utf-8")
        return path

    def test_v98_external_selection_dispatch_and_receipt_first_recovery(self):
        from bench_router import decision
        self.cfg = config([*self.cfg["profile"], profile("b")])
        t = self.task()
        def evaluate(response=None):
            return decision.evaluate(t, self.cfg, MAPPING, None, [], NOW, host="codex", env={}, response=response)
        assessment = evaluate(guided_responses(evaluate(), evaluate, "__tie__"))
        self.assertIsNone(assessment["recommendation"]["profile"])
        self.assertIn("upstream_selection_required", assessment["recommendation"]["diagnostics"])
        selection = decision.bind(assessment, "b", {"id": "team", "version": "1"}, "specialist", True)
        fake = FakeProjects(on_prompt=write_result(), profiles={p["id"]: p for p in self.cfg["profile"]})
        def dispatch():
            return hd.dispatch(t, self.cfg, MAPPING, None, [], session="default", runner=fake, which=which,
                               selection=selection, decision_options={"host": "codex", "env": {}})
        out = dispatch()
        self.assertEqual((out["status"], out["selected"]["profile"], out["selection"]["schema_version"]),
                     ("completed", "b", "6.0"))
        with patch.object(decision, "load_guidelines", side_effect=AssertionError("must collect saved run")):
            again = dispatch()
        self.assertEqual((again["run_id"], len(fake.prompts)), (out["run_id"], 1))

    def test_v76_guided_live_preflight_and_receipt_first_recovery(self):
        from bench_router import decision
        fake = FakeProjects(on_prompt=write_result())
        fake.profiles = {p["id"]: p for p in self.cfg["profile"]}
        opts = {"host": "codex", "env": {}}
        pending = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], session="default", runner=fake,
                              which=which, decision_options=opts)
        self.assertEqual((pending["status"], fake.calls), ("decision_required", []))
        self.assertFalse((Path(self.cwd) / ".bench-router").exists())
        response = guided_responses(pending, lambda response: r.route(
            self.task(), self.cfg, MAPPING, None, [], NOW, host="codex", env={}, response=response), "a")
        first = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], session="default", runner=fake,
                            which=which, decision_options={**opts, "response": response})
        self.assertEqual((first["status"], first["selection"]["schema_version"]), ("completed", "5.0"))
        with patch.object(decision, "load_guidelines", side_effect=AssertionError("must recover without new choice")):
            again = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], session="default", runner=fake,
                                which=which, decision_options=opts)
        self.assertEqual((again["reused_receipt"], len(fake.prompts)), (True, 1))

    @patch("bench_router.herdr._now", return_value=NOW)
    def test_v35_pinned_profile_replay_and_retry_guidance(self, _now):
        self.cfg = config([*self.cfg["profile"], profile("b", kind="claude", executable="claude")])
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
        changed = config([*self.cfg["profile"], profile("b", kind="claude", executable="claude")])
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
        t = fake.tasks["repo#1"]
        self.assertEqual((out["thread_id"], out["worktree"], out["branch"]), ("repo#1", t["worktree"], t["branch"]))
        add = fake.adds[0]
        self.assertEqual(add[1], "br-" + out["run_id"])
        self.assertEqual(add[add.index("--agent") + 1:add.index("--agent") + 6],
                         ["claude", "--model", "m", "--effort", "high"])
        self.assertNotIn("--delegate", add)
        self.assertIn("review=off", add)
        self.assertIn("merge=ask me first", add)
        self.assertNotIn("--worker.access", add)
        self.assertIn("--prompt-file", add)
        self.assertTrue(Path(out["result_path"]).is_relative_to(self.cwd))  # copied next to the receipt

    def test_completed_agent_is_released_then_resumed(self):
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(fake)
        self.assertEqual((out["status"], fake.closed), ("completed", ["t1"]))
        self.assertEqual(out["release"]["terminals"], [{"terminal_id": "t1", "agent": "claude"}])
        res = hd.resume_run(self.cwd, out["run_id"], runner=fake)
        self.assertEqual((res["resumed"]["terminal_id"], res["resumed"]["session_resumed"]), ("t1", True))
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "completed")
        self.assertEqual(fake.closed, ["t1"])  # a resumed session is never closed again by the router
        self.assertEqual(len(fake.prompts), 1)  # resume sends nothing

    def test_poll_near_deadline_keeps_call_budget(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake)
        fake.kwargs.clear()
        res = hd.collect_run(self.cwd, out["run_id"], 1, runner=fake)  # the wait ends before the poll returns
        self.assertEqual(res["status"], "timed_out")  # still working, not delivery_uncertain
        self.assertEqual({kw["timeout"] for cmd, kw in fake.kwargs if cmd == "show"}, {hd.OBSERVE_FLOOR_S})

    def test_wait_zero_returns_after_submission(self):
        fake = FakeProjects(after_status="working", on_prompt=write_result())
        out = self.run_(fake, wait_ms=0)
        self.assertEqual((out["status"], len(fake.adds), out["thread_id"]), ("timed_out", 1, "repo#1"))
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
        self.assertEqual(len(fake.adds), 1)  # headless has a tracked board task
        cmd = shlex.split(fake.runs[0])[2]
        self.assertIn("claude -p --model m --effort high --dangerously-skip-permissions", cmd)
        self.assertNotIn("do the thing", cmd)  # the prompt reaches the CLI from input.txt only
        log = Path(hd.load_receipt(self.cwd, out["run_id"])["run_dir"]) / "output.log"
        self.assertTrue(cmd.endswith(f"2>&1 | tee {shlex.quote(str(log))}"), cmd)
        self.assertEqual((fake.reports, len(fake.closed)), ([], 1))
        with self.assertRaisesRegex(r.InputError, "headless"):
            hd.tell_run(self.cwd, out["run_id"], "hi", runner=fake)
        fake.calls.clear()
        with self.assertRaisesRegex(r.InputError, "headless"):
            hd.resume_run(self.cwd, out["run_id"], runner=fake)
        self.assertFalse(any(c[0] == "resume" for c in fake.calls))

    def test_headless_running_then_pane_closed_is_failure(self):
        fake = FakeProjects()  # no exit_code yet: the CLI is still running
        out = self.run_(fake, self.task(execution="headless"), wait_ms=0)
        self.assertEqual(out["status"], "timed_out")
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "timed_out")
        fake.panes.clear()  # closed by hand = stopped
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "execution_failed")

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
        self.assertEqual((res["status"], fake.tells), ("sent", [("t1", "use the v2 API")]))
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
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["release"]["terminals"][0]["terminal_id"], "t1")

    def test_v21_inexpressible_profile_sends_nothing(self):
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["--add-dir", "/x"])])
        fake = FakeProjects()
        out = self.run_(fake)
        self.assertEqual((out["status"], out["delivery_state"], fake.prompts), ("execution_failed", "not_attempted", []))
        missing = self.run_(FakeProjects(), self.task(task_id="missing"), w=lambda _: None)
        self.assertEqual(missing["excluded"], [{"profile": "a", "reasons": ["executable_not_found"]}])

    def test_v111_caller_owned_profile_is_not_dispatched(self):
        api = {k: v for k, v in profile("a").items() if k not in r.EXECUTION_KEYS}
        self.cfg = {"schema_version": "2.0", "profile": [api]}
        fake = FakeProjects()
        out = self.run_(fake)
        self.assertEqual(out["excluded"], [{"profile": "a", "reasons": ["unsupported_execution_profile"]}])
        self.assertEqual((fake.prompts, hd.receipts(self.cwd)), ([], []))
        ext = self.run_(fake, backend=hd.EXTERNAL_BACKEND)  # the caller owns its execution
        self.assertEqual((ext["status"], ext["invocation"]["argv"]), ("handed_off", None))
        def missing(*a, **kw):
            raise FileNotFoundError("herdr-projects")
        with self.assertRaisesRegex(r.InputError, "--dry-run"):
            hd.project_binding(runner=missing)

    def test_v112_external_runner_hands_off_and_collects(self):
        fake = FakeProjects()
        out = self.run_(fake, w=lambda _: None, backend=hd.EXTERNAL_BACKEND)  # the caller owns availability
        inv = out["invocation"]
        self.assertEqual((out["status"], out["reassignment"], out["backend"], fake.prompts),
                         ("handed_off", "collect_first", hd.EXTERNAL_BACKEND, []))
        from bench_router import cli
        self.assertEqual(cli.EXIT["handed_off"], 11)
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0)["status"], "handed_off")
        write_result()(SimpleNamespace(worktree_of=lambda _: inv["cwd"]), Path(inv["prompt_path"]).read_text("utf-8"))
        done = hd.collect_run(self.cwd, out["run_id"], 0)
        self.assertEqual((done["status"], done["task_outcome"]), ("completed", "success"))
        again = self.run_(fake, backend=hd.LOCAL_BACKEND)  # a recorded run keeps its backend and is never resent
        self.assertEqual((again["status"], again["reused_receipt"], again["backend"]), ("completed", True, hd.EXTERNAL_BACKEND))
        out = self.run_(fake, self.task(task_id="t2"), backend=hd.EXTERNAL_BACKEND, wait_ms=0)
        self.assertEqual(hd.stop_run(self.cwd, out["run_id"])["status"], "stop_sent")
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0)["status"], "execution_failed")

    def test_v112b_external_stop_yields_to_a_running_collect(self):
        out = self.run_(FakeProjects(), w=lambda _: None, backend=hd.EXTERNAL_BACKEND)
        with hd.dispatch_lock(self.cwd):
            res = hd.stop_run(self.cwd, out["run_id"])
        self.assertEqual(res["status"], "conflict")
        self.assertEqual(hd.stop_run(self.cwd, out["run_id"])["status"], "stop_sent")

    def test_v113_local_runner_runs_a_subprocess(self):
        self.enterContext(patch.object(hd, "time", time))  # a real process needs real waiting
        writer = (f"import os, sys; sys.path.insert(0, {str(Path(__file__).parent)!r}); from test_p2 import write_result; "
                  "from types import SimpleNamespace; write_result()(SimpleNamespace(worktree_of=lambda _: os.getcwd()), sys.argv[1])")
        cases = (([sys.executable, "-c", writer], "completed", "0"), (["sh", "-c", "exit 3", "x"], "execution_failed", "3"))
        for i, (argv, status, code) in enumerate(cases):
            with patch.object(hd, "headless_argv", return_value=argv):
                out = self.run_(FakeProjects(), self.task(task_id=f"t{i}", execution="headless"), backend=hd.LOCAL_BACKEND)
            self.assertEqual((out["status"], self.receipt(out)["exit_code"]), (status, code), out["last_observation"])
        with patch.object(hd, "headless_argv", return_value=["sleep", "30"]):
            out = self.run_(FakeProjects(), self.task(task_id="slow", execution="headless"), backend=hd.LOCAL_BACKEND, wait_ms=0)
        self.assertEqual(out["status"], "timed_out")
        self.assertEqual(hd.stop_run(self.cwd, out["run_id"])["status"], "stop_sent")
        for _ in range(50):  # SIGTERM is asynchronous
            res = hd.collect_run(self.cwd, out["run_id"], 0)
            if res["status"] != "timed_out":
                break
            time.sleep(0.1)
        self.assertEqual((res["status"], self.receipt(res)["process_exited"]), ("execution_failed", True))
        with self.assertRaisesRegex(r.InputError, "headless"):
            self.run_(FakeProjects(), self.task(task_id="board"), backend=hd.LOCAL_BACKEND)

    def test_v113b_herdr_tui_runner_runs_in_its_own_workspace(self):
        self.enterContext(patch.object(hd, "time", time))  # a real process needs real waiting
        writer = (f"import os, sys; sys.path.insert(0, {str(Path(__file__).parent)!r}); from test_p2 import write_result; "
                  "from types import SimpleNamespace; write_result()(SimpleNamespace(worktree_of=lambda _: os.getcwd()), sys.argv[1])")
        for i, (argv, status, code) in enumerate((([sys.executable, "-c", writer], "completed", "0"),
                                                  (["sh", "-c", "echo boom; exit 3", "x"], "execution_failed", "3"))):
            fake = FakeTui()
            with patch.object(hd, "headless_argv", return_value=argv):
                out = self.run_(fake, self.task(task_id=f"t{i}", execution="headless"), backend=hd.TUI_BACKEND)
            rc = self.receipt(out)
            self.assertEqual((out["status"], rc["exit_code"], out["backend"]), (status, code, hd.TUI_BACKEND), out["last_observation"])
            self.assertEqual((fake.ws_closed, rc["release"]["workspace_id"]), ([rc["workspace_id"]], rc["workspace_id"]))
            self.assertEqual(fake.runs[0][fake.runs[0].index("--cwd") + 1], rc["worktree"])  # the run's own worktree
            wait, = [w for w in fake.waits if w[1:3] == ["pane", "wait-output"]][:1]  # herdr waited, no 1 s polling
            self.assertEqual(wait[wait.index("--regex") + 1], f"^bench-router-exited-{rc['run_id']}$")
            self.assertNotRegex(fake.typed[0], f"bench-router-exited-{rc['run_id']}")  # the typed line never matches
        self.assertIn("boom", (Path(rc["run_dir"]) / "output.log").read_text("utf-8"))  # output survives the close
        fake = FakeTui()
        with patch.object(hd, "headless_argv", return_value=["sleep", "30"]):
            out = self.run_(fake, self.task(task_id="slow", execution="headless"), backend=hd.TUI_BACKEND, wait_ms=0)
        self.assertEqual(out["status"], "timed_out")
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "timed_out")  # pane still there
        self.assertIn("</dev/null 2>&1 | tee", fake.typed[0])  # stdin as in local, output kept
        self.assertNotIn("&& mv", fake.typed[0])  # exit_code is published only after tee has ended:
        self.assertRegex(fake.typed[0], r"\| tee \S+output\.log; mv \S+exit_code\.tmp \S+exit_code; printf ")
        home, fake.socket = fake.socket, "/home/u/.config/herdr/sessions/other/herdr.sock"  # another herdr session
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "delivery_uncertain")
        self.assertEqual(hd.stop_run(self.cwd, out["run_id"], runner=fake)["status"], "delivery_uncertain")
        self.assertEqual(fake.ws_closed, [])  # ids there name someone else's workspaces: nothing closed
        fake.socket = home
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "timed_out")
        self.assertEqual(hd.stop_run(self.cwd, out["run_id"], runner=fake)["status"], "stop_sent")
        res = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((res["status"], self.receipt(res)["process_exited"]), ("execution_failed", True))
        from bench_router import runners
        self.assertEqual(runners.stop({"backend": hd.TUI_BACKEND})["code"], "stop_error")  # dispatch not done yet
        fake = FakeTui()
        fake.close_fail = 1  # the close after settling fails once
        with patch.object(hd, "headless_argv", return_value=[sys.executable, "-c", writer]):
            out = self.run_(fake, self.task(task_id="retry", execution="headless"), backend=hd.TUI_BACKEND)
        self.assertEqual((out["status"], fake.ws_closed, "error" in self.receipt(out)["release"]), ("completed", [], True))
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "completed")
        rc = self.receipt(out)
        self.assertEqual((fake.ws_closed, "error" in rc["release"]), ([rc["workspace_id"]], False))  # retried, closed
        hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual(fake.ws_closed, [rc["workspace_id"]])  # nothing left to retry
        fake = FakeTui()
        with patch.object(hd, "headless_argv", return_value=["sleep", "30"]):
            out = self.run_(fake, self.task(task_id="gone", execution="headless"), backend=hd.TUI_BACKEND, wait_ms=0)
        rc = self.receipt(out)
        fake.ws_closed.append(rc["workspace_id"])  # closed (stop or a human) just as the CLI wrote its exit code
        (Path(rc["run_dir"]) / "exit_code").write_text("0\n", "utf-8")
        res = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertNotIn("error", self.receipt(res)["release"])  # already closed counts as released, no retries
        for proc in fake.procs.values():
            os.killpg(proc.pid, 9)
            proc.wait()
        fake = FakeTui()  # herdr restarts while the CLI runs: same pane id, new shell, nothing running
        with patch.object(hd, "headless_argv", return_value=["sleep", "30"]):
            out = self.run_(fake, self.task(task_id="restart", execution="headless"), backend=hd.TUI_BACKEND, wait_ms=0)
        rc = self.receipt(out)
        self.assertEqual(rc["herdr_terminal"], "term_1")
        fake.restart()
        res = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((res["status"], fake.ws_closed), ("execution_failed", [rc["workspace_id"]]))  # not "running" forever
        self.assertIn("replaced", res["last_observation"]["note"])
        fake = FakeTui()
        fake.version = "0.9.1"  # before 0.9.2 there is no completion_seq: refused before anything starts
        with patch.object(hd, "headless_argv", return_value=["true"]):
            out = self.run_(fake, self.task(task_id="old", execution="headless"), backend=hd.TUI_BACKEND)
        self.assertEqual((out["status"], fake.runs), ("execution_failed", []))
        self.assertIn("herdr update", out["last_observation"]["note"])
        fake.version = "0.9.2"  # the oldest accepted server
        with patch.object(hd, "headless_argv", return_value=["true"]):
            self.run_(fake, self.task(task_id="oldest", execution="headless"), backend=hd.TUI_BACKEND)
        self.assertEqual(len(fake.runs), 1)  # its workspace was created
        fake = FakeTui(run_error="herdr: server not running")
        with patch.object(hd, "headless_argv", return_value=["true"]):
            out = self.run_(fake, self.task(task_id="lost", execution="headless"), backend=hd.TUI_BACKEND)
        self.assertEqual(out["status"], "delivery_uncertain")
        again = self.run_(fake, self.task(task_id="lost", execution="headless"), backend=hd.TUI_BACKEND)
        self.assertEqual((again["reused_receipt"], len(fake.runs)), (True, 1))  # never typed a second time
        with self.assertRaisesRegex(r.InputError, "headless"):
            self.run_(FakeTui(), self.task(task_id="board"), backend=hd.LOCAL_BACKEND)
        self.assertEqual(hd.resolve_runner("herdr-tui", lambda _: None), hd.TUI_BACKEND)

    def test_v113c_herdr_tui_interactive_runs_a_live_agent(self):
        fake = FakeTui()
        out = self.run_(fake, self.task(task_id="chat"), backend=hd.TUI_BACKEND, wait_ms=0)
        rc = self.receipt(out)
        self.assertEqual(out["status"], "timed_out")  # the turn was seen working; not finished
        self.assertEqual(fake.last_prompt_cmd[5:], ["--wait", "--until", "working", "--until", "blocked", "--timeout", "20000"])
        start = next(iter(fake.agents.values()))
        self.assertEqual((start[start.index("--kind") + 1], start[start.index("--pane") + 1], start[start.index("--") + 1:]),
                         ("claude", rc["pane_id"], ["--model", "m", "--effort", "high"]))
        (name, prompt), = fake.agent_prompts
        self.assertEqual(name, rc["agent_name"])
        self.assertIn("do the thing", prompt)
        self.assertIn("end your turn", prompt)
        self.assertEqual(hd.tell_run(self.cwd, out["run_id"], "also this", runner=fake)["status"], "sent")
        self.assertEqual(fake.agent_prompts[-1], (name, "also this"))
        self.assertIn("--wait", fake.last_prompt_cmd)  # tell, too, returns only once herdr saw the turn
        fake.agent_status = "blocked"  # a permission question: surfaced, nothing closed
        res = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((res["status"], self.receipt(res)["diagnostic_tail"], fake.ws_closed),
                         ("blocked", fake.screen, []))
        self.assertEqual(hd.tell_run(self.cwd, out["run_id"], "x", runner=fake)["status"], "delivery_uncertain")
        fake.agent_status = "working"  # answered in the pane
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "timed_out")
        fake.socket = "/other/herdr.sock"
        with self.assertRaisesRegex(r.InputError, "another herdr server"):
            hd.tell_run(self.cwd, out["run_id"], "x", runner=fake)
        fake.socket = "/home/u/.config/herdr/herdr.sock"
        fake.agent_status = "idle"  # idle but herdr marks no finished turn: not settled
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "timed_out")
        fake.finish()  # turn ended without results: invalid, workspace stays for inspection
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "result_invalid")
        self.assertEqual(fake.ws_closed, [])
        # a second run, finished with valid results: completed, its own workspace closed
        fake = FakeTui()  # the receipt already says "attempted" while the prompt is in flight (a crash there must not resend)
        seen = []
        fake.on_agent_prompt = lambda: seen.append(next(x for x in hd.receipts(self.cwd) if x["task_id"] == "chat2")["delivery_state"])
        out = self.run_(fake, self.task(task_id="chat2"), backend=hd.TUI_BACKEND, wait_ms=0)
        self.assertEqual(seen, ["submission_attempted"])
        rc = self.receipt(out)
        write_result()(SimpleNamespace(worktree_of=lambda _: rc["worktree"]), fake.agent_prompts[0][1])
        fake.finish("idle")  # the first turn wrote valid results, but nobody collected yet
        self.assertEqual(hd.tell_run(self.cwd, out["run_id"], "one more change", runner=fake)["status"], "sent")
        res = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((res["status"], fake.ws_closed), ("timed_out", []))  # the told turn runs on, not cut off
        fake.finish()
        res = hd.collect_run(self.cwd, out["run_id"], 60000, runner=fake)
        self.assertEqual((res["status"], fake.ws_closed), ("completed", [rc["workspace_id"]]))
        wait = fake.waits[-1]  # the waiting collect asked herdr to block, instead of polling agent get each second
        self.assertEqual((wait[1:3], wait[wait.index("--until") + 1]), (["agent", "wait"], "idle"))
        self.assertIn("--timeout", wait)
        with self.assertRaisesRegex(r.InputError, "settled"):
            hd.tell_run(self.cwd, out["run_id"], "late", runner=fake)
        # the agent cannot start (folder trust question): nothing sent, workspace closed, round stays free
        fake = FakeTui()
        fake.start_error = '{"error":{"code":"agent_not_ready"}}'
        out = self.run_(fake, self.task(task_id="trust"), backend=hd.TUI_BACKEND, wait_ms=0)
        self.assertEqual((out["status"], fake.prompt_calls, len(fake.ws_closed)), ("execution_failed", 0, 1))
        self.assertIn("nothing sent", out["last_observation"]["note"])
        self.assertIn("trust", out["last_observation"]["note"])
        # herdr restarts mid-turn and resumes the conversation in a new terminal: failed, not "working" forever
        fake = FakeTui()
        out = self.run_(fake, self.task(task_id="restart2"), backend=hd.TUI_BACKEND, wait_ms=0)
        fake.restart()
        res = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual((res["status"], len(fake.ws_closed)), ("execution_failed", 1))
        # the agent vanished (workspace closed by a human)
        fake = FakeTui()
        out = self.run_(fake, self.task(task_id="gone2"), backend=hd.TUI_BACKEND, wait_ms=0)
        fake.agents.clear()
        self.assertEqual(hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)["status"], "execution_failed")
        # interactive tasks need a profile herdr can express and a prompt that fits one argument
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["--add-dir", "/x"])])
        out = self.run_(FakeTui(), self.task(task_id="args"), backend=hd.TUI_BACKEND, wait_ms=0)
        self.assertEqual(out["status"], "execution_failed")
        self.cfg = config([profile("a", kind="claude", executable="claude", args=["--model", "m", "--effort", "high"])])
        # last: an unresolved run holds the repository, so nothing can follow it
        # a lost prompt response is never resubmitted
        fake = FakeTui()
        fake.prompt_error = "herdr: timeout"
        out = self.run_(fake, self.task(task_id="lost2"), backend=hd.TUI_BACKEND, wait_ms=0)
        self.assertEqual(out["status"], "delivery_uncertain")
        self.run_(fake, self.task(task_id="lost2"), backend=hd.TUI_BACKEND, wait_ms=0)
        self.assertEqual(fake.prompt_calls, 1)
        res = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)  # idle, but no turn ever finished
        self.assertEqual(res["status"], "timed_out")  # left for a human to inspect, never settled as invalid

    def test_v114_auto_runner_follows_herdr_projects_on_path(self):
        self.assertEqual(hd.resolve_runner("auto", which), hd.BACKEND)
        self.assertEqual(hd.resolve_runner("auto", lambda _: None), hd.LOCAL_BACKEND)
        self.assertEqual(hd.resolve_runner("external", lambda _: None), hd.EXTERNAL_BACKEND)
        with patch.dict(os.environ, {"BENCH_ROUTER_RUNNER": "local"}):
            self.assertEqual(hd.resolve_runner(None, which), hd.LOCAL_BACKEND)
        with self.assertRaises(r.InputError):
            hd.resolve_runner("cloud", which)

    def test_validated_results_handoff_once_without_merging_or_cleanup(self):
        from bench_router.lifecycle import finalize
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(fake)
        rc = self.receipt(out)
        self.assertEqual(rc["ready"]["state"], "ready")
        self.assertTrue(Path(out["worktree"]).exists())
        self.assertTrue(Path(out["result_path"]).exists())
        self.assertTrue(finalize(rc, fake))
        self.assertEqual(sum(c[0] == "ready" for c in fake.calls), 1)
        self.assertFalse(any(c[0] in ("accept", "merge", "done") for c in fake.calls))
        self.assertFalse(any(c[0] == "hc" and c[1] == "rm" for c in fake.calls))
        self.assertFalse(subprocess.run(["git", "-C", self.cwd, "branch", "--list", "br-base/*"],
                                        check=True, capture_output=True, text=True).stdout.strip())

    def test_ready_can_remove_worktree_after_result_copy(self):
        fake = FakeProjects(on_prompt=write_result())
        def cleanup_on_ready(cmd, **kw):
            if cmd[1] == "ready":
                task = fake.tasks[cmd[2]]
                subprocess.run(["git", "-C", task["folder"], "worktree", "remove", "--force", task["worktree"]],
                               check=True, capture_output=True)
            return fake(cmd, **kw)
        out = self.run_(cleanup_on_ready)
        self.assertEqual(out["status"], "completed")
        self.assertFalse(Path(out["worktree"]).exists())
        self.assertIsNone(hd.check_result(self.receipt(out))[1])

    def test_ready_skips_partial_and_legacy_runs(self):
        from bench_router.lifecycle import finalize
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(fake)
        rc = self.receipt(out)
        fake.calls.clear()
        for extra in ({"task_outcome": "partial"}, {"base_branch": "br-base/old"}):
            self.assertFalse(finalize({**rc, "ready": None, **extra}, fake))
        self.assertFalse(fake.calls)

    def test_ready_response_loss_does_not_repeat_submission(self):
        from bench_router.lifecycle import finalize
        fake = FakeProjects(on_prompt=write_result())
        def lost(cmd, **kw):
            if cmd[1] == "ready":
                raise subprocess.TimeoutExpired(cmd, 15)
            return fake(cmd, **kw)
        out = self.run_(lost)
        rc = self.receipt(out)
        self.assertEqual(rc["ready"]["state"], "uncertain")
        self.assertFalse(finalize(rc, fake))
        self.assertFalse(any(c[0] == "ready" for c in fake.calls))

    def test_worker_settings(self):
        p = lambda kind, args: {"kind": kind, "args": args}
        self.assertEqual(hd.worker_settings(p("claude", [])), ["--agent", "claude", "--model", "default"])
        self.assertEqual(hd.worker_settings(p("codex", ["-m", "x", "-c", 'model_reasoning_effort="high"'])),
                         ["--agent", "codex", "--model", "x", "--effort", "high"])
        for bad in (["--add-dir", "/x"], ["-m"], ["-c", "sandbox=x"]):
            self.assertIsNone(hd.worker_settings(p("codex", bad)), bad)

    def test_agy_interactive_keeps_profile_flags_through_start_and_resume(self):
        for i, args in enumerate((["--model", "gemini-4-argon", "--effort", "high"],
                                  ["--model", "gemini-4-argon-high"], [])):
            with self.subTest(args=args):
                self.cfg = config([profile("a", kind="agy", executable="agy", args=args)])
                fake = FakeProjects(on_prompt=write_result())
                out = self.run_(fake, self.task(task_id=f"agy-{i}"))
                self.assertEqual(out["status"], "completed")
                task = fake.tasks[out["thread_id"]]
                expected = ["agy", *args, "--prompt-interactive"]
                self.assertEqual(task["argv"], expected)
                self.assertNotIn("--dangerously-skip-permissions", task["argv"])
                hd.resume_run(self.cwd, out["run_id"], runner=fake)
                self.assertEqual(task["resumed_argv"], expected)

    def test_codex_interactive_runs_without_sandbox_through_start_and_resume(self):
        p = profile("a")
        args = p["args"]
        self.cfg = config([p])
        fake = FakeProjects(on_prompt=write_result())
        out = self.run_(fake, self.task(task_id="codex-sbx"))
        self.assertEqual(out["status"], "completed")
        task = fake.tasks[out["thread_id"]]
        expected = ["codex", *args, "--dangerously-bypass-approvals-and-sandbox"]
        self.assertEqual(task["argv"], expected)
        hd.resume_run(self.cwd, out["run_id"], runner=fake)
        self.assertEqual(task["resumed_argv"], expected)

    def test_shepherdr_split_start_recovers_without_starting_twice(self):
        fake = FakeProjects(on_prompt=write_result())
        fake.start_error = True
        out = self.run_(fake)
        self.assertEqual((out["status"], out["thread_id"]), ("delivery_uncertain", "repo#1"))
        fake.start_error = False
        self.assertEqual(self.run_(fake)["status"], "completed")
        self.assertEqual((len(fake.adds), len(fake.prompts)), (1, 1))

    def test_shepherdr_worktrees_off_never_starts_in_user_checkout(self):
        fake = FakeProjects()
        fake.mode = "here"
        out = self.run_(fake)
        self.assertEqual((out["status"], fake.prompts), ("execution_failed", []))
        self.assertEqual(len(fake.adds), 1)
        from bench_router import coordination
        self.assertEqual(coordination.inspect()["active"], 0)

    def test_target_branch_failure_settles_before_submission(self):
        from bench_router import parallel, coordination
        original = parallel._git
        def git(cwd, *args, **kwargs):
            if args[0] == "branch":
                raise r.InputError("cannot lock ref")
            return original(cwd, *args, **kwargs)
        fake = FakeProjects()
        with patch.object(parallel, "_git", side_effect=git):
            out = self.run_(fake)
        self.assertEqual((out["status"], out["delivery_state"], fake.adds),
                         ("execution_failed", "not_attempted", []))
        self.assertEqual(coordination.inspect()["active"], 0)

    def test_shepherdr_finished_turn_hands_off_after_collection(self):
        fake = FakeProjects(on_prompt=write_result())
        fake.updates = {"state": "running", "status": "working", "needs": None}
        out = self.run_(fake)
        self.assertEqual(out["status"], "completed")
        self.assertIn("do not call herdr-task ready", fake.prompts[0])
        self.assertTrue(any(c[0] == "ready" for c in fake.calls))
        self.assertFalse(any(c[0] in ("accept", "done") for c in fake.calls))

    def test_legacy_receipt_never_controls_new_core(self):
        fake = FakeProjects(after_status="working")
        out = self.run_(fake, wait_ms=0)
        rc = self.receipt(out)
        rc["backend"] = "projects-1.2"
        hd.save(rc)
        fake.calls.clear()
        for operation in (lambda: hd.collect(rc, 0, runner=fake),
                          lambda: hd.stop_run(self.cwd, out["run_id"], runner=fake),
                          lambda: hd.resume_run(self.cwd, out["run_id"], runner=fake),
                          lambda: hd.tell_run(self.cwd, out["run_id"], "hello", runner=fake)):
            with self.assertRaises(r.InputError):
                operation()
        self.assertEqual(fake.calls, [])

    def test_auto_requires_core_and_task_cli(self):
        for missing in (hd.HERDR_BIN, hd.PROJECTS_BIN):
            self.assertEqual(hd.resolve_runner("auto", lambda name: None if name == missing else "/bin/tool"),
                             hd.LOCAL_BACKEND)

    def test_stop_cancels_queued_task_without_starting_it_again(self):
        fake = FakeProjects(after_status="working")
        fake.pending = fake.queue_only = True
        out = self.run_(fake, wait_ms=0)
        self.assertEqual(hd.stop_run(self.cwd, out["run_id"], runner=fake)["status"], "stop_sent")
        got = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual(got["status"], "execution_failed")
        self.assertTrue(self.receipt(got)["process_exited"])
        self.assertEqual(len(fake.prompts), 0)

    def test_stop_cancels_queued_headless_card(self):
        fake = FakeProjects(after_status="working")
        fake.pending = fake.queue_only = True
        out = self.run_(fake, self.task(execution="headless"), wait_ms=0)
        self.assertEqual(hd.stop_run(self.cwd, out["run_id"], runner=fake)["status"], "stop_sent")
        got = hd.collect_run(self.cwd, out["run_id"], 0, runner=fake)
        self.assertEqual(got["status"], "execution_failed")
        self.assertTrue(self.receipt(got)["process_exited"])

    def test_per_repository_space_is_recorded_and_replayed(self):
        path = Path(self.cwd) / ".bench-router" / "shepherdr.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text('{"space":"sp-repository"}', "utf-8")
        fake = FakeProjects(on_prompt=write_result())
        with patch.dict(os.environ, {"BENCH_ROUTER_HERDR_SESSION":"", "BENCH_ROUTER_SPACE":""}):
            out = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], runner=fake, which=which, profile_id="a")
            self.assertEqual(self.receipt(out)["herdr_session"], "sp-repository")
            path.unlink()
            again = hd.dispatch(self.task(), self.cfg, MAPPING, None, [], runner=fake, which=which, profile_id="a")
            self.assertEqual((again["status"], len(fake.prompts)), ("completed", 1))

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
        self.assertTrue(all(0 < kw["timeout"] <= 5 for cmd, kw in fake.kwargs if cmd not in ("--version",)))
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

    def test_dispatch_lock_waits_out_a_brief_holder(self):
        import threading
        held = threading.Event()
        def observer():
            with hd.dispatch_lock(self.cwd):
                held.set()
                REAL_SLEEP(0.3)
        th = threading.Thread(target=observer)
        th.start()
        held.wait()
        with hd.dispatch_lock(self.cwd):  # a brief observer poll is not a conflict
            pass
        th.join()

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
        fake.version = "2"
        with self.assertRaises(r.InputError):
            self.run_(fake)
        self.assertEqual((fake.prompts, hd.receipts(self.cwd)), ([], []))

    def test_newer_core_version_is_accepted(self):
        fake = FakeProjects(on_prompt=write_result())
        fake.core_version = "hc 0.1.19"
        self.assertEqual(self.run_(fake)["status"], "completed")

    def test_message_log_survives_unicode_line_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = {"run_dir": tmp}
            hd._log_event(rc, {"state": "sent", "text": "pasted\u2028text"})
            hd._log_event(rc, {"state": "stop_sent"})
            self.assertEqual([e["state"] for e in hd._events(rc)], ["sent", "stop_sent"])

    def test_prompt_size_limit(self):
        with self.assertRaises(r.InputError):
            self.run_(FakeProjects(), self.task(prompt="x" * hd.MAX_PROMPT_ARG_BYTES))

    def test_prepare_repo_rejects_non_git_without_writes(self):
        from bench_router import parallel
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "hello.txt"
            source.write_text("private data")
            with self.assertRaises(r.InputError):
                parallel.prepare_repo(tmp)
            self.assertFalse((Path(tmp) / ".git").exists())
            self.assertEqual(source.read_text(), "private data")

    def test_prepare_repo_rejects_unborn_repo_without_staging(self):
        from bench_router import parallel
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "-C", tmp, "init", "-q"], check=True)
            source = Path(tmp) / "hello.txt"
            source.write_text("private data")
            with self.assertRaises(r.InputError):
                parallel.prepare_repo(tmp)
            staged = subprocess.run(["git", "-C", tmp, "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
            self.assertEqual(staged.stdout, "")
            self.assertEqual(source.read_text(), "private data")

    def test_prepare_repo_fails_when_git_missing(self):
        from bench_router import parallel
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(parallel.shutil, "which", return_value=None):
                with self.assertRaisesRegex(r.InputError, "git is not installed"):
                    parallel.prepare_repo(tmp)


class P2Availability(unittest.TestCase):
    def test_agy_native_model_list_precedes_codexbar_quota(self):
        def runner(cmd, **kw):
            if cmd[:2] == ["agy", "models"]:
                return SimpleNamespace(returncode=0, stdout="gemini-4-argon-high\tGemini 4 Argon (High)\n", stderr="")
            return SimpleNamespace(returncode=0, stdout=json.dumps([{"provider": "antigravity", "source": "cli", "usage": {"updatedAt": hd._iso(hd._now()), "primary": {"usedPercent": 10}}}]), stderr="")
        profiles = [profile("ok", kind="agy", executable="agy", args=["--model", "gemini-4-argon-high"]),
                    profile("missing", kind="agy", executable="agy", args=["--model", "gone-high"])]
        with patch.object(hd.shutil, "which", return_value="/usr/bin/tool"):
            got = hd.probe_profiles(profiles, which=lambda _: "/usr/bin/tool", runner=runner)
        self.assertEqual(got, {"ok": None, "missing": "agy_model_unavailable"})


if __name__ == "__main__":
    unittest.main()
