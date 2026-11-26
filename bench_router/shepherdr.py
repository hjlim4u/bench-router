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
from .board import CAPABILITIES, observation

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
    """herdr.repo_cwd; a port-only rc (no receipt) uses the folder given to bind()."""
    return rc.get("repo_cwd", rc["cwd"]) if "cwd" in rc else rc.get("repo_cwd") or (rc.get("binding") or {}).get("folder")


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
        obj, err = self._tasks(["add", "br-" + rc["run_id"], "--prompt-file", str(Path(rc.get("run_dir", ".")) / "input.txt"),
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

    def task(self, rc, timeout_s=SHORT_CALL_S):
        """show the recorded card; InputError unless it is this run's. Records the card's worktree/branch in rc."""
        obj, err = self._tasks(["show", rc["thread_id"], "--folder", _repo(rc), "--json"], timeout_s=timeout_s)
        if err or not isinstance(obj, dict) or obj.get("key") != rc["thread_id"] or type(obj.get("id")) is not int or obj.get("id") != rc.get("task_id_on_board") \
                or obj.get("title") != "br-" + rc["run_id"] or obj.get("folder") != _repo(rc) \
                or obj.get("agent") != rc.get("kind"):
            raise r.InputError("Shepherdr task identity differs from the receipt")
        if obj.get("state") not in ("todo", "queued", "scheduled"):
            wt = obj.get("worktree")
            if obj.get("mode") != "worktree" or not isinstance(wt, str) or not os.path.isabs(wt) \
                    or os.path.realpath(wt) == os.path.realpath(_repo(rc)) or obj.get("branch") != f"br/{rc['run_id']}":
                raise r.InputError("Shepherdr task worktree differs from the receipt")
            if rc.get("worktree") and os.path.realpath(wt) != os.path.realpath(rc["worktree"]):
                raise r.InputError("Shepherdr task worktree changed")
            rc.update(worktree=wt, branch=obj["branch"])
        return obj

    def verify_terminal(self, rc, terminal):
        label = f"herdr.task={rc['thread_id']}" if rc.get("thread_id") else f"bench-router.run={rc['run_id']}"
        obj, err = self._core(["ls", "--label", label, "--json"])
        if err or not isinstance(obj, dict) or not isinstance(obj.get("terminals"), list) or not any(
                t.get("address") == terminal for t in obj["terminals"] if isinstance(t, dict)):
            raise r.InputError("recorded terminal is absent from the task's core session")

    def terminal_state(self, terminal, timeout_s):
        """hc get state: "live" or "exited"; InputError otherwise."""
        obj, err = self._core(["get", terminal, "--json"], timeout_s=timeout_s)
        if err:
            raise r.InputError(err["message"])
        # T5: hc 0.1.20 reports an ended terminal as "finished", which this rejects (docs/evidence/shepherdr-spike.md).
        if not isinstance(obj, dict) or obj.get("state") not in ("live", "exited"):
            raise r.InputError("unexpected hc terminal response")
        return obj["state"]

    def kill(self, terminal, raw=False):
        """End one core terminal; returns the call's error or None."""
        return self._core(["kill", terminal, "--json"], raw=raw)[1]

    def reopen(self, rc):
        """Cancel a queued card back to To do; True only when the board confirms it."""
        obj, err = self._tasks(["reopen", rc["thread_id"], "--folder", _repo(rc), "--json"])
        return not err and isinstance(obj, dict) and obj.get("key") == rc["thread_id"] and obj.get("state") == "todo"

    # ---- Board port ----

    def bind(self, session, cwd):
        return {**project_binding(session, self.runner, None, self.call), "folder": cwd}

    def _process(self, terminal, key):
        """(process state, label matches key) from hc get; finished -> exited, rc 3 not_found -> gone."""
        if not terminal:
            return "gone", True
        obj, err = self._core(["get", terminal, "--json"])
        if err:
            return ("gone" if "not_found" in (err.get("message") or "") else "unknown"), True
        if not isinstance(obj, dict):
            return "unknown", True
        label = (obj.get("labels") or {}).get("herdr.task")
        state = obj.get("state")
        return ("live" if state == "live" else "exited" if state in ("finished", "exited") else "unknown"), label in (None, key)

    @staticmethod
    def _task_state(row, live, process):
        state, status, needs = row.get("state"), row.get("status"), row.get("needs")
        if state == "todo":
            return "not_started"
        if state in ("queued", "scheduled"):
            return "queued"
        if needs == "stopped":
            return "stopped"
        if status in ("ready", "done") or (live and all(x.get("status") in ("idle", "done") for x in live)):
            return "turn_done"
        if status == "needs":
            return "blocked"
        if live:
            return "working"
        # show keeps status=working with live=[] for 2-5 s after a kill: fall back to the terminal.
        return "working" if process == "live" else "stopped"

    def observe(self, rc):
        extra, key = {}, rc.get("thread_id")
        if not key:  # lost create: look the card up by its run-id title only
            obj, err = self._tasks(["list", "--json"])
            if err or not isinstance(obj, dict):
                return observation(None, "unknown", retryable=True, why=(err or {}).get("message"))
            found = [t for t in obj.get("tasks") or [] if isinstance(t, dict) and t.get("title") == "br-" + rc["run_id"]]
            if len(found) != 1:
                raise r.InputError(f"{len(found)} Shepherdr cards titled br-{rc['run_id']}")
            key = found[0].get("key")
            extra["ids"] = {"thread_id": key, "task_id_on_board": found[0].get("id")}
        row, err = self._tasks(["show", key, "--folder", _repo(rc), "--json"])
        if err or not isinstance(row, dict):
            return observation(None, "unknown", retryable=True, why=(err or {}).get("message"))
        live = [x for x in row.get("live") or [] if isinstance(x, dict)]
        addresses = [x.get("address") for x in live]
        process, label_ok = self._process(rc.get("terminal_id") or (addresses[0] if addresses else None), key)
        ok = label_ok and row.get("key") == key and row.get("title") == "br-" + rc["run_id"] \
            and (not rc.get("task_id_on_board") or row.get("id") == rc["task_id_on_board"]) \
            and (not rc.get("terminal_id") or not addresses or rc["terminal_id"] in addresses)
        return observation(self._task_state(row, live, process), process, "ok" if ok else "mismatch",
                           why=row.get("why"), **extra)

    def stop(self, rc):
        row = self.task(dict(rc))
        terminals = [t["address"] for t in row.get("live") or []] or ([rc["terminal_id"]] if rc.get("terminal_id") else [])
        if not terminals:
            raise r.InputError("no live terminal to stop")
        for terminal in terminals:
            self.verify_terminal(rc, terminal)
            err = self.kill(terminal, raw=True)
            if err:
                raise BoardError(err)
        return self.observe(rc)

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
