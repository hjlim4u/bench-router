"""Shepherdr CLI execution with durable receipts and per-run result validation."""
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

from . import usage
from . import locking
from . import routing as r

PROJECTS_BIN = os.environ.get("BENCH_ROUTER_TASKS", "herdr-task")
HERDR_BIN = os.environ.get("BENCH_ROUTER_HC", "hc")
BACKEND = "shepherdr-3"
LOCAL_BACKEND = "local-1"  # one-shot CLI as a local subprocess (runners.py)
EXTERNAL_BACKEND = "external-1"  # the caller runs the agent; the router keeps receipt and result contract
RUNNERS = {"herdr": BACKEND, "local": LOCAL_BACKEND, "external": EXTERNAL_BACKEND}
TASK_PROTOCOL = "1"  # herdr-task --version is its protocol, not Shepherdr's release number
SHORT_CALL_S = 15
OBSERVE_FLOOR_S = 2  # one task observation; keeps calls inside a 5s task budget
START_CALL_S = 60  # task start may prepare a worktree before it answers
MAX_PROMPT_ARG_BYTES = 120 * 1024  # the prompt is one argv entry (--desc); Linux caps one at 128 KiB
DISCOVERED_KIND = {"claude": ("claude", "claude-code", "--model"),
                   "codex": ("codex", "codex-cli", "-m")}
# Codex keeps the models its -m accepts, with each model's efforts; "hide" marks internal models.
CODEX_MODELS_CACHE = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "models_cache.json"
RESULT_REL = Path(".bench-router") / "runs"  # agent writes results here, relative to its board worktree
WORK_SETTINGS = ["--worktree", "--set", "review=off", "--set", "merge=ask me first", "--set", "proof=off"]
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


# ---------- Shepherdr public CLIs ----------

def project_call(argv, runner=subprocess.run, raw=False, timeout_s=SHORT_CALL_S, exe=None):
    cmd = [exe or PROJECTS_BIN, *argv]
    try:
        p = runner(cmd, capture_output=True, text=True, encoding="utf-8", errors="strict",
                   timeout=timeout_s, shell=False)
        if p.returncode:
            raise ValueError((p.stderr or p.stdout)[:300])
        if len(p.stdout.encode("utf-8")) > r.SNAPSHOT_MAX_BYTES:
            raise ValueError("Shepherdr response too large")
        return (p.stdout if raw else json.loads(p.stdout)), None
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, {"code": "shepherdr_error", "message": str(e)[:300]}


def project_binding(session=None, runner=subprocess.run):
    """Bind to the task protocol and core build, never interpret legacy Projects receipts as tasks."""
    if (os.environ.get("HC_SESSION") or "default") != "default":
        raise r.InputError("Shepherdr uses the default herdr-core session; unset HC_SESSION")
    version, err = project_call(["--version"], runner, raw=True)
    if err or (version or "").strip() != TASK_PROTOCOL:
        raise r.InputError("Shepherdr 3.x herdr-task protocol 1 is required for live dispatch; "
                           "install Shepherdr, use --runner local|external, or use route --dry-run")
    core, err = project_call(["--version"], runner, raw=True, exe=HERDR_BIN)
    m = re.fullmatch(r"hc (\d+)\.(\d+)\.(\d+)(?:[-+ ].*)?", (core or "").strip())
    if err or not m or tuple(map(int, m.groups())) < (0, 1, 17):
        raise r.InputError("Shepherdr requires herdr-core (hc) >= 0.1.17")
    space = session or os.environ.get("BENCH_ROUTER_SPACE") or os.environ.get("BENCH_ROUTER_HERDR_SESSION")
    if not space and os.environ.get("HC_TERMINAL_ID"):
        obj, err = project_call(["get", os.environ["HC_TERMINAL_ID"], "--json"], runner, exe=HERDR_BIN)
        labels = (obj or {}).get("labels", {})
        space = labels.get("herdr.space") or labels.get("herdr.task.space") or labels.get("herdr.coordinator.space")
    if not isinstance(space, str) or not space.strip() or "/" in space:
        raise r.InputError("a local Shepherdr space is required: use --herdr-space SPACE or BENCH_ROUTER_SPACE")
    return {"task_protocol": TASK_PROTOCOL, "core_version": core.strip(), "space": space, "session": "default"}


def resolve_runner(name=None, which=shutil.which):
    """--runner → receipt backend. auto: Shepherdr when herdr-task and hc are on PATH, else a local subprocess."""
    name = name or os.environ.get("BENCH_ROUTER_RUNNER") or "auto"
    if name == "auto":
        name = "herdr" if which(PROJECTS_BIN) and which(HERDR_BIN) else "local"
    if name not in RUNNERS:
        raise r.InputError(f"runner must be one of {['auto', *RUNNERS]} (got {name!r})")
    return RUNNERS[name]


def runner_binding(backend, session=None, runner=subprocess.run, cwd=None):
    if backend != BACKEND:
        return {"runner": backend}
    path = Path(cwd) / ".bench-router" / "shepherdr.json" if cwd else None
    if not session and not (os.environ.get("BENCH_ROUTER_SPACE") or os.environ.get("BENCH_ROUTER_HERDR_SESSION")) and path and path.exists():
        config = r.load_json_strict(path, r.TASK_MAX_BYTES)
        if not isinstance(config, dict) or not isinstance(config.get("space"), str):
            raise r.InputError(f"{path}: an object with a space string is required")
        session = config["space"]
    return project_binding(session, runner)


def _availability(availability, cfg, which, backend, requests=()):
    """External callers own availability: leave it unverified instead of probing local CLIs."""
    if availability is not None or backend == EXTERNAL_BACKEND:
        return availability
    profiles = [p for p in cfg["profile"] if p["enabled"]]
    requests = [(t, r.validate_context(ctx, [p["id"] for p in cfg["profile"]]) if ctx is not None else None)
                for t, ctx in requests]
    now = _now()
    def fits(p, t, ctx):
        cost, facts, metrics = r.context_facts(p, ctx, now) if ctx is not None else (None, None, {})
        x = {"context": ctx, "facts": facts, "cost": cost, "metrics": metrics, "live": False}
        return all(f["passed"] for check in r.CONSTRAINTS.values() for f in check(p, t, x))
    if requests:
        profiles = [p for p in profiles if any(fits(p, t, ctx) for t, ctx in requests)]
    return probe_profiles(profiles, which)


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
    """Profile model/effort flags expressed by herdr-task; permissions stay the user's CLI settings."""
    me = model_effort(profile)
    if me is None:
        return None
    model, effort = me
    return (["--agent", profile["kind"], "--model", model or "default"]
            + (["--effort", effort] if effort else []))


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
    if "kind" not in p:  # profiles 2.0 caller-owned profile: Herdr runs CLIs only and never converts one
        return "unsupported_execution_profile"
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


def probe_profiles(profiles, which=shutil.which, runner=subprocess.run, collector=None):
    """Native CLI/model checks, then CodexBar's model-scoped quota and credit checks."""
    out = usage.Availability({p["id"]: probe(p, which) if p.get("enabled", True) else "disabled" for p in profiles})
    agy = [p for p in profiles if out[p["id"]] is None and p["kind"] == "agy"]
    if agy:
        models = agy_models(runner)
        for p in agy:
            model = model_effort(p)
            out[p["id"]] = "agy_models_unavailable" if models is None else (None if model and model[0] in models else "agy_model_unavailable")
    eligible = [p for p in profiles if out[p["id"]] is None]
    quota = usage.probe(eligible, collector=collector, runner=None if runner is subprocess.run else runner, which=which)
    out.update(quota)
    out.details.update(quota.details)
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
    """Discover accepted models from native CLI caches and vendor guidance, never usage history."""
    if claude_models is None:
        from . import decision  # the guidance file is the only local list of current Claude models
        claude_models = [m for m, x in decision.load_guidelines()["models"].items() if x["vendor"] == "claude"]
    listed = codex_models(codex_cache)
    candidates = {}  # (provider, model) -> (efforts or None for the CLI default list, config_revision)
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
            profile_id = re.sub(r"[^a-z0-9_-]", "-", f"{kind}-{model.lower()[:48 - len(kind) - len(effort) - 2]}-{effort}").rstrip("-")
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
        raise r.InputError("No supported CLI models found; refresh the Codex model cache or check installed CLI model lists")
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


def run_worktree(rc):
    return bench_dir(rc["cwd"]) / "worktrees" / "runs" / rc["run_id"]


def repo_cwd(rc):
    """The checkout a runner operates on; old receipts used their receipt cwd for both."""
    return rc.get("repo_cwd", rc["cwd"])


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
    # The run observer holds this lock briefly every 5s; wait it out instead of reporting a false conflict.
    with locking.exclusive(bench_dir(cwd) / "dispatch.lock",
                           Busy("another bench-router dispatch/collect holds the lock for this cwd"), wait_s=2):
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


def headless_script(rc, argv):
    """sh script: the one-shot CLI in the worktree with the prompt from input.txt, then its exit code, atomically."""
    q, rd = shlex.quote, Path(rc["run_dir"])
    return (f"cd {q(rc['worktree'])} && {shlex.join(argv)} \"$(cat {q(str(rd / 'input.txt'))})\"; "
            f"echo $? > {q(str(rd / 'exit_code.tmp'))} && mv {q(str(rd / 'exit_code.tmp'))} {q(str(rd / 'exit_code'))}")



def _binding_unchanged(rc, session, runner):
    """Pre-submission check. On failure nothing was sent: settle the receipt so it cannot stay `dispatching`."""
    try:
        if project_binding(session, runner) == rc["project_binding"]:
            return True
        why = "Shepherdr binding changed before submission"
    except r.InputError as e:
        why = str(e)
    rc["status"] = "execution_failed"
    _observe(rc, note=f"{why}; nothing submitted")
    save(rc)
    return False


def execute(rc, prompt, profile, session=None, runner=subprocess.run, wait_ms=None):
    if rc["backend"] != BACKEND:
        from . import runners
        return runners.start(rc, prompt, profile, wait_ms)
    if not _binding_unchanged(rc, session, runner):
        return rc
    settings = worker_settings(profile)
    if settings is None:
        rc["status"] = "execution_failed"
        _observe(rc, note="profile args beyond model/effort cannot be expressed; nothing submitted")
        save(rc)
        return rc
    # ponytail: native ready opens PRs or deletes ignored results; keep acceptance manual until upstream can retain both.
    prompt += ("\nShepherdr: do not call herdr-task ready, done, accept or merge; do not open a PR. "
               "Keep this worktree and branch. After writing the results, end your turn. "
               "bench-router validates and collects the results; the person decides how the work lands.\n")
    r.atomic_write(Path(rc["run_dir"]) / "input.txt", prompt.encode("utf-8"))
    remaining = (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds()
    if remaining <= 0:
        rc["status"] = "execution_failed"
        _observe(rc, note="deadline elapsed before task submission")
        save(rc)
        return rc
    from . import parallel
    # herdr-task --base accepts branch names only. A private base branch pins the caller's HEAD;
    # passing the current branch could fetch and start from a newer remote commit instead.
    base = f"br-base/{rc['run_id']}"
    try:
        parallel._git(repo_cwd(rc), "branch", base, "HEAD")
    except r.InputError as e:
        rc["status"] = "execution_failed"
        _observe(rc, note=f"could not pin HEAD: {e}; nothing submitted")
        save(rc)
        return rc
    rc["base_branch"] = base
    rc["base_commit"] = parallel._git(repo_cwd(rc), "rev-parse", base)
    rc["delivery_state"] = "submission_attempted"
    save(rc)  # An add with a lost response must never be repeated, even though it starts nothing.
    obj, err = project_call(["add", "br-" + rc["run_id"], "--prompt-file", str(Path(rc["run_dir"]) / "input.txt"),
                             "--folder", repo_cwd(rc), "--base", base, "--branch", f"br/{rc['run_id']}",
                             *settings, *WORK_SETTINGS, "--json"], runner, timeout_s=min(START_CALL_S, remaining))
    if err or not isinstance(obj, dict) or not re.fullmatch(r"[^#\s]+#[0-9]+", str(obj.get("key", ""))) \
            or type(obj.get("id")) is not int or obj["id"] < 1 or not obj["key"].endswith(f"#{obj['id']}") \
            or obj.get("title") != "br-" + rc["run_id"] or obj.get("folder") != repo_cwd(rc) or obj.get("agent") != rc["kind"]:
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        _observe(rc, error=err, note=f"task add unconfirmed; find br-{rc['run_id']}, never resubmit")
        save(rc)
        return rc
    rc["thread_id"] = obj["key"]
    rc["task_id_on_board"] = obj.get("id")
    save(rc)  # Persist identity before start; recovery only observes, it never starts an added task again.
    if obj.get("mode") != "worktree":
        rc.update(status="execution_failed", process_exited=True)
        _observe(rc, note="Shepherdr worktrees are disabled for this folder; task added but nothing started")
        save(rc)
        return rc
    if (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds() <= 0:
        rc.update(status="execution_failed", process_exited=True)
        _observe(rc, note="task added but deadline elapsed before start; nothing started")
        save(rc)
        return rc
    rc["start_attempted"] = True
    save(rc)
    # Shepherdr only translates model/effort for Claude and Codex. Its public argv override keeps agy's flags.
    launch_args = (["--argv", json.dumps([profile["executable"], *profile["args"], "--prompt-interactive"])]
                   if profile["kind"] == "agy" else [])
    if rc.get("execution") == "headless":
        argv = headless_argv(profile)
        if argv is None:
            rc.update(status="execution_failed", process_exited=True)
            save(rc)
            return rc
        launch_args = ["--argv", json.dumps(["sh", "-c", headless_script({**rc, "worktree": "."}, argv)])]
    obj, err = project_call(["start", rc["thread_id"], "--folder", repo_cwd(rc), "--space", rc["project_binding"]["space"],
                             *launch_args, "--json"], runner,
                            timeout_s=min(START_CALL_S, max(0.001, (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds())))
    if err or not isinstance(obj, dict):
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        _observe(rc, error=err, note="task start unconfirmed; collect the recorded task, never restart")
        save(rc)
        return rc
    rc["terminal_id"] = obj.get("terminal")
    rc["worktree"], rc["branch"] = obj.get("worktree"), obj.get("branch")
    save(rc)
    # One durable core terminal observes the run and its later merge even when the caller disconnects.
    import sys
    monitor, monitor_error = project_call(["run", "--bg", "--rm", "--json", "--no-parent",
        "--label", f"bench-router.watch={rc['run_id']}", "--", "env",
        f"PYTHONPATH={Path(__file__).resolve().parents[1]}", sys.executable, "-m", "bench_router.lifecycle",
        "--cwd", rc["cwd"], "--run-id", rc["run_id"]], runner, exe=HERDR_BIN)
    rc["monitor"] = {"terminal_id": (monitor or {}).get("address"), "error": monitor_error}
    remaining = _wait(rc, wait_ms)
    rc["status"] = "timed_out"
    save(rc)
    return collect(rc, remaining, session, runner) if remaining > 0 else rc


def settle_exit(rc):
    """Settle a one-shot CLI from its exit_code file; False while it has not exited."""
    code = Path(rc["run_dir"]) / "exit_code"
    if not code.exists():
        return False
    rc.update(exit_code=code.read_text("utf-8").strip(), delivery_state="activity_observed", process_exited=True)
    settle(rc, "done")
    if rc["status"] == "result_invalid" and rc["exit_code"] != "0":
        rc["status"] = "execution_failed"
        _observe(rc, "done", note=f"headless CLI exited {rc['exit_code']} without a valid result")
    return True


def _poll_headless(rc, runner, timeout_s):
    if rc.get("thread_id"):
        row = _task(rc, runner, timeout_s)
        if row.get("state") in ("todo", "queued", "scheduled"):
            cancelled = row.get("state") == "todo" and any(e.get("cancelled_queue") for e in _events(rc))
            if cancelled:
                rc.update(status="execution_failed", process_exited=True)
            else:
                rc["status"] = "timed_out"
            return
    if settle_exit(rc):
        if rc["status"] == "completed":
            release(rc, runner)
        return
    if not rc.get("terminal_id"):
        raise r.InputError("hc run response was lost; inspect the recorded run label before resolving")
    obj, err = project_call(["get", rc["terminal_id"], "--json"], runner, timeout_s=timeout_s, exe=HERDR_BIN)
    if err:
        raise r.InputError(err["message"])
    if not isinstance(obj, dict) or obj.get("state") not in ("live", "exited"):
        raise r.InputError("unexpected hc terminal response")
    if obj["state"] == "exited":
        rc.update(status="execution_failed", process_exited=True)
        _observe(rc, note="headless terminal ended before writing its exit code")
    else:
        rc["status"] = "timed_out"
        _observe(rc, "working", note="headless CLI still running")


def _task(rc, runner, timeout_s=SHORT_CALL_S):
    obj, err = project_call(["show", rc["thread_id"], "--folder", repo_cwd(rc), "--json"], runner, timeout_s=timeout_s)
    if err or not isinstance(obj, dict) or obj.get("key") != rc["thread_id"] or type(obj.get("id")) is not int or obj.get("id") != rc.get("task_id_on_board") \
            or obj.get("title") != "br-" + rc["run_id"] or obj.get("folder") != repo_cwd(rc) \
            or obj.get("agent") != rc["kind"]:
        raise r.InputError("Shepherdr task identity differs from the receipt")
    if obj.get("state") not in ("todo", "queued", "scheduled"):
        wt = obj.get("worktree")
        if obj.get("mode") != "worktree" or not isinstance(wt, str) or not os.path.isabs(wt) \
                or os.path.realpath(wt) == os.path.realpath(repo_cwd(rc)) or obj.get("branch") != f"br/{rc['run_id']}":
            raise r.InputError("Shepherdr task worktree differs from the receipt")
        if rc.get("worktree") and os.path.realpath(wt) != os.path.realpath(rc["worktree"]):
            raise r.InputError("Shepherdr task worktree changed")
        rc.update(worktree=wt, branch=obj["branch"])
    return obj


def collect(rc, wait_ms=0, session=None, runner=subprocess.run):
    """Observe the recorded board task only; never delegate, retry or re-prompt it."""
    if rc.get("backend") not in (BACKEND, LOCAL_BACKEND, EXTERNAL_BACKEND):
        raise r.InputError("legacy receipt: inspect the original worker; automatic backend migration is refused")
    native = rc["backend"] == BACKEND
    if rc["status"] == "completed" and rc.get("settled_contract"):
        if native and rc.get("release") is None:  # completed before releasing existed, or the last close failed
            release(rc, runner)
            save(rc)
        return rc
    if rc["delivery_state"] == "not_attempted":
        return rc
    headless = rc.get("execution") == "headless"
    if native and not headless and not rc.get("thread_id"):
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        save(rc)
        return rc
    deadline = time.monotonic() + wait_ms / 1000
    # Calls stay within the wait budget, but never below a floor: a near-zero budget made the last poll time out
    # and misreported a working agent as delivery_uncertain.
    timeout = lambda: min(SHORT_CALL_S, max(OBSERVE_FLOOR_S, deadline - time.monotonic())) if wait_ms > 0 else SHORT_CALL_S
    while True:
        try:
            if not native:
                from . import runners
                runners.poll(rc)
            elif headless:
                _poll_headless(rc, runner, timeout())
            elif project_binding(session, runner) != rc["project_binding"]:
                raise r.InputError("Shepherdr protocol, space or core version changed; inspect the recorded worker")
            else:
                row = _task(rc, runner, timeout())
                state, status, needs = row.get("state"), row.get("status"), row.get("needs")
                if state in ("todo", "queued", "scheduled"):
                    cancelled = state == "todo" and any(e.get("cancelled_queue") for e in _events(rc))
                    if cancelled:
                        rc.update(status="execution_failed", process_exited=True)
                    else:
                        rc["status"] = "delivery_uncertain" if state == "todo" else "timed_out"
                    _observe(rc, status, note="task not started; recovery never calls start")
                elif needs == "stopped":
                    stopped = any(e.get("state") == "stop_sent" for e in _events(rc))
                    rc.update(status="execution_failed", process_exited=stopped)
                    _observe(rc, status, note=row.get("why") or "task agent stopped")
                elif status == "needs" and needs != "reply":
                    rc.update(status="blocked", delivery_state="activity_observed", diagnostic_tail=row.get("why"))
                    _observe(rc, "blocked", note=row.get("why"))
                # Shepherdr calls even an already-done first turn "working" for its 90s startup grace.
                # The live worker's status and this run's final manifest are the completion evidence.
                elif status in ("ready", "done") or (state == "running" and row.get("live") and
                        all(x.get("status") in ("idle", "done") for x in row["live"]) and
                        (Path(rc["worktree"]) / RESULT_REL / rc["run_id"] / "result.json").exists()):
                    if rc.get("terminal_id") or rc["delivery_state"] not in ("uncertain", "submission_attempted"):
                        rc["delivery_state"] = "activity_observed"
                    settle(rc, "done")
                    if rc["status"] == "completed":
                        release(rc, runner)
                elif status == "needs":
                    rc.update(status="blocked", delivery_state="activity_observed", diagnostic_tail=row.get("why"))
                    _observe(rc, "blocked", note=row.get("why"))
                else:
                    rc.update(status="timed_out", delivery_state="activity_observed")
                    _observe(rc, status, note=row.get("why"))
        except (r.InputError, OSError) as e:
            rc.update(status="delivery_uncertain", delivery_state="uncertain")
            _observe(rc, note=str(e))
        save(rc)
        if rc["status"] in SETTLED_STATUSES | {"blocked", "delivery_uncertain"} or time.monotonic() >= deadline:
            return rc
        time.sleep(min(1, max(0, deadline - time.monotonic())))


def dispatch(t, cfg, mapping, snap, snap_warnings, session=None, runner=subprocess.run, which=shutil.which,
             profile_id=None, context=None, selection_mode="parallel_pinned",
             selection=None, check_digest=True, decision_options=None, wait_ms=None, availability=None,
             backend=BACKEND, repo_cwd=None, repo_prepared=False):
    """wait_ms: how long to wait after submission (None = until the task deadline; 0 = return at once).
    backend: BACKEND (Herdr), LOCAL_BACKEND or EXTERNAL_BACKEND; a recorded run keeps its own backend."""
    from . import coordination as co
    key = co.key_for(t)
    try:
        with co.operation(key):
            existing = [x for x in receipts(t["cwd"]) if x["task_id"] == t["task_id"] and x["round"] == t["round"]]
            if existing and session is not None and existing[0]["herdr_session"] != session:
                raise co.Conflict("dispatch space differs from the recorded native run; use collect")
            if existing:
                co.observe_receipt(existing[0])
                backend = existing[0].get("backend", BACKEND)
            elif backend == LOCAL_BACKEND and t["execution"] != "headless":
                raise r.InputError('the local runner runs one-shot CLIs: set "execution": "headless", '
                                   "or use --runner herdr|external")
            if not existing:
                availability = _availability(availability, cfg, which, backend, [(t, context)])
            if not existing and profile_id is None and selection is None:
                choice = r.route(t, cfg, mapping, snap, snap_warnings, _now(), availability, context,
                                 **(decision_options or {}))
                if choice["status"] != "selected":
                    return choice
                if choice["selection"].get("schema_version") == "5.0":
                    selection = {k: v for k, v in choice["selection"].items() if k != "source"}
                    profile_id = selection["profile"]
                    selection_mode = "vendor-guided"
            binding = existing[0].get("project_binding") if existing else runner_binding(backend, session, runner, repo_cwd or t["cwd"])
            rec, fresh = co.reserve(t, backend, binding)
            if not fresh and not existing:
                raise co.Conflict("recorded native submission has no receipt; inspect effects before resolving, never resend")
            try:
                result = _dispatch(t, cfg, mapping, snap, snap_warnings, session, runner, which,
                                   profile_id, context, selection_mode, selection, check_digest, decision_options, wait_ms,
                                   availability, backend, repo_cwd, repo_prepared)
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
             selection=None, check_digest=True, decision_options=None, wait_ms=None, availability=None,
             backend=BACKEND, repo_cwd=None, repo_prepared=False):
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
                if wait_ms is None:  # an external run finishes whenever the caller does: report, don't block
                    wait_ms = 0 if rc.get("backend") == EXTERNAL_BACKEND else t["constraints"]["timeout_ms"]
                rc = collect(rc, wait_ms, rc["herdr_session"], runner)
                out = output(prior, rc, reused=True)
                if selection is not None and any(prior.get("selection", {}).get(k) != v for k, v in selection.items()):
                    out["warnings"] = out.get("warnings", []) + [r.warn(
                        "selection_differs_from_recorded", "returning the recorded run; use a new round to act on a new selection")]
                return out
            now = _now()
            availability = _availability(availability, cfg, which, backend, [(t, context)])
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
            binding = runner_binding(backend, session, runner, repo_cwd or t["cwd"])
            rc = {"schema_version": r.SCHEMA_VERSION, "task_id": t["task_id"], "round": t["round"],
                  "semantic_task_hash": res["task_hash"], "run_id": run_id, "nonce": secrets.token_hex(16),
                  "backend": backend, "project_binding": binding,
                  "kind": profile.get("kind"), "thread_id": None, "execution": t["execution"],
                  "profile": profile["id"], "profile_fingerprint": res["selected"]["profile_fingerprint"],
                  "cwd": t["cwd"], "repo_cwd": repo_cwd or t["cwd"], "run_dir": str(run_dir(t["cwd"], run_id)),
                  "worktree": None, "branch": None,
                  "herdr_session": binding.get("space", session), "status": "dispatching", "delivery_state": "not_attempted",
                  "timeout_ms": t["constraints"]["timeout_ms"], "created_at": _iso(now),
                  "deadline_at": _iso(now + timedelta(milliseconds=t["constraints"]["timeout_ms"])),
                  "result_path": None, "manifest_path": None, "task_outcome": None, "herdr_state": None,
                  "settled_contract": False, "last_observation": None}
            prompt = t["prompt"] + contract_text({**rc, "run_dir": (RESULT_REL / run_id).as_posix()})
            if len(prompt.encode("utf-8")) > MAX_PROMPT_ARG_BYTES:
                raise r.InputError(f"prompt + contract exceeds {MAX_PROMPT_ARG_BYTES} bytes (argument limit)")
            from . import parallel  # keeps .bench-router/ out of the board's commit of the agent's work
            if not repo_prepared and parallel.prepare_repo(repo_cwd or t["cwd"]):
                res["warnings"] = res["warnings"] + [r.warn(
                    "dirty_base", "uncommitted changes in cwd are not in the board worktree (based on HEAD)")]
            if not repo_prepared:  # group members skip this: run_group already swept before its fanout
                parallel._auto_prune(repo_cwd or t["cwd"])
            Path(rc["run_dir"]).mkdir(parents=True)
            # 판단 기록 = 출력 + 같은 입력의 evaluate 2.0(통과·탈락 제약의 관측값·기준값, facts).
            # ponytail: assess를 한 번 더 돈다(결정적, 입력 동일). 느려지면 route가 assessment를 넘기게
            assessment = r.evaluate(t, cfg, mapping, snap, snap_warnings, now, availability, context)
            r.atomic_write(Path(rc["run_dir"]) / "decision.json",
                           json.dumps({**res, "assessment": assessment}, ensure_ascii=False).encode("utf-8"))
            save(rc)  # receipt 저장 실패 시 예외 → 전송하지 않음
            return output(res, execute(rc, prompt, profile, rc["herdr_session"], runner, wait_ms))
    except Busy as e:
        return {**res, "status": "conflict", "warnings": res["warnings"] + [r.warn("dispatch_lock", str(e))]}


def release(rc, runner=subprocess.run):
    """End only idle terminals belonging to this run; leave working and blocked agents alone."""
    argv = ["ls", "--label", f"bench-router.run={rc['run_id']}", "--json"] if not rc.get("thread_id") else \
        ["ls", "--label", f"herdr.task={rc['thread_id']}", "--json"]
    obj, err = project_call(argv, runner, exe=HERDR_BIN)
    terminals = obj.get("terminals") if isinstance(obj, dict) else None
    if err or not isinstance(terminals, list):
        rc["release"] = None
        _observe(rc, error=err, note="completed; could not list core terminals, agent left open")
        return
    closed = []
    for t in terminals:
        status = t.get("status")
        status = status.get("state") if isinstance(status, dict) else status
        if t.get("state") != "exited" and status not in ("idle", "done") and rc.get("execution") != "headless":
            rc["release"] = None
            _observe(rc, note="completed; task still has an active agent, left open")
            return
    for t in terminals:
        _, err = project_call(["kill", t["address"], "--json"], runner, exe=HERDR_BIN)
        if err:
            rc["release"] = None
            _observe(rc, error=err, note="completed; ending the core terminal failed")
            return
        closed.append({"terminal_id": t["address"], "agent": t.get("agent")})
    rc["release"] = {"at": _iso(_now()), "terminals": closed}


def resume_run(cwd, run_id, runner=subprocess.run):
    """Resume the task's recorded session, or Shepherdr's handoff when no session is available."""
    cwd = os.path.realpath(cwd)
    with dispatch_lock(cwd):
        rc = load_receipt(cwd, run_id)
        if rc.get("backend") != BACKEND or not rc.get("thread_id"):
            raise r.InputError("only a Shepherdr task run can be resumed")
        if project_binding(rc["herdr_session"], runner) != rc["project_binding"]:
            raise r.InputError("Shepherdr protocol or core version changed; inspect the recorded worker")
        _task(rc, runner)
        obj, err = project_call(["resume", rc["thread_id"], "--folder", repo_cwd(rc), "--space", rc["project_binding"]["space"], "--json"], runner, timeout_s=START_CALL_S)
        if err or not isinstance(obj, dict) or not obj.get("terminal"):
            raise r.InputError(f"resume failed: {(err or {}).get('message')}")
        rc["terminal_id"] = obj["terminal"]
        rc["resumed"] = {"at": _iso(_now()), "terminal_id": obj["terminal"], "session_resumed": obj.get("resumed") is True}
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
        raise r.InputError("only a Shepherdr task run can receive a message")
    if rc["status"] in SETTLED_STATUSES and not rc.get("resumed"):
        raise r.InputError("run is settled; `resume` it first (tell on a finished board task starts a new agent)")
    if project_binding(rc["herdr_session"], runner) != rc["project_binding"]:
        raise r.InputError("Shepherdr protocol, space or core version changed; inspect the recorded worker")
    row = _task(rc, runner)
    live = row.get("live") or []
    if row.get("state") != "running" or len(live) != 1 or (row.get("needs") == "reply" and not rc.get("resumed")):
        raise r.InputError("task finished on the board or has no single live worker; collect/resume first")
    terminal = live[0]["address"]
    # No dispatch lock or receipt write: a blocking parallel/collect on this cwd must not stall the message.
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    _log_event(rc, {"sha256": digest, "state": "attempted", "bytes": len(text.encode("utf-8")), "text": text})
    obj, err = project_call(["send", terminal, text, "--json"], runner, exe=HERDR_BIN)
    log = _log_event(rc, {"sha256": digest, "state": "uncertain" if err else "sent", "error": err})
    return {"schema_version": r.SCHEMA_VERSION, "status": "delivery_uncertain" if err else "sent",
            "run_id": rc["run_id"], "thread_id": rc["thread_id"], "sha256": digest, "messages_path": str(log),
            **({"error": err} if err else {})}


def stop_run(cwd, run_id, runner=subprocess.run):
    """Stop a task's observed core workers, cancel its queue, or end a local/external run.
    The next collect records it as execution_failed. Never automatic; logged like a message."""
    rc = _target(os.path.realpath(cwd), run_id)
    if rc["status"] in SETTLED_STATUSES:
        raise r.InputError(f"run is already settled ({rc['status']}); nothing to stop")
    if rc.get("backend") in (LOCAL_BACKEND, EXTERNAL_BACKEND):
        from . import runners
        external = rc["backend"] == EXTERNAL_BACKEND
        try:
            # An external stop rewrites the receipt; under the lock a running collect cannot overwrite it afterwards.
            with dispatch_lock(rc["cwd"]) if external else contextlib.nullcontext():
                if external:
                    rc = load_receipt(rc["cwd"], rc["run_id"])
                    if rc["status"] in SETTLED_STATUSES:
                        raise r.InputError(f"run is already settled ({rc['status']}); nothing to stop")
                _log_event(rc, {"state": "stop_attempted"})
                err = runners.stop(rc)
        except Busy as e:
            return {"schema_version": r.SCHEMA_VERSION, "status": "conflict", "run_id": rc["run_id"],
                    "warnings": [r.warn("dispatch_lock", f"{e}; retry stop when collect returns")]}
        log = _log_event(rc, {"state": "stop_uncertain" if err else "stop_sent", "error": err})
        return {"schema_version": r.SCHEMA_VERSION, "status": "delivery_uncertain" if err else "stop_sent",
                "run_id": rc["run_id"], "thread_id": None, "messages_path": str(log), **({"error": err} if err else {})}
    if rc.get("backend") != BACKEND:
        raise r.InputError("legacy receipt: stop its original herdr-projects worker manually; no automatic migration")
    if project_binding(rc["herdr_session"], runner) != rc["project_binding"]:
        raise r.InputError("Shepherdr protocol or core version changed; inspect the recorded worker")
    if rc.get("execution") == "headless" and not rc.get("thread_id"):
        terminals = [rc["terminal_id"]] if rc.get("terminal_id") else []
    else:
        row = _task(rc, runner)
        if row.get("state") in ("queued", "scheduled", "todo"):
            _log_event(rc, {"state": "stop_attempted"})
            obj, err = project_call(["reopen", rc["thread_id"], "--folder", repo_cwd(rc), "--json"], runner)
            cancelled = not err and isinstance(obj, dict) and obj.get("key") == rc["thread_id"] and obj.get("state") == "todo"
            log = _log_event(rc, {"state": "stop_sent" if cancelled else "stop_uncertain", "cancelled_queue": cancelled})
            return {"schema_version": r.SCHEMA_VERSION, "status": "stop_sent" if cancelled else "delivery_uncertain",
                    "run_id": rc["run_id"], "thread_id": rc["thread_id"], "messages_path": str(log)}
        terminals = [t["address"] for t in row.get("live", [])]
    if not terminals:
        raise r.InputError("no recorded live terminal; inspect it before declaring the worker stopped")
    _log_event(rc, {"state": "stop_attempted"})
    err = None
    for terminal in terminals:
        _, err = project_call(["kill", terminal, "--json"], runner, raw=True, exe=HERDR_BIN)
        if err:
            break
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


def _events(rc):
    """messages.jsonl entries. split("\\n"), not splitlines(): U+2028 in a logged message is not a record break."""
    log = Path(rc["run_dir"]) / "messages.jsonl"
    return [json.loads(x) for x in log.read_text("utf-8").split("\n") if x] if log.exists() else []


def collect_run(cwd, run_id, wait_ms, session=None, runner=subprocess.run):
    from . import coordination as co
    cwd = os.path.realpath(cwd)
    try:
        with dispatch_lock(cwd):
            rc = load_receipt(cwd, run_id)
            if session is not None and session != rc["herdr_session"]:
                raise r.InputError("collect space differs from the recorded run")
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
                "receipt_path": str(Path(rc["run_dir"]) / "receipt.json"), "receipt_cwd": rc["cwd"],
                "deadline_at": rc["deadline_at"],
                "thread_id": rc.get("thread_id"), "worktree": rc.get("worktree"), "branch": rc.get("branch"),
                "last_observation": rc["last_observation"],
                "diagnostic_tail": rc.get("diagnostic_tail"), "release": rc.get("release"), "reused_receipt": reused,
                "backend": rc.get("backend"), "invocation": rc.get("invocation"),
                "monitor": rc.get("monitor"), "cleanup": rc.get("cleanup")})
    out["selected"] = {**(out.get("selected") or {}), "profile": rc["profile"],
                       "profile_fingerprint": rc["profile_fingerprint"]}
    out["reassignment"] = ("collect_first" if rc["delivery_state"] in ("submission_attempted", "uncertain")
                            or rc["status"] in ("timed_out", "waiting", "delivery_uncertain", "handed_off") else
                            "safe_to_retry" if rc["delivery_state"] == "not_attempted" else "review_result")
    return out
