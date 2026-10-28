"""Herdr-free execution behind the same receipts, admission and result contract as herdr.py.

local: the profile's one-shot CLI runs as a detached local subprocess in a router git worktree.
external: the router prepares worktree, prompt and receipt, returns an `invocation`, and the caller runs the
agent however its environment allows (API, host Agent tool, remote job); `collect` then checks the result files.
"""
import os
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


def start(rc, prompt, profile, wait_ms):
    argv = h.headless_argv(profile) if profile.get("kind") else None
    if rc["backend"] == h.LOCAL_BACKEND and argv is None:
        return _fail(rc, f"local: no one-shot CLI for kind {profile.get('kind')!r} or args beyond model/effort")
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


def poll(rc):
    """One observation of a local or external run; settled receipts stay settled."""
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
    if h.settle_exit(rc):
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


def stop(rc):
    """local: end the process group. external: record the caller's word that its agent stopped. Returns an error."""
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
