"""Shepherdr adapter: the herdr-task and hc (herdr-core) CLIs behind the Board port (board.py).

herdr.py (the router) owns receipts, events and success decisions. It drives Shepherdr runs through the
lower-level calls below, which keep the router's pre-port behavior exactly; the Board methods are built on
the same calls. Nothing here writes a receipt.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from . import routing as r
from .board import CAPABILITIES

PROJECTS_BIN = os.environ.get("BENCH_ROUTER_TASKS", "herdr-task")
HERDR_BIN = os.environ.get("BENCH_ROUTER_HC", "hc")
BACKEND = "shepherdr-3"
TASK_PROTOCOL = "1"  # herdr-task --version is its protocol, not Shepherdr's release number
SHORT_CALL_S = 15
START_CALL_S = 60  # task start may prepare a worktree before it answers
WORK_SETTINGS = ["--worktree", "--set", "review=off", "--set", "merge=ask me first", "--set", "proof=off"]
PROMPT_NOTE = ("\nShepherdr: do not call herdr-task ready, done, accept or merge yourself. "
               "Commit requested code changes, keep this worktree and branch, then write results and end your turn. "
               "bench-router validates and copies results before marking the task Ready; the person accepts it.\n")


class BoardError(Exception):
    """A Shepherdr call failed after it may have had an effect (lost response). error: project_call's error dict."""

    def __init__(self, error):
        super().__init__((error or {}).get("message"))
        self.error = error


def project_call(argv, runner=subprocess.run, raw=False, timeout_s=SHORT_CALL_S, exe=None):
    cmd = [exe or PROJECTS_BIN, *argv]
    try:
        p = runner(cmd, capture_output=True, text=True, encoding="utf-8", errors="strict",
                   timeout=timeout_s, shell=False)
        if p.returncode:
            raise ValueError((p.stderr or p.stdout)[:300])
        if len(p.stdout.encode("utf-8")) > r.SNAPSHOT_MAX_BYTES:
            raise ValueError("Shepherdr response too large")
        return (p.stdout if raw else json.loads(p.stdout)), None
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, {"code": "shepherdr_error", "message": str(e)[:300]}


def project_binding(session=None, runner=subprocess.run, core_session=None, call=None):
    """Bind to the task protocol and core build, never interpret legacy Projects receipts as tasks.
    call: the project_call to use (the router passes its own so it can be replaced as one seam)."""
    call = call or project_call
    # T5: 3.2 runs in $SHEPHERDR_SESSION or "shepherdr", not HC_SESSION/default (docs/evidence/shepherdr-spike.md).
    core_session = core_session or os.environ.get("HC_SESSION") or "default"
    version, err = call(["--version"], runner, raw=True)
    if err or (version or "").strip() != TASK_PROTOCOL:
        raise r.InputError("Shepherdr 3.x herdr-task protocol 1 is required for live dispatch; "
                           "install Shepherdr, use --runner local|external, or use route --dry-run")
    core, err = call(["--version"], runner, raw=True, exe=HERDR_BIN)
    m = re.fullmatch(r"hc (\d+)\.(\d+)\.(\d+)(?:[-+ ].*)?", (core or "").strip())
    if err or not m or tuple(map(int, m.groups())) < (0, 1, 17):
        raise r.InputError("Shepherdr requires herdr-core (hc) >= 0.1.17")
    space = session or os.environ.get("BENCH_ROUTER_SPACE") or os.environ.get("BENCH_ROUTER_HERDR_SESSION")
    if not space and os.environ.get("HC_TERMINAL_ID"):
        obj, err = call(["get", os.environ["HC_TERMINAL_ID"], "--json"], runner, exe=HERDR_BIN)
        labels = (obj or {}).get("labels", {})
        space = labels.get("herdr.space") or labels.get("herdr.task.space") or labels.get("herdr.coordinator.space")
    if not isinstance(space, str) or not space.strip() or "/" in space:
        raise r.InputError("a local Shepherdr space is required: use --herdr-space SPACE or BENCH_ROUTER_SPACE")
    return {"task_protocol": TASK_PROTOCOL, "core_version": core.strip(), "space": space, "session": core_session}


def bound_runner(rc, runner):
    """Run task and core commands in the session recorded before submission."""
    core_session = rc["project_binding"]["session"]
    def run(cmd, **kwargs):
        env = {**kwargs.pop("env", os.environ), "HC_SESSION": core_session}
        if (os.environ.get("HC_SESSION") or "default") != core_session:
            for key in ("HC_SOCKET", "HC_TERMINAL_SOCKET", "HC_TERMINAL_ID"):
                env.pop(key, None)
        return runner(cmd, env=env, **kwargs)
    return run


def _repo(rc):
    return rc.get("repo_cwd", rc["cwd"]) if "cwd" in rc else rc.get("repo_cwd")


class ShepherdrBoard:
    """Board adapter. runner: already bound to the run's core session (bound_runner) by the router."""
    backend = BACKEND

    def __init__(self, runner=subprocess.run, call=None, capabilities=CAPABILITIES):
        self.runner, self.call, self.capabilities = runner, call or project_call, frozenset(capabilities)

    def _tasks(self, argv, **kw):
        return self.call(argv, self.runner, **kw)

    def _core(self, argv, **kw):
        return self.call(argv, self.runner, exe=HERDR_BIN, **kw)

    # ---- router calls (behavior kept from herdr.py) ----

    def add(self, rc, settings, base, timeout_s):
        """Add this run's card without starting it. Returns (row, err); row is None unless confirmed."""
        obj, err = self._tasks(["add", "br-" + rc["run_id"], "--prompt-file", str(Path(rc["run_dir"]) / "input.txt"),
                                "--folder", _repo(rc), "--base", base, "--branch", f"br/{rc['run_id']}",
                                *settings, *WORK_SETTINGS, "--json"], timeout_s=timeout_s)
        if err or not isinstance(obj, dict) or not re.fullmatch(r"[^#\s]+#[0-9]+", str(obj.get("key", ""))) \
                or type(obj.get("id")) is not int or obj["id"] < 1 or not obj["key"].endswith(f"#{obj['id']}") \
                or obj.get("title") != "br-" + rc["run_id"] or obj.get("folder") != _repo(rc) or obj.get("agent") != rc.get("kind"):
            return None, err
        return obj, None

    @staticmethod
    def launch_args(profile, script=None):
        """start --argv override: a headless sh script, or the agent CLI when Shepherdr cannot translate its flags."""
        if script is not None:
            return ["--argv", json.dumps(["sh", "-c", script])]
        # Shepherdr only translates model/effort for Claude and Codex. Its public argv override keeps agy's flags.
        # Codex's workspace-write sandbox cannot commit in a git worktree (the lock files live in the main .git).
        return (["--argv", json.dumps([profile["executable"], *profile["args"], "--prompt-interactive"])]
                if profile["kind"] == "agy" else
                ["--argv", json.dumps([profile["executable"], *profile["args"],
                                       "--dangerously-bypass-approvals-and-sandbox"])]
                if profile["kind"] == "codex" else [])

    def start_task(self, rc, launch_args, timeout_s):
        """Start the added card. Returns (row, err); row is None unless the response is an object."""
        obj, err = self._tasks(["start", rc["thread_id"], "--folder", _repo(rc), "--space", rc["project_binding"]["space"],
                                *launch_args, "--json"], timeout_s=timeout_s)
        return (None, err) if err or not isinstance(obj, dict) else (obj, None)

    def watch(self, rc):
        """One durable core terminal observes the run and its later merge even when the caller disconnects."""
        return self._core(["run", "--bg", "--rm", "--json", "--no-parent",
            "--label", f"bench-router.watch={rc['run_id']}", "--", "env",
            f"PYTHONPATH={Path(__file__).resolve().parents[1]}", sys.executable, "-m", "bench_router.lifecycle",
            "--cwd", rc["cwd"], "--run-id", rc["run_id"]])

    # ---- Board port ----

    def bind(self, session, cwd):
        return project_binding(session, self.runner, None, self.call)

    def create(self, rc):
        obj, err = self.add(rc, rc.get("board_settings", []), rc.get("base", "main"), START_CALL_S)
        if obj is None:
            raise BoardError(err or {"code": "shepherdr_error", "message": "task add unconfirmed"})
        return {"thread_id": obj["key"], "task_id_on_board": obj["id"]}

    def start(self, rc):
        b = rc["binding"]
        current = project_binding(b["space"], self.runner, b["session"], self.call)
        if any(current[k] != b[k] for k in ("task_protocol", "space", "session")):
            raise r.InputError("Shepherdr binding changed since bind; nothing started")
        obj, err = self.start_task({**rc, "project_binding": b}, rc.get("launch_args", []), START_CALL_S)
        if obj is None:
            raise BoardError(err or {"code": "shepherdr_error", "message": "task start unconfirmed"})
        return {"terminal_id": obj.get("terminal"), "worktree": obj.get("worktree"), "branch": obj.get("branch")}
