"""Observe router results and hand validated success to the board (Shepherdr)."""
import argparse
import subprocess
import time

from . import herdr as h, routing as r, shepherdr


def finalize(rc, runner=subprocess.run):
    """Hand validated success to the board; it owns acceptance, merge and cleanup."""
    if (rc.get("backend") not in h.BOARDS or rc.get("status") != "completed"
            or not rc.get("settled_contract") or rc.get("task_outcome") != "success"):
        return False
    if rc.get("base_branch"):  # Legacy runs target a private base; finish those manually.
        return False
    if rc.get("ready"):
        return rc["ready"].get("state") in ("ready", "done")
    _, why = h.check_result(rc)  # Results must survive native worktree cleanup.
    if why:
        raise r.InputError(why)
    if rc["backend"] == h.BACKEND:
        runner = h._checked_runner(rc, None, runner)
    board = h._board(rc["backend"], runner)
    if hasattr(board, "verify"):  # adapter's identity check before the mutating handoff
        board.verify(rc)
    rc["ready"] = {"state": "attempted"}
    h.save(rc)  # A lost response must not repeat a potentially PR-creating command.
    # Board port: any non-InputError is a lost response. Shepherdr reports one as BoardError only.
    lost = shepherdr.BoardError if rc["backend"] == h.BACKEND else Exception
    try:
        state, err = board.handoff(rc), None
    except r.InputError:
        raise
    except lost as e:
        state, err = "uncertain", getattr(e, "error", None) or {"code": "board_error", "message": str(e)[:300]}
    rc["ready"] = {"state": state, "error": err}
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
