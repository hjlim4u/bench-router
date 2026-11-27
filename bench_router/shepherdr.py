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
from functools import wraps
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
            message = (p.stderr or p.stdout)[:300]
            return None, {"code": "shepherdr_error", "message": message, "returncode": p.returncode}
        if len(p.stdout.encode("utf-8")) > r.SNAPSHOT_MAX_BYTES:
            raise ValueError("Shepherdr response too large")
        return (p.stdout if raw else json.loads(p.stdout)), None
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, {"code": "shepherdr_error", "message": str(e)[:300]}


def project_binding(session=None, runner=subprocess.run, core_session=None, call=None):
    """Bind to the task protocol and core build, never interpret legacy Projects receipts as tasks.
    call: the project_call to use (the router passes its own so it can be replaced as one seam)."""
    call = call or project_call
    version, err = call(["--version"], runner, raw=True)
    if err or (version or "").strip() != TASK_PROTOCOL:
        raise r.InputError("Shepherdr 3.x herdr-task protocol 1 is required for live dispatch; "
                           "install Shepherdr, use --runner local|external, or use route --dry-run")
    help_text, err = call(["--help"], runner, raw=True)
    commands = re.search(r"\{([^{}]*\bstart\b[^{}]*)\}", help_text or "")
    if err or not commands:
        raise r.InputError("cannot identify the installed Shepherdr subcommands")
    modern = "stop" in commands[1].split(",")
    selected = "default"
    if modern:
        selected = getattr(runner, "_shepherdr_session", None) or os.environ.get("SHEPHERDR_SESSION") or "shepherdr"
    if selected in (".", "..") or "/" in selected or not selected.strip():
        raise r.InputError("invalid Shepherdr core session")
    if core_session and selected != core_session:
        raise r.InputError(f"Shepherdr session {selected!r} differs from recorded/configured {core_session!r}")
    caller = os.environ.get("HC_SESSION")
    if not core_session and caller and caller not in (("default", "shepherdr", selected) if modern else ("default",)):
        raise r.InputError(f"caller session {caller!r} is incompatible with Shepherdr session {selected!r}")
    runner = bound_runner({"project_binding": {"session": selected}}, runner)
    core, err = call(["--version"], runner, raw=True, exe=HERDR_BIN)
    m = re.fullmatch(r"hc (\d+)\.(\d+)\.(\d+)(?:[-+ ].*)?", (core or "").strip())
    if err or not m or tuple(map(int, m.groups())) < (0, 1, 17):
        raise r.InputError("Shepherdr requires herdr-core (hc) >= 0.1.17")
    space = session or os.environ.get("BENCH_ROUTER_SPACE") or os.environ.get("BENCH_ROUTER_HERDR_SESSION")
    if not space and (caller or "default") == selected and not os.environ.get("HC_SOCKET") and os.environ.get("HC_TERMINAL_ID"):
        obj, err = call(["get", os.environ["HC_TERMINAL_ID"], "--json"], runner, exe=HERDR_BIN)
        labels = (obj or {}).get("labels", {})
        space = labels.get("herdr.space") or labels.get("herdr.task.space") or labels.get("herdr.coordinator.space")
    if not isinstance(space, str) or not space.strip() or "/" in space:
        raise r.InputError("a local Shepherdr space is required: use --herdr-space SPACE or BENCH_ROUTER_SPACE")
    state = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    try:
        identity = json.loads((state / "herdr-core" / selected / "core.json").read_text("utf-8"))
    except FileNotFoundError:
        obj, err = call(["server", "status", "--json"], runner, exe=HERDR_BIN)
        identity = obj.get("core") if not err and isinstance(obj, dict) else None
    except (OSError, ValueError) as exc:
        raise r.InputError(f"cannot read core identity for session {selected!r}: {exc}") from exc
    if not isinstance(identity, dict) or not isinstance(identity.get("id"), str) or not identity["id"]:
        raise r.InputError(f"missing core identity for session {selected!r}")
    return {"task_protocol": TASK_PROTOCOL, "core_version": core.strip(), "space": space,
            "session": selected, "core_id": identity["id"]}


def bound_runner(rc, runner):
    """Run task and core commands in the session recorded before submission."""
    core_session = rc["project_binding"]["session"]
    def run(cmd, **kwargs):
        env = {**kwargs.pop("env", os.environ), "HC_SESSION": core_session}
        env["SHEPHERDR_SESSION"] = core_session
        for key in ("HC_SOCKET", "HC_TERMINAL_SOCKET", "HC_TERMINAL_ID"):
            env.pop(key, None)
        return runner(cmd, env=env, **kwargs)
    run._shepherdr_session = core_session
    return run


def _repo(rc):
    """herdr.repo_cwd; a port-only rc (no receipt) uses the folder given to bind()."""
    return rc.get("repo_cwd", rc["cwd"]) if "cwd" in rc else rc.get("repo_cwd") or (rc.get("binding") or {}).get("folder")


def matches_binding(current, recorded):
    return all(current.get(k) == recorded.get(k) for k in ("task_protocol", "space", "session", "core_id"))


def _board_operation(method):
    """Port callers supply the binding in rc. Router calls already use a checked runner."""
    @wraps(method)
    def checked(self, rc, *args):
        if "binding" not in rc:
            return method(self, rc, *args)
        binding = rc["binding"]
        runner = bound_runner({"project_binding": binding}, self.runner)
        current = project_binding(binding["space"], runner, binding["session"], self.call)
        if not matches_binding(current, binding):
            raise r.InputError("Shepherdr session or core binding differs from the receipt")
        scoped = ShepherdrBoard(runner, self.call, self.capabilities)
        return method(scoped, rc, *args)
    return checked


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

    def _terminal(self, terminal, timeout_s):
        obj, err = self._core(["get", terminal, "--json"], timeout_s=timeout_s)
        if err:
            if err.get("returncode") == 3:
                try:
                    detail = json.loads(err["message"])
                except ValueError:
                    detail = None
                if isinstance(detail, dict) and isinstance(detail.get("error"), dict) and detail["error"].get("kind") == "not_found":
                    return "gone", {}
            raise r.InputError(err["message"])
        if not isinstance(obj, dict) or obj.get("state") not in ("live", "finished", "exited"):
            raise r.InputError("unexpected hc terminal response")
        return ("live" if obj["state"] == "live" else "exited"), obj

    def terminal_state(self, terminal, timeout_s, rc=None):
        state, obj = self._terminal(terminal, timeout_s)
        if rc and state != "gone":
            labels = obj.get("labels") or {}
            owned = (labels.get("herdr.task") == rc["thread_id"] if rc.get("thread_id")
                     else labels.get("bench-router.run") == rc["run_id"])
            if not owned or obj.get("address") != terminal:
                raise r.InputError("terminal identity mismatch in the recorded core session")
        return state

    def kill(self, terminal, raw=False):
        """End one core terminal; returns the call's error or None."""
        return self._core(["kill", terminal, "--json"], raw=raw)[1]

    def reopen(self, rc):
        """Cancel a queued card back to To do; True only when the board confirms it."""
        obj, err = self._tasks(["reopen", rc["thread_id"], "--folder", _repo(rc), "--json"])
        return not err and isinstance(obj, dict) and obj.get("key") == rc["thread_id"] and obj.get("state") == "todo"

    def verify(self, rc):
        """Identity check the router runs before a mutating handoff (records worktree/branch like task())."""
        self.task(rc)

    def tell_target(self, rc):
        """The single live worker of a running card that may take a message; InputError otherwise."""
        row = self.task(rc)
        live = row.get("live") or []
        if row.get("state") != "running" or len(live) != 1 or (row.get("needs") == "reply" and not rc.get("resumed")):
            raise r.InputError("task finished on the board or has no single live worker; collect/resume first")
        terminal = live[0]["address"]
        self.verify_terminal(rc, terminal)
        return terminal

    def send(self, terminal, text):
        return self._core(["send", terminal, text, "--json"])

    def resume_task(self, rc):
        return self._tasks(["resume", rc["thread_id"], "--folder", _repo(rc), "--space", rc["project_binding"]["space"],
                            "--json"], timeout_s=START_CALL_S)

    # ---- Board port ----

    def _need(self, capability):
        if capability not in self.capabilities:
            raise r.InputError(f"this Shepherdr board does not support {capability}")

    def bind(self, session, cwd):
        return {**project_binding(session, self.runner, None, self.call), "folder": cwd}

    def _process(self, terminal, key):
        """(process state, label matches key) from hc get; finished -> exited, rc 3 not_found -> gone."""
        if not terminal:
            return "gone", True
        try:
            state, obj = self._terminal(terminal, SHORT_CALL_S)
        except r.InputError:
            return "unknown", True
        return state, state == "gone" or (obj.get("labels") or {}).get("herdr.task") == key

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

    @_board_operation
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

    @_board_operation
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

    @_board_operation
    def handoff(self, rc):
        obj, err = self._tasks(["ready", rc["thread_id"], "--folder", _repo(rc),
                                "--summary", "Results validated by bench-router", "--json"])
        if err:
            raise BoardError(err)
        return (obj or {}).get("state", "uncertain")

    @_board_operation
    def cleanup(self, rc):
        """End only idle terminals belonging to this run; leave working and blocked agents alone.
        Also returns error (the failed call's error) and terminals ([{terminal_id, agent}] closed)."""
        argv = ["ls", "--label", f"bench-router.run={rc['run_id']}", "--json"] if not rc.get("thread_id") else \
            ["ls", "--label", f"herdr.task={rc['thread_id']}", "--json"]
        obj, err = self._core(argv)
        terminals = obj.get("terminals") if isinstance(obj, dict) else None
        if err or not isinstance(terminals, list):
            return {"closed": [], "left_open": "could not list core terminals, agent left open", "error": err}
        for t in terminals:
            status = t.get("status")
            status = status.get("state") if isinstance(status, dict) else status
            if t.get("state") not in ("exited", "finished") and status not in ("idle", "done") and rc.get("execution") != "headless":
                return {"closed": [], "left_open": "task still has an active agent, left open", "error": None}
        closed = []
        for t in terminals:
            err = self.kill(t["address"])
            if err:
                return {"closed": [c["terminal_id"] for c in closed], "left_open": "ending the core terminal failed",
                        "error": err, "terminals": closed}
            closed.append({"terminal_id": t["address"], "agent": t.get("agent")})
        return {"closed": [c["terminal_id"] for c in closed], "left_open": None, "error": None, "terminals": closed}

    @_board_operation
    def tell(self, rc, text):
        self._need("tell")
        _, err = self.send(self.tell_target(dict(rc)), text)
        if err:
            raise BoardError(err)

    @_board_operation
    def resume(self, rc):
        self._need("resume")
        rc = {**rc, "project_binding": rc.get("project_binding") or rc["binding"]}
        self.task(rc)
        obj, err = self.resume_task(rc)
        if err or not isinstance(obj, dict) or not obj.get("terminal"):
            raise BoardError(err or {"code": "shepherdr_error", "message": "resume returned no terminal"})
        return {"terminal_id": obj["terminal"], "resumed": obj.get("resumed") is True}

    @_board_operation
    def create(self, rc):
        obj, err = self.add(rc, rc.get("board_settings", []), rc.get("base", "main"), START_CALL_S)
        if obj is None:
            raise BoardError(err or {"code": "shepherdr_error", "message": "task add unconfirmed"})
        return {"thread_id": obj["key"], "task_id_on_board": obj["id"]}

    @_board_operation
    def start(self, rc):
        b = rc["binding"]
        obj, err = self.start_task({**rc, "project_binding": b}, rc.get("launch_args", []), START_CALL_S)
        if obj is None:
            raise BoardError(err or {"code": "shepherdr_error", "message": "task start unconfirmed"})
        return {"terminal_id": obj.get("terminal"), "worktree": obj.get("worktree"), "branch": obj.get("branch")}
