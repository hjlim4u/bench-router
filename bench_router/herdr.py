"""live 위임: 실행 receipt(중복 전송 방지) + herdr CLI(argv) + 실행별 결과 계약 검사. 계약은 04 문서.

herdr 0.9.3 실측(docs/evidence/herdr-0.9.3): 성공은 stdout JSON {"result": ...}, 실패는 stderr JSON
{"error": {"code", "message"}} + exit 1, 문법 오류 exit 2.
"""
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

from . import routing as r

# herdr 0.9.3 `agent start --help`의 --kind 값. 각 kind는 같은 이름의 canonical executable을 실행한다.
HERDR_KINDS = {"pi", "claude", "codex", "gemini", "cursor", "devin", "agy", "cline", "omp", "mastracode", "opencode",
               "copilot", "kimi", "kiro", "droid", "amp", "grok", "hermes", "kilo", "qodercli", "qwen", "letta",
               "maki", "muse"}
HERDR_BIN = os.environ.get("BENCH_ROUTER_HERDR", "herdr")
START_TIMEOUT_MAX_MS = 300_000  # herdr agent start 상한
START_TIMEOUT_MIN_MS = 5_000    # ponytail: herdr에 명시된 최소값 없음. 이보다 적은 예산이면 시작하지 않는다.
SHORT_CALL_S = 15
CALL_GRACE_S = 10
MAX_PROMPT_ARG_BYTES = 120 * 1024  # Linux MAX_ARG_STRLEN(128 KiB) — herdr prompt는 positional 인자만 받는다
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


# ---------- herdr 호출 ----------

def call(argv, timeout_s, session=None, runner=subprocess.run, raw=False):
    """(result, error). shell 없이 argv 전달 — prompt 문자열은 해석되지 않는다.
    raw=True: stdout 텍스트 그대로 (pane/agent read는 JSON이 아닌 텍스트를 출력 — 0.9.3 실측)."""
    cmd = [HERDR_BIN, *(["--session", session] if session else []), *argv]
    try:
        p = runner(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                   timeout=timeout_s, shell=False)
    except subprocess.TimeoutExpired:
        return None, {"code": "subprocess_timeout", "message": f"herdr {argv[0]} {argv[1] if len(argv) > 1 else ''} "
                                                               f"exceeded {timeout_s:.0f}s"}
    except FileNotFoundError:
        return None, {"code": "herdr_not_found", "message": f"{HERDR_BIN} not on PATH"}
    if p.returncode == 0:
        if raw:
            return p.stdout, None
        try:
            return json.loads(p.stdout)["result"], None
        except (ValueError, KeyError, TypeError):
            return None, {"code": "unparseable_output", "message": p.stdout[:300]}
    try:
        err = json.loads(p.stderr)["error"]
        return None, {"code": str(err["code"]), "message": str(err["message"])}
    except (ValueError, KeyError, TypeError):
        return None, {"code": f"exit_{p.returncode}", "message": (p.stderr or p.stdout)[:300]}


def probe(p, which=shutil.which):
    """live 가용성. 실행 파일 존재와 herdr kind 지원만 확인한다(로그인/모델 접근은 확인하지 않음)."""
    if p["kind"] not in HERDR_KINDS:
        return "herdr_kind_unsupported"
    if p["executable"] != p["kind"]:
        return "executable_kind_mismatch"  # herdr --kind는 canonical executable을 실행
    if not which(p["executable"]):
        return "executable_not_found"
    return None


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
    import fcntl  # Linux/macOS(WSL)
    bench_dir(cwd).mkdir(exist_ok=True)
    with open(bench_dir(cwd) / "dispatch.lock", "a") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Busy("another bench-router dispatch/collect holds the lock for this cwd")
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


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


def _tail(rc, h):
    if not rc.get("pane_id"):
        return None
    # visible: blocked 상태의 alternate-screen에서는 긴 recent 읽기가 거부된다(agent_not_idle, 0.9.3 실측)
    text, err = h(["pane", "read", rc["pane_id"], "--source", "visible"], SHORT_CALL_S, raw=True)
    return None if err else text[-4000:]


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


def _remaining_ms(deadline_mono):
    return int((deadline_mono - time.monotonic()) * 1000)


def execute(rc, prompt, profile, session=None, runner=subprocess.run):
    """새 workspace → agent start → 상태 확인 → (submission_attempted 기록) → prompt --wait 1회 → 계약 검사."""
    def h(argv, timeout_s, raw=False):
        return call(argv, timeout_s, session, runner, raw)

    deadline = time.monotonic() + rc["timeout_ms"] / 1000

    def fail(status, error=None, note=None):
        rc["status"] = status
        _observe(rc, error=error, note=note)
        rc["diagnostic_tail"] = _tail(rc, h) if status in ("execution_failed", "blocked") else None
        save(rc)
        return rc

    ws, err = h(["workspace", "create", "--cwd", rc["cwd"], "--label", f"bench-router {rc['task_id']} r{rc['round']}",
                 "--no-focus"], SHORT_CALL_S)
    if err:
        return fail("execution_failed", err, "workspace create failed")
    try:
        rc["workspace_id"], rc["pane_id"] = ws["workspace"]["workspace_id"], ws["root_pane"]["pane_id"]
    except (KeyError, TypeError):
        return fail("execution_failed", None, "workspace create: unexpected response")
    save(rc)

    _, err = h(["agent", "get", rc["agent_name"]], SHORT_CALL_S)
    if not err or err["code"] != "agent_not_found":
        return fail("execution_failed", err, "agent name already in use or unverifiable")

    start_ms = min(_remaining_ms(deadline), START_TIMEOUT_MAX_MS)
    if start_ms < START_TIMEOUT_MIN_MS:
        return fail("timed_out", None, "not enough budget to start an agent")
    st, err = h(["agent", "start", rc["agent_name"], "--kind", profile["kind"], "--pane", rc["pane_id"],
                 "--timeout", str(start_ms), "--", *profile["args"]], start_ms / 1000 + CALL_GRACE_S)
    if err:
        return fail("blocked" if err["code"] == "agent_not_ready" else "execution_failed", err, "agent start failed")
    agent = (st or {}).get("agent") or {}
    if agent.get("name") != rc["agent_name"] or agent.get("pane_id") != rc["pane_id"]:
        return fail("execution_failed", None, f"started agent identity mismatch: {agent.get('name')}@{agent.get('pane_id')}")
    rc["agent_argv"] = st.get("argv")
    save(rc)

    g, err = h(["agent", "get", rc["agent_name"]], SHORT_CALL_S)
    state = ((g or {}).get("agent") or {}).get("agent_status")
    if err or state not in ("idle", "done") or g["agent"].get("pane_id") != rc["pane_id"]:
        return fail("blocked" if state == "blocked" else "execution_failed", err, f"not ready for prompt (state={state})")

    remaining = _remaining_ms(deadline)
    if remaining < 1000:
        return fail("timed_out", None, "deadline reached before prompt")
    rc["delivery_state"] = "submission_attempted"
    save(rc)  # 전송 전에 fsync: 이후 crash가 나도 자동 재전송하지 않는다
    pr, err = h(["agent", "prompt", rc["agent_name"], prompt, "--wait", "--timeout", str(remaining)],
                remaining / 1000 + CALL_GRACE_S)
    if err:
        code = err["code"]
        if code == "agent_blocked":  # 입력 전송 전 거부 (herdr 문서)
            rc.update(status="blocked", delivery_state="not_attempted")
        elif code == "timeout":
            rc.update(status="timed_out", delivery_state="uncertain")
        else:  # agent_prompt_stalled, subprocess_timeout, unparseable 등: 전송 여부 모름
            rc.update(status="delivery_uncertain", delivery_state="uncertain")
        _observe(rc, error=err, note="prompt not confirmed; do not resend, use collect")
        g, gerr = h(["agent", "get", rc["agent_name"]], SHORT_CALL_S)
        if not gerr:
            rc["herdr_state"] = g["agent"].get("agent_status")
        save(rc)
        return rc
    rc["delivery_state"] = "activity_observed"  # --wait는 working/blocked 관찰을 요구한다
    settle(rc, ((pr or {}).get("agent") or {}).get("agent_status"))
    if rc["status"] == "blocked":  # 승인/질문 화면을 Orchestrator에 전달
        rc["diagnostic_tail"] = _tail(rc, h)
    save(rc)
    return rc


def collect(rc, wait_ms=0, session=None, runner=subprocess.run):
    """기존 run을 관찰·회수한다. prompt는 다시 보내지 않는다."""
    def h(argv, timeout_s):
        return call(argv, timeout_s, session, runner)

    if rc["status"] == "completed" and rc.get("settled_contract"):
        return rc
    if rc["delivery_state"] == "not_attempted":  # prompt를 보낸 적 없음: 회수할 작업이 없다
        if rc["status"] not in SETTLED_STATUSES:
            rc["pre_prompt_failure"] = {"status": rc["status"], "observation": rc["last_observation"]}
            rc["status"] = "execution_failed"
            _observe(rc, note=f"prompt was never sent (was {rc['pre_prompt_failure']['status']}); "
                              "resolve the cause, then dispatch a new round")
            save(rc)
        return rc
    g, err = h(["agent", "get", rc["agent_name"]], SHORT_CALL_S)
    if err:
        if err["code"] == "agent_not_found":
            if rc["status"] not in SETTLED_STATUSES:
                rc["status"] = "execution_failed"
                _observe(rc, error=err, note="agent exited without a settled observation; check partial work")
        else:
            _observe(rc, error=err, note="herdr unavailable")
        save(rc)
        return rc
    if g["agent"].get("pane_id") != rc["pane_id"]:
        rc["status"] = "execution_failed"
        _observe(rc, note="agent name now refers to a different pane")
        save(rc)
        return rc
    state = g["agent"].get("agent_status")
    if state == "working" and wait_ms > 0:
        w, err = h(["agent", "wait", rc["agent_name"], "--timeout", str(wait_ms)], wait_ms / 1000 + CALL_GRACE_S)
        state = ((w or {}).get("agent") or {}).get("agent_status", "working") if not err else "working"
    settle(rc, state)
    save(rc)
    return rc


# ---------- 진입점 ----------

def dispatch(t, cfg, mapping, snap, snap_warnings, session=None, runner=subprocess.run, which=shutil.which):
    """live route. 선택 → receipt → herdr 실행. 같은 (task_id, round)는 재전송 없이 collect."""
    now = _now()
    availability = {p["id"]: probe(p, which) for p in cfg["profile"]}
    res = r.route(t, cfg, mapping, snap, snap_warnings, now, availability)
    if res["status"] != "selected":
        return res
    profile = next(p for p in cfg["profile"] if p["id"] == res["selected"]["profile"])
    try:
        with dispatch_lock(t["cwd"]):
            existing = [x for x in receipts(t["cwd"]) if x["task_id"] == t["task_id"] and x["round"] == t["round"]]
            if existing:
                rc = existing[0]
                if rc["semantic_task_hash"] != res["task_hash"]:
                    return {**res, "status": "conflict", "run_id": rc["run_id"],
                            "warnings": res["warnings"] + [r.warn("task_round_conflict",
                                                                  "same task_id/round with different content")]}
                rc = collect(rc, t["constraints"]["timeout_ms"], session, runner)
                return output(res, rc, reused=True)
            unresolved = [x["run_id"] for x in receipts(t["cwd"]) if x["status"] not in SETTLED_STATUSES]
            if unresolved:
                return {**res, "status": "conflict", "warnings": res["warnings"] + [r.warn(
                    "unresolved_run", f"run {unresolved[0]} is not settled; collect it before a new dispatch")]}
            run_id = str(uuid.uuid4())
            rc = {"schema_version": r.SCHEMA_VERSION, "task_id": t["task_id"], "round": t["round"],
                  "semantic_task_hash": res["task_hash"], "run_id": run_id, "nonce": secrets.token_hex(16),
                  "profile": profile["id"], "profile_fingerprint": res["selected"]["profile_fingerprint"],
                  "cwd": t["cwd"], "run_dir": str(run_dir(t["cwd"], run_id)),
                  "agent_name": "br-" + run_id.replace("-", "")[:12], "workspace_id": None, "pane_id": None,
                  "herdr_session": session, "status": "dispatching", "delivery_state": "not_attempted",
                  "timeout_ms": t["constraints"]["timeout_ms"], "created_at": _iso(now),
                  "deadline_at": _iso(now + timedelta(milliseconds=t["constraints"]["timeout_ms"])),
                  "result_path": None, "manifest_path": None, "task_outcome": None, "herdr_state": None,
                  "settled_contract": False, "last_observation": None}
            prompt = t["prompt"] + contract_text(rc)
            if len(prompt.encode("utf-8")) > MAX_PROMPT_ARG_BYTES:
                raise r.InputError(f"prompt + contract exceeds {MAX_PROMPT_ARG_BYTES} bytes (herdr takes it as argv)")
            Path(rc["run_dir"]).mkdir(parents=True)
            r.atomic_write(Path(rc["run_dir"]) / "decision.json", json.dumps(res, ensure_ascii=False).encode("utf-8"))
            save(rc)  # receipt 저장 실패 시 예외 → 전송하지 않음
            return output(res, execute(rc, prompt, profile, session, runner))
    except Busy as e:
        return {**res, "status": "conflict", "warnings": res["warnings"] + [r.warn("dispatch_lock", str(e))]}


def collect_run(cwd, run_id, wait_ms, session=None, runner=subprocess.run):
    cwd = os.path.realpath(cwd)
    try:
        with dispatch_lock(cwd):
            rc = collect(load_receipt(cwd, run_id), wait_ms, session or None, runner)
    except Busy as e:
        return {"schema_version": r.SCHEMA_VERSION, "status": "conflict", "run_id": run_id,
                "warnings": [r.warn("dispatch_lock", str(e))]}
    return output(None, rc)


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
    out.update({"status": rc["status"], "run_id": rc["run_id"], "result_path": rc["result_path"],
                "manifest_path": rc["manifest_path"], "task_outcome": rc["task_outcome"],
                "herdr_state": rc["herdr_state"], "delivery_state": rc["delivery_state"],
                "receipt_path": str(Path(rc["run_dir"]) / "receipt.json"), "deadline_at": rc["deadline_at"],
                "workspace_id": rc["workspace_id"], "last_observation": rc["last_observation"],
                "diagnostic_tail": rc.get("diagnostic_tail"), "reused_receipt": reused})
    out["selected"] = {**(out.get("selected") or {}), "profile": rc["profile"],
                       "profile_fingerprint": rc["profile_fingerprint"], "agent_name": rc["agent_name"],
                       "pane_id": rc["pane_id"]}
    return out
