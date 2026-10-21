"""Shared input validation, assessment, constraints and selection entry points.

Vendor-guided decisions are the default; legacy scores require explicit opt-in.
Network decisions are opt-in for live callers. This module never dispatches or writes files.
"""
import contextlib
import hashlib
import json
import math
import os
import re
import time
import tomllib
from datetime import datetime
from decimal import Decimal
from pathlib import Path

SCHEMA_VERSION = "1.0"
POLICY_VERSION = "1.0"
CLASSIFIER_VERSION = "l1-rules-2"
EPS = 1e-9

CATEGORIES = ("coding_repo", "terminal_ops", "code_gen", "webdev", "math_reasoning",
              "analysis", "writing", "vision_doc", "general")
TIERS = {"low": 0, "medium": 1, "high": 2}
PRIORITIES = ("quality", "balanced", "cost")
SCOPES = ("exact_profile", "model_proxy")

# P: 초기 정책. 값을 바꾸면 POLICY_VERSION을 올린다.
POLICY = {
    "coverage_threshold": 0.5,
    "missing_prior": 0.5,
    "missing_penalty": 0.1,
    "near_tie_epsilon": 0.02,
    "tier_proxy": {"low": 0.0, "medium": 0.5, "high": 1.0},
    "lambda_cost": {"quality": 0.0, "balanced": 0.15, "cost": 0.30},
}

# L1: summary 키워드와 context_files 확장자. 한 카테고리에서 서로 다른 규칙 2개 이상이 맞아야 채택.
# ponytail: 키워드 목록은 휴리스틱. 로그에서 abstain/오분류가 선택 실패를 만들 때 L2(임베딩)로 간다.
L1_RULES = {
    "coding_repo": (["refactor", "bug", "repository", "repo", "pull request", "test suite",
                     "리팩터", "버그", "저장소"], [".py", ".go", ".rs", ".java", ".kt", ".c", ".cpp", ".cs"]),
    "terminal_ops": (["shell", "bash", "terminal", "docker", "systemd", "cron", "deploy",
                      "터미널", "배포", "쉘"], [".sh", ".service", "dockerfile"]),
    "code_gen": (["implement", "write a function", "generate code", "script", "구현", "함수 작성", "코드 생성"], []),
    "webdev": (["react", "vue", "svelte", "next.js", "css", "html", "frontend", "web page",
                "프론트엔드", "웹페이지", "웹 페이지"], [".tsx", ".jsx", ".css", ".html", ".vue", ".svelte"]),
    "math_reasoning": (["prove", "proof", "theorem", "equation", "integral", "증명", "방정식", "수학"], []),
    "analysis": (["analyze", "analyse", "research", "compare", "investigate", "분석", "조사", "비교"], [".csv", ".xlsx"]),
    "writing": (["essay", "blog", "article", "copywriting", "에세이", "블로그", "글쓰기", "기사"], []),
    "vision_doc": (["pdf", "image", "screenshot", "diagram", "이미지", "스크린샷", "도표"],
                   [".pdf", ".png", ".jpg", ".jpeg", ".webp"]),
}


class InputError(ValueError):
    """입력/설정 계약 위반 (CLI exit 2)."""


def warn(code, message, source_id=None):
    return {"code": code, "message": message, "source_id": source_id}


def canonical_hash(obj):
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def atomic_write(path, data):
    path = Path(path)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    try:
        for attempt in range(10):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if os.name != "nt" or attempt == 9:
                    raise
                time.sleep(0.05)  # Windows readers can briefly block replacement.
    finally:
        tmp.unlink(missing_ok=True)
    with contextlib.suppress(OSError):  # 디렉터리 fsync는 POSIX에서만
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


# ---------- 엄격 JSON ----------

def _no_dupes(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise InputError(f"duplicate JSON key: {k}")
        out[k] = v
    return out


def _reject_const(name):
    raise InputError(f"non-finite number not allowed: {name}")


# .env에서 읽는 키. 프로젝트 .env에 다른 비밀이 섞여 있어도 이 목록 밖의 값은 읽지도 넘기지도 않는다.
DOTENV_KEYS = ("JEV_API_KEY", "TYPESAFE_API_KEY", "JEV_MODEL", "BENCH_ROUTER_DECISION_MODEL", "ARTIFICIAL_ANALYSIS_API_KEY")


def env_with_dotenv(config_dir=None, cwd=None):
    """우선순위: 프로세스 환경 > <cwd>/.env > <config_dir>/env. 파일이 없거나 깨져도 조용히 건너뛴다.
    shortcut: KEY=VALUE 한 줄 형식만(보간·여러 줄 값 없음), 필요해지면 python-dotenv로 교체."""
    out = {}
    for path in (Path(config_dir or Path.home() / ".config/bench-router") / "env", Path(cwd or ".") / ".env"):
        try:
            text = path.read_text("utf-8") if path.stat().st_size <= 64 * 1024 else ""
        except OSError:
            continue
        for line in text.splitlines():
            k, sep, v = line.strip().removeprefix("export ").partition("=")
            k, v = k.strip(), v.strip()
            if sep and k in DOTENV_KEYS:
                out[k] = v[1:-1] if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'" else v
    return {**out, **os.environ}


def load_json_strict(path, max_bytes):
    try:
        data = Path(path).read_bytes()
    except FileNotFoundError:
        raise InputError(f"file not found: {path}")
    if len(data) > max_bytes:
        raise InputError(f"{path}: larger than {max_bytes} bytes")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_no_dupes, parse_constant=_reject_const)
    except UnicodeDecodeError as e:
        raise InputError(f"{path}: invalid UTF-8 ({e.reason})")
    except json.JSONDecodeError as e:
        raise InputError(f"{path}: invalid JSON ({e})")


def _num(v, name, lo=None, hi=None):
    if type(v) not in (int, float) or not math.isfinite(v) or (lo is not None and v < lo) or (hi is not None and v > hi):
        raise InputError(f"{name}: finite number in [{lo}, {hi}] required")
    return v


def _int(v, name, lo, hi=None):
    if type(v) is not int or v < lo or (hi is not None and v > hi):
        raise InputError(f"{name}: integer in [{lo}, {hi}] required")
    return v


def _str(v, name, max_len=None):
    if not isinstance(v, str) or not v.strip() or (max_len and len(v) > max_len):
        raise InputError(f"{name}: non-empty string (max {max_len}) required")
    return v


def _str_list(v, name):
    if not isinstance(v, list) or not all(isinstance(x, str) and x for x in v):
        raise InputError(f"{name}: array of non-empty strings required")
    return v


def _bool(v, name):
    if type(v) is not bool:
        raise InputError(f"{name}: boolean required")
    return v


def _parse_time(v, name):
    try:
        t = datetime.fromisoformat(_str(v, name))
    except ValueError:
        raise InputError(f"{name}: ISO-8601 time required")
    if t.tzinfo is None:
        raise InputError(f"{name}: timezone required")
    return t


# ---------- task.json (04 입력 계약) ----------

TASK_REQUIRED = ("schema_version", "task_id", "round", "summary", "prompt", "cwd")
TASK_OPTIONAL = ("context_files", "constraints", "priority", "exclude_profiles", "facets", "execution")
EXECUTIONS = ("interactive", "headless")
CONSTRAINT_DEFAULTS = {"max_cost_tier": "high", "min_context_tokens": 0, "local_only": False,
                       "timeout_ms": 900000, "required_capabilities": []}
TASK_MAX_BYTES = 1024 * 1024


# ---------- context.json: Orchestrator 공급 지표 (docs/routing-contracts.md §2) ----------

CONTEXT_SCHEMA_VERSION = "2.0"
EVALUATE_SCHEMA_VERSION = "2.0"
ROUTER_COST_SOURCE = "router:io2-v1"
METRIC_REGISTRY_VERSION = "1"
# 지표 정의표. 단위·대상·수명 검증이 필요한 새 지표는 여기에 한 줄 추가한다.
# 선호 방향(클수록 좋다 등)은 정책이므로 두지 않는다. 의미·단위를 바꾸면 METRIC_REGISTRY_VERSION을 올린다.
# id: (applies_to task|profile, kind int|number|bool|enum:a|b, unit|None, max_age_hours|None)
METRICS = {
    "tokens.estimated_input": ("profile", "int", "tokens", None),
    "tokens.estimated_output": ("profile", "int", "tokens", None),
    "tokens.required_context": ("profile", "int", "tokens", None),
    "price.input_usd_per_mtok": ("profile", "number", "usd/mtok", 24 * 30),
    "price.output_usd_per_mtok": ("profile", "number", "usd/mtok", 24 * 30),
    "cost.estimated_usd": ("profile", "number", "usd", None),
    "task.complexity": ("task", "enum:low|medium|high", None, None),
}
METRIC_KEYS = {"value", "unit", "source", "observed_at", "expires_at", "status", "reason"}
COST_INPUTS = ("tokens.estimated_input", "tokens.estimated_output", "price.input_usd_per_mtok", "price.output_usd_per_mtok")
V1_SOURCE = "context-1.0"


def _metric(mid, raw, applies_to, path):
    """관측값 1개 검증. 결측은 status=missing(+reason)으로 표현하며 value=null은 허용하지 않는다."""
    if not isinstance(mid, str) or not re.fullmatch(r"[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*", mid):
        raise InputError(f"{path}: namespaced metric id required")
    name = f"{path}.{mid}"
    if not isinstance(raw, dict) or set(raw) - METRIC_KEYS:
        raise InputError(f"{name}: object with fields {sorted(METRIC_KEYS)} only")
    m = {"source": _str(raw.get("source"), f"{name}.source", 500), "status": raw.get("status", "ok")}
    if m["status"] not in ("ok", "missing"):
        raise InputError(f"{name}.status: ok|missing")
    for k in ("observed_at", "expires_at"):
        if k in raw:
            _parse_time(raw[k], f"{name}.{k}")
            m[k] = raw[k]
    if "reason" in raw:
        m["reason"] = _str(raw["reason"], f"{name}.reason", 4000)
    if "unit" in raw:
        m["unit"] = _str(raw["unit"], f"{name}.unit", 100)
    if m["status"] == "missing":
        if "value" in raw or "reason" not in m:
            raise InputError(f"{name}: status=missing takes reason and no value")
    elif "value" not in raw:
        raise InputError(f"{name}.value required (use status=missing for an absent value)")
    v = raw.get("value")
    spec = METRICS.get(mid)
    if spec is None:  # 미등록 지표: 전달만 한다. 제약·평가에 쓰지 않는다.
        if "value" in raw and (type(v) not in (int, float, bool, str) or (type(v) is float and not math.isfinite(v))):
            raise InputError(f"{name}.value: finite number, boolean or string required")
    else:
        applies, kind, unit, max_age = spec
        if applies != applies_to:
            raise InputError(f"{name}: {applies}-level metric")
        if m.get("unit") != unit:  # ponytail: 단위 변환 없음. ms/s 혼용이 실제로 생기면 지표별 배수 추가
            raise InputError(f"{name}.unit must be {unit!r}" if unit else f"{name}: unit not allowed")
        if max_age is not None and m["status"] == "ok" and "observed_at" not in m:
            raise InputError(f"{name}.observed_at required (expires after {max_age}h)")
        if "value" in raw:
            if kind == "int":
                _int(v, f"{name}.value", 0, 1_000_000_000_000)
            elif kind == "number":  # ponytail: 등록 수치 지표는 모두 0 이상. 음수 지표가 생기면 범위를 정의표로
                _num(v, f"{name}.value", 0, 1_000_000_000)
            elif kind == "bool":
                _bool(v, f"{name}.value")
            elif v not in kind[len("enum:"):].split("|"):
                raise InputError(f"{name}.value: one of {kind[len('enum:'):]}")
    if "value" in raw:
        m["value"] = v
    return m


def _metrics(raw, applies_to, path):
    if not isinstance(raw, dict):
        raise InputError(f"{path}: object required")
    return {mid: _metric(mid, m, applies_to, path) for mid, m in raw.items()}


def validate_context(raw, profile_ids):
    """Orchestrator 공급 지표 검증 → 2.0 정규형. 1.0은 변환해서 받는다. 가격은 Router가 가져오지 않는다.
    출력은 다시 넣어도 그대로인 2.0 입력이다."""
    if isinstance(raw, dict) and raw.get("schema_version") == SCHEMA_VERSION:
        raw = _context_v1_to_v2(_validate_context_v1(raw, profile_ids))
    if not isinstance(raw, dict) or set(raw) - {"schema_version", "task_metrics", "max_estimated_cost_usd", "profiles"}:
        raise InputError("context: object with known fields required")
    if raw.get("schema_version") != CONTEXT_SCHEMA_VERSION:
        raise InputError(f"context.schema_version must be {SCHEMA_VERSION!r} or {CONTEXT_SCHEMA_VERSION!r}")
    out = {"schema_version": CONTEXT_SCHEMA_VERSION,
           "task_metrics": _metrics(raw.get("task_metrics", {}), "task", "context.task_metrics"), "profiles": {}}
    if "max_estimated_cost_usd" in raw:
        out["max_estimated_cost_usd"] = _num(raw["max_estimated_cost_usd"], "context.max_estimated_cost_usd", 0)
    profiles = raw.get("profiles", {})
    if not isinstance(profiles, dict) or set(profiles) - set(profile_ids):
        raise InputError("context.profiles: object with configured profile ids required")
    for pid, item in profiles.items():
        if not isinstance(item, dict) or set(item) - {"metrics"}:
            raise InputError(f"context.profiles.{pid}: only metrics allowed")
        out["profiles"][pid] = {"metrics": _metrics(item.get("metrics", {}), "profile", f"context.profiles.{pid}.metrics")}
    return out


def _context_v1_to_v2(c):
    out = {"schema_version": CONTEXT_SCHEMA_VERSION, "task_metrics": {}, "profiles": {}}
    if "complexity" in c:
        out["task_metrics"]["task.complexity"] = {"value": c["complexity"]["level"], "reason": c["complexity"]["reason"],
                                                  "source": V1_SOURCE}
    if "max_estimated_cost_usd" in c:
        out["max_estimated_cost_usd"] = c["max_estimated_cost_usd"]
    for pid, p in c["profiles"].items():
        m = dict(p["signals"])  # 등록 id와 같은 이름의 signal은 등록 규칙으로 검증된다
        for old, new in (("estimated_input_tokens", "tokens.estimated_input"),
                         ("estimated_output_tokens", "tokens.estimated_output"),
                         ("required_context_tokens", "tokens.required_context")):
            if old in p:
                m[new] = {"value": p[old], "unit": "tokens", "source": V1_SOURCE}
        if "price" in p:
            for d in ("input", "output"):
                m[f"price.{d}_usd_per_mtok"] = {"value": p["price"][f"{d}_usd_per_million_tokens"], "unit": "usd/mtok",
                                                "source": p["price"]["source"], "observed_at": p["price"]["as_of"]}
        out["profiles"][pid] = {"metrics": m}
    return out


def _validate_context_v1(raw, profile_ids):
    if not isinstance(raw, dict) or set(raw) - {"schema_version", "complexity", "max_estimated_cost_usd", "profiles"}:
        raise InputError("context: object with known fields required")
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise InputError(f"context.schema_version must be {SCHEMA_VERSION!r}")
    out = {"schema_version": SCHEMA_VERSION, "profiles": {}}
    if "complexity" in raw:
        item = raw["complexity"]
        if not isinstance(item, dict) or set(item) != {"level", "reason"} or item["level"] not in TIERS:
            raise InputError("context.complexity: level low|medium|high and reason required")
        out["complexity"] = {"level": item["level"], "reason": _str(item["reason"], "context.complexity.reason", 4000)}
    if "max_estimated_cost_usd" in raw:
        out["max_estimated_cost_usd"] = _num(raw["max_estimated_cost_usd"], "context.max_estimated_cost_usd", 0)
    profiles = raw.get("profiles", {})
    if not isinstance(profiles, dict) or set(profiles) - set(profile_ids):
        raise InputError("context.profiles: object with configured profile ids required")
    for pid, item in profiles.items():
        if not isinstance(item, dict) or set(item) - {"estimated_input_tokens", "estimated_output_tokens", "required_context_tokens", "price", "signals"}:
            raise InputError(f"context.profiles.{pid}: unknown fields")
        p = {}
        for key in ("estimated_input_tokens", "estimated_output_tokens", "required_context_tokens"):
            if key in item:
                p[key] = _int(item[key], f"context.profiles.{pid}.{key}", 0, 1_000_000_000_000)
        if "price" in item:
            price = item["price"]
            keys = {"input_usd_per_million_tokens", "output_usd_per_million_tokens", "source", "as_of"}
            if not isinstance(price, dict) or set(price) != keys:
                raise InputError(f"context.profiles.{pid}.price: {sorted(keys)} required")
            p["price"] = {key: _num(price[key], f"context.profiles.{pid}.price.{key}", 0, 1_000_000_000)
                          for key in ("input_usd_per_million_tokens", "output_usd_per_million_tokens")}
            p["price"]["source"] = _str(price["source"], f"context.profiles.{pid}.price.source", 500)
            _parse_time(price["as_of"], f"context.profiles.{pid}.price.as_of")
            p["price"]["as_of"] = price["as_of"]
        signals = item.get("signals", {})
        if not isinstance(signals, dict):
            raise InputError(f"context.profiles.{pid}.signals: object required")
        p["signals"] = {}
        for name, signal in signals.items():
            if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*", name):
                raise InputError(f"context.profiles.{pid}.signals: namespaced name required")
            if not isinstance(signal, dict) or set(signal) != {"value", "unit", "source"}:
                raise InputError(f"context.profiles.{pid}.signals.{name}: value, unit, source required")
            p["signals"][name] = {"value": _num(signal["value"], f"context.profiles.{pid}.signals.{name}.value"),
                                  "unit": _str(signal["unit"], f"context.profiles.{pid}.signals.{name}.unit", 100),
                                  "source": _str(signal["source"], f"context.profiles.{pid}.signals.{name}.source", 500)}
        out["profiles"][pid] = p
    return out


def metric_facts(metrics, now):
    """지표 + freshness(fresh|expired|missing). 수명은 지표마다 다르며, expires_at이 더 이르면 그쪽을 따른다."""
    out = {}
    for mid, m in metrics.items():
        f = dict(m)
        if m["status"] == "missing":
            f["freshness"] = "missing"
        else:
            expired = "expires_at" in m and now >= _parse_time(m["expires_at"], mid)
            if "observed_at" in m:
                age = (now - _parse_time(m["observed_at"], mid)).total_seconds() / 3600
                f["age_hours"] = round(age, 2)
                max_age = METRICS[mid][3] if mid in METRICS else None
                expired = expired or (max_age is not None and age > max_age)
            f["freshness"] = "expired" if expired else "fresh"
        out[mid] = f
    return out


def context_facts(profile, context, now):
    """(정확한 Decimal 비용 | None, 1.0 출력용 facts, 지표+freshness). 제약 판단은 CONSTRAINTS가 한다.
    결측·만료 값은 계산에 쓰지 않는다(0이 아니다)."""
    raw = context["profiles"].get(profile["id"], {}).get("metrics", {})
    metrics = metric_facts(raw, now)
    usable = {k: m["value"] for k, m in metrics.items() if k in METRICS and m["freshness"] == "fresh"}
    cost, missing = None, None
    if "cost.estimated_usd" in usable:  # Orchestrator 견적(캐시·부가 비용 포함 가능)이 계산보다 우선
        cost = Decimal(str(usable["cost.estimated_usd"]))
    elif all(k in usable for k in COST_INPUTS):  # ponytail: 입출력 2요율 식 1개. 그 이상은 견적으로 받는다
        cost = (Decimal(usable["tokens.estimated_input"]) * Decimal(str(usable["price.input_usd_per_mtok"]))
                + Decimal(usable["tokens.estimated_output"]) * Decimal(str(usable["price.output_usd_per_mtok"]))) / 1_000_000
    else:
        missing = ("price_expired" if any(metrics.get(k, {}).get("freshness") == "expired" for k in COST_INPUTS)
                   else "estimate_or_price_missing")
    if "cost.estimated_usd" not in usable and (cost is not None or "cost.estimated_usd" not in metrics):
        metrics["cost.estimated_usd"] = (
            {"value": float(cost), "unit": "usd", "source": ROUTER_COST_SOURCE, "status": "ok", "freshness": "fresh"}
            if cost is not None else
            {"status": "missing", "reason": missing, "source": ROUTER_COST_SOURCE, "freshness": "missing"})
    pin, pout = raw.get("price.input_usd_per_mtok", {}), raw.get("price.output_usd_per_mtok", {})
    price = ({"input_usd_per_million_tokens": pin["value"], "output_usd_per_million_tokens": pout["value"],
              "source": pin["source"], "as_of": pin.get("observed_at")} if "value" in pin and "value" in pout else None)
    facts = {"estimated_cost_usd": float(cost) if cost is not None else None,
             "cost_missing_reason": missing, "required_context_tokens": usable.get("tokens.required_context", 0),
             "estimated_input_tokens": usable.get("tokens.estimated_input"),
             "estimated_output_tokens": usable.get("tokens.estimated_output"),
             "price": price, "signals": {k: m for k, m in raw.items() if k not in METRICS}}
    return cost, facts, metrics


def validate_task(raw):
    if not isinstance(raw, dict):
        raise InputError("task: JSON object required")
    unknown = set(raw) - set(TASK_REQUIRED) - set(TASK_OPTIONAL)
    if unknown:
        raise InputError(f"task: unknown fields {sorted(unknown)}")
    missing = [k for k in TASK_REQUIRED if k not in raw]
    if missing:
        raise InputError(f"task: missing fields {missing}")
    if raw["schema_version"] != SCHEMA_VERSION:
        raise InputError(f"task.schema_version must be {SCHEMA_VERSION!r}")
    if not isinstance(raw["task_id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", raw["task_id"]):
        raise InputError("task.task_id: [A-Za-z0-9][A-Za-z0-9_-]{0,63} required")
    t = {"task_id": raw["task_id"], "round": _int(raw["round"], "task.round", 1),
         "summary": _str(raw["summary"], "task.summary", 4000), "prompt": _str(raw["prompt"], "task.prompt")}
    if len(t["prompt"].encode("utf-8")) > 256 * 1024:
        raise InputError("task.prompt: larger than 256 KiB")

    cwd = _str(raw["cwd"], "task.cwd")
    if not os.path.isabs(cwd) or not os.path.isdir(cwd):
        raise InputError("task.cwd: existing absolute directory required")
    t["cwd"] = os.path.realpath(cwd)

    t["context_files"] = _str_list(raw.get("context_files", []), "task.context_files")
    for f in t["context_files"]:
        real = os.path.realpath(os.path.join(t["cwd"], f))
        try:
            inside = not os.path.isabs(f) and os.path.commonpath([t["cwd"], real]) == t["cwd"]
        except ValueError:  # 다른 드라이브(Windows)
            inside = False
        if not inside:
            raise InputError(f"task.context_files: path escapes cwd: {f}")

    cons = raw.get("constraints", {})
    if not isinstance(cons, dict):
        raise InputError("task.constraints: object required")
    unknown = set(cons) - set(CONSTRAINT_DEFAULTS)
    if unknown:
        raise InputError(f"task.constraints: unknown fields {sorted(unknown)}")
    c = {**CONSTRAINT_DEFAULTS, **cons}
    if c["max_cost_tier"] not in TIERS:
        raise InputError("task.constraints.max_cost_tier: low|medium|high")
    _int(c["min_context_tokens"], "task.constraints.min_context_tokens", 0)
    _bool(c["local_only"], "task.constraints.local_only")
    _int(c["timeout_ms"], "task.constraints.timeout_ms", 1000, 3_600_000)
    _str_list(c["required_capabilities"], "task.constraints.required_capabilities")
    t["constraints"] = c

    t["priority"] = raw.get("priority", "balanced")
    if t["priority"] not in PRIORITIES:
        raise InputError("task.priority: quality|balanced|cost")
    t["exclude_profiles"] = _str_list(raw.get("exclude_profiles", []), "task.exclude_profiles")
    t["execution"] = raw.get("execution", "interactive")  # board agent, or a one-shot CLI run in a herdr pane
    if t["execution"] not in EXECUTIONS:
        raise InputError("task.execution: " + "|".join(EXECUTIONS))
    facets = raw.get("facets", {})  # Orchestrator가 직접 태그한 {axis: [values]}. 어휘 검증은 index가 있는 evidence에서
    if not isinstance(facets, dict):
        raise InputError("task.facets: object {axis: [values]} required")
    t["facets"] = {a: _str_list(v, f"task.facets.{a}") for a, v in facets.items()}
    return t


def semantic_task_hash(t):
    keys = ("prompt", "summary", "constraints", "priority", "cwd", "context_files", "exclude_profiles")
    extra = {"execution": t["execution"]} if t.get("execution", "interactive") != "interactive" else {}  # keeps old hashes
    return canonical_hash({**{k: t[k] for k in keys}, **extra})


# ---------- 설정 ----------

PROFILE_KEYS = ("id", "enabled", "kind", "executable", "args", "model_id", "harness_id", "reasoning_effort",
                "config_revision", "cost_tier", "inference_local", "context_tokens", "capabilities")


def _load_toml(path):
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        raise InputError(f"config not found: {path}")
    except tomllib.TOMLDecodeError as e:
        raise InputError(f"{path}: invalid TOML ({e})")


def load_profiles(path):
    cfg = _load_toml(path)
    unknown = set(cfg) - {"schema_version", "default_profile", "fallback_order", "profile"}
    if unknown:
        raise InputError(f"profiles: unknown keys {sorted(unknown)}")
    if cfg.get("schema_version") != SCHEMA_VERSION:
        raise InputError(f"profiles.schema_version must be {SCHEMA_VERSION!r}")
    profiles = cfg.get("profile", [])
    if not isinstance(profiles, list):
        raise InputError("profiles: [[profile]] array required")
    ids = set()
    for p in profiles:
        if set(p) != set(PROFILE_KEYS):
            raise InputError(f"profile {p.get('id')!r}: keys must be exactly {list(PROFILE_KEYS)}")
        if not isinstance(p["id"], str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,47}", p["id"]) or p["id"] in ids:
            raise InputError(f"profile id invalid or duplicate: {p['id']!r}")
        ids.add(p["id"])
        for k in ("kind", "executable", "model_id", "harness_id", "reasoning_effort", "config_revision"):
            _str(p[k], f"profile {p['id']}.{k}")
        if not isinstance(p["args"], list) or not all(isinstance(a, str) for a in p["args"]):
            raise InputError(f"profile {p['id']}.args: array of strings (argv) required")
        _bool(p["enabled"], f"profile {p['id']}.enabled")
        _bool(p["inference_local"], f"profile {p['id']}.inference_local")
        _int(p["context_tokens"], f"profile {p['id']}.context_tokens", 0)
        _str_list(p["capabilities"], f"profile {p['id']}.capabilities")
        if p["cost_tier"] not in TIERS:
            raise InputError(f"profile {p['id']}.cost_tier: low|medium|high")
    default = cfg.get("default_profile")
    fallback = _str_list(cfg.get("fallback_order", []), "profiles.fallback_order")
    for ref in ([default] if default is not None else []) + fallback:
        if ref not in ids:
            raise InputError(f"profiles: unknown profile reference {ref!r}")
    return {"schema_version": SCHEMA_VERSION, "default_profile": default, "fallback_order": fallback,
            "profile": profiles}


def load_categories(path):
    mapping = _load_toml(path).get("mapping")
    if not isinstance(mapping, dict) or set(mapping) != set(CATEGORIES):
        raise InputError(f"categories: [mapping.*] must cover exactly {list(CATEGORIES)}")
    for c, ev in mapping.items():
        if not isinstance(ev, dict) or not ev:
            raise InputError(f"categories.{c}: evidence weights required")
        for b, v in ev.items():
            _num(v, f"categories.{c}.{b}", lo=0)
        if abs(sum(ev.values()) - 1) > 1e-6:
            raise InputError(f"categories.{c}: weights must sum to 1")
    return mapping


def config_hash(cfg, mapping):
    return canonical_hash({"profiles": cfg, "categories": mapping})


def profile_fingerprint(p):
    # ponytail: CLI 버전 미포함("unknown") — dry-run은 프로세스를 띄우지 않는다.
    # P2에서 --version probe를 넣으면 refresh의 snapshot fingerprint도 같은 입력으로 계산해야 한다.
    keys = ("kind", "executable", "args", "model_id", "harness_id", "reasoning_effort", "config_revision")
    return canonical_hash({**{k: p[k] for k in keys}, "cli_version": "unknown"})


# ---------- snapshot ----------

SNAPSHOT_KEYS = ("schema_version", "snapshot_id", "generated_at", "policy_version", "config_hash",
                 "sources", "cohorts", "profiles")
SNAPSHOT_MAX_BYTES = 64 * 1024 * 1024


def snapshot_hash(snap):
    """snapshot_id = snapshot_id 필드를 뺀 canonical JSON의 SHA-256."""
    return canonical_hash({k: v for k, v in snap.items() if k != "snapshot_id"})


def validate_snapshot(s):
    if not isinstance(s, dict) or s.get("schema_version") != SCHEMA_VERSION:
        raise InputError("snapshot: unsupported schema_version")
    missing = [k for k in SNAPSHOT_KEYS if k not in s]
    if missing:
        raise InputError(f"snapshot: missing {missing}")
    if s["snapshot_id"] != snapshot_hash(s):
        raise InputError("snapshot: snapshot_id does not match content hash")
    for sid, src in s["sources"].items():
        _parse_time(src.get("last_success_at"), f"snapshot.sources.{sid}.last_success_at")
        _num(src.get("ttl_hours"), f"snapshot.sources.{sid}.ttl_hours", lo=0)
        _num(src.get("max_stale_hours"), f"snapshot.sources.{sid}.max_stale_hours", lo=0)
    for pid, sp in s["profiles"].items():
        _str(sp.get("fingerprint"), f"snapshot.profiles.{pid}.fingerprint")
        for eid, ev in sp.get("evidence", {}).items():
            name = f"snapshot.profiles.{pid}.evidence.{eid}"
            if ev.get("normalized") is not None:
                _num(ev["normalized"], f"{name}.normalized", 0, 1)
            if ev.get("scope") not in SCOPES:
                raise InputError(f"{name}.scope: {SCOPES}")
            conditions = ev.get("conditions")
            if conditions is not None and not isinstance(conditions, dict):
                raise InputError(f"{name}.conditions: object required")
            if ev["scope"] == "exact_profile" and conditions is not None:
                for key in ("suite", "version", "subset", "metric", "direction", "variant", "dataset_revision",
                            "evaluation_harness", "aggregation", "scoring_version", "agent_scaffold",
                            "reasoning_effort"):
                    _str(conditions.get(key), f"{name}.conditions.{key}")
            if ev.get("source_id") not in s["sources"]:
                raise InputError(f"{name}.source_id: unknown source")
    return s


def load_snapshot(cache_dir):
    """현재 snapshot → last-good 순으로 읽는다. 둘 다 실패하면 None (네트워크 호출 없음)."""
    warnings = []
    for name in ("snapshot.json", "snapshot.last-good.json"):
        try:
            snap = validate_snapshot(load_json_strict(Path(cache_dir) / name, SNAPSHOT_MAX_BYTES))
        except InputError as e:
            warnings.append(warn("snapshot_unusable", f"{name}: {e}"))
            continue
        if name != "snapshot.json":
            warnings.append(warn("snapshot_last_good", "using last-good snapshot"))
        return snap, warnings
    return None, warnings


def source_status(snap, now):
    out = {}
    for sid, src in sorted(snap["sources"].items()):
        age_h = (now - _parse_time(src["last_success_at"], sid)).total_seconds() / 3600
        out[sid] = {"last_success_at": src["last_success_at"], "age_hours": round(age_h, 2),
                    "published_at": src.get("published_at"), "attribution": src.get("attribution"),
                    "stale": age_h > src["ttl_hours"], "excluded": age_h > src["max_stale_hours"]}
    return out


# ---------- 분류 ----------

def _kw_match(kw, text):
    if kw.isascii():  # 영문은 단어 경계, 한글은 조사가 붙으므로 부분 문자열
        return re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", text, re.I) is not None
    return kw in text


def classify(t):
    base = {"classifier_version": CLASSIFIER_VERSION}
    hits = {}
    for cat, (kws, exts) in L1_RULES.items():
        m = [f"{cat}:kw:{k}" for k in kws if _kw_match(k, t["summary"])]
        m += [f"{cat}:ext:{e}" for e in exts if any(f.lower().endswith(e) for f in t["context_files"])]
        if m:
            hits[cat] = m
    matched = sorted(r for rules in hits.values() for r in rules)
    if len(hits) == 1 and len(matched) >= 2:
        return {"stage": "L1", "categories": {next(iter(hits)): 1.0}, "matched_rules": matched,
                "fallback_reason": None, **base}
    reason = "no_rule_match" if not hits else "rule_conflict" if len(hits) > 1 else "weak_signal"
    return {"stage": "fallback", "categories": {"general": 1.0}, "matched_rules": matched,
            "fallback_reason": reason, **base}


# ---------- 점수 ----------

def percentile_ranks(values, higher_is_better=True):
    """{key: raw} → {key: (평균 rank-1)/(N-1)}; 최악 0, 최고 1, N=1이면 0.5. refresh 정규화용."""
    n = len(values)
    if n == 1:
        return {k: 0.5 for k in values}
    order = sorted(values.items(), key=lambda kv: kv[1] if higher_is_better else -kv[1])
    out, i = {}, 0
    while i < n:
        j = i
        while j + 1 < n and order[j + 1][1] == order[i][1]:
            j += 1
        for k in range(i, j + 1):
            out[order[k][0]] = ((i + j) / 2) / (n - 1)
        i = j + 1
    return out


def evidence_weights(categories, mapping):
    """a_b = Σ_c w_c × v_cb."""
    a = {}
    for c, w in categories.items():
        for b, v in mapping[c].items():
            a[b] = a.get(b, 0.0) + w * v
    return {b: x for b, x in sorted(a.items()) if x > 0}


def coverage_quality(a, normalized):
    """(C, Q). 관측 없음이면 Q=None. 측정된 0은 coverage에 포함."""
    obs = [b for b in a if normalized.get(b) is not None]
    c = sum(a[b] for b in obs)
    if c <= EPS:
        return 0.0, None
    q_obs = sum(a[b] * normalized[b] for b in obs) / c
    return c, c * q_obs + (1 - c) * POLICY["missing_prior"] - POLICY["missing_penalty"] * (1 - c)


def coverage_band(c):
    return "sufficient" if c >= 0.8 - EPS else "partial" if c >= 0.5 - EPS else "insufficient"


def legacy_score(c, priority):
    """legacy 자동 선택 점수 = quality − λ·cost tier proxy. coverage 문턱 미달이면 None. 종합 점수가 아니다."""
    c["cost_proxy"] = POLICY["tier_proxy"][c["cost_tier"]]
    ranked = c["quality"] is not None and c["coverage"] >= POLICY["coverage_threshold"] - EPS
    c["score"] = c["quality"] - POLICY["lambda_cost"][priority] * c["cost_proxy"] if ranked else None


def select(cands, priority, default, fallback_order):
    """cands: 제약 통과 후보 [{profile, cost_tier, coverage, quality}]. score를 채우고 (선택 id, mode)."""
    for c in cands:
        legacy_score(c, priority)
    ranked = [c for c in cands if c["score"] is not None]
    if ranked:
        top = max(c["score"] for c in ranked)
        if priority == "quality":  # 비용으로 near-tie를 뒤집지 않음
            pool = [c for c in ranked if top - c["score"] <= EPS]
            return min(pool, key=lambda c: c["profile"])["profile"], "benchmark_score"
        pool = [c for c in ranked if top - c["score"] < POLICY["near_tie_epsilon"] - EPS]
        return min(pool, key=lambda c: (TIERS[c["cost_tier"]], c["profile"]))["profile"], "benchmark_score"
    eligible = {c["profile"] for c in cands}
    if default in eligible:
        return default, "default_insufficient_evidence"
    for pid in fallback_order:
        if pid in eligible:
            return pid, "fallback_insufficient_evidence"
    return None, "none"


def _check(passed, code, metric=None, observed=None, limit=None, **kw):
    """제약 결과 1개. code는 실패 시에만 채운다(1.0 탈락 사유 문자열과 동일)."""
    return [{"passed": passed, "code": None if passed else code, "metric": metric,
             "observed": observed, "limit": limit, **kw}]


def _context_capacity(p, t, x):
    # task 최소 요구와 context의 필요 토큰 중 큰 쪽이 기준. 용량 미설정(0)은 결측 → 제외.
    reqs = [(t["constraints"]["min_context_tokens"], "min_context_tokens"),
            ((x["facts"] or {}).get("required_context_tokens", 0), "tokens.required_context")]
    required, metric = max(reqs, key=lambda r: r[0])
    if not required:
        return []
    cap = p["context_tokens"]
    return _check(cap >= required, "context_unknown" if cap == 0 else "context_insufficient",
                  metric, cap, required, on_missing="exclude")


def _estimated_cost(p, t, x):
    cap = x["context"].get("max_estimated_cost_usd") if x["context"] else None
    if cap is None:
        return []
    if x["cost"] is None:  # 결측은 0이 아니다: 상한이 있으면 제외
        return _check(False, "estimated_cost_unknown", "cost.estimated_usd", None, cap, on_missing="exclude")
    return _check(x["cost"] <= Decimal(str(cap)), "estimated_cost_exceeds_max", "cost.estimated_usd",
                  float(x["cost"]), cap, on_missing="exclude")


def _capabilities(p, t, x):
    need = sorted(set(t["constraints"]["required_capabilities"]))
    missing = [c for c in need if c not in p["capabilities"]]
    if not need:
        return []
    if not missing:
        return _check(True, None, "capabilities", sorted(p["capabilities"]), need)
    return [r for c in missing for r in _check(False, f"missing_capability:{c}", "capabilities", None, c)]


# 필수 제약. 이름 → (profile, task, x) -> 결과 목록([] = 적용 안 됨). x = {context, facts, cost, metrics, availability}.
# 실패는 어떤 점수로도 상쇄되지 않는다. 새 지표로 거르려면 여기에 함수 하나를 추가한다.
# dict 순서 = 탈락 사유 출력 순서(route 1.0 호환).
CONSTRAINTS = {
    "enabled": lambda p, t, x: _check(p["enabled"], "disabled", "enabled", p["enabled"], True),
    "task_exclusion": lambda p, t, x: _check(p["id"] not in t["exclude_profiles"], "excluded_by_task",
                                             "exclude_profiles", p["id"], t["exclude_profiles"])
    if t["exclude_profiles"] else [],
    "cost_tier": lambda p, t, x: _check(TIERS[p["cost_tier"]] <= TIERS[t["constraints"]["max_cost_tier"]],
                                        "cost_tier_exceeds_max", "cost_tier", p["cost_tier"],
                                        t["constraints"]["max_cost_tier"]),
    "context_capacity": _context_capacity,
    "capabilities": _capabilities,
    "local_only": lambda p, t, x: _check(p["inference_local"], "not_local_inference", "inference_local",
                                         p["inference_local"], True) if t["constraints"]["local_only"] else [],
    "estimated_cost": _estimated_cost,
    "availability": lambda p, t, x: [] if not x["live"] else _check(not x["availability"], x["availability"],
                                                                      "availability", x["availability"], None),
}


EVIDENCE_FIELDS = ("raw", "normalized", "scope", "cohort_id", "metric_version", "conditions", "source_id", "source_revision",
                   "fetched_at", "published_at", "evaluated_at")


def benchmark_evaluation(p, fp, a, snap, sources, warnings, priority):
    """benchmark 평가기. coverage는 benchmark 근거 충족도일 뿐, 전체 판단 정보의 충족도가 아니다.
    legacy_score는 기존 자동 선택 정책의 점수이며 종합 순위가 아니다."""
    sp = snap["profiles"].get(p["id"]) if snap else None
    stale_cfg = sp is not None and sp["fingerprint"] != fp
    if stale_cfg:
        warnings.append(warn("stale_config", f"{p['id']}: profile config changed since snapshot; evidence ignored"))
    rows, normalized = [], {}
    for b, w in a.items():
        e = sp.get("evidence", {}).get(b) if sp and not stale_cfg else None
        reason = ("no_snapshot" if snap is None else "profile_not_in_snapshot" if sp is None
                  else "stale_config" if stale_cfg else "no_observation" if e is None
                  else "null_value" if e.get("normalized") is None
                  else "missing_conditions" if e.get("scope") == "exact_profile" and not e.get("conditions")
                  else "max_stale_exceeded" if sources[e["source_id"]]["excluded"] else None)
        normalized[b] = None if reason else e["normalized"]
        row = {"id": b, "weight": round(w, 6), **{k: (e or {}).get(k) for k in EVIDENCE_FIELDS}}
        row["stale"] = bool(e and sources[e["source_id"]]["stale"])
        row["missing_reason"] = reason
        rows.append(row)
    cov, q = coverage_quality(a, normalized)
    exact = sum(a[b] for b in a if normalized[b] is not None and sp["evidence"][b]["scope"] == "exact_profile")
    ev = {"coverage": cov, "quality": q, "exact_evidence_weight": exact, "evidence": rows, "cost_tier": p["cost_tier"]}
    legacy_score(ev, priority)
    ev["status"] = ("unavailable" if q is None else "ok" if cov >= POLICY["coverage_threshold"] - EPS
                    else "insufficient")
    del ev["cost_tier"]
    return ev


def assess(t, cfg, mapping, snap, snap_warnings, now, availability=None, context=None, *, benchmarks=True):
    """후보 평가 공통 경계: 사실 수집 → 필수 제약 → 평가기. 선택하지 않는다.
    candidates는 전 프로필(profile ID순). 평가기는 제약을 통과한 후보에만 돈다.
    availability=None이면 dry-run(미확인), live면 {profile_id: 제외 사유 또는 None}."""
    if context is not None:
        context = validate_context(context, [p["id"] for p in cfg["profile"]])
    warnings = list(snap_warnings)
    cls = classify(t)
    if cls["stage"] == "fallback":
        warnings.append(warn("classification_fallback", f"general fallback: {cls['fallback_reason']}"))
    a = evidence_weights(cls["categories"], mapping)

    sources = source_status(snap, now) if snap else {}
    for sid, s in sources.items():
        if s["excluded"]:
            warnings.append(warn("source_too_stale", f"older than max_stale; observations excluded", sid))
        elif s["stale"]:
            warnings.append(warn("source_stale", "older than TTL; using last-good", sid))

    cands = []
    for p in sorted(cfg["profile"], key=lambda p: p["id"]):
        cost, facts, metrics = context_facts(p, context, now) if context is not None else (None, None, {})
        x = {"context": context, "facts": facts, "cost": cost, "metrics": metrics, "live": availability is not None,
             "availability": availability.get(p["id"]) if availability is not None else None}
        results = [dict(f, constraint=name) for name, check in CONSTRAINTS.items() for f in check(p, t, x)]
        c = {"profile": p["id"], "profile_fingerprint": profile_fingerprint(p), "cost_tier": p["cost_tier"],
             "eligible": all(f["passed"] for f in results), "constraints": results, "context_facts": facts,
             "metrics": metrics, "evaluations": {}}
        if c["eligible"] and benchmarks:
            # ponytail: 평가기 1개라 직접 호출. 두 번째가 생기면 evaluations에 키 하나 추가.
            c["evaluations"]["benchmark"] = benchmark_evaluation(p, c["profile_fingerprint"], a, snap, sources,
                                                                 warnings, t["priority"])
        cands.append(c)
    return {"task": t, "classification": cls, "candidates": cands, "warnings": warnings, "sources": sources,
            "context": context, "availability_verified": availability is not None,
            "snapshot_id": snap["snapshot_id"] if snap else None, "config_hash": config_hash(cfg, mapping),
            "task_hash": semantic_task_hash(t),
            "task_metrics": metric_facts(context["task_metrics"], now) if context is not None else {}}


def _inputs(asmt):
    """판단의 정적 입력. now·availability·freshness처럼 시간·환경에 따라 변하는 값은 넣지 않는다
    (그건 실행 직전 재검사 대상이지 동일성 비교 대상이 아니다)."""
    context = asmt["context"]
    return {"task_hash": asmt["task_hash"], "config_hash": asmt["config_hash"], "snapshot_id": asmt["snapshot_id"],
            "context_hash": canonical_hash(context) if context is not None else None,
            "router_policy_version": POLICY_VERSION, "metric_registry_version": METRIC_REGISTRY_VERSION}


def _complexity_v1(context):
    m = context["task_metrics"].get("task.complexity", {})
    return {"level": m["value"], "reason": m.get("reason")} if "value" in m else None


def _legacy_cands(asmt):
    """select()가 읽는 1.0 후보 형태. benchmark 결과를 그대로 펼친다."""
    return [{"profile": c["profile"], "profile_fingerprint": c["profile_fingerprint"], "cost_tier": c["cost_tier"],
              "context_facts": c["context_facts"], **c["evaluations"].get("benchmark", {
                  "quality": None, "coverage": 0, "exact_evidence_weight": 0,
                  "score": None, "cost_proxy": None, "evidence": []})}
            for c in asmt["candidates"] if c["eligible"]]


def _result_v1(asmt, cands, status, selected, mode, warnings):
    """route/evaluate 1.0 출력. score는 legacy 정책(select) 점수이며 종합 순위가 아니다."""
    context = asmt["context"]
    cands = sorted(cands, key=lambda c: (c["score"] is None, -(c["score"] or 0), c["profile"]))
    out_cands = [{"profile": c["profile"], "score": _r(c["score"]), "quality": _r(c["quality"]),
                  "coverage": _r(c["coverage"]), "coverage_band": coverage_band(c["coverage"]),
                  "exact_evidence_weight": _r(c["exact_evidence_weight"]), "cost_proxy": c["cost_proxy"],
                  "evidence": c["evidence"], "availability_verified": asmt["availability_verified"],
                  **({"context_facts": c["context_facts"]} if context is not None else {})} for c in cands]
    t = asmt["task"]
    return {"schema_version": SCHEMA_VERSION, "status": status,
            "task_id": t["task_id"], "round": t["round"], "run_id": None, "selected": selected,
            "selection_mode": mode, "classification": asmt["classification"], "candidates": out_cands,
            "excluded": [{"profile": c["profile"], "reasons": [f["code"] for f in c["constraints"] if not f["passed"]]}
                         for c in asmt["candidates"] if not c["eligible"]],
            "snapshot_id": asmt["snapshot_id"], "policy_version": POLICY_VERSION,
            "config_hash": asmt["config_hash"], "task_hash": asmt["task_hash"],
            "warnings": warnings, "sources": asmt["sources"],
            "assessment_digest": canonical_hash(_inputs(asmt)),
            **({"decision_context": context, "context_hash": canonical_hash(context), "complexity": _complexity_v1(context),
                "max_estimated_cost_usd": context.get("max_estimated_cost_usd")} if context is not None else {})}


def route_legacy(t, cfg, mapping, snap, snap_warnings, now, availability=None, context=None):
    """legacy 자동 선택 = assess + select. 같은 task/config/snapshot/availability/now면 결과가 동일하다."""
    asmt = assess(t, cfg, mapping, snap, snap_warnings, now, availability, context)
    cands = _legacy_cands(asmt)
    pick, mode = select(cands, t["priority"], cfg["default_profile"], cfg["fallback_order"])
    warnings, selected = list(asmt["warnings"]), None
    if pick:
        chosen = next(c for c in cands if c["profile"] == pick)
        selected = {"profile": pick, "profile_fingerprint": chosen["profile_fingerprint"],
                    "agent_name": None, "pane_id": None}
        if availability is None:
            warnings.append(warn("availability_unverified", "dry-run: CLI/auth readiness not probed"))
        else:
            warnings.append(warn("availability_checked", "live preflight passed; provider may still reject execution"))
        if mode != "benchmark_score":
            warnings.append(warn("insufficient_evidence", f"no candidate with coverage >= "
                                 f"{POLICY['coverage_threshold']}; {mode}, not a benchmark-optimal choice"))
        elif coverage_band(chosen["coverage"]) == "partial":
            warnings.append(warn("partial_evidence", f"{pick}: coverage {chosen['coverage']:.2f}"))
        if chosen["coverage"] > 0 and chosen["exact_evidence_weight"] <= EPS:
            warnings.append(warn("proxy_only", f"{pick}: model-proxy evidence only, no exact profile evaluation"))
    return {**_result_v1(asmt, cands, "selected" if pick else "no_eligible_profile", selected, mode, warnings),
            "selection": {"source": "router_legacy"}}


def route(t, cfg, mapping, snap, snap_warnings, now, availability=None, context=None,
          *, policy="vendor-guided", host=None, response=None, selection=None, index=None,
          allow_network=False, env=None, check_digest=True, omit_profiles=(), decision_cache=None):
    """Default: vendor-guided decision packet/validated choice. Legacy requires explicit opt-in."""
    if policy == "legacy":
        if response is not None or selection is not None:
            raise InputError("legacy policy does not accept a decision response or vendor selection")
        return route_legacy(t, cfg, mapping, snap, snap_warnings, now, availability, context)
    if policy != "vendor-guided":
        raise InputError("policy: vendor-guided|legacy required")
    from . import decision
    return decision.route(t, cfg, mapping, snap, snap_warnings, now, availability, context,
                          host=host, response=response, selection=selection, index=index,
                          allow_network=allow_network, env=env, check_digest=check_digest,
                          omit_profiles=omit_profiles, decision_cache=decision_cache)


def evaluate_v1(t, cfg, mapping, snap, snap_warnings, now, availability=None, context=None):
    """1.0 형식의 선택 없는 후보 목록. route --profile 경로와 `evaluate --format 1`이 쓴다."""
    asmt = assess(t, cfg, mapping, snap, snap_warnings, now, availability, context)
    return _result_v1(asmt, _legacy_cands(asmt), "ok", None, "orchestrator_choice", asmt["warnings"])


def evaluate(t, cfg, mapping, snap, snap_warnings, now, availability=None, context=None):
    """evaluate 2.0: 전 프로필의 사실·제약 결과·평가기 결과. 순위와 최종 선택은 Orchestrator 몫.
    candidates는 profile ID순이며 순서에 의미가 없다."""
    asmt = assess(t, cfg, mapping, snap, snap_warnings, now, availability, context)
    context = asmt["context"]
    cands = []
    for c in asmt["candidates"]:
        ev = c["evaluations"].get("benchmark")
        cands.append({"profile": c["profile"], "profile_fingerprint": c["profile_fingerprint"],
                      "eligible": c["eligible"], "constraints": c["constraints"],
                      "facts": {k: m for k, m in c["metrics"].items() if k in METRICS},
                      "unrecognized_metrics": {k: m for k, m in c["metrics"].items() if k not in METRICS},
                      "evaluations": {} if ev is None else {"benchmark": {
                          **{k: v for k, v in ev.items() if k != "score"},
                          "quality": _r(ev["quality"]), "coverage": _r(ev["coverage"]),
                          "coverage_band": coverage_band(ev["coverage"]),
                          "exact_evidence_weight": _r(ev["exact_evidence_weight"]),
                          "legacy_score": _r(ev["score"])}}})
    t = asmt["task"]
    return {"schema_version": EVALUATE_SCHEMA_VERSION, "status": "ok", "task_id": t["task_id"], "round": t["round"],
            "assessment_digest": canonical_hash(_inputs(asmt)), "inputs": _inputs(asmt),
            "task_facts": asmt["task_metrics"], "max_estimated_cost_usd": (context or {}).get("max_estimated_cost_usd"),
            "candidates": cands, "availability_verified": asmt["availability_verified"],
            "classification": asmt["classification"], "sources": asmt["sources"], "warnings": asmt["warnings"]}


def pin_selection(res, cfg, profile_id, mode="orchestrator_pinned"):
    p = next((p for p in cfg["profile"] if p["id"] == profile_id), None)
    if p is None or profile_id not in {c["profile"] for c in res["candidates"]}:
        return {**res, "status": "no_eligible_profile", "selected": None}
    return {**res, "status": "selected", "selection_mode": mode,
            "selected": {"profile": profile_id, "profile_fingerprint": profile_fingerprint(p),
                         "agent_name": None, "pane_id": None}}


SELECTION_KEYS = {"schema_version", "profile", "assessment_digest", "policy", "reason"}


def validate_selection(raw):
    """Orchestrator의 선택 기록: 무엇을(profile) 어떤 평가(assessment_digest)를 근거로 왜(policy, reason) 골랐나."""
    if isinstance(raw, dict) and raw.get("schema_version") == "3.0":
        from . import decision
        return decision.validate_selection(raw)
    if not isinstance(raw, dict) or set(raw) != SELECTION_KEYS:
        raise InputError(f"selection: exactly {sorted(SELECTION_KEYS)} required")
    if raw["schema_version"] != EVALUATE_SCHEMA_VERSION:
        raise InputError(f"selection.schema_version must be {EVALUATE_SCHEMA_VERSION!r}")
    if not isinstance(raw["assessment_digest"], str) or not re.fullmatch(r"[0-9a-f]{64}", raw["assessment_digest"]):
        raise InputError("selection.assessment_digest: digest from evaluate required")
    pol = raw["policy"]
    if not isinstance(pol, dict) or set(pol) != {"id", "version"}:
        raise InputError("selection.policy: id and version required")
    return {"schema_version": raw["schema_version"], "profile": _str(raw["profile"], "selection.profile", 200),
            "assessment_digest": raw["assessment_digest"],
            "policy": {"id": _str(pol["id"], "selection.policy.id", 200),
                       "version": _str(pol["version"], "selection.policy.version", 100)},
            "reason": _str(raw["reason"], "selection.reason", 4000)}


def apply_selection(res, cfg, profile_id, selection=None, mode="orchestrator_pinned", check_digest=True):
    """evaluate_v1 결과에 외부 선택을 적용한다. selection이 있으면 평가 당시 정적 입력과 지금이 같아야 한다.
    profile_id만 오면(기록 없는 고정) 실행은 하되 selection_unrecorded로 알린다.
    check_digest=False는 호출자가 이미 같은 판단 입력으로 digest를 검사한 경우만(parallel worker)."""
    if selection is not None:
        if selection.get("schema_version") == "3.0":
            from . import decision
            return decision.apply_record(res, cfg, selection, check_digest)
        if check_digest and selection["assessment_digest"] != res["assessment_digest"]:
            return {**res, "status": "stale_assessment", "selected": None,
                    "selection": {"source": "orchestrator", **selection},
                    "warnings": res["warnings"] + [warn("stale_assessment",
                        "task/config/snapshot/context changed since evaluate; re-evaluate and select again")]}
        out = pin_selection(res, cfg, selection["profile"], mode)
        return {**out, "selection": {"source": "orchestrator", **selection},
                "warnings": out["warnings"] + [warn("selection_legacy", "2.0 selection was not validated by vendor guidance")]}
    out = pin_selection(res, cfg, profile_id, mode)
    if mode == "orchestrator_pinned":
        out["warnings"] = out["warnings"] + [warn("selection_unrecorded",
                                                  "--profile without --selection: no policy/reason/digest recorded")]
    return {**out, "selection": {"source": "unrecorded" if mode == "orchestrator_pinned" else mode}}


def _r(x):
    return None if x is None else round(x, 6)
