"""Herdr-free execution behind the same receipts, admission and result contract as herdr.py.

local: the profile's one-shot CLI runs as a detached local subprocess in a router git worktree.
herdr-tui: the same one-shot CLI, typed into the root pane of its own herdr TUI workspace (herdr CLI only, no
plugin), so a human can watch it; the workspace is closed once the run settles.
external: the router prepares worktree, prompt and receipt, returns an `invocation`, and the caller runs the
agent however its environment allows (API, host Agent tool, remote job); `collect` then checks the result files.
"""
import os
import shlex
import signal
import subprocess
from pathlib import Path

from . import herdr as h
from . import routing as r


def _prepare(rc, prompt):
    """Router worktree from HEAD + input.txt. Nothing has been started yet, so a failure settles as not attempted."""
    wt, branch = h.run_worktree(rc), f"br/{rc['run_id']}"
    from . import parallel
    parallel._git(h.repo_cwd(rc), "worktree", "add", "-b", branch, str(wt), "HEAD")
    rc.update(worktree=str(wt), branch=branch)
    r.atomic_write(Path(rc["run_dir"]) / "input.txt", prompt.encode("utf-8"))
    (wt / h.RESULT_REL / rc["run_id"]).mkdir(parents=True, exist_ok=True)


def _fail(rc, note):
    rc["status"] = "execution_failed"
    h._observe(rc, note=note)
    h.save(rc)
    return rc


def _herdr(argv, runner, raw=False):
    return h.project_call(argv, runner, raw=raw, exe=h.TUI_BIN)


def _socket(runner):
    """The herdr server this call reaches; workspace and pane ids are only unique within one server."""
    out, _ = _herdr(["status", "server"], runner, raw=True)
    return next((line[len("socket: "):] for line in (out or "").splitlines() if line.startswith("socket: ")), None)


def _same_server(rc, runner):
    if _socket(runner) != rc["herdr_socket"]:
        raise r.InputError(f"herdr-tui: this shell reaches another herdr server than the run's ({rc['herdr_socket']}); "
                           "collect or stop it from that herdr session")


def _start_tui(rc, argv, runner, wait_ms):
    rc["herdr_socket"] = _socket(runner)
    if not rc["herdr_socket"]:
        return _fail(rc, "herdr-tui: no running herdr server (herdr status server); nothing started")
    obj, err = _herdr(["workspace", "create", "--cwd", rc["worktree"], "--no-focus",
                       "--label", f"bench-router {rc['task_id']} r{rc['round']}"], runner)
    try:
        res = obj["result"]
        rc.update(workspace_id=res["workspace"]["workspace_id"], pane_id=res["root_pane"]["pane_id"])
    except (KeyError, TypeError):
        return _fail(rc, f"herdr-tui: workspace create failed ({(err or {}).get('message')}); nothing started")
    rc["delivery_state"] = "submission_attempted"
    h.save(rc)  # Persist before typing the command: a lost response must never start a second CLI.
    log = shlex.quote(str(Path(rc["run_dir"]) / "output.log"))
    _, err = _herdr(["pane", "run", rc["pane_id"],
                     # stdin from /dev/null as in local: the CLI never reads the pane's keyboard
                     f"{shlex.join(['sh', '-c', h.headless_script(rc, argv)])} </dev/null 2>&1 | tee {log}"], runner,
                    raw=True)  # pane run prints nothing on success
    if err:
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        h._observe(rc, error=err, note="herdr-tui: pane run unconfirmed; inspect the pane, never rerun")
        h.save(rc)
        return rc
    h.save(rc)
    return h.collect(rc, h._wait(rc, wait_ms), runner=runner)


def _release_tui(rc, runner):
    """Close the run's own workspace once it settled; the CLI has exited and output.log keeps its output."""
    _, err = _herdr(["workspace", "close", rc["workspace_id"]], runner)
    # shortcut: a failed close is recorded, not retried; the workspace then stays open until a human closes it
    rc["release"] = {"at": h._iso(h._now()), "workspace_id": rc["workspace_id"], **({"error": err} if err else {})}


def start(rc, prompt, profile, wait_ms, runner=subprocess.run):
    argv = h.headless_argv(profile) if profile.get("kind") else None
    if rc["backend"] in (h.LOCAL_BACKEND, h.TUI_BACKEND) and argv is None:
        return _fail(rc, f"{rc['backend']}: no one-shot CLI for kind {profile.get('kind')!r} or args beyond model/effort")
    try:
        _prepare(rc, prompt)
    except (r.InputError, OSError) as e:
        return _fail(rc, f"worktree: {e}; nothing started")
    if rc["backend"] == h.EXTERNAL_BACKEND:
        rd = Path(rc["worktree"]) / h.RESULT_REL / rc["run_id"]
        rc.update(status="handed_off", delivery_state="submission_attempted", invocation={
            "cwd": rc["worktree"], "prompt_path": str(Path(rc["run_dir"]) / "input.txt"), "result_dir": str(rd),
            "argv": argv, "model_id": profile["model_id"], "deadline_at": rc["deadline_at"]})
        h._observe(rc, note="handed off: run the agent, then collect; never resend under a new task_id")
        h.save(rc)
        return rc
    if rc["backend"] == h.TUI_BACKEND:
        return _start_tui(rc, argv, runner, wait_ms)
    rc["delivery_state"] = "submission_attempted"
    h.save(rc)  # Persist before starting: a lost response must never start a second CLI.
    try:
        with open(Path(rc["run_dir"]) / "output.log", "wb") as log:
            # A new session makes the pid a process group: stop ends the shell and the CLI together.
            p = subprocess.Popen(["sh", "-c", h.headless_script(rc, argv)], stdin=subprocess.DEVNULL, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    except OSError as e:
        rc["process_exited"] = True
        return _fail(rc, f"local: could not start sh ({e})")
    rc["pid"] = p.pid
    h.save(rc)
    return h.collect(rc, h._wait(rc, wait_ms))


def poll(rc, runner=subprocess.run):
    """One observation of a local, herdr-tui or external run; settled receipts stay settled."""
    if rc["status"] in h.SETTLED_STATUSES:
        return
    if rc["backend"] == h.EXTERNAL_BACKEND:
        manifest, why = h.check_result({**rc, "run_dir": str(Path(rc["worktree"]) / h.RESULT_REL / rc["run_id"])})
        if manifest:
            h.settle(rc, "done")
        else:
            rc["status"] = "handed_off"
            h._observe(rc, note=f"waiting for the caller's result ({why})")
        return
    tui = rc["backend"] == h.TUI_BACKEND
    if tui:
        _same_server(rc, runner)  # collect turns this into delivery_uncertain; nothing is closed or settled
    if h.settle_exit(rc):
        if tui:
            _release_tui(rc, runner)
        return
    if tui:
        _, err = _herdr(["pane", "get", rc["pane_id"]], runner)
        if not err:
            rc["status"] = "timed_out"
            h._observe(rc, "working", note="herdr-tui CLI still running")
        elif "pane_not_found" in err["message"]:  # closed by stop or a human before the CLI wrote its exit code
            rc.update(status="execution_failed", process_exited=True)
            h._observe(rc, note="herdr-tui pane closed without an exit code (stopped or closed)")
        else:
            rc["status"] = "timed_out"
            h._observe(rc, error=err, note="herdr unreachable; the CLI may still be running, collect again")
        return
    try:
        os.waitpid(rc["pid"], os.WNOHANG)  # reap our own child so a dead shell is not seen as a live zombie
    except ChildProcessError:
        pass  # started by another router process
    try:
        os.killpg(rc["pid"], 0)
        rc["status"] = "timed_out"
        h._observe(rc, "working", note="local CLI still running")
    except ProcessLookupError:
        rc.update(status="execution_failed", process_exited=True)
        h._observe(rc, note="local CLI ended without an exit code (killed or stopped)")
    # shortcut: pid reuse is not detected, compare /proc start time if runs outlive a reboot or last for days


def stop(rc, runner=subprocess.run):
    """local: end the process group. herdr-tui: close the run's own workspace, which ends its CLI.
    external: record the caller's word that its agent stopped. Returns an error."""
    if rc["backend"] == h.TUI_BACKEND:
        try:
            _same_server(rc, runner)
        except r.InputError as e:
            return {"code": "herdr_server_changed", "message": str(e)[:300]}
        return _herdr(["workspace", "close", rc["workspace_id"]], runner)[1]
    if rc["backend"] == h.EXTERNAL_BACKEND:
        rc.update(status="execution_failed", process_exited=True)
        h._observe(rc, note="caller declared the external run stopped")
        h.save(rc)
        return None
    try:
        os.killpg(rc["pid"], signal.SIGTERM)
    except ProcessLookupError:
        pass  # already gone; collect records it
    except (OSError, KeyError) as e:
        return {"code": "stop_error", "message": str(e)[:300]}
    return None
