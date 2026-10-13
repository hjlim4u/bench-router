"""bench-router v1 선택: 입력 검증 → 분류(L0/L1/general) → 제약 필터 → 점수 → 선택.

route 경로는 네트워크·herdr·파일 쓰기를 하지 않는다. 계산 정책은 03 문서, 계약은 04 문서.
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
from pathlib import Path

SCHEMA_VERSION = "1.0"
POLICY_VERSION = "1.0"
CLASSIFIER_VERSION = "l1-rules-1"
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
    "l0_min_confidence": 0.6,
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
TASK_OPTIONAL = ("context_files", "categories", "category_confidence", "constraints", "priority", "exclude_profiles")
CONSTRAINT_DEFAULTS = {"max_cost_tier": "high", "min_context_tokens": 0, "local_only": False,
                       "timeout_ms": 900000, "required_capabilities": []}
TASK_MAX_BYTES = 1024 * 1024


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

    cats = raw.get("categories")
    if cats is not None:
        if not isinstance(cats, dict) or not cats:
            raise InputError("task.categories: non-empty object required")
        for k, v in cats.items():
            if k not in CATEGORIES:
                raise InputError(f"task.categories: unknown category {k!r}")
            _num(v, f"task.categories.{k}", lo=0)
        if sum(cats.values()) <= 0:
            raise InputError("task.categories: sum must be > 0")
        if "category_confidence" not in raw:
            raise InputError("task.category_confidence: required when categories is present")
    t["categories"] = cats
    conf = raw.get("category_confidence")
    t["category_confidence"] = None if conf is None else _num(conf, "task.category_confidence", 0, 1)

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
    return t


def semantic_task_hash(t):
    keys = ("prompt", "summary", "constraints", "priority", "categories", "cwd", "context_files", "exclude_profiles")
    return canonical_hash({k: t[k] for k in keys})


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
    conf = t["category_confidence"]
    base = {"self_reported_confidence": conf, "classifier_version": CLASSIFIER_VERSION}
    if t["categories"] and conf >= POLICY["l0_min_confidence"]:
        total = sum(t["categories"].values())
        cats = {k: v / total for k, v in sorted(t["categories"].items()) if v > 0}
        return {"stage": "L0", "categories": cats, "matched_rules": [], "fallback_reason": None, **base}

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


def select(cands, priority, default, fallback_order):
    """cands: 제약 통과 후보 [{profile, cost_tier, coverage, quality}]. score를 채우고 (선택 id, mode)."""
    lam = POLICY["lambda_cost"][priority]
    for c in cands:
        c["cost_proxy"] = POLICY["tier_proxy"][c["cost_tier"]]
        ranked = c["quality"] is not None and c["coverage"] >= POLICY["coverage_threshold"] - EPS
        c["score"] = c["quality"] - lam * c["cost_proxy"] if ranked else None
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


def hard_filter(p, t):
    c, r = t["constraints"], []
    if not p["enabled"]:
        r.append("disabled")
    if p["id"] in t["exclude_profiles"]:
        r.append("excluded_by_task")
    if TIERS[p["cost_tier"]] > TIERS[c["max_cost_tier"]]:
        r.append("cost_tier_exceeds_max")
    if c["min_context_tokens"] > 0 and p["context_tokens"] < c["min_context_tokens"]:
        r.append("context_unknown" if p["context_tokens"] == 0 else "context_insufficient")
    r += [f"missing_capability:{x}" for x in sorted(set(c["required_capabilities"]) - set(p["capabilities"]))]
    if c["local_only"] and not p["inference_local"]:
        r.append("not_local_inference")
    return r


EVIDENCE_FIELDS = ("raw", "normalized", "scope", "cohort_id", "metric_version", "source_id", "source_revision",
                   "fetched_at", "published_at", "evaluated_at")


def route(t, cfg, mapping, snap, snap_warnings, now, availability=None):
    """프로필 선택. availability=None이면 dry-run(미확인), live면 {profile_id: 제외 사유 또는 None}.
    같은 task/config/snapshot/availability/now면 결과가 동일하다."""
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

    cands, excluded = [], []
    for p in sorted(cfg["profile"], key=lambda p: p["id"]):
        reasons = hard_filter(p, t)
        if availability is not None and availability.get(p["id"]):
            reasons.append(availability[p["id"]])
        if reasons:
            excluded.append({"profile": p["id"], "reasons": reasons})
            continue
        fp = profile_fingerprint(p)
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
                      else "max_stale_exceeded" if sources[e["source_id"]]["excluded"] else None)
            normalized[b] = None if reason else e["normalized"]
            row = {"id": b, "weight": round(w, 6), **{k: (e or {}).get(k) for k in EVIDENCE_FIELDS}}
            row["stale"] = bool(e and sources[e["source_id"]]["stale"])
            row["missing_reason"] = reason
            rows.append(row)
        cov, q = coverage_quality(a, normalized)
        exact = sum(a[b] for b in a if normalized[b] is not None
                    and sp["evidence"][b]["scope"] == "exact_profile")
        cands.append({"profile": p["id"], "profile_fingerprint": fp, "cost_tier": p["cost_tier"],
                      "coverage": cov, "quality": q, "exact_evidence_weight": exact, "evidence": rows})

    pick, mode = select(cands, t["priority"], cfg["default_profile"], cfg["fallback_order"])
    cands.sort(key=lambda c: (c["score"] is None, -(c["score"] or 0), c["profile"]))
    out_cands = []
    for c in cands:
        out_cands.append({"profile": c["profile"], "score": _r(c["score"]), "quality": _r(c["quality"]),
                          "coverage": _r(c["coverage"]), "coverage_band": coverage_band(c["coverage"]),
                          "exact_evidence_weight": _r(c["exact_evidence_weight"]), "cost_proxy": c["cost_proxy"],
                          "evidence": c["evidence"], "availability_verified": availability is not None})

    selected = None
    if pick:
        chosen = next(c for c in cands if c["profile"] == pick)
        selected = {"profile": pick, "profile_fingerprint": chosen["profile_fingerprint"],
                    "agent_name": None, "pane_id": None}
        if availability is None:
            warnings.append(warn("availability_unverified", "dry-run: CLI/auth readiness not probed"))
        else:
            warnings.append(warn("auth_unverified", "executable found; model access/login not probed"))
        if mode != "benchmark_score":
            warnings.append(warn("insufficient_evidence", f"no candidate with coverage >= "
                                 f"{POLICY['coverage_threshold']}; {mode}, not a benchmark-optimal choice"))
        elif coverage_band(chosen["coverage"]) == "partial":
            warnings.append(warn("partial_evidence", f"{pick}: coverage {chosen['coverage']:.2f}"))
        if chosen["coverage"] > 0 and chosen["exact_evidence_weight"] <= EPS:
            warnings.append(warn("proxy_only", f"{pick}: model-proxy evidence only, no exact profile evaluation"))

    return {"schema_version": SCHEMA_VERSION, "status": "selected" if pick else "no_eligible_profile",
            "task_id": t["task_id"], "round": t["round"], "run_id": None, "selected": selected,
            "selection_mode": mode, "classification": cls, "candidates": out_cands, "excluded": excluded,
            "snapshot_id": snap["snapshot_id"] if snap else None, "policy_version": POLICY_VERSION,
            "config_hash": config_hash(cfg, mapping),
            "task_hash": semantic_task_hash(t), "warnings": warnings, "sources": sources}


def _r(x):
    return None if x is None else round(x, 6)
