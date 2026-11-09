"""Observe router results, then finalize the board and resources after a verified merge."""
import argparse
import json
import subprocess
import time
from pathlib import Path

from . import herdr as h, parallel as p, routing as r


def finalize(rc, runner=subprocess.run, dry_run=False):
    """Only a validated, clean, integrated worktree may be removed. Receipts/results stay outside it."""
    if rc.get("backend") != h.BACKEND or rc.get("status") != "completed" or not rc.get("settled_contract"):
        return False
    repo, wt, branch = h.repo_cwd(rc), rc.get("worktree"), rc.get("branch")
    if not wt or branch != f"br/{rc['run_id']}":
        return False
    if Path(wt).exists():
        if p._git(wt, "status", "--porcelain"):
            return False
        if p._git(wt, "branch", "--show-current") != branch:
            raise r.InputError("cleanup worktree branch changed")
    pending = rc.get("cleanup_pending") or {}
    exists = bool(p._git(repo, "show-ref", "--verify", f"refs/heads/{branch}", check=False))
    tip = p._git(repo, "rev-parse", branch) if exists else pending.get("tip")
    if not tip:
        return False
    head = p._git(repo, "rev-parse", "HEAD")
    merged = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", tip, head],
                            capture_output=True).returncode == 0
    if not merged:
        # A squash merge preserves changes without preserving commit ancestry.
        result = subprocess.run(["git", "-C", repo, "merge-tree", "--write-tree", head, tip],
                                capture_output=True, text=True)
        merged = result.returncode == 0 and result.stdout.strip() == p._git(repo, "rev-parse", "HEAD^{tree}")
    if not merged:
        return False
    obj, err = h.project_call(["ls", "--label", f"herdr.task={rc['thread_id']}", "--json"], runner, exe=h.HERDR_BIN)
    if err or not isinstance(obj, dict) or not isinstance(obj.get("terminals"), list):
        raise r.InputError("cannot verify task resources before cleanup")
    terminals = obj["terminals"]
    for terminal in terminals:
        status = terminal.get("status")
        status = status.get("state") if isinstance(status, dict) else status
        if status in ("working", "blocked"):
            return False
        if status not in ("idle", "done"):
            detail, err = h.project_call(["get", terminal["address"], "--json"], runner, exe=h.HERDR_BIN)
            if err or not isinstance(detail, dict) or (detail.get("foreground") or {}).get("name", "").split("/")[-1] not in ("bash", "sh", "zsh", "fish", "dash"):
                return False
    if dry_run:
        return True
    rc["cleanup_pending"] = {"tip": tip, "terminals": sorted(set(pending.get("terminals", [])) | {t["address"] for t in terminals})}
    h.save(rc)
    # User authorization covers done after merge, not accepting or merging outstanding work.
    h._task(rc, runner)
    obj, err = h.project_call(["done", rc["thread_id"], "--folder", repo, "--json"], runner)
    if err or not isinstance(obj, dict) or obj.get("state") != "done":
        raise r.InputError("board completion unconfirmed; cleanup deferred")
    for terminal in terminals:
        for args in (["keep", terminal["address"], "--off", "--json"], ["kill", terminal["address"], "--json"]):
            _, err = h.project_call(args, runner, exe=h.HERDR_BIN)
            if err:
                raise r.InputError("task terminal cleanup unconfirmed")
    if Path(wt).exists():
        p._git(repo, "worktree", "remove", wt)
    # Compare-and-delete refuses a branch moved concurrently by the user.
    if exists:
        p._git(repo, "update-ref", "-d", f"refs/heads/{branch}", tip)
    base = rc.get("base_branch")
    if base == f"br-base/{rc['run_id']}":
        original = rc.get("base_commit")
        if original and p._git(repo, "show-ref", "--verify", f"refs/heads/{base}", check=False):
            p._git(repo, "update-ref", "-d", f"refs/heads/{base}", original)
    remaining, err = h.project_call(["ls", "--all", "--label", f"herdr.task={rc['thread_id']}", "--json"], runner, exe=h.HERDR_BIN)
    if err or not isinstance(remaining, dict) or not isinstance(remaining.get("terminals"), list):
        raise r.InputError("cannot confirm finished terminals")
    addresses = {t["address"] for t in remaining["terminals"]}
    for address in set(rc["cleanup_pending"]["terminals"]) & addresses:
        _, err = h.project_call(["rm", address, "--json"], runner, exe=h.HERDR_BIN)
        if err:
            raise r.InputError("finished terminal removal unconfirmed; will retry")
    rc["cleanup"] = {"at": h._iso(h._now()), "board": "done", "worktree_removed": True}
    h.save(rc)
    return True


def watch(cwd, run_id):
    """The core owns this observer's lifetime; no resubmission, merge, or paid model calls."""
    while True:
        try:
            out = h.collect_run(cwd, run_id, 0)
            rc = h.load_receipt(cwd, run_id)
            if out["status"] in ("execution_failed", "result_invalid"):
                return
            if out["status"] == "completed":
                with h.dispatch_lock(cwd):
                    rc = h.load_receipt(cwd, run_id)
                    if rc.get("cleanup") or finalize(rc):
                        return
            if rc.get("thread_id"):
                label = "Result validated; waiting for merge" if out["status"] == "completed" else "Running headless task" if rc.get("execution") == "headless" else "Running task"
                h.project_call(["status", rc["thread_id"], label, "--folder", h.repo_cwd(rc), "--json"])
        except (h.Busy, r.InputError, OSError, ValueError) as exc:
            # ponytail: retry transient core/Git contention every 5s; add backoff if fleets need it.
            print(f"bench-router observer: {exc}", flush=True)
        time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    watch(args.cwd, args.run_id)
