"""Herdr-free execution behind the same receipts, admission and result contract as herdr.py.

local: the profile's one-shot CLI runs as a detached local subprocess in a router git worktree.
herdr-tui: the same one-shot CLI, typed into the root pane of its own herdr TUI workspace (herdr CLI only, no
plugin), so a human can watch it; the workspace is closed once the run settles.
external: the router prepares worktree, prompt and receipt, returns an `invocation`, and the caller runs the
agent however its environment allows (API, host Agent tool, remote job); `collect` then checks the result files.
"""
import os
import re
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


def _herdr(argv, runner, raw=False, timeout_s=h.SHORT_CALL_S):
    return h.project_call(argv, runner, raw=raw, timeout_s=timeout_s, exe=h.TUI_BIN)


def _wait_args(wait_s):
    """A herdr-side wait within collect's budget, instead of collect polling each second; None when no budget."""
    return (["--timeout", str(int(wait_s * 1000))], wait_s + h.SHORT_CALL_S) if wait_s >= 1 else None


def _end_marker(rc):
    return f"bench-router-exited-{rc['run_id']}"


HERDR_MIN = (0, 9, 5)  # tested; older servers may omit completion_seq, and interactive runs would never settle


def _status(runner):
    """`herdr status server` as {field: value}; it has no JSON form."""
    out, _ = _herdr(["status", "server"], runner, raw=True)
    return dict(line.split(": ", 1) for line in (out or "").splitlines() if ": " in line)


def _socket(runner):
    """The herdr server this call reaches; workspace and pane ids are only unique within one server."""
    return _status(runner).get("socket")


def _same_server(rc, runner):
    if _socket(runner) != rc["herdr_socket"]:
        raise r.InputError(f"herdr-tui: this shell reaches another herdr server than the run's ({rc['herdr_socket']}); "
                           "collect or stop it from that herdr session")


def _start_tui(rc, argv, runner, wait_ms, chat=None):
    status = _status(runner)
    rc["herdr_socket"] = status.get("socket")
    if not rc["herdr_socket"]:
        return _fail(rc, "herdr-tui: no running herdr server (herdr status server); nothing started")
    m = re.match(r"(\d+)\.(\d+)\.(\d+)", status.get("version", ""))
    if not m or tuple(map(int, m.groups())) < HERDR_MIN:
        return _fail(rc, f"herdr-tui: herdr {status.get('version', '?')} is older than "
                         f"{'.'.join(map(str, HERDR_MIN))}; run herdr update; nothing started")
    obj, err = _herdr(["workspace", "create", "--cwd", rc["worktree"], "--no-focus",
                       "--label", f"bench-router {rc['task_id']} r{rc['round']}"], runner)
    try:
        res = obj["result"]
        # the terminal id changes when herdr restarts and restores the pane as a new shell
        rc.update(workspace_id=res["workspace"]["workspace_id"], pane_id=res["root_pane"]["pane_id"],
                  herdr_terminal=res["root_pane"]["terminal_id"])
    except (KeyError, TypeError):
        return _fail(rc, f"herdr-tui: workspace create failed ({(err or {}).get('message')}); nothing started")
    if chat:
        h.save(rc)
        return _start_agent(rc, *chat, runner, wait_ms)
    rc["delivery_state"] = "submission_attempted"
    h.save(rc)  # Persist before typing the command: a lost response must never start a second CLI.
    rd = Path(rc["run_dir"])
    q = lambda name: shlex.quote(str(rd / name))
    # stdin from /dev/null as in local; exit_code appears only after tee ends, so closing on it loses no output
    command = (f"{shlex.join(['sh', '-c', h.headless_script(rc, argv, publish=False)])} </dev/null 2>&1 "
               f"| tee {q('output.log')}; mv {q('exit_code.tmp')} {q('exit_code')}; "
               f"printf 'bench-router-%s-%s\\n' exited {rc['run_id']}")  # the end marker pane wait-output waits for
    _, err = _herdr(["pane", "run", rc["pane_id"], command], runner, raw=True)  # pane run prints nothing on success
    if err:
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        h._observe(rc, error=err, note="herdr-tui: pane run unconfirmed; inspect the pane, never rerun")
        h.save(rc)
        return rc
    return h.collect(rc, h._wait(rc, wait_ms), runner=runner)


def _screen_tail(rc, runner):
    out, _ = _herdr(["agent", "read", rc["agent_name"]], runner, raw=True)
    return (out or "").strip()[-400:]


def _start_agent(rc, profile, prompt, runner, wait_ms):
    """Interactive: start the profile's agent in the workspace pane, then submit the prompt once."""
    rc["agent_name"] = "br-" + rc["run_id"][:12]
    h.save(rc)
    _, err = _herdr(["agent", "start", rc["agent_name"], "--kind", profile["kind"], "--pane", rc["pane_id"],
                     "--timeout", "60000", "--", *profile["args"]], runner)
    if err:  # nothing was sent yet, so failing is safe; e.g. the folder-trust question blocks a new folder
        note = f"herdr-tui: agent did not start ({err['message']}); screen: {_screen_tail(rc, runner)!r}; nothing sent"
        _herdr(["workspace", "close", rc["workspace_id"]], runner)
        return _fail(rc, note)
    rc["delivery_state"] = "submission_attempted"
    h.save(rc)  # Persist before the prompt: a lost response must never submit it twice.
    _, err = _herdr(["agent", "prompt", rc["agent_name"], prompt, "--wait", "--until", "working", "--until", "blocked",
                     "--timeout", "20000"], runner)
    if err:
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        h._observe(rc, error=err, note="herdr-tui: prompt unconfirmed; inspect the agent, never resubmit")
        h.save(rc)
        return rc
    rc["delivery_state"] = "activity_observed"
    h.save(rc)
    return h.collect(rc, h._wait(rc, wait_ms), runner=runner)


def _replaced(rc, current, runner):
    """True, and the run failed and its workspace closed, when herdr replaced the run's terminal: a server restart
    restores the pane under the same id as a new shell, and what ran in it (CLI or agent) is gone."""
    if not rc.get("herdr_terminal") or not current or current == rc["herdr_terminal"]:
        return False
    rc.update(status="execution_failed", process_exited=True)
    h._observe(rc, note=f"herdr-tui: the pane's terminal was replaced ({rc['herdr_terminal']} -> {current}), "
                        "e.g. by a herdr server restart; what ran in it is gone")
    _release_tui(rc, runner)
    return True


def _poll_agent(rc, runner, wait_s=0):
    obj = err = None
    if wait := _wait_args(wait_s):  # herdr returns when the turn settles or asks; a timeout falls back to agent get
        obj, _ = _herdr(["agent", "wait", rc["agent_name"], "--until", "idle", "--until", "done", "--until", "blocked",
                         *wait[0]], runner, timeout_s=wait[1])
    if obj is None:
        obj, err = _herdr(["agent", "get", rc["agent_name"]], runner)
    if err:
        if "not_found" in err["message"]:  # closed by stop or a human before the turn ended with results
            rc.update(status="execution_failed", process_exited=True)
            h._observe(rc, note="herdr-tui agent is gone (stopped or closed)")
        else:
            rc["status"] = "timed_out"
            h._observe(rc, error=err, note="herdr unreachable; the agent may still be working, collect again")
        return
    agent = obj["result"]["agent"]
    if _replaced(rc, agent.get("terminal_id"), runner):
        return
    status = agent["agent_status"]
    if status == "blocked":  # a question or permission: a human answers it in herdr, then collect again
        rc.update(status="blocked", diagnostic_tail=_screen_tail(rc, runner))
        h._observe(rc, "blocked", note="herdr-tui agent waits for an answer in its pane")
    elif status in ("idle", "done") and agent.get("completion_seq") is not None:  # herdr: a turn really ended
        h.settle(rc, "done")
        if rc["status"] == "completed":
            _release_tui(rc, runner)
    else:  # working, unknown, or idle without a finished turn (the prompt may never have landed)
        rc["status"] = "timed_out"
        h._observe(rc, status, note="herdr-tui agent has not finished a turn")


def _release_tui(rc, runner):
    """Close the run's own workspace once it settled; the CLI has exited and output.log keeps its output."""
    _, err = _herdr(["workspace", "close", rc["workspace_id"]], runner)
    if err and "workspace_not_found" in err["message"]:
        err = None  # already closed (by stop or a human)
    rc["release"] = {"at": h._iso(h._now()), "workspace_id": rc["workspace_id"], **({"error": err} if err else {})}


def retry_release(rc, runner=subprocess.run):
    """A settled herdr-tui run whose workspace close failed: try again, only on the run's own herdr server.
    Returns whether the receipt changed."""
    if rc.get("backend") != h.TUI_BACKEND or not (rc.get("release") or {}).get("error"):
        return False
    if _socket(runner) != rc["herdr_socket"]:
        return False
    _release_tui(rc, runner)
    return True


def start(rc, prompt, profile, wait_ms, runner=subprocess.run):
    argv = h.headless_argv(profile) if profile.get("kind") else None
    chat = rc["backend"] == h.TUI_BACKEND and rc.get("execution") != "headless"  # a live agent in the pane
    if chat:
        prompt += ("\nherdr-tui: do not open a PR or merge; keep this worktree and branch. After writing the "
                   "results, end your turn. bench-router validates and collects the results.\n")
        if h.model_effort(profile) is None or len(prompt.encode("utf-8")) > h.MAX_PROMPT_ARG_BYTES:
            return _fail(rc, "herdr-tui: profile args beyond model/effort or a prompt over "
                             f"{h.MAX_PROMPT_ARG_BYTES} bytes; nothing started")
    elif rc["backend"] in (h.LOCAL_BACKEND, h.TUI_BACKEND) and argv is None:
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
        return _start_tui(rc, argv, runner, wait_ms, (profile, prompt) if chat else None)
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


def poll(rc, runner=subprocess.run, wait_s=0):
    """One observation of a local, herdr-tui or external run; settled receipts stay settled."""
    if rc["status"] in h.SETTLED_STATUSES:
        retry_release(rc, runner)
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
    if tui and rc.get("agent_name"):
        return _poll_agent(rc, runner, wait_s)
    if tui and (wait := _wait_args(wait_s)) and not (Path(rc["run_dir"]) / "exit_code").exists():
        _herdr(["pane", "wait-output", rc["pane_id"], "--regex", f"^{_end_marker(rc)}$", *wait[0]], runner,
               raw=True, timeout_s=wait[1])  # returns at the end marker, or at the budget; the checks below decide
    if h.settle_exit(rc):
        if tui:
            _release_tui(rc, runner)
        return
    if tui:
        obj, err = _herdr(["pane", "get", rc["pane_id"]], runner)
        if not err and _replaced(rc, obj["result"]["pane"].get("terminal_id"), runner):
            return
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
        if not rc.get("workspace_id"):  # dispatch is still creating it
            return {"code": "stop_error", "message": "herdr-tui: no workspace recorded yet; stop again once dispatch returns"}
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
