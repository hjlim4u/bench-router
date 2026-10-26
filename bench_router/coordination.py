"""Durable task admission and acceptance; Projects owns agent execution."""
import contextlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from . import locking
from . import routing as r

MAX_ACTIVE = 4


class Conflict(Exception):
    pass


def directory():
    override = os.environ.get("BENCH_ROUTER_COORDINATION_DIR")
    base = Path(override) if override else Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "bench-router/coordination"
    if not base.is_absolute():
        raise r.InputError("coordination directory must be absolute and shared by all orchestrators")
    base.mkdir(parents=True, exist_ok=True)
    return base


def key_for(t):
    return r.canonical_hash([os.path.normcase(os.path.realpath(t["cwd"])), t["task_id"], t["round"]])


def _path(key):
    if not isinstance(key, str) or not re.fullmatch(r"[0-9a-f]{64}", key):
        raise r.InputError("coordination key: SHA-256 required")
    return directory() / f"{key}.json"


def load(key):
    return r.load_json_strict(_path(key), 16 * 1024 * 1024)


def _save(rec):
    rec["updated_at"] = datetime.now(timezone.utc).isoformat()
    r.atomic_write(_path(rec["key"]), json.dumps(rec, ensure_ascii=False, indent=2).encode("utf-8"))


@contextlib.contextmanager
def gate():
    deadline = time.monotonic() + 2
    with contextlib.ExitStack() as stack:
        while True:
            try:
                stack.enter_context(locking.exclusive(directory() / "admission.lock", Conflict("coordination admission is busy")))
                break
            except Conflict:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.01)
        yield


@contextlib.contextmanager
def operation(key):
    _path(key)
    with locking.exclusive(directory() / f"{key}.lock", Conflict("this logical task already has an operation in progress")):
        yield


def _records():
    # shortcut: linear record scan, add an index when the ledger becomes large.
    return [r.load_json_strict(p, 16 * 1024 * 1024) for p in sorted(directory().glob("*.json"))]


def _overlap(a, b):
    a, b = os.path.normcase(a), os.path.normcase(b)
    try:
        return os.path.commonpath([a, b]) in (a, b)
    except ValueError:
        return False


def reserve(t, backend, binding, workspace=None):
    key = key_for(t)
    digest = r.semantic_task_hash(t)
    workspace = workspace or t["cwd"]
    with gate():
        if _path(key).exists():
            rec = load(key)
            if (rec["backend"], rec["request_hash"], rec["binding"]) != (backend, digest, binding):
                raise Conflict("logical task is already bound to another backend, input or execution configuration")
            return rec, False
        active = [x for x in _records() if x["active"]]
        if len(active) >= MAX_ACTIVE:
            raise Conflict(f"combined active task limit ({MAX_ACTIVE}) reached; collect or inspect existing tasks")
        paths = [x.get("workspace", x["cwd"]) for x in active]
        paths += [x["worktree"] for x in active if x.get("worktree")]
        if any(_overlap(workspace, path) for path in paths):
            raise Conflict("workspace overlaps an active writer or review; use isolated worktrees or collect first")
        rec = {"schema_version": "1.0", "key": key, "backend": backend, "cwd": t["cwd"],
               "workspace": workspace,
               "task_id": t["task_id"], "round": t["round"], "request_hash": digest, "binding": binding,
               "active": True, "status": "delivery_uncertain", "reference": None,
               "acceptance": {"decision": "withheld", "reason": "not assessed"}}
        _save(rec)  # Durable intent precedes any external submission; no expiry-based re-send.
        return rec, True


def update(key, **changes):
    with gate():
        rec = load(key)
        rec.update(changes)
        _save(rec)
        return rec


def discard(key):
    with gate():
        _path(key).unlink()


def observe_receipt(rc):
    key = key_for(rc)
    with gate():
        rec = load(key) if _path(key).exists() else {
            "schema_version": "1.0", "key": key, "backend": rc.get("backend", "herdr"), "cwd": rc["cwd"],
            "task_id": rc["task_id"], "round": rc["round"], "request_hash": rc["semantic_task_hash"],
            "binding": rc.get("project_binding", {"session": rc["herdr_session"]}), "acceptance": {"decision": "withheld", "reason": "not assessed"}}
        if rec["backend"] != rc.get("backend", "herdr"):
            raise Conflict("receipt conflicts with the recorded backend")
        rec.update(status=rc["status"], reference={"cwd": rc["cwd"], "run_id": rc["run_id"]},
                   workspace=rc["cwd"], repo_cwd=rc.get("repo_cwd", rc["cwd"]), worktree=rc.get("worktree"),
                   profile=rc["profile"], profile_fingerprint=rc["profile_fingerprint"],
                   active=not rec.get("released", False) and (rc["status"] not in {"completed", "result_invalid", "execution_failed"}
                           or (rc["status"] == "execution_failed" and rc["delivery_state"] != "not_attempted"
                               and not rc.get("process_exited"))))  # a headless CLI's exit is proof it stopped
        _save(rec)


def inspect():
    with gate():
        records = _records()
    return {"schema_version": "1.0", "status": "ok", "max_active": MAX_ACTIVE,
            "active": sum(x["active"] for x in records), "records": records}


def resolve(key, note):
    if not isinstance(note, str) or not note.strip():
        raise r.InputError("a reason confirming the worker stopped and effects were inspected is required")
    with operation(key):
        return update(key, active=False, released=True, resolution=note)


def feedback(key, input_hash, decision, note):
    if decision not in {"accepted", "withheld", "rejected"} or not isinstance(note, str) or not note.strip():
        raise r.InputError("valid decision and nonempty verification note required")
    with operation(key), gate():
        rec = load(key)
        if rec["request_hash"] != input_hash:
            raise Conflict("reviewed input differs from the recorded task")
        if decision == "accepted" and (rec["status"] != "completed" or rec["active"]):
            raise Conflict("only an observed completed result can be accepted")
        rec["acceptance"] = {"decision": decision, "reason": note, "input_hash": input_hash}
        _save(rec)
        return rec


def conflict(t, error):
    return {"schema_version": "1.0", "status": "conflict", "task_id": t["task_id"], "round": t["round"],
            "coordination_key": key_for(t), "candidates": [], "selected": None,
            "warnings": [r.warn("coordination", str(error))]}
