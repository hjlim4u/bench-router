"""Projects CLI execution with durable receipts and per-run result validation."""
import contextlib
import hashlib
import json
import os
import re
import secrets
import shlex
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import locking
from . import routing as r

PROJECTS_BIN = os.environ.get("BENCH_ROUTER_PROJECTS", "herdr-projects")
HERDR_BIN = os.environ.get("BENCH_ROUTER_HERDR", "herdr")
BACKEND = "projects-1.2"
PROJECTS_VERSION_RE = re.compile(r"herdr-projects 1\.2\.1(?:[ +].*)?")
SHORT_CALL_S = 15
OBSERVE_FLOOR_S = 2  # one list/details round trip; keeps calls inside a 5s task budget
START_CALL_S = 60  # add --delegate starts the agent before it answers
MAX_PROMPT_ARG_BYTES = 120 * 1024  # the prompt is one argv entry (--desc); Linux caps one at 128 KiB
_LOCAL_CODEBURN_BIN = Path(__file__).resolve().parents[1] / ".bench-router" / "codeburn" / "node_modules" / ".bin" / "codeburn"
CODEBURN_BIN = os.environ.get("BENCH_ROUTER_CODEBURN", str(_LOCAL_CODEBURN_BIN) if _LOCAL_CODEBURN_BIN.exists() else "codeburn")
CODEBURN_KIND = {"claude": "claude", "codex": "codex", "agy": "antigravity"}
DISCOVERED_KIND = {"claude": ("claude", "claude-code", "--model"),
                   "codex": ("codex", "codex-cli", "-m")}
# Codex keeps the models its -m accepts, with each model's efforts; "hide" marks internal models.
CODEX_MODELS_CACHE = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "models_cache.json"
RESULT_REL = Path(".bench-router") / "runs"  # agent writes results here, relative to its board worktree
# One agent run per receipt: no review rounds, attempts, plan gate or merge. worker.access stays the board's setting.
WORK_SETTINGS = ["--workspace.from", "here", "--workspace.cleanup", "false", "--review.when", "never",
                 "--review.rounds", "0", "--merge.by", "you", "--merge.pr", "false", "--attempts.by", "1",
                 "--plan.approve", "none", "--no-research"]
AT_REST_STAGES = {"approval", "done"}
PENDING_STAGES = {"after", "queued", "starting"}
FAILED_STAGES = {"failed", "nosummary", "stopped", "todo"}  # todo: added, but no agent was put on it
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

def project_call(argv, runner=subprocess.run, raw=False, timeout_s=SHORT_CALL_S, exe=None):
    cmd = [exe or PROJECTS_BIN, *argv]
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


def project_binding(session=None, runner=subprocess.run):
    """The board this run belongs to: the Projects build and the caller's Herdr session."""
    version, err = project_call(["version"], runner, raw=True)
    version = (version or "").strip()
    if err or not PROJECTS_VERSION_RE.fullmatch(version):
        raise r.InputError(f"herdr-projects 1.2.1 is required (found {version or (err or {}).get('message')!r})")
    return {"projects_version": version.split(" (")[0], "session": session}


def model_effort(profile):
    """Profile args → (model, effort); None when the args hold anything else."""
    args, model, effort, i = profile["args"], None, None, 0
    while i < len(args) - 1:
        flag, value = args[i], args[i + 1]
        if flag in ("--model", "-m"):
            model = value
        elif flag == "--effort":
            effort = value
        elif flag == "-c" and (m := re.fullmatch(r'model_reasoning_effort="?(\w+)"?', value)):
            effort = m.group(1)
        else:
            return None
        i += 2
    return (model, effort) if i == len(args) else None


def worker_settings(profile):
    """Router profile args → Projects work settings. Only a model and an effort can be expressed; else None."""
    me = model_effort(profile)
    if me is None:
        return None
    model, effort = me
    return (["--worker.agent", profile["kind"] + (f"/{model}" if model else "")]
            + (["--worker.effort", effort] if effort else []))


def headless_argv(profile):
    """Profile → one-shot CLI argv (the prompt is appended). Approvals are off: nobody can answer them headless."""
    me = model_effort(profile)
    if me is None:
        return None
    model, effort = me
    opt = lambda flag, v: [flag, v] if v else []
    if profile["kind"] == "claude":
        return ["claude", "-p", *opt("--model", model), *opt("--effort", effort), "--dangerously-skip-permissions"]
    if profile["kind"] == "codex":
        return ["codex", "exec", *opt("-m", model), *opt("-c", effort and f'model_reasoning_effort="{effort}"'),
                "--dangerously-bypass-approvals-and-sandbox"]
    if profile["kind"] == "agy":
        # agy's -p takes the prompt as its value, so it must come last, right before the appended prompt
        return ["agy", *opt("--model", model), *opt("--effort", effort), "--dangerously-skip-permissions", "-p"]
    return None


def probe(p, which=shutil.which):
    if p["executable"] != p["kind"]:
        return "executable_kind_mismatch"
    return None if which(p["executable"]) else "executable_not_found"


def agy_models(runner=subprocess.run):
    try:
        res = runner(["agy", "models"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                     timeout=SHORT_CALL_S, shell=False)
        return {line.split("\t", 1)[0] for line in res.stdout.splitlines() if "\t" in line} if not res.returncode else None
    except (OSError, subprocess.SubprocessError):
        return None


def claude_efforts(runner=subprocess.run):
    try:
        res = runner(["claude", "--help"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                     timeout=SHORT_CALL_S, shell=False)
        match = re.search(r"--effort <level>.*?\(([^)]+)\)", res.stdout, re.S)
        return tuple(x.strip() for x in match.group(1).split(",")) if not res.returncode and match else ()
    except (OSError, subprocess.SubprocessError):
        return ()


def probe_profiles(profiles, which=shutil.which, runner=subprocess.run):
    """CLI preflight plus optional CodeBurn account/quota preflight."""
    out = {p["id"]: probe(p, which) for p in profiles}
    agy = [p for p in profiles if p["kind"] == "agy" and out[p["id"]] is None]
    if agy:
        models = agy_models(runner)
        for p in agy:
            model = model_effort(p)
            out[p["id"]] = "agy_models_unavailable" if models is None else (None if model and model[0] in models else "agy_model_unavailable")
    if not shutil.which(CODEBURN_BIN):
        return out
    try:
        res = runner([CODEBURN_BIN, "quota", "--format", "json"], capture_output=True, text=True,
                     encoding="utf-8", errors="replace", timeout=SHORT_CALL_S, shell=False)
        raw = json.loads(res.stdout) if res.returncode == 0 else {}
        providers = raw.get("providers", []) if isinstance(raw, dict) else []
        providers = {p["id"]: p for p in providers if isinstance(p, dict) and isinstance(p.get("id"), str)}
    except (OSError, ValueError, subprocess.SubprocessError):
        return out
    for p in profiles:
        if p["kind"] == "agy" or out[p["id"]]:
            continue
        provider = providers.get(CODEBURN_KIND.get(p["kind"]))
        if provider is None:
            continue
        if provider.get("available") is False:
            out[p["id"]] = "codeburn_provider_unavailable"
            continue
        windows = provider.get("windows", [])
        exhausted = [w for w in windows if isinstance(w, dict) and isinstance(w.get("usedPct"), (int, float))
                     and not isinstance(w["usedPct"], bool) and w["usedPct"] >= 100] if isinstance(windows, list) else []
        # ponytail: all-window check avoids model-limit false exclusions; add a profile-to-window map when CodeBurn exposes one.
        if windows and len(exhausted) == len(windows):
            out[p["id"]] = "codeburn_quota_exhausted"
    return out


def codex_models(path=CODEX_MODELS_CACHE):
    """{model: efforts} for every listed model in Codex's model cache; {} when absent or unreadable."""
    try:
        models = json.loads(Path(path).read_text("utf-8")).get("models", [])
        return {m["slug"]: tuple(level["effort"] for level in m.get("supported_reasoning_levels", []))
                for m in models if m.get("visibility") == "list" and isinstance(m.get("slug"), str) and m["slug"]}
    except (OSError, ValueError, AttributeError, KeyError, TypeError):
        return {}


def discover_profiles(which=shutil.which, runner=subprocess.run, codex_cache=CODEX_MODELS_CACHE, claude_models=None):
    """Profiles for every model each CLI's model flag accepts: CodeBurn's observed models, Codex's listed
    models and, since the Claude CLI cannot list models, the Claude models in the vendor guidance."""
    if claude_models is None:
        from . import decision  # the guidance file is the only local list of current Claude models
        claude_models = [m for m, x in decision.load_guidelines()["models"].items() if x["vendor"] == "claude"]
    rows = []
    if which(CODEBURN_BIN):
        try:
            res = runner([CODEBURN_BIN, "models", "--format", "json"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=SHORT_CALL_S, shell=False)
            rows = json.loads(res.stdout) if res.returncode == 0 else []
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    if not isinstance(rows, list):
        rows = []
    listed = codex_models(codex_cache)
    candidates = {}  # (provider, model) -> (efforts or None for the CLI default list, config_revision)
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("provider"), str) and isinstance(row.get("model"), str) and row["model"]:
            candidates[row["provider"], row["model"]] = (None, "codeburn-discovery")
    candidates.update({("codex", m): (efforts or None, "codex-models-cache") for m, efforts in listed.items()})
    candidates.update({("claude", m): (None, "claude-guidance") for m in claude_models if ("claude", m) not in candidates})
    profiles = []
    for (provider, model), (efforts, revision) in sorted(candidates.items()):
        spec = DISCOVERED_KIND.get(provider)
        if spec is None:
            continue
        kind, harness_id, model_flag = spec
        efforts = efforts or (claude_efforts(runner) if kind == "claude" else ("low", "medium", "high", "xhigh"))
        for effort in efforts or ("unknown",):
            profile_id = re.sub(r"[^a-z0-9_-]", "-", f"{kind}-{model.lower()}-{effort}")[:48].rstrip("-")
            if not profile_id or any(p["id"] == profile_id for p in profiles):
                continue
            args = [model_flag, model]
            args += ["--effort", effort] if kind == "claude" and effort != "unknown" else []
            args += ["-c", f'model_reasoning_effort="{effort}"'] if kind == "codex" else []
            profiles.append({"id": profile_id, "enabled": True, "kind": kind, "executable": kind,
                             "args": args, "model_id": model, "harness_id": harness_id,
                             "reasoning_effort": effort, "config_revision": revision,
                             "cost_tier": "high", "inference_local": False, "context_tokens": 0,
                             "capabilities": ["filesystem_write"]})
    profiles = [p for p in profiles if probe(p, which) is None]
    if which("agy"):
        for model in agy_models(runner) or ():
            match = re.fullmatch(r"(.+)-(low|medium|high)", model)
            if not match:
                continue
            model_id, effort = match.groups()
            profile_id = re.sub(r"[^a-z0-9_-]", "-", f"agy-{model.lower()}")[:48].rstrip("-")
            if any(p["id"] == profile_id for p in profiles):
                continue
            profiles.append({"id": profile_id, "enabled": True, "kind": "agy", "executable": "agy",
                             "args": ["--model", model], "model_id": model_id, "harness_id": "antigravity-cli",
                             "reasoning_effort": effort, "config_revision": "agy-models",
                             "cost_tier": "high", "inference_local": False, "context_tokens": 0,
                             "capabilities": ["filesystem_write"]})
    if not profiles:
        raise r.InputError("CodeBurn found no model with an available supported CLI and provider quota")
    return sorted(profiles, key=lambda p: p["id"])


def profiles_toml(profiles):
    fields = ("id", "enabled", "kind", "executable", "args", "model_id", "harness_id", "reasoning_effort",
              "config_revision", "cost_tier", "inference_local", "context_tokens", "capabilities")
    lines = ['schema_version = "1.0"']
    for profile in profiles:
        lines += ["", "[[profile]]"] + [f"{field} = {json.dumps(profile[field], ensure_ascii=False)}" for field in fields]
    return "\n".join(lines) + "\n"


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
            f"결과 디렉터리({'절대 경로' if os.path.isabs(rd) else '현재 worktree 기준 상대 경로'}): {rd}\n\n"
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
        src = Path(rc["worktree"]) / RESULT_REL / rc["run_id"]
        manifest, why = check_result({**rc, "run_dir": str(src)})
        if manifest:
            for name in ("result.json", "result.md"):  # checked regular files inside src; keep a copy with the receipt
                shutil.copyfile(src / name, Path(rc["run_dir"]) / name)
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


def _wait(rc, wait_ms):
    """Post-submission wait: the task deadline, or less when the caller asked to return early."""
    remaining = max(0, (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds() * 1000)
    return remaining if wait_ms is None else min(remaining, wait_ms)


def _report(rc, state, msg, runner):
    """Mirror a headless run on its agent-less board task; the board is a view, so a failure is only noted."""
    if rc.get("thread_id"):
        _, err = project_call(["report", rc["thread_id"], "--state", state, "--msg", msg], runner, raw=True)
        if err:
            _observe(rc, rc.get("herdr_state"), error=err, note=f"board report {state} failed")


def _execute_headless(rc, prompt, profile, session, runner, wait_ms):
    """Board task (no agent) for visibility + a one-shot CLI in its own herdr worktree pane. The prompt reaches
    the CLI from input.txt, never through the typed command line."""
    argv = headless_argv(profile)
    if argv is None:
        rc["status"] = "execution_failed"
        _observe(rc, note=f"headless: no one-shot CLI for kind {profile['kind']!r} or args beyond model/effort")
        save(rc)
        return rc
    rd, wt = Path(rc["run_dir"]), bench_dir(rc["cwd"]) / "worktrees" / "runs" / rc["run_id"]
    obj, err = project_call(["worktree", "create", "--cwd", rc["cwd"], "--branch", f"br/{rc['run_id']}",
                             "--path", str(wt), "--label", f"bench-router {rc['task_id']} r{rc['round']}", "--no-focus"],
                            runner, timeout_s=START_CALL_S, exe=HERDR_BIN)
    res = (obj or {}).get("result") if isinstance(obj, dict) else None
    try:
        rc.update(pane_id=res["root_pane"]["pane_id"], workspace_id=res["workspace"]["workspace_id"],
                  worktree=res["worktree"]["path"], branch=res["worktree"]["branch"])
    except (KeyError, TypeError):
        rc["status"] = "execution_failed"
        _observe(rc, error=err, note="headless: herdr worktree create failed or returned an unexpected shape")
        save(rc)
        return rc
    save(rc)
    obj, err = project_call(["add", "br-" + rc["run_id"], "--desc", prompt, "--repo", rc["cwd"], "--json"],
                            runner, timeout_s=SHORT_CALL_S)
    if not err and isinstance(obj, dict) and re.fullmatch(r"[^/\s]+/[0-9]+", str(obj.get("id", ""))):
        rc["thread_id"] = obj["id"]  # agent-less board task: a view of this run, never delegated
    else:
        _observe(rc, error=err, note="headless: board task not created; the run continues without it")
    _report(rc, "working", "headless run", runner)
    q = shlex.quote
    script = (f"cd {q(rc['worktree'])} && {shlex.join(argv)} \"$(cat {q(str(rd / 'input.txt'))})\"; "
              f"echo $? > {q(str(rd / 'exit_code.tmp'))} && mv {q(str(rd / 'exit_code.tmp'))} {q(str(rd / 'exit_code'))}")
    rc["delivery_state"] = "submission_attempted"
    save(rc)  # Persist before typing the command: a lost response must never start a second CLI.
    _, err = project_call(["pane", "run", rc["pane_id"], shlex.join(["sh", "-c", script])], runner, raw=True, exe=HERDR_BIN)
    if err:
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        _observe(rc, error=err, note="headless: pane run unconfirmed; inspect the pane, never rerun")
        save(rc)
        return rc
    return collect(rc, _wait(rc, wait_ms), session, runner)


def _binding_unchanged(rc, session, runner):
    """Pre-submission check. On failure nothing was sent: settle the receipt so it cannot stay `dispatching`."""
    try:
        if project_binding(session, runner) == rc["project_binding"]:
            return True
        why = "Projects version changed before submission"
    except r.InputError as e:
        why = str(e)
    rc["status"] = "execution_failed"
    _observe(rc, note=f"{why}; nothing submitted")
    save(rc)
    return False


def execute(rc, prompt, profile, session=None, runner=subprocess.run, wait_ms=None):
    if not _binding_unchanged(rc, session, runner):
        return rc
    if rc.get("execution") == "headless":
        r.atomic_write(Path(rc["run_dir"]) / "input.txt", prompt.encode("utf-8"))
        return _execute_headless(rc, prompt, profile, session, runner, wait_ms)
    settings = worker_settings(profile)
    if settings is None:
        rc["status"] = "execution_failed"
        _observe(rc, note="profile args other than a model/effort cannot be expressed as Projects settings; nothing submitted")
        save(rc)
        return rc
    r.atomic_write(Path(rc["run_dir"]) / "input.txt", prompt.encode("utf-8"))
    remaining = (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds()
    if remaining <= 0:
        rc["status"] = "execution_failed"
        _observe(rc, note="deadline elapsed before task submission")
        save(rc)
        return rc
    rc["delivery_state"] = "submission_attempted"
    save(rc)  # Persist before add: a lost response must never create a second task.
    obj, err = project_call(["add", "br-" + rc["run_id"], "--desc", prompt, "--repo", rc["cwd"], "--delegate",
                             *settings, *WORK_SETTINGS, "--json"], runner, timeout_s=min(START_CALL_S, remaining))
    if err or not isinstance(obj, dict) or not re.fullmatch(r"[^/\s]+/[0-9]+", str(obj.get("id", ""))):
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        _observe(rc, error=err, note=f"task add unconfirmed; find br-{rc['run_id']} on the board, never resubmit")
        save(rc)
        return rc
    rc["thread_id"] = obj["id"]  # the board task id (repo/N)
    save(rc)
    remaining = _wait(rc, wait_ms)
    if remaining <= 0:
        rc["status"] = "timed_out"
        save(rc)
        return rc
    return collect(rc, remaining, session, runner)


def _poll_headless(rc, runner, timeout_s):
    """One observation of a headless run: its exit_code file, else whether its pane still exists."""
    code = Path(rc["run_dir"]) / "exit_code"
    if code.exists():
        rc.update(exit_code=code.read_text("utf-8").strip(), delivery_state="activity_observed", process_exited=True)
        settle(rc, "done")
        if rc["status"] == "result_invalid" and rc["exit_code"] != "0":
            rc["status"] = "execution_failed"
            _observe(rc, "done", note=f"headless CLI exited {rc['exit_code']} without a valid result")
        if rc["status"] == "completed":
            release(rc, runner)
        _report(rc, "done" if rc["status"] == "completed" else "error", rc["status"], runner)
        return
    obj, err = project_call(["pane", "get", rc["pane_id"]], runner, timeout_s=timeout_s, exe=HERDR_BIN)
    if "pane_not_found" in json.dumps(err or obj or {}):  # closed by hand = stopped
        rc.update(status="execution_failed", process_exited=True)  # closing the pane ends its shell and CLI
        _observe(rc, note="headless pane closed before the CLI finished")
        _report(rc, "error", "pane closed", runner)
    elif err:
        raise r.InputError(err["message"])
    else:
        rc["status"] = "timed_out"
        _observe(rc, "working", note="headless CLI still running")


def collect(rc, wait_ms=0, session=None, runner=subprocess.run):
    """Observe the recorded board task only; never delegate, retry or re-prompt it."""
    if rc.get("backend") != BACKEND:
        raise r.InputError("legacy receipt: inspect the original worker; automatic backend migration is refused")
    if rc["status"] == "completed" and rc.get("settled_contract"):
        if rc.get("release") is None:  # completed before releasing existed, or the last close failed
            release(rc, runner)
            save(rc)
        return rc
    if rc["delivery_state"] == "not_attempted":
        return rc
    headless = rc.get("execution") == "headless"
    if not headless and not rc.get("thread_id"):
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        save(rc)
        return rc
    deadline = time.monotonic() + wait_ms / 1000
    # Calls stay within the wait budget, but never below a floor: a near-zero budget made the last poll time out
    # and misreported a working agent as delivery_uncertain.
    timeout = lambda: min(SHORT_CALL_S, max(OBSERVE_FLOOR_S, deadline - time.monotonic())) if wait_ms > 0 else SHORT_CALL_S
    while True:
        try:
            if headless:
                _poll_headless(rc, runner, timeout())
            elif project_binding(session, runner) != rc["project_binding"]:
                raise r.InputError("Projects version or session changed; inspect the recorded worker")
            else:
                rows, err = project_call(["list", "--all", "--json"], runner, timeout_s=timeout())
                if err:
                    raise r.InputError(err["message"])
                row = next((x for x in rows if isinstance(x, dict) and x.get("id") == rc["thread_id"]), None) \
                    if isinstance(rows, list) else None
                if not row or row.get("title") != "br-" + rc["run_id"]:
                    raise r.InputError("Projects task is missing or its title differs from the receipt")
                stage, state = row.get("stage"), row.get("state")
                if stage in AT_REST_STAGES:  # the board took the agent's finish; its work is in the task worktree
                    det, err = project_call(["details", rc["thread_id"], "--json"], runner, timeout_s=timeout())
                    if err or not isinstance(det, dict) or (det.get("task") or {}).get("id") != rc["thread_id"] \
                            or not det.get("worktree") or not str(det.get("agent", "")).startswith(rc["kind"]):
                        raise r.InputError("Projects task details differ from the receipt")
                    rc.update(worktree=det["worktree"], branch=det.get("branch"), delivery_state="activity_observed")
                    settle(rc, "done")
                    if rc["status"] == "completed":
                        release(rc, runner)
                elif state == "blocked":
                    rc["status"] = "blocked"
                    rc["diagnostic_tail"] = row.get("msg")
                    if stage not in PENDING_STAGES:
                        rc["delivery_state"] = "activity_observed"
                    _observe(rc, state, note=f"Projects stage {stage}: {row.get('msg') or ''}")
                elif state == "error" or stage in FAILED_STAGES:
                    rc.update(status="execution_failed", process_exited=stage == "stopped" or rc.get("process_exited", False))
                    _observe(rc, state, note=f"Projects stage {stage}: {row.get('msg') or ''}")
                elif stage in PENDING_STAGES:
                    rc["status"] = "timed_out"
                    _observe(rc, state, note="Projects has not started the agent yet")
                else:
                    rc.update(status="timed_out", delivery_state="activity_observed")
                    _observe(rc, state, note=f"Projects stage {stage}")
        except (r.InputError, OSError) as e:
            rc.update(status="delivery_uncertain", delivery_state="uncertain")
            _observe(rc, note=str(e))
        save(rc)
        if rc["status"] in SETTLED_STATUSES | {"blocked", "delivery_uncertain"} or time.monotonic() >= deadline:
            return rc
        time.sleep(min(1, max(0, deadline - time.monotonic())))


def dispatch(t, cfg, mapping, snap, snap_warnings, session=None, runner=subprocess.run, which=shutil.which,
             profile_id=None, context=None, selection_mode="parallel_pinned",
              selection=None, check_digest=True, decision_options=None, wait_ms=None, availability=None):
    """wait_ms: how long to wait after submission (None = until the task deadline; 0 = return at once)."""
    from . import coordination as co
    key = co.key_for(t)
    try:
        with co.operation(key):
            existing = [x for x in receipts(t["cwd"]) if x["task_id"] == t["task_id"] and x["round"] == t["round"]]
            if existing and existing[0]["herdr_session"] != session:
                raise co.Conflict("dispatch session differs from the recorded native run; use collect")
            if existing:
                co.observe_receipt(existing[0])
            availability = availability if availability is not None else probe_profiles(cfg["profile"], which)
            if not existing and profile_id is None and selection is None:
                choice = r.route(t, cfg, mapping, snap, snap_warnings, _now(), availability, context,
                                 **(decision_options or {}))
                if choice["status"] != "selected":
                    return choice
                if choice["selection"].get("schema_version") == "5.0":
                    selection = {k: v for k, v in choice["selection"].items() if k != "source"}
                    profile_id = selection["profile"]
                    selection_mode = "vendor-guided"
            binding = existing[0].get("project_binding") if existing else project_binding(session, runner)
            rec, fresh = co.reserve(t, BACKEND, binding)
            if not fresh and not existing:
                raise co.Conflict("recorded native submission has no receipt; inspect effects before resolving, never resend")
            try:
                result = _dispatch(t, cfg, mapping, snap, snap_warnings, session, runner, which,
                                   profile_id, context, selection_mode, selection, check_digest, decision_options, wait_ms,
                                   availability)
            except BaseException:
                if fresh and not any(x["task_id"] == t["task_id"] and x["round"] == t["round"] for x in receipts(t["cwd"])):
                    co.discard(key)  # failed before any receipt: nothing was sent, so release the admission record
                raise
            if result.get("run_id"):
                co.observe_receipt(load_receipt(t["cwd"], result["run_id"]))
            elif fresh:
                co.discard(key)  # No native receipt means dispatch never reached execution.
            return {**result, "coordination_key": key}
    except co.Conflict as e:
        return co.conflict(t, e)


def _dispatch(t, cfg, mapping, snap, snap_warnings, session=None, runner=subprocess.run, which=shutil.which,
             profile_id=None, context=None, selection_mode="parallel_pinned",
              selection=None, check_digest=True, decision_options=None, wait_ms=None, availability=None):
    """live route. 선택 → receipt → herdr 실행. 같은 (task_id, round)는 재전송 없이 collect.
    profile_id: 제약·가용성을 통과한 후보 중 이 프로필로 고정(parallel fanout).
    selection: Orchestrator 선택 기록(validate_selection). digest가 지금 입력과 다르면 실행하지 않는다(stale_assessment).
    같은 round 회수가 digest 검사보다 우선한다: 새 판단으로 다시 실행하려면 새 round."""
    if selection is not None:
        profile_id = selection["profile"]
    # Recovery precedes new selection, including unavailable decision providers or changed guides.
    res = {"schema_version": r.SCHEMA_VERSION, "task_id": t["task_id"], "round": t["round"],
           "run_id": None, "selected": None, "candidates": [], "warnings": list(snap_warnings)}
    try:
        with dispatch_lock(t["cwd"]):
            existing = [x for x in receipts(t["cwd"]) if x["task_id"] == t["task_id"] and x["round"] == t["round"]]
            if existing:
                rc = existing[0]
                prior = r.load_json_strict(Path(rc["run_dir"]) / "decision.json", r.SNAPSHOT_MAX_BYTES)
                if rc["semantic_task_hash"] != r.semantic_task_hash(t):
                    return {**prior, "status": "conflict", "run_id": rc["run_id"],
                            "warnings": prior["warnings"] + [r.warn("task_round_conflict",
                                                                  "same task_id/round with different content")]}
                if profile_id and rc["profile"] != profile_id:
                    return {**prior, "status": "conflict", "run_id": rc["run_id"],
                            "warnings": prior["warnings"] + [r.warn("profile_round_conflict",
                                                                  "same task_id/round already uses another profile")]}
                rc = collect(rc, t["constraints"]["timeout_ms"] if wait_ms is None else wait_ms, session, runner)
                out = output(prior, rc, reused=True)
                if selection is not None and any(prior.get("selection", {}).get(k) != v for k, v in selection.items()):
                    out["warnings"] = out.get("warnings", []) + [r.warn(
                        "selection_differs_from_recorded", "returning the recorded run; use a new round to act on a new selection")]
                return out
            now = _now()
            availability = availability if availability is not None else probe_profiles(cfg["profile"], which)
            if selection is not None and selection.get("schema_version") in r.GUIDED_SELECTIONS:
                opts = {**(decision_options or {}), "allow_network": False}
                opts.pop("response", None)
                res = r.route(t, cfg, mapping, snap, snap_warnings, now, availability, context,
                              selection=selection, check_digest=check_digest, **opts)
            elif profile_id:
                res = r.evaluate_v1(t, cfg, mapping, snap, snap_warnings, now, availability, context)
                res = r.apply_selection(res, cfg, profile_id, selection, selection_mode, check_digest)
            else:
                res = r.route(t, cfg, mapping, snap, snap_warnings, now, availability, context,
                              **(decision_options or {}))
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
                  "backend": BACKEND, "project_binding": project_binding(session, runner),
                  "kind": profile["kind"], "thread_id": None, "execution": t["execution"],
                  "profile": profile["id"], "profile_fingerprint": res["selected"]["profile_fingerprint"],
                  "cwd": t["cwd"], "run_dir": str(run_dir(t["cwd"], run_id)),
                  "worktree": None, "branch": None,
                  "herdr_session": session, "status": "dispatching", "delivery_state": "not_attempted",
                  "timeout_ms": t["constraints"]["timeout_ms"], "created_at": _iso(now),
                  "deadline_at": _iso(now + timedelta(milliseconds=t["constraints"]["timeout_ms"])),
                  "result_path": None, "manifest_path": None, "task_outcome": None, "herdr_state": None,
                  "settled_contract": False, "last_observation": None}
            prompt = t["prompt"] + contract_text({**rc, "run_dir": (RESULT_REL / run_id).as_posix()})
            if len(prompt.encode("utf-8")) > MAX_PROMPT_ARG_BYTES:
                raise r.InputError(f"prompt + contract exceeds {MAX_PROMPT_ARG_BYTES} bytes (argument limit)")
            from . import parallel  # keeps .bench-router/ out of the board's commit of the agent's work
            if parallel.prepare_repo(t["cwd"]):
                res["warnings"] = res["warnings"] + [r.warn(
                    "dirty_base", "uncommitted changes in cwd are not in the board worktree (based on HEAD)")]
            Path(rc["run_dir"]).mkdir(parents=True)
            # 판단 기록 = 출력 + 같은 입력의 evaluate 2.0(통과·탈락 제약의 관측값·기준값, facts).
            # ponytail: assess를 한 번 더 돈다(결정적, 입력 동일). 느려지면 route가 assessment를 넘기게
            assessment = r.evaluate(t, cfg, mapping, snap, snap_warnings, now, availability, context)
            r.atomic_write(Path(rc["run_dir"]) / "decision.json",
                           json.dumps({**res, "assessment": assessment}, ensure_ascii=False).encode("utf-8"))
            save(rc)  # receipt 저장 실패 시 예외 → 전송하지 않음
            return output(res, execute(rc, prompt, profile, session, runner, wait_ms))
    except Busy as e:
        return {**res, "status": "conflict", "warnings": res["warnings"] + [r.warn("dispatch_lock", str(e))]}


def release(rc, runner=subprocess.run):
    """Close a completed run's agent panes so it stops holding resources. The board keeps the agent's
    conversation; `resume` reopens it. Runs once: a resumed session is never closed again by the router."""
    obj, err = project_call(["pane", "list"], runner, exe=HERDR_BIN)
    panes = (obj or {}).get("result", {}).get("panes") if isinstance(obj, dict) else None
    if err or not isinstance(panes, list):
        rc["release"] = None
        _observe(rc, rc.get("herdr_state"), error=err, note="completed; could not list herdr panes, agent left open")
        return
    wt = os.path.realpath(rc["worktree"])
    mine = [p for p in panes if isinstance(p, dict) and isinstance(p.get("cwd"), str)
            and os.path.commonpath([wt, os.path.realpath(p["cwd"])]) == wt]
    busy = [p["pane_id"] for p in mine if p.get("agent_status") in ("working", "blocked")]
    if busy:  # someone is still talking to it on the board: leave it, try again on the next collect
        rc["release"] = None
        _observe(rc, rc.get("herdr_state"), note=f"completed; agent pane {busy[0]} is still active, left open")
        return
    closed = []
    for p in mine:
        _, err = project_call(["pane", "close", p["pane_id"]], runner, exe=HERDR_BIN)
        if err:
            rc["release"] = None
            _observe(rc, rc.get("herdr_state"), error=err, note=f"completed; closing pane {p['pane_id']} failed")
            return
        closed.append({"pane_id": p["pane_id"], "agent": p.get("agent"),
                       "session": (p.get("agent_session") or {}).get("value")})
    rc["release"] = {"at": _iso(_now()), "panes": closed}


def resume_run(cwd, run_id, runner=subprocess.run):
    """Reopen a released run's board task and restart its agent in the same conversation (nothing is sent)."""
    cwd = os.path.realpath(cwd)
    with dispatch_lock(cwd):
        rc = load_receipt(cwd, run_id)
        if rc.get("backend") != BACKEND or not rc.get("thread_id"):
            raise r.InputError("only a Projects 1.2.1 run with a board task can be resumed")
        if project_binding(rc["herdr_session"], runner) != rc["project_binding"]:
            raise r.InputError("Projects version or session changed; inspect the recorded worker")
        obj, err = project_call(["reopen", rc["thread_id"], "--json"], runner, timeout_s=START_CALL_S)
        if err or not isinstance(obj, dict):
            raise r.InputError(f"reopen failed: {(err or {}).get('message')}")
        rc["resumed"] = {"at": _iso(_now()), "pane_id": obj.get("pane"), "has_agent": obj.get("hasAgent") is True}
        save(rc)
    return {**output(None, rc), "resumed": rc["resumed"]}


def tell_run(cwd, run_id, text, runner=subprocess.run):
    """Relay one explicit orchestrator message to a run's live agent. Never automatic; logged before sending."""
    cwd = os.path.realpath(cwd)
    if not isinstance(text, str) or not text.strip() or len(text.encode("utf-8")) > MAX_PROMPT_ARG_BYTES:
        raise r.InputError(f"message: nonempty text up to {MAX_PROMPT_ARG_BYTES} bytes required")
    rc = _target(cwd, run_id)
    if rc.get("execution") == "headless":
        raise r.InputError("headless runs take no messages; use the shared scratchpad or a new round")
    if rc.get("backend") != BACKEND or not rc.get("thread_id"):
        raise r.InputError("only a Projects 1.2.1 run with a board task can receive a message")
    if rc["status"] in SETTLED_STATUSES and not rc.get("resumed"):
        raise r.InputError("run is settled; `resume` it first (tell on a finished board task starts a new agent)")
    if project_binding(rc["herdr_session"], runner) != rc["project_binding"]:
        raise r.InputError("Projects version or session changed; inspect the recorded worker")
    if not rc.get("resumed"):  # the receipt lags until collect: ask the board whether the agent already finished
        rows, err = project_call(["list", "--all", "--json"], runner)
        row = next((x for x in rows if isinstance(x, dict) and x.get("id") == rc["thread_id"]), None) \
            if isinstance(rows, list) else None
        if err or row is None:
            raise r.InputError(f"board task {rc['thread_id']} not observable; inspect it before sending")
        if row.get("stage") in AT_REST_STAGES | FAILED_STAGES:
            raise r.InputError(f"task finished on the board (stage {row.get('stage')}); collect first")
    # No dispatch lock or receipt write: a blocking parallel/collect on this cwd must not stall the message.
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    _log_event(rc, {"sha256": digest, "state": "attempted", "bytes": len(text.encode("utf-8")), "text": text})
    obj, err = project_call(["tell", rc["thread_id"], text, "--json"], runner)
    log = _log_event(rc, {"sha256": digest, "state": "uncertain" if err else "sent", "error": err})
    return {"schema_version": r.SCHEMA_VERSION, "status": "delivery_uncertain" if err else "sent",
            "run_id": rc["run_id"], "thread_id": rc["thread_id"], "sha256": digest, "messages_path": str(log),
            **({"error": err} if err else {})}


def stop_run(cwd, run_id, runner=subprocess.run):
    """Stop one live run: the board stops its agent, or a headless run's workspace is closed (ending its CLI).
    The next collect records it as execution_failed. Never automatic; logged like a message."""
    rc = _target(os.path.realpath(cwd), run_id)
    if rc["status"] in SETTLED_STATUSES:
        raise r.InputError(f"run is already settled ({rc['status']}); nothing to stop")
    if rc.get("execution") == "headless":
        if not rc.get("workspace_id"):
            raise r.InputError("headless run has no recorded workspace; inspect it before stopping")
        argv, exe = ["workspace", "close", rc["workspace_id"]], HERDR_BIN  # every pane, not just the CLI's
    else:
        if rc.get("backend") != BACKEND or not rc.get("thread_id"):
            raise r.InputError("only a Projects 1.2.1 run with a board task can be stopped")
        argv, exe = ["stop", rc["thread_id"]], None
    _log_event(rc, {"state": "stop_attempted"})
    _, err = project_call(argv, runner, raw=True, exe=exe)
    log = _log_event(rc, {"state": "stop_uncertain" if err else "stop_sent", "error": err})
    return {"schema_version": r.SCHEMA_VERSION, "status": "delivery_uncertain" if err else "stop_sent",
            "run_id": rc["run_id"], "thread_id": rc.get("thread_id"), "messages_path": str(log),
            **({"error": err} if err else {})}


def _target(cwd, run_id):
    """The run a control command acts on: the given run, else the only unsettled one under cwd."""
    if run_id:
        return load_receipt(cwd, run_id)
    live = [x for x in receipts(cwd) if x["status"] not in SETTLED_STATUSES]
    if len(live) != 1:  # one active run per workspace (overlap guard), so a parallel member's worktree identifies it
        raise r.InputError(f"--run-id required: {len(live)} unsettled runs under {cwd}")
    return live[0]


def _log_event(rc, entry):
    """Append one control event (message, stop) to the run's messages.jsonl; returns the log path."""
    log = Path(rc["run_dir"]) / "messages.jsonl"
    with open(log, "a", encoding="utf-8") as f:  # shortcut: one O_APPEND write per line; lock if senders get concurrent
        f.write(json.dumps({"at": _iso(_now()), **entry}, ensure_ascii=False) + "\n")
    return log


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


def collect_many(runs, wait_ms, until="any", session=None, runner=subprocess.run):
    """Poll several runs (cwd, run_id) with collect_run until any or all of them need the caller:
    settled or blocked. A utility over collect; choosing among the runs stays with the caller."""
    if until not in ("any", "all") or not runs:
        raise r.InputError("collect: one or more runs and until any|all required")
    deadline, outs = time.monotonic() + wait_ms / 1000, {}
    while True:
        for cwd, run_id in runs:
            if outs.get(run_id, {}).get("status") not in SETTLED_STATUSES:
                outs[run_id] = collect_run(cwd, run_id, 0, session, runner)
        ready = [k for k, o in outs.items() if o["status"] in SETTLED_STATUSES | {"blocked"}]
        if (ready and until == "any") or len(ready) == len(runs) or time.monotonic() >= deadline:
            return {"schema_version": r.SCHEMA_VERSION, "status": "ok" if ready and (until == "any" or len(ready) == len(runs))
                    else "timed_out", "until": until, "ready": ready, "runs": [outs[k] for _, k in runs]}
        time.sleep(min(1, max(0, deadline - time.monotonic())))


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
                "thread_id": rc.get("thread_id"), "worktree": rc.get("worktree"), "branch": rc.get("branch"),
                "last_observation": rc["last_observation"],
                "diagnostic_tail": rc.get("diagnostic_tail"), "release": rc.get("release"), "reused_receipt": reused})
    out["selected"] = {**(out.get("selected") or {}), "profile": rc["profile"],
                       "profile_fingerprint": rc["profile_fingerprint"]}
    out["reassignment"] = ("collect_first" if rc["delivery_state"] in ("submission_attempted", "uncertain")
                            or rc["status"] in ("timed_out", "waiting", "delivery_uncertain") else
                            "safe_to_retry" if rc["delivery_state"] == "not_attempted" else "review_result")
    return out
