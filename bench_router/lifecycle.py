"""Observe router results and hand validated success to Shepherdr."""
import argparse
import subprocess
import time

from . import herdr as h, routing as r


def finalize(rc, runner=subprocess.run):
    """Hand validated success to Shepherdr; it owns acceptance, merge and cleanup."""
    if (rc.get("backend") != h.BACKEND or rc.get("status") != "completed"
            or not rc.get("settled_contract") or rc.get("task_outcome") != "success"):
        return False
    if rc.get("base_branch"):  # Legacy runs target a private base; finish those manually.
        return False
    if rc.get("ready"):
        return rc["ready"].get("state") in ("ready", "done")
    _, why = h.check_result(rc)  # Results must survive native worktree cleanup.
    if why:
        raise r.InputError(why)
    h._task(rc, runner)
    rc["ready"] = {"state": "attempted"}
    h.save(rc)  # A lost response must not repeat a potentially PR-creating command.
    obj, err = h.project_call(["ready", rc["thread_id"], "--folder", h.repo_cwd(rc),
                              "--summary", "Results validated by bench-router", "--json"], runner)
    rc["ready"] = {"state": (obj or {}).get("state", "uncertain"), "error": err}
    h.save(rc)
    return rc["ready"]["state"] in ("ready", "done")


def watch(cwd, run_id):
    """The core owns this observer's lifetime; no resubmission, merge, or paid model calls."""
    while True:
        try:
            out = h.collect_run(cwd, run_id, 0)
            if out["status"] in ("execution_failed", "result_invalid"):
                return
            if out["status"] == "completed":
                return  # collect/release already recorded the Ready handoff.
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
