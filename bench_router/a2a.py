"""Opt-in review adapter using only the stock herdr-a2a public CLI."""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from . import coordination as co
from . import routing as r

A2A_BIN = os.environ.get("BENCH_ROUTER_A2A", "herdr-a2a")
STATES = {1: "submitted", 2: "working", 3: "completed", 4: "failed", 5: "canceled",
          6: "input-required", 7: "rejected", 8: "auth-required"}  # SDK 1.0.1 TaskState


def binding(path, profile):
    doc = r.load_json_strict(path, r.TASK_MAX_BYTES)
    if not isinstance(doc, dict) or set(doc) != {"schema_version", "bindings"} or doc["schema_version"] != "1.0" or not isinstance(doc["bindings"], list):
        raise r.InputError("a2a bindings: schema_version 1.0 and bindings array required")
    rows = [b for b in doc["bindings"] if isinstance(b, dict) and b.get("profile") == profile["id"]]
    if len(rows) != 1:
        raise r.InputError("exactly one A2A binding for the selected profile is required")
    b = rows[0]
    fields = {"profile", "profile_fingerprint", "agent", "gateway", "model", "config_file", "config_sha256", "review_only"}
    command = b.get("command")
    if set(b) - fields - {"command"} or not fields <= set(b) or b["review_only"] is not True or not all(isinstance(b[k], str) and b[k] for k in fields - {"review_only"}):
        raise r.InputError(f"A2A review binding: required {sorted(fields)} and optional command argv")
    if command is not None and (not isinstance(command, list) or not command or not all(isinstance(x, str) and x and "\0" not in x for x in command) or not Path(command[0]).is_absolute()):
        raise r.InputError("A2A command must be a nonempty argv with an absolute executable")
    fingerprint = r.profile_fingerprint(profile)
    if b["profile_fingerprint"] != fingerprint or b["agent"] != f"{profile['id']}-{fingerprint[:12]}" or b["model"] != profile["model_id"]:
        raise r.InputError("A2A binding/profile differs; use a fingerprint-versioned agent name and matching model")
    try:
        url = urlsplit(b["gateway"])
        url.port
    except ValueError as e:
        raise r.InputError("invalid A2A gateway origin") from e
    if url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost", "::1"} or url.username or url.password or url.path not in {"", "/"} or url.query or url.fragment:
        raise r.InputError("A2A gateway: explicit loopback HTTP origin without credentials required")
    b = {**b, "gateway": b["gateway"].rstrip("/")}
    path = Path(b["config_file"])
    if not path.is_absolute() or not re.fullmatch(r"[0-9a-f]{64}", b["config_sha256"]):
        raise r.InputError("A2A config: absolute local file and SHA-256 required")
    if path.stat().st_size > r.TASK_MAX_BYTES or hashlib.sha256(path.read_bytes()).hexdigest() != b["config_sha256"]:
        raise r.InputError("A2A operator-attested configuration changed; reconcile workers and renew binding")
    return {**b, "runtime": profile["kind"]}


def _argv(args, gateway, command=None):
    cmd = [*(command or [A2A_BIN]), *args, "--base-url", gateway, "--json"]
    if any("\0" in a for a in cmd):
        raise r.InputError("A2A arguments must not contain NUL")
    if (os.name == "nt" and len(subprocess.list2cmdline(cmd).encode("utf-16-le")) // 2 > 30000) or any(len(a.encode("utf-8")) > 120 * 1024 for a in cmd):
        raise r.InputError("A2A command too large; split review content into bounded tasks")
    return cmd


def _call(cmd, runner):
    p = runner(cmd, capture_output=True, text=True, encoding="utf-8", errors="strict", shell=False, timeout=30)
    if len(p.stdout.encode("utf-8")) > 16 * 1024 * 1024:
        raise ValueError("A2A response exceeds 16 MiB")
    obj = json.loads(p.stdout)
    if not isinstance(obj, dict):
        raise ValueError("A2A response must be an object")
    # A failed task is valid JSON with a nonzero exit status in the stock CLI.
    if p.returncode not in (0, 1) or (p.returncode and not isinstance(obj.get("status"), dict)):
        raise ValueError("A2A CLI did not return a task")
    return obj


def _payload(key, name, obj):
    path = co.directory() / key / name
    path.parent.mkdir(exist_ok=True)
    r.atomic_write(path, json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8"))
    return str(path)


def summary(rec):
    status = rec["status"]
    normalized = "waiting" if status in {"submitted", "working"} else "blocked" if status in {"input-required", "auth-required"} else "execution_failed" if status in {"failed", "canceled", "rejected"} else status
    return {"schema_version": "1.0", "status": normalized, "backend_status": status,
            "coordination_key": rec["key"], "input_hash": rec["request_hash"],
            "reference": rec["reference"], "active": rec["active"],
            "response_path": rec.get("response_path"), "acceptance": rec["acceptance"],
            "continuation_uncertain": rec.get("continuation_uncertain", False)}


def _observe(rec, obj):
    response = _payload(rec["key"], f"response-{r.canonical_hash(obj)}.json", obj)
    task_id = obj.get("id")
    status = obj.get("status")
    state = status.get("state") if isinstance(status, dict) else None
    if isinstance(state, str) and state.startswith("TASK_STATE_"):
        state = state.removeprefix("TASK_STATE_").lower().replace("_", "-")
    else:
        state = STATES.get(state) if type(state) is int else state
    if not isinstance(task_id, str) or not task_id or state not in STATES.values():
        raise ValueError("unrecognized A2A task response")
    reference = rec["reference"]
    if reference and reference["task_id"] != task_id:
        raise ValueError("A2A task identity changed")
    metadata = obj.get("metadata", {})
    target = metadata.get("target") if isinstance(metadata, dict) else None
    if target != rec["binding"]["agent"] or metadata.get("runtime") != rec["binding"]["runtime"]:
        raise ValueError("A2A logical target or runtime differs from the selected agent")
    instance = metadata.get("instance")
    if not isinstance(instance, str) or not instance or (rec.get("instance") and rec["instance"] != instance):
        raise ValueError("A2A worker instance is missing or changed")
    return co.update(rec["key"], status=state, reference={"gateway": rec["binding"]["gateway"], "task_id": task_id},
                     response_path=response, instance=instance, active=not rec.get("released", False) and state != "completed")


def delegate(t, cfg, mapping, snap, warnings, profile_id, bindings_path, context=None, runner=subprocess.run):
    if t["context_files"] or t["constraints"]["required_capabilities"]:
        raise r.InputError("A2A reviews require explicit prompt content; use native dispatch for context files or runtime capabilities")
    profile = next((p for p in cfg["profile"] if p["id"] == profile_id), None)
    if profile is None:
        raise r.InputError("unknown A2A profile")
    b = binding(bindings_path, profile)
    packet = {"purpose": "Review supplied content only; do not modify files, invoke tools or delegate further.",
              "input_hash": r.semantic_task_hash(t), "summary": t["summary"], "content": t["prompt"]}
    cmd = _argv(["delegate", b["agent"], json.dumps(packet, ensure_ascii=False), "--headless"], b["gateway"], b.get("command"))
    key = co.key_for(t)
    try:
        with co.operation(key):
            # Repeated submissions observe; binding changes fail closed and explicit get still works.
            if co._path(key).exists():
                rec, _ = co.reserve(t, "a2a", b)
                return _get(rec, runner)
            from . import herdr
            for receipt in herdr.receipts(t["cwd"]):
                if receipt["status"] not in herdr.SETTLED_STATUSES or co.key_for(receipt) == key:
                    co.native_observed(receipt)
            try:
                catalog = _call(_argv(["discover"], b["gateway"], b.get("command")), runner)
            except (OSError, subprocess.SubprocessError, ValueError):
                return {"schema_version": "1.0", "status": "execution_failed",
                        "error": {"code": "a2a_discovery", "message": "could not verify the A2A catalog; no task submitted"}}
            candidates = catalog.get("agents", [])
            if not isinstance(candidates, list):
                raise r.InputError("A2A discovery returned an invalid agents list")
            match = next((x for x in candidates if isinstance(x, dict) and x.get("name") == b["agent"]), None)
            if not match or match.get("available") is not True or match.get("runtime") != profile["kind"]:
                raise r.InputError("A2A agent missing, unavailable or runtime mismatched")
            assessment = r.evaluate_v1(t, cfg, mapping, snap, warnings, datetime.now(timezone.utc), context=context)
            selected = r.apply_selection(assessment, cfg, profile_id)
            if selected["status"] != "selected":
                return selected
            rec, _ = co.reserve(t, "a2a", b)
            _payload(key, "input.json", {"task": t, "assessment": selected})
            try:
                rec = _observe(rec, _call(cmd, runner))
            except (OSError, subprocess.SubprocessError, ValueError):
                return summary(co.update(key, status="delivery_uncertain"))
            return summary(rec)
    except co.Conflict as e:
        return co.conflict(t, e)


def _get(rec, runner):
    if not rec["reference"]:
        return summary(rec)  # Lost initial response: never submit again to obtain an id.
    try:
        obj = _call(_argv(["get", rec["reference"]["task_id"]], rec["binding"]["gateway"], rec["binding"].get("command")), runner)
        return summary(_observe(rec, obj))
    except (OSError, subprocess.SubprocessError, ValueError):
        return summary(co.update(rec["key"], status="delivery_uncertain"))


def control(key, action, answer=None, runner=subprocess.run):
    if action not in {"get", "continue", "cancel", "close"}:
        raise r.InputError("unsupported A2A operation")
    with co.operation(key):
        rec = co.load(key)
        if rec["backend"] != "a2a":
            raise r.InputError("this task belongs to native Herdr; use collect")
        if action == "get":
            return _get(rec, runner)
        if not rec["reference"]:
            raise co.Conflict("A2A task id is unknown; inspect effects, do not resubmit")
        if action == "continue":
            if rec.get("released") or rec.get("continuation_uncertain") or rec["status"] != "input-required":
                raise co.Conflict("only a confirmed input-required task can continue; inspect uncertain delivery first")
            if not isinstance(answer, str) or not answer.strip():
                raise r.InputError("nonempty answer required")
        args = [action, rec["reference"]["task_id"], *([answer] if action == "continue" else [])]
        cmd = _argv(args, rec["binding"]["gateway"], rec["binding"].get("command"))
        if action == "continue":
            answer_path = _payload(key, f"answer-{r.canonical_hash(answer)}.json", {"answer": answer})
            co.update(key, status="delivery_uncertain", continuation_uncertain=True, answer_path=answer_path)
        try:
            obj = _call(cmd, runner)
            rec = _observe(rec, obj)
            if action == "continue":
                rec = co.update(key, continuation_uncertain=False)
            return summary(rec)
        except (OSError, subprocess.SubprocessError, ValueError):
            return summary(co.update(key, status="delivery_uncertain"))
