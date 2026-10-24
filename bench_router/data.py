"""bench-router 데이터 경로: source 수집·정규화(SQLite 이력) → routing snapshot 원자 게시.

refresh/import/status 전용. route는 이 모듈을 import하지 않는다(요청 경로 네트워크 0).
"""
import contextlib
import io
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from . import locking
from . import routing as r

ADAPTER_VERSION = "4"  # 3: arena rows carry the effort parsed from the model name; 4: AA rows too
DB_SCHEMA_VERSION = 2
HTTP_TIMEOUT_S = 30
HTTP_MAX_BYTES = 20 * 1024 * 1024
HTTP_RETRIES = 2  # 일시 장애만, 최초 1회 + 2회
SOURCE_MAX_SECONDS = 180  # 소스 1회 refresh의 전체 상한(요청·재시도·대기 포함). 넘으면 실패, last-good 유지
KEEP_PAYLOADS = 3
ARCHIVE_DAYS = 30

AA_URL = "https://artificialanalysis.ai/api/v2/language/models/free"
AA_KEY_ENV = "ARTIFICIAL_ANALYSIS_API_KEY"
AA_FIELDS = {"aa_intelligence": "artificial_analysis_intelligence_index",
             "aa_coding": "artificial_analysis_coding_index"}
ARENA_DATASET = "lmarena-ai/leaderboard-dataset"
ARENA_REVISION_URL = f"https://huggingface.co/api/datasets/{ARENA_DATASET}"
# evidence → (subset, category). text/document/vision은 style-control subset으로 고정; webdev는 그 subset만 존재.
ARENA_COHORTS = {"arena_text": ("text_style_control", "overall"),
                 "arena_text_math": ("text_style_control", "math"),
                 "arena_webdev": ("webdev", "overall"),
                 "arena_document": ("document_style_control", "overall"),
                 "arena_vision": ("vision_style_control", "overall")}
# 수동 import로만 들어오는 exact_profile evidence. suite/version이 다르면 거부(점수 혼합 금지).
MG_URL = "https://themodelgap.com/data"
EXACT_PINS = {"swe_verified_exact": {"source_id": "swe", "suite": "swe-bench", "version": "verified"},
              "terminal_exact": {"source_id": "tb", "suite": "terminal-bench", "version": "4.0"}}
EVIDENCE_IDS = sorted([*AA_FIELDS, *ARENA_COHORTS, *EXACT_PINS])

SOURCES = {
    "aa": {"url": AA_URL, "ttl_hours": 24, "max_stale_hours": 168, "max_requests": 50,
           "attribution": "Artificial Analysis (artificialanalysis.ai)"},
    # revision 1 + config별 latest parquet 1개. wiki unit(arena:*)이 늘어도 config 수(현재 약 20)만큼만 는다
    "arena": {"url": f"https://huggingface.co/datasets/{ARENA_DATASET}", "ttl_hours": 24, "max_stale_hours": 168,
              "max_requests": 50, "attribution": "LMArena leaderboard-dataset (CC BY 4.0)"},
    "mg": {"url": MG_URL, "ttl_hours": 24, "max_stale_hours": 168, "max_requests": 4,
           "attribution": "The Model Gap (themodelgap.com, CC BY 4.0)"},
    "swe": {"url": "https://www.swebench.com/", "ttl_hours": 168, "max_stale_hours": 720, "manual": True,
            "attribution": "SWE-bench (manual import)"},
    "tb": {"url": "https://www.tbench.ai/", "ttl_hours": 168, "max_stale_hours": 720, "manual": True,
           "attribution": "Terminal-Bench (manual import)"},
}
AUTO_SOURCES = [s for s, m in SOURCES.items() if not m.get("manual")]


class SourceError(Exception):
    """source 수집/스키마 실패. 해당 source의 새 snapshot은 게시하지 않는다."""


class LockBusy(Exception):
    pass


def _iso(t):
    return t.isoformat(timespec="seconds")


# ---------- HTTP ----------

def _left_s(budget):
    if budget is None or "deadline" not in budget:
        return float("inf")
    left = budget["deadline"] - time.monotonic()
    if left <= 0:
        raise SourceError(f"source deadline exceeded ({budget['max_seconds']}s)")
    return left


def http_get_json(url, headers=None, budget=None):
    """bounded GET. 401/403/429는 재시도 없음, 5xx/네트워크는 최대 HTTP_RETRIES회. 헤더(키)는 에러에 넣지 않는다.
    URL이 .parquet이면 JSON 대신 행 dict 목록으로 디코드한다.
    budget: {"used", "max"} 요청 수 상한, 선택적으로 {"deadline"(monotonic), "max_seconds"} 전체 시간 상한."""
    for attempt in range(HTTP_RETRIES + 1):
        timeout = min(HTTP_TIMEOUT_S, _left_s(budget))
        if budget is not None:
            if budget["used"] >= budget["max"]:
                raise SourceError(f"request budget exhausted ({budget['max']})")
            budget["used"] += 1
        req = urllib.request.Request(url, headers={"User-Agent": "bench-router/1", "Accept": "application/json",
                                                   **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read(HTTP_MAX_BYTES + 1)
            if len(data) > HTTP_MAX_BYTES:
                raise SourceError("response too large")
            if url.endswith(".parquet"):
                return _parquet_rows(data)
            try:
                return json.loads(data.decode("utf-8"), object_pairs_hook=r._no_dupes,
                                  parse_constant=r._reject_const)
            except (UnicodeDecodeError, json.JSONDecodeError, r.InputError) as e:
                raise SourceError(f"invalid JSON response: {e}")
        except urllib.error.HTTPError as e:
            e.close()
            print(f"bench-router: GET {url.split('?')[0]} -> HTTP {e.code} (attempt {attempt + 1})", file=sys.stderr)
            if e.code in (401, 403):
                raise SourceError(f"HTTP {e.code}: authentication/permission (not retried)")
            if e.code == 429:
                raise SourceError(f"HTTP 429: rate limited, Retry-After={e.headers.get('Retry-After')} (not retried)")
            if e.code < 500 or attempt == HTTP_RETRIES:
                raise SourceError(f"HTTP {e.code}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"bench-router: GET {url.split('?')[0]} -> {getattr(e, 'reason', e)!r} (attempt {attempt + 1})",
                  file=sys.stderr)
            if attempt == HTTP_RETRIES:
                raise SourceError(f"network error: {getattr(e, 'reason', e)}")
        time.sleep(min(2 ** attempt, _left_s(budget)))


def _parquet_rows(data):
    try:
        import pyarrow.parquet as pq  # Arena refresh에만 필요한 의존성. 없으면 그 source만 실패하고 last-good 유지
    except ImportError:
        raise SourceError("pyarrow not installed (pip install pyarrow)")
    try:
        return pq.read_table(io.BytesIO(data)).to_pylist()
    except (ValueError, OSError) as e:  # pyarrow ArrowInvalid/ArrowIOError
        raise SourceError(f"invalid parquet response: {e}")


# ---------- adapters: fetch → payload(원본) / parse(payload) → observations ----------

def fetch_aa(get_json, env):
    key = env.get(AA_KEY_ENV)
    if not key:
        raise SourceError(f"{AA_KEY_ENV} not set")
    pages, page = [], 1
    while True:
        body = get_json(f"{AA_URL}?page={page}", {"x-api-key": key})
        pages.append(body)
        pg = body.get("pagination") if isinstance(body, dict) else None
        if not isinstance(pg, dict) or pg.get("page") != page or type(pg.get("has_more")) is not bool:
            raise SourceError(f"AA page {page}: unexpected pagination")
        if not pg["has_more"]:
            break
        page += 1
    return {"pages": pages}, None, None


def parse_aa(payload):
    pages = payload["pages"]
    version = pages[0].get("intelligence_index_version")
    if type(version) not in (int, float):
        raise SourceError("AA: intelligence_index_version missing")
    if pages[-1]["pagination"].get("total_pages") != len(pages):
        raise SourceError("AA: total_pages does not match pages fetched")
    seen, obs = set(), []
    for body in pages:
        if body.get("intelligence_index_version") != version or not isinstance(body.get("data"), list):
            raise SourceError("AA: inconsistent index version or missing data")
        for m in body["data"]:
            slug = m.get("slug") if isinstance(m, dict) else None
            ev = m.get("evaluations") if slug else None
            if not isinstance(slug, str) or not isinstance(ev, dict) or slug in seen:
                raise SourceError(f"AA: invalid or duplicate model entry {slug!r}")
            seen.add(slug)
            for eid, field in AA_FIELDS.items():
                v = ev.get(field)
                if v is not None and (type(v) not in (int, float) or v != v or v in (float("inf"), float("-inf"))):
                    raise SourceError(f"AA: {slug}.{field} not a finite number")
                obs.append({"evidence_id": eid, "cohort_id": f"aa:{field}:v{version}", "source_model": slug,
                            "raw": v, "metric_version": f"v{version}", "scope": "model_proxy",
                            "conditions": {"suite": "artificial-analysis", "version": f"v{version}", "subset": "all",
                                           "metric": field, "direction": "higher", "variant": None,
                                           "dataset_revision": None, "evaluation_harness": None,
                                           "aggregation": None, "agent_scaffold": None, "reasoning_effort": effort_from_name(slug)},
                            "harness_id": None, "reasoning_effort": effort_from_name(slug), "published_at": None, "evaluated_at": None})
    return obs


def fetch_arena(get_json, env, cohorts_spec=ARENA_COHORTS):
    """cohorts_spec: {evidence_id: (config, category)}. config별 latest parquet를 revision sha에 고정해 한 번만 받고
    category는 로컬에서 거른다(datasets-server /filter는 페이지당 20-60초에 5xx가 잦았다)."""
    info = get_json(ARENA_REVISION_URL, None)
    revision = info.get("sha") if isinstance(info, dict) else None
    if not isinstance(revision, str):
        raise SourceError("Arena: dataset revision missing")
    files = [s.get("rfilename") for s in info.get("siblings") or [] if isinstance(s, dict)]
    cohorts, fetched, failed = {}, {}, {}
    for eid, (subset, category) in cohorts_spec.items():
        try:
            if subset not in fetched:
                fetched[subset] = _arena_rows(get_json, revision, files, subset)
        except SourceError as e:
            if eid in ARENA_COHORTS:
                raise
            failed[eid] = str(e)  # wiki 추가 조각의 일시 장애가 legacy evidence 수집 전체를 실패시키지 않게 한다
            continue
        cohorts[eid] = [x for x in fetched[subset] if isinstance(x, dict) and x.get("category") == category]
    return {"revision": revision, "cohorts": cohorts, "failed": failed,
            "spec": {e: list(c) for e, c in cohorts_spec.items() if e in cohorts}}, revision, None


def _arena_rows(get_json, revision, files, subset):
    shards = sorted(f for f in files if isinstance(f, str) and f.startswith(f"{subset}/latest-") and f.endswith(".parquet"))
    if not shards:
        raise SourceError(f"Arena {subset}: no latest parquet at {revision}")
    rows = []
    for f in shards:
        body = get_json(f"https://huggingface.co/datasets/{ARENA_DATASET}/resolve/{revision}/{f}", None)
        if not isinstance(body, list):
            raise SourceError(f"Arena {f}: unexpected response")
        rows += body
    return rows


ARENA_EFFORT = re.compile(r"(?i)[(\- ,](xhigh|low|medium|high|max)(?=[,)]|$)")


def effort_from_name(name):
    """Arena names and AA slugs. 'Claude Opus 5.5 (High)', 'claude-opus-5-5-high', 'gpt-6.1-sol-max', 'GPT-5.4 (High, Codex Harness)' → 'high' / 'max' / 'high'; none → None.
    shortcut: a model whose own name ends in a tier word (e.g. '...-max') is read as an effort; informational only, never used to match, upgrade when a source publishes effort as a column."""
    m = ARENA_EFFORT.search(name)
    return m.group(1).lower() if m else None


def parse_arena(payload):
    obs = []
    for eid, (subset, category) in payload.get("spec", ARENA_COHORTS).items():
        rows = payload["cohorts"].get(eid)
        if not rows:
            raise SourceError(f"Arena {subset}/{category}: no rows")
        dates = {x.get("leaderboard_publish_date") for x in rows if isinstance(x, dict)}
        if len(dates) != 1 or not isinstance(next(iter(dates)), str):
            raise SourceError(f"Arena {subset}/{category}: expected one publish date, got {sorted(map(str, dates))}")
        date = next(iter(dates))[:10]
        metric = "score" if "score" in rows[0] else "rating"  # agent_* config는 IPS score(τ̂), 나머지는 Bradley-Terry rating
        # legacy evidence와 같은 (config, category)를 wiki unit이 다시 쓰면 cohort를 나눠 모집단을 두 번 세지 않는다
        cohort = f"arena:{subset}:{category}:{date}" if eid in ARENA_COHORTS else f"{eid}@{date}"
        names = [x.get("model_name") for x in rows]
        for x in rows:
            name, rating = x.get("model_name"), x.get(metric)
            if not isinstance(name, str) or type(rating) not in (int, float) or rating != rating:
                raise SourceError(f"Arena {subset}/{category}: invalid row {name!r}")
            if names.count(name) > 1:
                # 원본에 같은 이름의 별개 항목 존재(실측: webdev 'gpt-5.3-codex (codex-harness)').
                # 모집단에는 남기고, 이름만으로는 매칭되지 않게 rank로 구분한다. 검증 후 alias에 이 키를 쓸 수 있다.
                name = f"{name}#rank={x.get('rank')}"
                if name in names:
                    raise SourceError(f"Arena {subset}/{category}: unresolvable duplicate {name!r}")
                names.append(name)
            effort = effort_from_name(name)
            obs.append({"evidence_id": eid, "cohort_id": cohort, "source_model": name,
                        "raw": rating, "metric_version": f"{subset}/{category}@{date}", "scope": "model_proxy",
                        "conditions": {"suite": "lmarena", "version": date, "subset": subset,
                                       "metric": metric, "direction": "higher", "variant": category,
                                       "dataset_revision": payload["revision"], "evaluation_harness": None,
                                       "aggregation": None, "agent_scaffold": None, "reasoning_effort": effort},
                        "harness_id": None, "reasoning_effort": effort, "published_at": date, "evaluated_at": None})
    return obs


def validate_import(doc, source_id):
    """승인된 수동 import(TB/SWE). 날짜·출처·버전 없는 데이터는 거부."""
    def need(cond, msg):
        if not cond:
            raise r.InputError(f"import: {msg}")
    need(isinstance(doc, dict) and doc.get("schema_version") == r.SCHEMA_VERSION, "schema_version '1.0' required")
    pin = EXACT_PINS.get(doc.get("evidence_id"))
    need(pin is not None and pin["source_id"] == source_id,
         f"evidence_id must be one of {[e for e, p in EXACT_PINS.items() if p['source_id'] == source_id]}")
    b = doc.get("benchmark")
    fields = ("suite", "version", "subset", "metric", "variant", "dataset_revision",
              "evaluation_harness", "aggregation")
    need(isinstance(b, dict) and all(isinstance(b.get(k), str) and b[k] for k in fields)
         and b.get("direction") in ("higher", "lower"),
         f"benchmark {{{', '.join(fields)}, direction}} required")
    need(b["suite"] == pin["suite"] and b["version"] == pin["version"],
         f"benchmark must be {pin['suite']} {pin['version']} (other versions are separate cohorts; change the pin)")
    if "scoring_version" in b:
        r._str(b["scoring_version"], "import.benchmark.scoring_version")
    for k in ("source_url", "attribution"):
        r._str(doc.get(k), f"import.{k}")
    need(doc.get("published_at") or doc.get("evaluated_at"), "published_at or evaluated_at required")
    for k in ("published_at", "evaluated_at"):
        if doc.get(k) is not None:
            try:
                datetime.fromisoformat(doc[k])
            except (TypeError, ValueError):
                raise r.InputError(f"import.{k}: ISO date required")
    rows = doc.get("rows")
    need(isinstance(rows, list) and rows, "rows required")
    keys = set()
    for x in rows:
        need(isinstance(x, dict) and set(x) == {"model_id", "harness_id", "reasoning_effort", "raw"},
             "row keys must be model_id, harness_id, reasoning_effort, raw")
        for k in ("model_id", "harness_id", "reasoning_effort"):
            r._str(x[k], f"import.rows.{k}")
        r._num(x["raw"], "import.rows.raw")
        key = (x["model_id"], x["harness_id"], x["reasoning_effort"])
        need(key not in keys, f"duplicate row {key}")
        keys.add(key)
    return doc


def parse_import(doc):
    b = doc["benchmark"]
    obs = []
    for x in doc["rows"]:
        conditions = {k: b[k] for k in ("suite", "version", "subset", "metric", "direction", "variant",
                                          "dataset_revision", "evaluation_harness", "aggregation")}
        conditions.update(scoring_version=b.get("scoring_version", b["version"]),
                          agent_scaffold=x["harness_id"], reasoning_effort=x["reasoning_effort"])
        cohort = f"{doc['evidence_id']}:{r.canonical_hash(conditions)[:16]}"
        obs.append({"evidence_id": doc["evidence_id"], "cohort_id": cohort, "source_model": x["model_id"],
                    "raw": x["raw"], "metric_version": conditions["scoring_version"], "scope": "exact_profile",
                    "harness_id": x["harness_id"], "reasoning_effort": x["reasoning_effort"], "conditions": conditions,
                    "published_at": doc.get("published_at"), "evaluated_at": doc.get("evaluated_at"),
                    "_lower_is_better": b["direction"] == "lower"})
    return obs


def fetch_mg(get_json, env):
    benchmarks, scores = get_json(f"{MG_URL}/benchmarks.json", None), get_json(f"{MG_URL}/scores.json", None)
    if not isinstance(benchmarks, list) or not isinstance(scores, list) or not benchmarks or not scores:
        raise SourceError("Model Gap: benchmarks.json and scores.json must be non-empty arrays")
    return {"benchmarks": benchmarks, "scores": scores}, None, None


def parse_mg(payload):
    """evidence_id = wiki unit id(mg:<benchmark>/<variant>). harness는 평가기관이라 agent_scaffold에 넣지 않는다."""
    variants = {}
    for b in payload["benchmarks"]:
        if not isinstance(b, dict) or not isinstance(b.get("id"), str) or not isinstance(b.get("variants"), list) \
                or b["id"] in variants:
            raise SourceError(f"Model Gap: invalid benchmark entry {b.get('id') if isinstance(b, dict) else b!r}")
        variants[b["id"]] = set(b["variants"])
    obs, seen = [], set()
    for x in payload["scores"]:
        bid, variant, model, v = (x.get(k) if isinstance(x, dict) else None
                                  for k in ("benchmark_id", "variant", "model_id", "value"))
        if variant not in variants.get(bid, ()) or not isinstance(model, str) or type(v) not in (int, float) \
                or v != v or v in (float("inf"), float("-inf")) or not isinstance(x.get("date_observed"), str):
            raise SourceError(f"Model Gap: invalid score row {model!r} {bid!r}/{variant!r}")
        eid = f"mg:{bid}/{variant}"
        if (eid, model) in seen:
            raise SourceError(f"Model Gap: duplicate score {model} {eid}")
        seen.add((eid, model))
        # Model Gap이 모델·변형마다 대표 점수 하나를 고른 큐레이션이라 unit 전체를 한 cohort로 둔다. 평가기관·자가보고는 conditions로 남긴다
        obs.append({"evidence_id": eid, "cohort_id": eid, "source_model": model, "raw": v, "metric_version": variant,
                    "scope": "model_proxy",
                    "conditions": {"suite": bid, "version": None, "subset": variant, "metric": "score", "direction": "higher",
                                   "variant": variant, "dataset_revision": None, "evaluation_harness": x.get("harness"),
                                   "aggregation": None, "agent_scaffold": None, "reasoning_effort": x.get("effort"),
                                   "source_type": x.get("source_type"), "source_url": x.get("source_url")},
                    "harness_id": None, "reasoning_effort": None, "published_at": None, "evaluated_at": x["date_observed"]})
    return obs


FETCH = {"aa": fetch_aa, "arena": fetch_arena, "mg": fetch_mg}
PARSE = {"aa": parse_aa, "arena": parse_arena, "mg": parse_mg, "swe": parse_import, "tb": parse_import}


def normalize(obs):
    """cohort 전체 모집단 기준 percentile. null은 결측으로 남긴다."""
    by_cohort = {}
    for i, o in enumerate(obs):
        if o["raw"] is not None:
            by_cohort.setdefault(o["cohort_id"], {})[i] = o["raw"]
    for vals in by_cohort.values():
        higher = not obs[next(iter(vals))].get("_lower_is_better")
        for i, n in r.percentile_ranks(vals, higher).items():
            obs[i]["normalized"] = n
    for o in obs:
        o.setdefault("normalized", None)
    return obs


# ---------- SQLite ----------

def open_db(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    v = db.execute("PRAGMA user_version").fetchone()[0]
    if v == 0:
        with db:
            db.executescript("""
            CREATE TABLE sources(id TEXT PRIMARY KEY, last_attempt_at TEXT, last_success_at TEXT, last_error TEXT,
              failure_count INTEGER NOT NULL DEFAULT 0, current_snapshot TEXT, last_requests INTEGER);
            CREATE TABLE snapshots(id TEXT PRIMARY KEY, source_id TEXT NOT NULL, fetched_at TEXT NOT NULL,
              payload_hash TEXT NOT NULL, source_revision TEXT, published_at TEXT, adapter_version TEXT NOT NULL,
              payload TEXT NOT NULL);
            CREATE TABLE observations(snapshot_id TEXT NOT NULL, evidence_id TEXT NOT NULL, cohort_id TEXT NOT NULL,
              source_model TEXT NOT NULL, harness_id TEXT, reasoning_effort TEXT, raw REAL, normalized REAL,
              scope TEXT NOT NULL, metric_version TEXT, published_at TEXT, evaluated_at TEXT, conditions TEXT);
            CREATE INDEX obs_snapshot ON observations(snapshot_id);
            PRAGMA user_version = 2;
            """)
    elif v == 1:
        with db:
            db.execute("ALTER TABLE observations ADD COLUMN conditions TEXT")
            db.execute("PRAGMA user_version = 2")
    elif v != DB_SCHEMA_VERSION:
        raise r.InputError(f"unsupported DB schema version {v}")
    return db


@contextlib.contextmanager
def refresh_lock(cache_dir):
    with locking.exclusive(Path(cache_dir) / "refresh.lock", LockBusy("another refresh is running")):
        yield


def refresh_source(db, sid, now, force=False, import_doc=None, get_json=None, env=None, arena_spec=ARENA_COHORTS):
    meta = SOURCES[sid]
    db.execute("INSERT OR IGNORE INTO sources(id) VALUES (?)", (sid,))
    src = db.execute("SELECT * FROM sources WHERE id=?", (sid,)).fetchone()
    if import_doc is None and not force and src["last_success_at"]:
        age_h = (now - datetime.fromisoformat(src["last_success_at"])).total_seconds() / 3600
        if age_h < meta["ttl_hours"]:
            return {"result": "skipped_fresh", "requests": 0}
    max_s = meta.get("max_seconds", SOURCE_MAX_SECONDS)
    budget = {"used": 0, "max": meta.get("max_requests", 0), "max_seconds": max_s, "deadline": time.monotonic() + max_s}
    db.execute("UPDATE sources SET last_attempt_at=? WHERE id=?", (_iso(now), sid))
    db.commit()
    try:
        if import_doc is not None:
            payload, revision, published = import_doc, None, import_doc.get("published_at") or import_doc.get("evaluated_at")
        else:
            get = lambda url, h: get_json(url, h, budget)
            payload, revision, published = (fetch_arena(get, env, arena_spec) if sid == "arena" else FETCH[sid](get, env))
        obs = normalize(PARSE[sid](payload))
    except (SourceError, KeyError, TypeError, ValueError, AttributeError) as e:  # a malformed payload fails this source only
        err = str(e) if isinstance(e, SourceError) else repr(e)
        with db:
            db.execute("UPDATE sources SET last_error=?, failure_count=failure_count+1, last_requests=? WHERE id=?",
                       (err, budget["used"], sid))
        return {"result": "failed", "error": err, "requests": budget["used"],
                "last_good_kept": src["current_snapshot"] is not None}

    payload_text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    payload_hash = r.canonical_hash(payload)
    if revision is None:
        revision = payload_hash[:16]
    snap_id = f"{sid}-" + r.canonical_hash([sid, ADAPTER_VERSION, payload_hash])[:24]
    with db:
        unchanged = db.execute("SELECT 1 FROM snapshots WHERE id=?", (snap_id,)).fetchone() is not None
        if not unchanged:
            db.execute("INSERT INTO snapshots VALUES (?,?,?,?,?,?,?,?)",
                       (snap_id, sid, _iso(now), payload_hash, revision, published, ADAPTER_VERSION, payload_text))
            db.executemany("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           [(snap_id, o["evidence_id"], o["cohort_id"], o["source_model"], o["harness_id"],
                             o["reasoning_effort"], o["raw"], o["normalized"], o["scope"], o["metric_version"],
                              o["published_at"], o["evaluated_at"],
                              json.dumps(o["conditions"], sort_keys=True) if o.get("conditions") else None) for o in obs])
        db.execute("UPDATE sources SET last_success_at=?, last_error=NULL, failure_count=0, current_snapshot=?, "
                   "last_requests=? WHERE id=?", (_iso(now), snap_id, budget["used"], sid))
        old = [x["id"] for x in db.execute("SELECT id FROM snapshots WHERE source_id=? ORDER BY fetched_at DESC",
                                           (sid,)).fetchall()[KEEP_PAYLOADS:]]
        for oid in old:
            db.execute("DELETE FROM observations WHERE snapshot_id=?", (oid,))
            db.execute("DELETE FROM snapshots WHERE id=?", (oid,))
    res = {"result": "unchanged" if unchanged else "updated", "requests": budget["used"], "snapshot": snap_id}
    if payload.get("failed"):
        res["skipped_units"] = payload["failed"]
    return res


# ---------- routing snapshot ----------

def load_aliases(path):
    """aliases.toml: [source_id] "출처의 정확한 모델 문자열" = "canonical model_id". 없으면 빈 매핑."""
    if not Path(path).exists():
        return {}
    data = r._load_toml(path)
    for sid, table in data.items():
        if sid not in SOURCES or not isinstance(table, dict) or not all(
                isinstance(k, str) and isinstance(v, str) and v for k, v in table.items()):
            raise r.InputError(f"aliases: [{sid}] must be a known source with string → string entries")
    return data


EFFORT_WORDS = r"(?:minimal|low|medium|high|xhigh|max|ultra)"


def model_key(name):
    """'Claude Opus 5.5 (High)', 'claude-opus-5.5-high', 'claude-opus-5-5' → 'claude-opus-5-5'. 구두점·대소문자를 같게 보고 effort 꼬리를 뗀다."""
    norm = lambda x: re.sub(r"[^a-z0-9]+", "-", x.lower()).strip("-")
    bare = re.sub(rf"(?i)(\s*\(\s*{EFFORT_WORDS}\s*\)|[-\s]{EFFORT_WORDS})$", "", name.strip())
    return norm(name), norm(bare)


def auto_canonical(cfg):
    """프로필 model_id의 정규화 키 → model_id. aliases.toml에 없는 출처 모델을 새 프로필·새 출처 행에도 자동으로 잇는다.
    shortcut: 하네스·컨텍스트 표기가 붙은 변형('(xHigh, Codex Harness)', '-preview')은 키가 달라 자동 매칭하지 않는다 — aliases.toml로 명시."""
    return {model_key(m)[0]: m for m in {p["model_id"] for p in cfg["profile"]}}


def build_snapshot(db, cfg, mapping, aliases, now):
    sources, cohorts, index, unmatched, ambiguous = {}, {}, {}, {}, []
    auto = auto_canonical(cfg)
    rows = db.execute("SELECT s.id, s.last_success_at, sn.source_revision, sn.published_at, sn.fetched_at, sn.id AS snap "
                      "FROM sources s JOIN snapshots sn ON sn.id = s.current_snapshot ORDER BY s.id").fetchall()
    for x in rows:
        meta = SOURCES[x["id"]]
        sources[x["id"]] = {"last_success_at": x["last_success_at"], "ttl_hours": meta["ttl_hours"],
                            "max_stale_hours": meta["max_stale_hours"], "published_at": x["published_at"],
                            "attribution": meta["attribution"], "url": meta["url"],
                            "source_revision": x["source_revision"], "snapshot": x["snap"]}
        for o in db.execute("SELECT * FROM observations WHERE snapshot_id=? ORDER BY cohort_id, source_model",
                            (x["snap"],)):
            o = dict(o)
            o["conditions"] = json.loads(o["conditions"]) if o["conditions"] else None
            c = cohorts.setdefault(o["cohort_id"], {"source_id": x["id"], "evidence_id": o["evidence_id"],
                                                    "metric_version": o["metric_version"],
                                                    "conditions": o["conditions"], "n": 0})
            c["n"] += o["raw"] is not None
            if o["scope"] == "exact_profile":
                canonical = o["source_model"]  # 수동 import는 canonical ID로 작성
            else:
                canonical = aliases.get(x["id"], {}).get(o["source_model"]) or next(
                    (auto[k] for k in model_key(o["source_model"]) if k in auto), None)  # 명시 alias가 우선
                if canonical is None:
                    unmatched.setdefault(x["id"], set()).add(o["source_model"])
                    continue
            o.update(source_id=x["id"], source_revision=x["source_revision"], fetched_at=x["fetched_at"])
            index.setdefault((o["evidence_id"], canonical), []).append(o)

    profiles = {}
    for p in cfg["profile"]:
        ev = {}
        for eid in sorted({e for e, _ in index} | set(EVIDENCE_IDS)):  # wiki unit evidence 포함
            found = index.get((eid, p["model_id"]), [])
            if eid in EXACT_PINS:  # 이름만 같다고 exact가 아님: harness·effort까지 일치
                found = [o for o in found if o["harness_id"] == p["harness_id"]
                         and o["reasoning_effort"] == p["reasoning_effort"] != "unknown"]
            if len(found) > 1:  # 출처가 effort별 행을 따로 낼 때(AA slug 등): 프로필 effort 행, 없으면 effort 표기 없는 행 하나
                found = ([o for o in found if o["reasoning_effort"] == p["reasoning_effort"]]
                         or [o for o in found if o["reasoning_effort"] is None] or found)
            if len(found) > 1:
                ambiguous.append({"profile": p["id"], "evidence_id": eid,
                                  "source_models": sorted(o["source_model"] for o in found)})
            elif found:
                o = found[0]
                ev[eid] = {k: o[k] for k in ("raw", "normalized", "scope", "cohort_id", "metric_version", "conditions", "source_id",
                                             "source_revision", "fetched_at", "published_at", "evaluated_at")}
        profiles[p["id"]] = {"fingerprint": r.profile_fingerprint(p), "evidence": ev}

    snap = {"schema_version": r.SCHEMA_VERSION, "generated_at": _iso(now), "policy_version": r.POLICY_VERSION,
            "config_hash": r.config_hash(cfg, mapping), "aliases_hash": r.canonical_hash(aliases),
            "sources": sources, "cohorts": cohorts, "profiles": profiles,
            "unmatched": {k: sorted(v) for k, v in sorted(unmatched.items())}, "ambiguous": ambiguous}
    snap["snapshot_id"] = r.snapshot_hash(snap)
    return r.validate_snapshot(snap)


def publish(cache_dir, snap, now):
    """현재 유효본 → last-good, 새 snapshot → snapshot.json (각각 원자 교체). 재현본은 ARCHIVE_DAYS 보관."""
    cache_dir = Path(cache_dir)
    data = json.dumps(snap, ensure_ascii=False, sort_keys=True).encode("utf-8")
    cur = cache_dir / "snapshot.json"
    try:
        r.validate_snapshot(r.load_json_strict(cur, r.SNAPSHOT_MAX_BYTES))
        r.atomic_write(cache_dir / "snapshot.last-good.json", cur.read_bytes())
    except r.InputError:
        pass  # 없거나 손상된 현재본은 last-good으로 승격하지 않음
    r.atomic_write(cur, data)
    archive = cache_dir / "snapshots"
    archive.mkdir(exist_ok=True)
    r.atomic_write(archive / f"{snap['snapshot_id']}.json", data)
    cutoff = now.timestamp() - ARCHIVE_DAYS * 86400
    for f in archive.glob("*.json"):
        if f.stat().st_mtime < cutoff:
            f.unlink(missing_ok=True)


def arena_spec(index):
    """기존 ARENA_COHORTS + wiki index의 수집 대상 arena:* unit(active·candidate)."""
    spec = dict(ARENA_COHORTS)
    for uid, u in (index or {}).get("units", {}).items():
        if uid.startswith("arena:") and u["adoption"] in ("active", "candidate"):
            spec[uid] = tuple(uid[len("arena:"):].split("/", 1))
    return spec


def refresh(cache_dir, cfg, mapping, aliases, now, only=None, force=False, import_doc=None,
            get_json=http_get_json, env=os.environ, index=None):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    with refresh_lock(cache_dir):
        db = open_db(cache_dir / "bench-router.db")
        try:
            results = {sid: refresh_source(db, sid, now, force, import_doc, get_json, env, arena_spec(index))
                       for sid in ([only] if only else AUTO_SOURCES)}
            snap = build_snapshot(db, cfg, mapping, aliases, now)
            publish(cache_dir, snap, now)
        finally:
            db.close()
    failed = [s for s, x in results.items() if x["result"] == "failed"]
    status = "ok" if not failed else "failed" if len(failed) == len(results) else "partial_failure"
    return {"schema_version": r.SCHEMA_VERSION, "status": status, "sources": results,
            "snapshot_id": snap["snapshot_id"], "unmatched_counts": {k: len(v) for k, v in snap["unmatched"].items()},
            "ambiguous": snap["ambiguous"]}


def status(cache_dir, now, cfg_hash=None):
    """네트워크 없음, 쓰기 없음."""
    cache_dir = Path(cache_dir)
    out = {"schema_version": r.SCHEMA_VERSION, "status": "ok", "snapshot": None, "sources": {}}
    snap, warnings = r.load_snapshot(cache_dir)
    out["warnings"] = warnings
    if snap:
        out["snapshot"] = {"snapshot_id": snap["snapshot_id"], "generated_at": snap["generated_at"],
                           "policy_version": snap["policy_version"],
                           "config_matches": cfg_hash is None or snap["config_hash"] == cfg_hash}
        if not out["snapshot"]["config_matches"]:
            out["warnings"].append(r.warn("config_changed", "profiles/categories changed since snapshot; run refresh"))
    dbp = cache_dir / "bench-router.db"
    if dbp.exists():
        db = sqlite3.connect(f"file:{dbp}?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        try:
            rows = db.execute("SELECT s.*, sn.published_at, sn.source_revision FROM sources s "
                              "LEFT JOIN snapshots sn ON sn.id = s.current_snapshot ORDER BY s.id").fetchall()
        finally:
            db.close()
        for x in rows:
            meta, age = SOURCES[x["id"]], None
            if x["last_success_at"]:
                age = round((now - datetime.fromisoformat(x["last_success_at"])).total_seconds() / 3600, 2)
            um = (snap or {}).get("unmatched", {}).get(x["id"], [])
            out["sources"][x["id"]] = {
                "last_success_at": x["last_success_at"], "last_attempt_at": x["last_attempt_at"], "age_hours": age,
                "stale": age is None or age > meta["ttl_hours"], "too_stale": age is None or age > meta["max_stale_hours"],
                "failure_count": x["failure_count"], "last_error": x["last_error"], "last_requests": x["last_requests"],
                "published_at": x["published_at"], "source_revision": x["source_revision"],
                "unmatched_count": len(um), "unmatched_sample": um[:20]}
            if x["failure_count"] >= 3:
                out["warnings"].append(r.warn("source_failing", f"{x['failure_count']} consecutive failures", x["id"]))
    return out
