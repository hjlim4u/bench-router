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
from . import shepherdr
# Shepherdr connect/bind calls live in the adapter; these names stay importable from herdr.
from .shepherdr import (BACKEND, HERDR_BIN, PROJECTS_BIN, SHORT_CALL_S, START_CALL_S, TASK_PROTOCOL,
                        WORK_SETTINGS, bound_runner, project_call)

LOCAL_BACKEND = "local-1"  # one-shot CLI as a local subprocess (runners.py)
EXTERNAL_BACKEND = "external-1"  # the caller runs the agent; the router keeps receipt and result contract
TUI_BACKEND = "herdr-tui-1"  # one-shot CLI in its own herdr TUI workspace, through the herdr CLI only (runners.py)
TUI_BIN = os.environ.get("BENCH_ROUTER_HERDR", "herdr")
RUNNERS = {"herdr": BACKEND, "herdr-tui": TUI_BACKEND, "local": LOCAL_BACKEND, "external": EXTERNAL_BACKEND}
OBSERVE_FLOOR_S = 2  # one task observation; keeps calls inside a 5s task budget
MAX_PROMPT_ARG_BYTES = 120 * 1024  # the prompt is one argv entry (--desc); Linux caps one at 128 KiB
DISCOVERED_KIND = {"claude": ("claude", "claude-code", "--model"),
                   "codex": ("codex", "codex-cli", "-m")}
# Codex keeps the models its -m accepts, with each model's efforts; "hide" marks internal models.
CODEX_MODELS_CACHE = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "models_cache.json"
RESULT_REL = Path(".bench-router") / "runs"  # agent writes results here, relative to its board worktree
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


# ---------- Board providers ----------

# backend id -> adapter factory(runner). New runs get their backend from resolve_runner, recorded runs from
# rc["backend"]. project_call is looked up at call time so it stays the one replaceable Shepherdr seam.
BOARDS = {BACKEND: lambda runner: shepherdr.ShepherdrBoard(runner, project_call)}


def _board(backend, runner):
    return BOARDS[backend](runner)


def project_binding(session=None, runner=subprocess.run, core_session=None):
    """Bind to the task protocol and core build, never interpret legacy Projects receipts as tasks."""
    return shepherdr.project_binding(session, runner, core_session, project_call)


def resolve_runner(name=None, which=shutil.which):
    """--runner → receipt backend. auto: Shepherdr when its task and core CLIs are on PATH, else a local subprocess."""
    name = name or os.environ.get("BENCH_ROUTER_RUNNER") or "auto"
    if name == "auto":
        name = "herdr" if which(PROJECTS_BIN) and which(HERDR_BIN) else "local"
    if name not in RUNNERS:
        raise r.InputError(f"runner must be one of {['auto', *RUNNERS]} (got {name!r})")
    return RUNNERS[name]


def runner_binding(backend, session=None, runner=subprocess.run, cwd=None):
    if backend in BOARDS and backend != BACKEND:
        return _board(backend, runner).bind(session, cwd)
    if backend != BACKEND:
        return {"runner": backend}
    path = Path(cwd) / ".bench-router" / "shepherdr.json" if cwd else None
    core_session = None
    if path and path.exists():
        config = r.load_json_strict(path, r.TASK_MAX_BYTES)
        if not isinstance(config, dict) or any(k in config and (not isinstance(config[k], str) or not config[k].strip() or "/" in config[k]) for k in ("space", "core_session")):
            raise r.InputError(f"{path}: space and core_session must be nonempty strings without slashes")
        if not session and not (os.environ.get("BENCH_ROUTER_SPACE") or os.environ.get("BENCH_ROUTER_HERDR_SESSION")):
            session = config.get("space")
        core_session = config.get("core_session")
    return project_binding(session, runner, core_session)


def same_binding(rc, session, runner, require_core_id=True):
    current = project_binding(session, bound_runner(rc, runner), rc["project_binding"]["session"])
    return shepherdr.matches_binding(current, rc["project_binding"], require_core_id=require_core_id)


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
    """Profile model/effort flags expressed by the board's task add; permissions stay the user's CLI settings."""
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


def cost_tier(model, output_prices):
    """List output price per 1M tokens: < $5 low, < $20 medium, else high; unpriced models stay high."""
    from .data import model_key
    price = output_prices.get(model_key(model)[0])
    return "high" if price is None else "low" if price < 5 else "medium" if price < 20 else "high"


def discover_profiles(which=shutil.which, runner=subprocess.run, codex_cache=CODEX_MODELS_CACHE, claude_models=None,
                      output_prices=None):
    """Discover accepted models from native CLI caches and vendor guidance, never usage history.
    output_prices: data.aa_output_prices() result that sets cost_tier; without it every profile is high."""
    output_prices = output_prices or {}
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
            name = model.lower().removeprefix(f"{kind}-")  # guide IDs already start with "claude-"
            profile_id = re.sub(r"[^a-z0-9_-]", "-", f"{kind}-{name[:48 - len(kind) - len(effort) - 2]}-{effort}").rstrip("-")
            if not profile_id or any(p["id"] == profile_id for p in profiles):
                continue
            args = [model_flag, model]
            args += ["--effort", effort] if kind == "claude" and effort != "unknown" else []
            args += ["-c", f'model_reasoning_effort="{effort}"'] if kind == "codex" else []
            profiles.append({"id": profile_id, "enabled": True, "kind": kind, "executable": kind,
                             "args": args, "model_id": model, "harness_id": harness_id,
                             "reasoning_effort": effort, "config_revision": revision,
                             "cost_tier": cost_tier(model, output_prices), "inference_local": False, "context_tokens": 0,
                             "capabilities": ["filesystem_write"]})
    profiles = [p for p in profiles if probe(p, which) is None]
    if which("agy"):
        for model in agy_models(runner) or ():
            match = re.fullmatch(r"(.+)-(low|medium|high|xhigh)", model)
            if not match:
                continue
            model_id, effort = match.groups()
            profile_id = re.sub(r"[^a-z0-9_-]", "-", f"agy-{model.lower()}")[:48].rstrip("-")
            if any(p["id"] == profile_id for p in profiles):
                continue
            profiles.append({"id": profile_id, "enabled": True, "kind": "agy", "executable": "agy",
                             "args": ["--model", model], "model_id": model_id, "harness_id": "antigravity-cli",
                             "reasoning_effort": effort, "config_revision": "agy-models",
                             "cost_tier": cost_tier(model_id, output_prices), "inference_local": False, "context_tokens": 0,
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
        if not rc.get("worktree"):
            rc.update(status="delivery_uncertain", delivery_state="uncertain")
            _observe(rc, state, note="worktree unknown; inspect board card before collecting")
            return rc
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


def headless_script(rc, argv, publish=True):
    """sh script: the one-shot CLI in the worktree with the prompt from input.txt, then its exit code, atomically.
    publish=False leaves exit_code.tmp for the caller to publish (herdr-tui: after tee has written the last output)."""
    q, rd = shlex.quote, Path(rc["run_dir"])
    tmp = q(str(rd / "exit_code.tmp"))
    return (f"cd {q(rc['worktree'])} && {shlex.join(argv)} \"$(cat {q(str(rd / 'input.txt'))})\"; echo $? > {tmp}"
            + (f" && mv {tmp} {q(str(rd / 'exit_code'))}" if publish else ""))



def _checked_runner(rc, session, runner, require_core_id=True):
    """Open the recorded session only after validating its protocol and binding."""
    if rc.get("identity") == "mismatch":
        raise r.InputError("resumed terminal identity mismatch; reconcile manually before any control")
    if not same_binding(rc, session or rc["project_binding"]["space"], runner, require_core_id=require_core_id):
        raise r.InputError("Shepherdr session or core binding differs from the receipt")
    return bound_runner(rc, runner)


def _bounded(rc, runner, until=None):
    """Every call's timeout within the run's remaining deadline (and until, a monotonic end), never below the floor:
    collect/stop after the deadline still get one short attempt per call."""
    end = time.monotonic() + (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds()
    end = end if until is None else min(end, until)

    def run(cmd, **kw):
        kw["timeout"] = min(kw.get("timeout") or SHORT_CALL_S, max(OBSERVE_FLOOR_S, end - time.monotonic()))
        return runner(cmd, **kw)
    return run


def _submission_runner(rc, session, runner):
    try:
        return _checked_runner(rc, session, runner)
    except r.InputError as exc:
        why = str(exc)
    rc["status"] = "execution_failed"
    _observe(rc, note=f"{why}; nothing submitted")
    save(rc)
    return None


def execute(rc, prompt, profile, session=None, runner=subprocess.run, wait_ms=None):
    if rc["backend"] in BOARDS and rc["backend"] != BACKEND:
        return _execute_board(rc, prompt, session, runner, wait_ms)
    if rc["backend"] != BACKEND:
        from . import runners
        return runners.start(rc, prompt, profile, wait_ms, runner)
    runner = _submission_runner(rc, session, runner)
    if runner is None:
        return rc
    board = _board(BACKEND, runner)
    settings = worker_settings(profile)
    if settings is None:
        rc["status"] = "execution_failed"
        _observe(rc, note="profile args beyond model/effort cannot be expressed; nothing submitted")
        save(rc)
        return rc
    prompt += shepherdr.PROMPT_NOTE
    r.atomic_write(Path(rc["run_dir"]) / "input.txt", prompt.encode("utf-8"))
    remaining = (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds()
    if remaining <= 0:
        rc["status"] = "execution_failed"
        _observe(rc, note="deadline elapsed before task submission")
        save(rc)
        return rc
    from . import parallel
    # Shepherdr owns merging into the repository's actual target branch.
    try:
        base = parallel._git(repo_cwd(rc), "branch", "--show-current")
        if not base:
            raise r.InputError("a checked-out target branch is required")
    except r.InputError as e:
        rc["status"] = "execution_failed"
        _observe(rc, note=f"{e}; nothing submitted")
        save(rc)
        return rc
    rc["delivery_state"] = "submission_attempted"
    save(rc)  # An add with a lost response must never be repeated, even though it starts nothing.
    obj, err = board.add(rc, settings, base, min(START_CALL_S, remaining))
    if obj is None:
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
    script = None
    if rc.get("execution") == "headless":
        argv = headless_argv(profile)
        if argv is None:
            rc.update(status="execution_failed", process_exited=True)
            save(rc)
            return rc
        # tee keeps the pane live while output.log outlives release() closing the terminal (as the local runner's log)
        log = shlex.quote(str(Path(rc["run_dir"]) / "output.log"))
        script = f"{{ {headless_script({**rc, 'worktree': '.'}, argv)}; }} 2>&1 | tee {log}"
    obj, err = board.start_task(rc, board.launch_args(profile, script),
                                min(START_CALL_S, max(0.001, (datetime.fromisoformat(rc["deadline_at"]) - _now()).total_seconds())))
    if obj is None:
        rc.update(status="delivery_uncertain", delivery_state="uncertain")
        try:
            state = board.task(rc).get("state")
        except r.InputError:
            state = "unknown"
        _observe(rc, state, error=err, note="task start unconfirmed; collect the recorded task, never restart")
        save(rc)
        return rc
    rc["terminal_id"] = obj.get("terminal")
    rc["worktree"], rc["branch"] = obj.get("worktree"), obj.get("branch")
    save(rc)
    if rc["terminal_id"]:
        try:
            board.verify_terminal(rc, rc["terminal_id"])
        except r.InputError as e:
            rc.update(status="delivery_uncertain", delivery_state="uncertain", terminal_unverified=True)
            _observe(rc, note=str(e))
            save(rc)
            return rc
    monitor, monitor_error = board.watch(rc)
    rc["monitor"] = {"terminal_id": (monitor or {}).get("address"), "error": monitor_error}
    remaining = _wait(rc, wait_ms)
    rc["status"] = "timed_out"
    save(rc)
    return collect(rc, remaining, session, runner) if remaining > 0 else rc


def _execute_board(rc, prompt, session, runner, wait_ms):
    """A non-Shepherdr board, through the Board port only. Stores before/after each call per board.PERSISTENCE."""
    board = _board(rc["backend"], runner)
    rc["binding"] = rc["project_binding"]
    r.atomic_write(Path(rc["run_dir"]) / "input.txt", prompt.encode("utf-8"))
    for op, attempted in (("create", ("delivery_state", "submission_attempted")), ("start", ("start_attempted", True))):
        rc[attempted[0]] = attempted[1]
        save(rc)  # a lost response is never re-called
        try:
            rc.update(getattr(board, op)(rc))
        except r.InputError as e:
            rc.update(status="execution_failed", process_exited=True)
            if op == "create":
                rc["delivery_state"] = "not_attempted"
            _observe(rc, note=f"{e}; nothing {'submitted' if op == 'create' else 'started'}")
            save(rc)
            return rc
        except Exception as e:
            rc.update(status="delivery_uncertain", delivery_state="uncertain")
            _observe(rc, note=f"board {op} unconfirmed ({e}); collect the recorded card, never resend")
            save(rc)
            return rc
    rc["status"] = "timed_out"
    save(rc)
    remaining = _wait(rc, wait_ms)
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


def _recorded_terminals(rc, primary=None, live_addresses=()):
    """Every terminal id recorded for this run: primary, live workers, and every stop target."""
    seen = []
    for t in (primary, rc.get("terminal_id"), *live_addresses,
              *(x["terminal_id"] for e in _events(rc) for x in e.get("terminals") or []
                if isinstance(x, dict) and x.get("terminal_id")),
              *(x["terminal_id"] for x in (rc.get("stop") or {}).get("terminals") or []
                if isinstance(x, dict) and x.get("terminal_id"))):
        if t and t not in seen:
            seen.append(t)
    return seen


def _all_exited(rc, board, primary, primary_state, timeout_s, live_addresses=()):
    """True only when every recorded terminal for this run has exited/gone evidence in the task's core."""
    if primary_state not in ("exited", "gone"):
        return False
    return all(board.terminal_state(t, timeout_s, rc) in ("exited", "gone")
               for t in _recorded_terminals(rc, primary, live_addresses) if t != primary)


def _poll_headless(rc, runner, timeout_s):
    board = _board(BACKEND, runner)
    board_stopped, live_addresses = False, ()
    if rc.get("thread_id"):
        row = board.task(rc, timeout_s)
        board_stopped = row.get("needs") == "stopped"
        live_addresses = [w.get("address") for w in row.get("live") or [] if isinstance(w, dict) and w.get("address")]
        if row.get("state") in ("todo", "queued", "scheduled"):
            cancelled = row.get("state") == "todo" and any(e.get("cancelled_queue") for e in _events(rc))
            if cancelled:
                rc.update(status="execution_failed", process_exited=True)
            else:
                rc["status"] = "timed_out"
            return
    if not rc.get("terminal_id"):
        recovered = board.find_terminal(rc, live_addresses, timeout_s)
        if not recovered:
            raise r.InputError("hc run response was lost; inspect the recorded run label before resolving")
        rc["terminal_id"] = recovered
    process = board.terminal_state(rc["terminal_id"], timeout_s, rc)
    exited = _all_exited(rc, board, rc["terminal_id"], process, timeout_s, live_addresses)
    stopped = board_stopped or any(e.get("state") in ("stop_attempted", "stop_sent", "stop_uncertain") for e in _events(rc))
    if (not stopped or exited) and settle_exit(rc):
        if rc["status"] == "completed" and (rc.get("project_binding") or {}).get("core_id"):
            release(rc, runner)
        return
    if process in ("exited", "gone"):
        rc.update(status="execution_failed", process_exited=exited)
        note = (f"headless terminal {process} before writing its exit code" if exited
                else "stop incomplete; another recorded terminal is still live")
        _observe(rc, note=note)
    else:
        rc["status"] = "timed_out"
        _observe(rc, "working", note="headless CLI still running")


def _observe_board(rc, runner):
    """One Board.observe of a non-Shepherdr board, mapped onto the receipt; success still needs the result files."""
    obs = _board(rc["backend"], runner).observe(rc)
    rc.update(obs.get("ids") or {})
    task, why = obs["task"], obs["why"]
    if obs["retryable"]:
        rc["status"] = "timed_out"
        _observe(rc, note=why or "board read failed; retry")
    elif obs["identity"] != "ok":
        raise r.InputError("board card or terminal differs from the receipt; reconcile manually")
    elif task == "turn_done":
        if rc.get("terminal_id") or rc["delivery_state"] not in ("uncertain", "submission_attempted"):
            rc["delivery_state"] = "activity_observed"
        settle(rc, "done")
        if rc["status"] == "completed":
            release(rc, runner)
    elif task == "blocked":
        rc.update(status="blocked", delivery_state="activity_observed", diagnostic_tail=why)
        _observe(rc, "blocked", note=why)
    elif task == "stopped":
        rc.update(status="execution_failed", process_exited=obs["process"] == "exited")
        _observe(rc, task, note=why or "board agent stopped")
    elif task == "not_started":
        rc["status"] = "delivery_uncertain"
        _observe(rc, task, note="card not started; recovery never calls start")
    else:
        rc.update(status="timed_out", delivery_state="activity_observed")
        _observe(rc, task, note=why)


def collect(rc, wait_ms=0, session=None, runner=subprocess.run):
    """Observe the recorded board task only; never delegate, retry or re-prompt it."""
    if rc.get("backend") not in (*BOARDS, LOCAL_BACKEND, EXTERNAL_BACKEND, TUI_BACKEND):
        raise r.InputError("legacy receipt: inspect the original worker; automatic backend migration is refused")
    native = rc["backend"] == BACKEND
    port = rc["backend"] in BOARDS and not native  # any other board, through the Board port only
    deadline = time.monotonic() + wait_ms / 1000
    has_core_id = bool((rc.get("project_binding") or {}).get("core_id"))
    if native:
        try:
            runner = _checked_runner(rc, session, _bounded(rc, runner, deadline if wait_ms > 0 else None),
                                     require_core_id=False)
        except r.InputError as exc:
            if rc["status"] == "completed" and rc.get("settled_contract"):
                return rc  # a finished record stays readable as-is; releasing needs a verified core
            rc.update(status="delivery_uncertain", delivery_state="uncertain")
            _observe(rc, note=str(exc))
            save(rc)
            return rc
    if rc["status"] == "completed" and rc.get("settled_contract"):
        if ((native and has_core_id) or port) and rc.get("release") is None:  # completed before releasing existed, or the last close failed
            release(rc, runner)
            save(rc)
        elif not native and not port:
            from . import runners
            if runners.retry_release(rc, runner):
                save(rc)
        return rc
    if rc["delivery_state"] == "not_attempted":
        return rc
    headless = rc.get("execution") == "headless"
    stops = [e["terminals"] for e in _events(rc) if e.get("terminals")]
    if stops:
        rc["stop"] = {"terminals": stops[-1]}  # per-terminal results of the last stop, mirrored under the lock
    # Calls stay within the wait budget, but never below a floor: a near-zero budget made the last poll time out
    # and misreported a working agent as delivery_uncertain.
    timeout = lambda: min(SHORT_CALL_S, max(OBSERVE_FLOOR_S, deadline - time.monotonic())) if wait_ms > 0 else SHORT_CALL_S
    while True:
        try:
            if native and not rc.get("thread_id") and (not headless or (not rc.get("terminal_id") and not rc.get("start_attempted"))):
                ids, err = _board(BACKEND, runner).lookup_card(rc, timeout())
                if err:
                    raise r.InputError(err.get("message") or "task list failed")
                rc.update(ids)
                save(rc)
            if native and rc.get("terminal_unverified"):
                _board(BACKEND, runner).verify_terminal(rc, rc["terminal_id"])
                rc.pop("terminal_unverified")
            if port:
                _observe_board(rc, runner)
            elif not native:
                from . import runners
                runners.poll(rc, runner, max(0.0, deadline - time.monotonic()))  # herdr-tui waits in herdr
            elif headless:
                _poll_headless(rc, runner, timeout())
            else:
                board = _board(BACKEND, runner)
                row = board.task(rc, timeout())
                terminal = rc.get("terminal_id")
                addresses = [worker.get("address") for worker in row.get("live") or []]
                if terminal and addresses and terminal not in addresses:
                    raise r.InputError("board worker differs from the recorded terminal")
                terminal = terminal or (addresses[0] if addresses else None)
                process = board.terminal_state(terminal, timeout(), rc) if terminal else None
                state, status, needs = row.get("state"), row.get("status"), row.get("needs")
                stopped_by_router = any(e.get("state", "").startswith("stop_") for e in _events(rc))
                finished_with_result = (
                    process == "exited" and not stopped_by_router and rc.get("worktree")
                    and check_result({**rc, "run_dir": str(Path(rc["worktree"]) / RESULT_REL / rc["run_id"])})[0] is not None
                )
                if state in ("todo", "queued", "scheduled"):
                    cancelled = state == "todo" and any(e.get("cancelled_queue") for e in _events(rc))
                    if cancelled:
                        rc.update(status="execution_failed", process_exited=True)
                    else:
                        rc["status"] = "delivery_uncertain" if state == "todo" else "timed_out"
                    _observe(rc, status, note="task not started; recovery never calls start")
                elif finished_with_result:
                    if rc.get("terminal_id") or rc["delivery_state"] not in ("uncertain", "submission_attempted"):
                        rc["delivery_state"] = "activity_observed"
                    settle(rc, "done")
                    if rc["status"] == "completed" and has_core_id:
                        release(rc, runner)
                elif needs == "stopped" or (process in ("exited", "gone") and status not in ("ready", "done")):
                    # Admission holds until every terminal the run recorded shows exit evidence.
                    exited = _all_exited(rc, board, terminal, process, timeout(), addresses)
                    rc.update(status="execution_failed", process_exited=exited)
                    _observe(rc, status, note=row.get("why") or "task agent stopped")
                elif process == "live" and stopped_by_router:
                    rc.update(status="timed_out", process_exited=False)
                    _observe(rc, status, note="stop requested; terminal still live")
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
                    if rc["status"] == "completed" and has_core_id:
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
                                   "or use --runner herdr|herdr-tui|external")
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
    if rc["backend"] == BACKEND:
        runner = _checked_runner(rc, None, runner)
        core_err = _board(BACKEND, runner).live_core_error(rc)
        if core_err:
            rc["release"] = None
            _observe(rc, error=core_err, note=f"completed; {core_err['message']}")
            return {"status": "delivery_uncertain", "error": core_err}
    from .lifecycle import finalize
    finalize(rc, runner)
    out = _board(rc["backend"], runner).cleanup(rc)
    if out["left_open"]:
        rc["release"] = None
        _observe(rc, error=out.get("error"), note=f"completed; {out['left_open']}")
        return {"status": "delivery_uncertain", "error": out.get("error")}
    rc["release"] = {"at": _iso(_now()), "terminals": out.get("terminals") or [{"terminal_id": t} for t in out["closed"]]}


def resume_run(cwd, run_id, runner=subprocess.run):
    """Resume the task's recorded session, or Shepherdr's handoff when no session is available."""
    cwd = os.path.realpath(cwd)
    with dispatch_lock(cwd):
        rc = load_receipt(cwd, run_id)
        if rc.get("backend") != BACKEND or not rc.get("thread_id"):
            raise r.InputError("only a Shepherdr task run can be resumed")
        if rc.get("execution") == "headless":  # its card has no conversation; resume would rerun the saved argv
            raise r.InputError("headless runs cannot be resumed; dispatch a new round")
        runner = _checked_runner(rc, None, runner)
        board = _board(BACKEND, runner)
        board.task(rc)
        obj, err = board.resume_task(rc)
        if err or not isinstance(obj, dict) or not obj.get("terminal"):
            raise r.InputError(f"resume failed: {(err or {}).get('message')}")
        rc["terminal_id"] = obj["terminal"]
        rc["resumed"] = {"at": _iso(_now()), "terminal_id": obj["terminal"], "session_resumed": obj.get("resumed") is True}
        rc["identity"] = board.resumed_identity(rc, obj["terminal"])
        if rc["identity"] == "mismatch":  # no further control; collect only reports, coordination keeps admission
            rc["status"] = "delivery_uncertain"
            _observe(rc, note="resumed terminal is not this task's in the recorded core session; reconcile manually")
        save(rc)
        if rc["identity"] == "mismatch":
            raise r.InputError(f"resumed terminal {obj['terminal']} identity mismatch; reconcile manually")
    return {**output(None, rc), "resumed": rc["resumed"]}


def tell_run(cwd, run_id, text, runner=subprocess.run):
    """Relay one explicit orchestrator message to a run's live agent. Never automatic; logged before sending."""
    cwd = os.path.realpath(cwd)
    if not isinstance(text, str) or not text.strip() or len(text.encode("utf-8")) > MAX_PROMPT_ARG_BYTES:
        raise r.InputError(f"message: nonempty text up to {MAX_PROMPT_ARG_BYTES} bytes required")
    rc = _target(cwd, run_id)
    if rc.get("execution") == "headless":
        raise r.InputError("headless runs take no messages; use the shared scratchpad or a new round")
    tui = rc.get("backend") == TUI_BACKEND and rc.get("agent_name")
    if not tui and (rc.get("backend") != BACKEND or not rc.get("thread_id")):
        raise r.InputError("only a Shepherdr or interactive herdr-tui run can receive a message")
    if rc["status"] in SETTLED_STATUSES and not (tui or rc.get("resumed")):
        raise r.InputError("run is settled; `resume` it first (tell on a finished board task starts a new agent)")
    if tui:  # herdr itself refuses a prompt to a blocked agent
        if rc["status"] in SETTLED_STATUSES:
            raise r.InputError("run is settled and its workspace is closed; dispatch a new round")
        from . import runners
        runners._same_server(rc, runner)
        # wait until the new turn is seen: before that the agent still reads idle and collect would settle it
        send = lambda: project_call(["agent", "prompt", rc["agent_name"], text, "--wait", "--until", "working",
                                     "--until", "blocked", "--timeout", "20000"], runner, exe=TUI_BIN)
    else:
        runner = _checked_runner(rc, None, runner)
        board = _board(BACKEND, runner)
        core_err = board.live_core_error(rc)
        if core_err:
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            log = _log_event(rc, {"sha256": digest, "state": "uncertain", "error": core_err})
            return {"schema_version": r.SCHEMA_VERSION, "status": "delivery_uncertain",
                    "run_id": rc["run_id"], "thread_id": rc.get("thread_id"), "sha256": digest,
                    "messages_path": str(log), "error": core_err}
        terminal = board.tell_target(rc)
        send = lambda: board.send(terminal, text)
    # No dispatch lock or receipt write: a blocking parallel/collect on this cwd must not stall the message.
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    _log_event(rc, {"sha256": digest, "state": "attempted", "bytes": len(text.encode("utf-8")), "text": text})
    obj, err = send()
    log = _log_event(rc, {"sha256": digest, "state": "uncertain" if err else "sent", "error": err})
    return {"schema_version": r.SCHEMA_VERSION, "status": "delivery_uncertain" if err else "sent",
            "run_id": rc["run_id"], "thread_id": rc.get("thread_id"), "sha256": digest, "messages_path": str(log),
            **({"error": err} if err else {})}


def stop_run(cwd, run_id, runner=subprocess.run):
    """Stop a task's observed core workers, cancel its queue, or end a local/external run.
    The next collect records it as execution_failed. Never automatic; logged like a message."""
    rc = _target(os.path.realpath(cwd), run_id)
    if rc["status"] in SETTLED_STATUSES:
        raise r.InputError(f"run is already settled ({rc['status']}); nothing to stop")
    if rc.get("backend") in (LOCAL_BACKEND, EXTERNAL_BACKEND, TUI_BACKEND):
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
                err = runners.stop(rc, runner)
        except Busy as e:
            return {"schema_version": r.SCHEMA_VERSION, "status": "conflict", "run_id": rc["run_id"],
                    "warnings": [r.warn("dispatch_lock", f"{e}; retry stop when collect returns")]}
        log = _log_event(rc, {"state": "stop_uncertain" if err else "stop_sent", "error": err})
        return {"schema_version": r.SCHEMA_VERSION, "status": "delivery_uncertain" if err else "stop_sent",
                "run_id": rc["run_id"], "thread_id": None, "messages_path": str(log), **({"error": err} if err else {})}
    if rc.get("backend") != BACKEND:
        raise r.InputError("legacy receipt: stop its original worker manually")
    runner = _checked_runner(rc, None, _bounded(rc, runner), require_core_id=False)
    board = _board(BACKEND, runner)
    core_err = board.live_core_error(rc)
    if core_err:
        log = _log_event(rc, {"state": "stop_uncertain", "error": core_err})
        return {"schema_version": r.SCHEMA_VERSION, "status": "delivery_uncertain",
                "run_id": rc["run_id"], "thread_id": rc.get("thread_id"), "messages_path": str(log),
                "error": core_err}
    if rc.get("execution") == "headless" and not rc.get("thread_id"):
        terminals = [rc["terminal_id"]] if rc.get("terminal_id") else []
    else:
        row = board.task(rc)
        if row.get("state") in ("queued", "scheduled", "todo"):
            _log_event(rc, {"state": "stop_attempted"})
            cancelled = board.reopen(rc)
            log = _log_event(rc, {"state": "stop_sent" if cancelled else "stop_uncertain", "cancelled_queue": cancelled})
            return {"schema_version": r.SCHEMA_VERSION, "status": "stop_sent" if cancelled else "delivery_uncertain",
                    "run_id": rc["run_id"], "thread_id": rc["thread_id"], "messages_path": str(log)}
        terminals = [t["address"] for t in row.get("live", [])]
    if not terminals:
        raise r.InputError("no recorded live terminal; inspect it before declaring the worker stopped")
    _log_event(rc, {"state": "stop_attempted"})
    results = board.kill_all(rc, terminals)
    err = next((x["error"] for x in results if x["error"]), None)
    # collect copies terminals into the receipt and holds admission until each has exit evidence
    log = _log_event(rc, {"state": "stop_uncertain" if err else "stop_sent", "error": err, "terminals": results})
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
                "monitor": rc.get("monitor"), "ready": rc.get("ready"), "cleanup": rc.get("cleanup")})
    out["selected"] = {**(out.get("selected") or {}), "profile": rc["profile"],
                       "profile_fingerprint": rc["profile_fingerprint"]}
    out["reassignment"] = ("collect_first" if rc["delivery_state"] in ("submission_attempted", "uncertain")
                            or rc["status"] in ("timed_out", "waiting", "delivery_uncertain", "handed_off") else
                            "safe_to_retry" if rc["delivery_state"] == "not_attempted" else "review_result")
    return out
