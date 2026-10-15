"""Projects CLI execution with durable receipts and per-run result validation."""
import contextlib
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import locking
from . import routing as r

PROJECTS_BIN = os.environ.get("BENCH_ROUTER_PROJECTS", "herdr-projects")
SHORT_CALL_S = 15
MAX_PROMPT_ARG_BYTES = r.TASK_MAX_BYTES
RESULT_MD_MAX = 10 * 1024 * 1024
RESULT_JSON_MAX = 64 * 1024
SETTLED_STATUSES = {"completed", "result_invalid", "execution_failed"}  # 이 외의 receipt는 새 live dispatch를 막는다
RUN_ID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


class Busy(Exception):
    pass


def _now():
    return datetime.now(timezone.utc)


def _iso(t):
    return t.isoformat(timespec="seconds")


# ---------- Projects public CLI ----------

def project_call(project, argv, runner=subprocess.run, raw=False, timeout_s=SHORT_CALL_S):
    cmd = [PROJECTS_BIN, "--root", str(Path(project).parent), *argv]
    try:
        p = runner(cmd, capture_output=True, text=True, encoding="utf-8", errors="strict",
                   timeout=timeout_s, shell=False)
        if p.returncode:
            raise ValueError((p.stderr or p.stdout)[:300])
        if len(p.stdout.encode("utf-8")) > r.SNAPSHOT_MAX_BYTES:
            raise ValueError("Projects response too large")
        return (p.stdout if raw else json.loads(p.stdout)), None
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, {"code": "projects_error", "message": str(e)[:300]}


def project_binding(session=None, project=None):
    path = Path(project or os.environ.get("BENCH_ROUTER_PROJECT_DIR", ""))
    if not path.is_absolute() or not (path / "PROJECT.md").is_file():
        raise r.InputError("BENCH_ROUTER_PROJECT_DIR must name an opened Projects project directory")
    path = path.resolve()
    cfg_path = Path(os.environ.get("HOME") or Path.home()) / ".config/herdr-projects/config.toml"
    cfg = r._load_toml(cfg_path)
    layers = cfg.get("safety", {})
    if not isinstance(layers, dict) or any(not isinstance(v, dict) for v in layers.values()):
        raise r.InputError("Projects safety settings must be TOML tables")
    safety = {**layers.get("default", {}), **layers.get(str(path), {})}
    if safety.get("yolo", False) or safety.get("thread_agent_args", []):
        raise r.InputError("Projects yolo and legacy thread_agent_args must be disabled; use named profiles")
    coordinator = r.load_json_strict(path / ".state/coordinator.json", r.TASK_MAX_BYTES)
    if not isinstance(coordinator, dict) or not isinstance(coordinator.get("socket"), str) or not coordinator["socket"]:
        raise r.InputError("Projects project has no recorded session socket")
    if session is not None and coordinator.get("session") != session:
        raise r.InputError("Projects project belongs to another Herdr session")
    return {"project": str(path), "socket": coordinator["socket"],
            "config_file": str(cfg_path), "config_sha256": hashlib.sha256(cfg_path.read_bytes()).hexdigest()}


def probe(p, which=shutil.which):
    if p["executable"] != p["kind"]:
        return "executable_kind_mismatch"
    return None if which(p["executable"]) else "executable_not_found"


# ---------- receipt ----------

def bench_dir(cwd):
    return Path(cwd) / ".bench-router"


def run_dir(cwd, run_id):
    if not RUN_ID_RE.fullmatch(run_id or ""):
        raise r.InputError("run_id: UUID required")
    return bench_dir(cwd) / "runs" / run_id


def save(rc):
    rc["updated_at"] = _iso(_now())
    r.atomic_write(Path(rc["run_dir"]) / "receipt.json",
                   json.dumps(rc, ensure_ascii=False, indent=1).encode("utf-8"))


def load_receipt(cwd, run_id):
    try:
        return json.loads((run_dir(cwd, run_id) / "receipt.json").read_text("utf-8"))
    except FileNotFoundError:
        raise r.InputError(f"no receipt for run {run_id} under {cwd}")


def receipts(cwd):
    out = []
    for f in sorted((bench_dir(cwd) / "runs").glob("*/receipt.json")):  # ponytail: 선형 스캔, run 수가 많아지면 인덱스
        out.append(json.loads(f.read_text("utf-8")))
    return out


@contextlib.contextmanager
def dispatch_lock(cwd):
    bench_dir(cwd).mkdir(exist_ok=True)
    with locking.exclusive(bench_dir(cwd) / "dispatch.lock",
                           Busy("another bench-router dispatch/collect holds the lock for this cwd")):
        yield


# ---------- 결과 계약 ----------

def contract_text(rc):
    rd = rc["run_dir"]
    return (f"\n\n---\n[bench-router 실행 계약 — 위 작업의 범위나 권한을 넓히지 않습니다]\n"
            f"실행 식별자: {rc['run_id']}\n검증 토큰: {rc['nonce']}\n프로필 지문: {rc['profile_fingerprint']}\n"
            f"결과 디렉터리(절대 경로): {rd}\n\n"
            "요청된 작업을 수행하고, result.md에 결과/변경/검증/미완료 사항을 기록하세요.\n"
            "result.md를 완성한 뒤 result.json을 마지막에 한 번에 작성하세요.\n"
            # 라우터는 settled(idle/done) 이후에만 검사하므로 원자적 쓰기는 불필요. mv/검증 스크립트는
            # 권한 승인(blocked)을 유발했다(smoke 2026-10-12 실측).
            "임시 파일·이동(mv)·별도 검증 스크립트는 필요 없습니다. 해시는 `sha256sum result.md`로 계산하세요.\n"
            "result.json은 schema_version(\"1.0\"), run_id, nonce, profile_fingerprint,\n"
            "status, result_file, result_sha256, checks를 포함해야 합니다.\n"
            "status는 success, partial, fail 중 실제 작업 결과에 맞게 선택하세요.\n"
            "result_file은 \"result.md\"이며 result_sha256은 최종 파일의 SHA-256(hex)입니다.\n"
            "checks는 {command, outcome(passed|failed|not_run), notes} 배열입니다(없으면 []).\n"
            "파일 작성에 실패하면 성공을 주장하지 말고 오류를 명확하게 출력하세요.\n"
            f"마지막 줄은 DONE {rc['run_id']} {rd}/result.json 으로 출력하세요.")


def _regular_inside(path, root, max_bytes):
    if path.is_symlink() or not path.is_file():
        return f"{path.name}: missing or not a regular file"
    if os.path.commonpath([str(path.resolve()), str(root.resolve())]) != str(root.resolve()):
        return f"{path.name}: escapes run directory"
    if path.stat().st_size > max_bytes:
        return f"{path.name}: larger than {max_bytes} bytes"
    return None


def check_result(rc):
    """(manifest|None, 사유|None). run_id·nonce·지문·경로·크기·SHA-256 모두 일치해야 유효."""
    root = Path(rc["run_dir"])
    rj, rm = root / "result.json", root / "result.md"
    for p, mx in ((rj, RESULT_JSON_MAX), (rm, RESULT_MD_MAX)):
        why = _regular_inside(p, root, mx)
        if why:
            return None, why
    try:
        m = r.load_json_strict(rj, RESULT_JSON_MAX)
    except r.InputError as e:
        return None, f"result.json: {e}"
    expect = {"schema_version": r.SCHEMA_VERSION, "run_id": rc["run_id"], "nonce": rc["nonce"],
              "profile_fingerprint": rc["profile_fingerprint"], "result_file": "result.md"}
    if not isinstance(m, dict):
        return None, "result.json: object required"
    for k, v in expect.items():
        if m.get(k) != v:
            return None, f"result.json: {k} mismatch (stale or foreign result)"
    if m.get("status") not in ("success", "partial", "fail"):
        return None, "result.json: status must be success|partial|fail"
    checks = m.get("checks")
    if not isinstance(checks, list) or not all(
            isinstance(c, dict) and isinstance(c.get("command"), str) and c.get("outcome") in ("passed", "failed", "not_run")
            and isinstance(c.get("notes", ""), str) for c in checks):
        return None, "result.json: checks must be [{command, outcome, notes}]"
    body = rm.read_bytes()
    try:
        empty = not body.decode("utf-8").strip()
    except UnicodeDecodeError:
        return None, "result.md: invalid UTF-8"
    if empty:
        return None, "result.md: empty"
    if m.get("result_sha256") != hashlib.sha256(body).hexdigest():
        return None, "result.json: result_sha256 does not match result.md"
    return m, None


# ---------- 상태 전이 ----------

def _observe(rc, state=None, error=None, note=None):
    rc["herdr_state"] = state if state is not None else rc.get("herdr_state")
    rc["last_observation"] = {"at": _iso(_now()), "agent_status": state, "error": error, "note": note}


def settle(rc, state):
    """관찰된 herdr 상태 + 결과 파일로 receipt 상태를 결정한다. idle/done만으로는 성공이 아니다."""
    _observe(rc, state)
    if state in ("idle", "done"):
        manifest, why = check_result(rc)
        if manifest:
            rc.update(status="completed", task_outcome=manifest["status"], settled_contract=True,
                      result_path=str(Path(rc["run_dir"]) / "result.md"),
                      manifest_path=str(Path(rc["run_dir"]) / "result.json"))
            if rc["delivery_state"] in ("submission_attempted", "uncertain"):
                rc["delivery_state"] = "activity_observed"  # nonce가 맞는 결과 = 전송·실행 증거
        elif rc["delivery_state"] in ("submission_attempted", "uncertain"):
            rc.update(status="delivery_uncertain", delivery_state="uncertain")
            _observe(rc, state, note=f"settled without valid result; delivery unknown ({why})")
        else:
            rc["status"] = "result_invalid"
            _observe(rc, state, note=why)
    elif state == "blocked":
        rc["status"] = "blocked"
    elif state == "working":
        rc["status"] = "timed_out"  # 계속 실행 중; collect로 회수
    else:
        rc.update(status="delivery_uncertain")
    return rc


def execute(rc, prompt, profile, session=None, runner=subprocess.run):
    project = rc["project_binding"]["project"]
    remaining = (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds()
    version, err = project_call(project, ["--version"], runner, raw=True, timeout_s=min(SHORT_CALL_S, max(0.001, remaining)))
    if err or not re.fullmatch(r"herdr-projects 0\.2\.34(?:\+[^\s]+)?", (version or "").strip()):
        rc["status"] = "execution_failed"
        _observe(rc, error=err, note="Projects 0.2.34 is required; nothing submitted")
        save(rc)
        return rc
    rc["projects_version"] = version.strip()
    remaining = (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds()
    resolved, err = project_call(project, ["profile", "resolve", profile["id"]], runner,
                                 timeout_s=min(SHORT_CALL_S, max(0.001, remaining)))
    if err or resolved != {"name": profile["id"], "agent": profile["kind"], "args": profile["args"]}:
        rc["status"] = "execution_failed"
        _observe(rc, error=err, note="Projects profile differs from the selected launch setup; nothing submitted")
        save(rc)
        return rc
    if project_binding(session, project) != rc["project_binding"]:
        raise r.InputError("Projects configuration changed before submission")
    task_file = Path(rc["run_dir"]) / "input.txt"
    r.atomic_write(task_file, prompt.encode("utf-8"))
    remaining = (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds()
    if remaining <= 0:
        rc["status"] = "execution_failed"
        _observe(rc, note="deadline elapsed before thread submission")
        save(rc)
        return rc
    rc["delivery_state"] = "submission_attempted"
    save(rc)  # Persist before thread start: a lost response must never create a second thread.
    obj, err = project_call(project, ["thread", "start", Path(project).name, "--title", "br-" + rc["run_id"],
                                     "--repo", rc["cwd"], "--kind", "checkout", "--profile", profile["id"],
                                     "--task-file", str(task_file)], runner, timeout_s=min(SHORT_CALL_S, remaining))
    if err or not isinstance(obj, dict) or not re.fullmatch(r"t-[0-9]{4,}", str(obj.get("id", ""))):
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        _observe(rc, error=err, note="thread start unconfirmed; inspect Projects, never resubmit")
        save(rc)
        return rc
    rc["thread_id"] = obj["id"]
    save(rc)
    remaining = max(0, (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds() * 1000)
    if remaining <= 0:
        rc["status"] = "timed_out"
        save(rc)
        return rc
    return collect(rc, remaining, session, runner)


def collect(rc, wait_ms=0, session=None, runner=subprocess.run):
    """Observe the recorded thread only; never start, restart or re-prompt it."""
    if rc.get("backend") != "projects":
        raise r.InputError("legacy receipt: inspect the original worker; automatic backend migration is refused")
    if rc["status"] == "completed" and rc.get("settled_contract"):
        return rc
    if rc["delivery_state"] == "not_attempted":
        return rc
    if not rc.get("thread_id"):
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        save(rc)
        return rc
    project = rc["project_binding"]["project"]
    deadline = time.monotonic() + wait_ms / 1000
    while True:
        try:
            if project_binding(session, project) != rc["project_binding"]:
                raise r.InputError("Projects configuration or session changed; inspect the recorded worker")
            timeout = min(SHORT_CALL_S, max(0.001, deadline - time.monotonic())) if wait_ms > 0 else SHORT_CALL_S
            version, err = project_call(project, ["--version"], runner, raw=True, timeout_s=timeout)
            if err or version.strip() != rc["projects_version"]:
                raise r.InputError("Projects executable version changed; inspect the recorded worker")
            timeout = min(SHORT_CALL_S, max(0.001, deadline - time.monotonic())) if wait_ms > 0 else SHORT_CALL_S
            obj, err = project_call(project, ["thread", "show", Path(project).name, rc["thread_id"], "--json"], runner,
                                    timeout_s=timeout)
            if err:
                raise r.InputError(err["message"])
            if (not isinstance(obj, dict) or obj.get("id") != rc["thread_id"]
                    or obj.get("profile") != rc["profile"] or obj.get("agent") != rc["kind"]
                    or obj.get("kind") != "checkout" or os.path.realpath(obj.get("cwd") or "") != rc["cwd"]
                    or obj.get("machine") or not obj.get("pane_id") or not obj.get("workspace_id")
                    or (rc["pane_id"] and obj["pane_id"] != rc["pane_id"])
                    or (rc["workspace_id"] and obj["workspace_id"] != rc["workspace_id"])
                    or obj.get("status") not in {"open", "starting", "failed"}):
                raise r.InputError("Projects thread identity or working directory differs from the receipt")
            rc.update(pane_id=obj["pane_id"], workspace_id=obj["workspace_id"], agent_name=obj.get("agent_name"))
            state = obj.get("note")
            if obj.get("status") == "failed":
                rc["status"] = "execution_failed"
                _observe(rc, state, note=obj.get("error") or "thread has no live agent")
            elif obj.get("prompt_pending") is True or obj.get("status") == "starting":
                rc["status"] = "blocked" if obj.get("group_token") == "waiting-on-you" else "timed_out"
                _observe(rc, state, note="Projects has not confirmed initial brief delivery")
            elif state in {"no agent", "pane closed"}:
                rc["status"] = "execution_failed"
                _observe(rc, state, note="thread has no live agent after brief delivery")
            elif obj.get("prompt_pending") is not False or state not in {"working", "blocked", "idle", "done"}:
                raise r.InputError("Projects has no confirmed live state; recorded/stale state is insufficient")
            else:
                rc["delivery_state"] = "activity_observed"
                settle(rc, state)
            if rc["status"] == "blocked":
                tail, _ = project_call(project, ["thread", "read", Path(project).name, rc["thread_id"]], runner, raw=True)
                rc["diagnostic_tail"] = (tail or "")[-4000:]
        except (r.InputError, OSError) as e:
            rc.update(status="delivery_uncertain", delivery_state="uncertain")
            _observe(rc, note=str(e))
        save(rc)
        if rc["status"] in SETTLED_STATUSES | {"blocked", "delivery_uncertain"} or time.monotonic() >= deadline:
            return rc
        time.sleep(min(1, max(0, deadline - time.monotonic())))


def dispatch(t, cfg, mapping, snap, snap_warnings, session=None, runner=subprocess.run, which=shutil.which,
             profile_id=None, context=None, selection_mode="parallel_pinned",
             selection=None, check_digest=True):
    from . import coordination as co
    key = co.key_for(t)
    try:
        with co.operation(key):
            existing = [x for x in receipts(t["cwd"]) if x["task_id"] == t["task_id"] and x["round"] == t["round"]]
            if existing and existing[0]["herdr_session"] != session:
                raise co.Conflict("dispatch session differs from the recorded native run; use collect")
            if existing:
                co.observe_receipt(existing[0])
            binding = existing[0].get("project_binding") if existing else project_binding(session)
            rec, fresh = co.reserve(t, "projects", binding)
            if not fresh and not existing:
                raise co.Conflict("recorded native submission has no receipt; inspect effects before resolving, never resend")
            result = _dispatch(t, cfg, mapping, snap, snap_warnings, session, runner, which,
                               profile_id, context, selection_mode, selection, check_digest)
            if result.get("run_id"):
                co.observe_receipt(load_receipt(t["cwd"], result["run_id"]))
            elif fresh:
                co.discard(key)  # No native receipt means dispatch never reached execution.
            return {**result, "coordination_key": key}
    except co.Conflict as e:
        return co.conflict(t, e)


def _dispatch(t, cfg, mapping, snap, snap_warnings, session=None, runner=subprocess.run, which=shutil.which,
             profile_id=None, context=None, selection_mode="parallel_pinned",
             selection=None, check_digest=True):
    """live route. 선택 → receipt → herdr 실행. 같은 (task_id, round)는 재전송 없이 collect.
    profile_id: 제약·가용성을 통과한 후보 중 이 프로필로 고정(parallel fanout).
    selection: Orchestrator 선택 기록(validate_selection). digest가 지금 입력과 다르면 실행하지 않는다(stale_assessment).
    같은 round 회수가 digest 검사보다 우선한다: 새 판단으로 다시 실행하려면 새 round."""
    now = _now()
    availability = {p["id"]: probe(p, which) for p in cfg["profile"]}
    if selection is not None:
        profile_id = selection["profile"]
    res = (r.evaluate_v1(t, cfg, mapping, snap, snap_warnings, now, availability, context) if profile_id
           else r.route(t, cfg, mapping, snap, snap_warnings, now, availability, context))
    if profile_id:
        res = r.apply_selection(res, cfg, profile_id, selection, selection_mode, check_digest)
    try:
        with dispatch_lock(t["cwd"]):
            existing = [x for x in receipts(t["cwd"]) if x["task_id"] == t["task_id"] and x["round"] == t["round"]]
            if existing:
                rc = existing[0]
                if rc["semantic_task_hash"] != res["task_hash"]:
                    return {**res, "status": "conflict", "run_id": rc["run_id"],
                            "warnings": res["warnings"] + [r.warn("task_round_conflict",
                                                                  "same task_id/round with different content")]}
                if profile_id and rc["profile"] != profile_id:
                    return {**res, "status": "conflict", "run_id": rc["run_id"],
                            "warnings": res["warnings"] + [r.warn("profile_round_conflict",
                                                                  "same task_id/round already uses another profile")]}
                rc = collect(rc, t["constraints"]["timeout_ms"], session, runner)
                prior = r.load_json_strict(Path(rc["run_dir"]) / "decision.json", r.SNAPSHOT_MAX_BYTES)
                out = output(prior, rc, reused=True)
                if selection is not None and prior.get("selection") != res["selection"]:
                    out["warnings"] = out.get("warnings", []) + [r.warn(
                        "selection_differs_from_recorded", "returning the recorded run; use a new round to act on a new selection")]
                return out
            if res["status"] != "selected":
                return res
            profile = next(p for p in cfg["profile"] if p["id"] == res["selected"]["profile"])
            unresolved = [x["run_id"] for x in receipts(t["cwd"]) if x["status"] not in SETTLED_STATUSES]
            if unresolved:
                return {**res, "status": "conflict", "warnings": res["warnings"] + [r.warn(
                    "unresolved_run", f"run {unresolved[0]} is not settled; collect it before a new dispatch")]}
            run_id = str(uuid.uuid4())
            rc = {"schema_version": r.SCHEMA_VERSION, "task_id": t["task_id"], "round": t["round"],
                  "semantic_task_hash": res["task_hash"], "run_id": run_id, "nonce": secrets.token_hex(16),
                  "backend": "projects", "project_binding": project_binding(session),
                  "kind": profile["kind"], "thread_id": None,
                  "profile": profile["id"], "profile_fingerprint": res["selected"]["profile_fingerprint"],
                  "cwd": t["cwd"], "run_dir": str(run_dir(t["cwd"], run_id)),
                  "agent_name": None, "workspace_id": None, "pane_id": None,
                  "herdr_session": session, "status": "dispatching", "delivery_state": "not_attempted",
                  "timeout_ms": t["constraints"]["timeout_ms"], "created_at": _iso(now),
                  "deadline_at": _iso(now + timedelta(milliseconds=t["constraints"]["timeout_ms"])),
                  "result_path": None, "manifest_path": None, "task_outcome": None, "herdr_state": None,
                  "settled_contract": False, "last_observation": None}
            prompt = t["prompt"] + contract_text(rc)
            if len(prompt.encode("utf-8")) > MAX_PROMPT_ARG_BYTES:
                raise r.InputError(f"prompt + contract exceeds {MAX_PROMPT_ARG_BYTES} bytes (task file limit)")
            Path(rc["run_dir"]).mkdir(parents=True)
            # 판단 기록 = 출력 + 같은 입력의 evaluate 2.0(통과·탈락 제약의 관측값·기준값, facts).
            # ponytail: assess를 한 번 더 돈다(결정적, 입력 동일). 느려지면 route가 assessment를 넘기게
            assessment = r.evaluate(t, cfg, mapping, snap, snap_warnings, now, availability, context)
            r.atomic_write(Path(rc["run_dir"]) / "decision.json",
                           json.dumps({**res, "assessment": assessment}, ensure_ascii=False).encode("utf-8"))
            save(rc)  # receipt 저장 실패 시 예외 → 전송하지 않음
            return output(res, execute(rc, prompt, profile, session, runner))
    except Busy as e:
        return {**res, "status": "conflict", "warnings": res["warnings"] + [r.warn("dispatch_lock", str(e))]}


def collect_run(cwd, run_id, wait_ms, session=None, runner=subprocess.run):
    from . import coordination as co
    cwd = os.path.realpath(cwd)
    try:
        with dispatch_lock(cwd):
            rc = load_receipt(cwd, run_id)
            if session is not None and session != rc["herdr_session"]:
                raise r.InputError("collect session differs from the recorded run")
            co.observe_receipt(rc)
            rc = collect(rc, wait_ms, rc["herdr_session"], runner)
            co.observe_receipt(rc)
    except (Busy, co.Conflict) as e:
        return {"schema_version": r.SCHEMA_VERSION, "status": "conflict", "run_id": run_id,
                "warnings": [r.warn("dispatch_lock", str(e))]}
    return {**output(None, rc), "coordination_key": co.key_for(rc)}


def feedback(cwd, run_id, outcome, evaluator=None, note=None):
    cwd = os.path.realpath(cwd)
    rc = load_receipt(cwd, run_id)
    entry = {"run_id": run_id, "outcome": outcome, "evaluator": evaluator, "note": note,
             "feedback_at": _iso(_now()), "task_outcome_reported": rc.get("task_outcome"),
             "receipt_status": rc["status"]}
    with open(Path(rc["run_dir"]) / "feedback.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return {"schema_version": r.SCHEMA_VERSION, "status": "recorded", **entry}


def output(res, rc, reused=False):
    out = dict(res) if res else {"schema_version": r.SCHEMA_VERSION, "task_id": rc["task_id"], "round": rc["round"]}
    out.pop("assessment", None)  # decision.json에만 둔다
    out.update({"status": rc["status"], "run_id": rc["run_id"], "result_path": rc["result_path"],
                "manifest_path": rc["manifest_path"], "task_outcome": rc["task_outcome"],
                "herdr_state": rc["herdr_state"], "delivery_state": rc["delivery_state"],
                "receipt_path": str(Path(rc["run_dir"]) / "receipt.json"), "deadline_at": rc["deadline_at"],
                "workspace_id": rc["workspace_id"], "thread_id": rc.get("thread_id"),
                "project": rc.get("project_binding", {}).get("project"), "last_observation": rc["last_observation"],
                "diagnostic_tail": rc.get("diagnostic_tail"), "reused_receipt": reused})
    out["selected"] = {**(out.get("selected") or {}), "profile": rc["profile"],
                       "profile_fingerprint": rc["profile_fingerprint"], "agent_name": rc["agent_name"],
                       "pane_id": rc["pane_id"]}
    out["reassignment"] = ("collect_first" if rc["delivery_state"] in ("submission_attempted", "uncertain")
                            or rc["status"] in ("timed_out", "waiting", "delivery_uncertain") else
                            "safe_to_retry" if rc["delivery_state"] == "not_attempted" else "review_result")
    return out
