"""Deliver a saved terminal receipt to its opted-in local Codex thread."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

from . import herdr as h, lifecycle, routing as r


def daemon_home():
    return str(Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").resolve())


def _thread_id(value):
    try:
        return str(uuid.UUID(value)) == value
    except (AttributeError, TypeError, ValueError):
        return False


def caller_binding():
    thread = os.environ.get("CODEX_THREAD_ID")
    if not _thread_id(thread):
        raise r.InputError("--notify-codex requires CODEX_THREAD_ID from the calling local Codex shell")
    return thread


def _final(rc):
    if rc["status"] == "completed":
        return rc.get("settled_contract") and rc.get("task_outcome") in ("success", "partial", "fail")
    if rc["status"] == "execution_failed":
        return rc.get("process_exited") or rc.get("delivery_state") == "not_attempted"
    return rc["status"] == "result_invalid"


def notify_final(rc):
    """Claim a run once, before enqueueing. An ambiguous send stays claimed."""
    thread = rc.get("codex_notify_thread")
    if not _thread_id(thread) or rc.get("codex_notify_home") != daemon_home() or not _final(rc):
        return False
    try:
        run_id = rc["run_id"]
        directory = h.run_dir(rc["cwd"], run_id)
        # Never send from a worktree's result directory or a redirected run directory.
        if directory != Path(rc["run_dir"]) or directory != directory.resolve():
            return False
        saved = h.load_receipt(rc["cwd"], run_id)
        if (saved.get("codex_notify_thread") != thread or saved.get("codex_notify_home") != daemon_home()
                or saved.get("run_id") != run_id or not _final(saved)):
            return False
        path = directory / "codex-notification.json"
        with path.open("x") as f:
            f.write('{"state":"attempted"}\n')
            f.flush()
            os.fsync(f.fileno())
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        location = Path(".bench-router", "runs", run_id)
        successful_contract = saved["status"] == "completed"
        payload = {"run_id": run_id, "status": saved["status"],
                   "task_outcome": saved["task_outcome"] if successful_contract else None,
                   "receipt": str(location / "receipt.json"),
                   "result": str(location / "result.md") if successful_contract else None}
        command = ["codex", "queue", "--thread", thread, "--resume", "--message",
                   "bench-router completion " + json.dumps(payload, separators=(",", ":"))]
        try:
            result = subprocess.run(command, cwd=daemon_home(), stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, errors="replace", timeout=10)
            match = re.search(r"Queued message ([0-9a-f-]+) for thread ([0-9a-f-]+)\.", result.stdout)
            accepted = result.returncode == 0 and match and _thread_id(match[1]) and match[2] == thread
            record = {"state": "queued" if accepted else "uncertain", "returncode": result.returncode,
                      "queue_id": match[1] if accepted else None, "warning": result.stderr.strip()[:1000]}
        except (OSError, subprocess.TimeoutExpired) as exc:
            record = {"state": "uncertain", "warning": str(exc)[:1000]}
        r.atomic_write(path, json.dumps(record).encode())
        return record["state"] == "queued"
    except FileExistsError:
        return False
    except (OSError, r.InputError, ValueError) as exc:
        print(f"bench-router Codex notification: {exc}", file=sys.stderr)
        return False


def spawn_local_observer(rc):
    if (rc["backend"] != h.LOCAL_BACKEND or not _thread_id(rc.get("codex_notify_thread"))
            or rc.get("codex_notify_home") != daemon_home() or _final(rc)):
        return False
    try:
        with (h.run_dir(rc["cwd"], rc["run_id"]) / "codex-observer.log").open("a") as log:
            try:
                subprocess.Popen([sys.executable, "-m", "bench_router.codex_notify", "--cwd", rc["cwd"],
                                  "--run-id", rc["run_id"]], cwd=Path(__file__).resolve().parent.parent,
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
            except OSError as exc:
                print(f"Observer could not start: {exc}. Use collect to recover the result.", file=log)
                return False
    except OSError as exc:
        print(f"bench-router Codex observer: {exc}", file=sys.stderr)
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    lifecycle.watch(args.cwd, args.run_id)
