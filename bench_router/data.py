"""bench-router 데이터 경로: source 수집·정규화(SQLite 이력) → routing snapshot 원자 게시.

refresh/import/status 전용. route는 이 모듈을 import하지 않는다(요청 경로 네트워크 0).
"""
import contextlib
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

from . import locking
from . import routing as r

ADAPTER_VERSION = "1"
DB_SCHEMA_VERSION = 1
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
ARENA_API = "https://datasets-server.huggingface.co/filter"
ARENA_REVISION_URL = f"https://huggingface.co/api/datasets/{ARENA_DATASET}"
# evidence → (subset, category). text/document/vision은 style-control subset으로 고정; webdev는 그 subset만 존재.
ARENA_COHORTS = {"arena_text": ("text_style_control", "overall"),
                 "arena_text_math": ("text_style_control", "math"),
                 "arena_webdev": ("webdev", "overall"),
                 "arena_document": ("document_style_control", "overall"),
                 "arena_vision": ("vision_style_control", "overall")}
# 수동 import로만 들어오는 exact_profile evidence. suite/version이 다르면 거부(점수 혼합 금지).
EXACT_PINS = {"swe_verified_exact": {"source_id": "swe", "suite": "swe-bench", "version": "verified"},
              "terminal_exact": {"source_id": "tb", "suite": "terminal-bench", "version": "4.0"}}
EVIDENCE_IDS = sorted([*AA_FIELDS, *ARENA_COHORTS, *EXACT_PINS])

SOURCES = {
    "aa": {"url": AA_URL, "ttl_hours": 24, "max_stale_hours": 168, "max_requests": 50,
           "attribution": "Artificial Analysis (artificialanalysis.ai)"},
    "arena": {"url": f"https://huggingface.co/datasets/{ARENA_DATASET}", "ttl_hours": 24, "max_stale_hours": 168,
              "max_requests": 60, "attribution": "LMArena leaderboard-dataset (CC BY 4.0)"},
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
                            "harness_id": None, "reasoning_effort": None, "published_at": None, "evaluated_at": None})
    return obs


def fetch_arena(get_json, env):
    info = get_json(ARENA_REVISION_URL, None)
    revision = info.get("sha") if isinstance(info, dict) else None
    if not isinstance(revision, str):
        raise SourceError("Arena: dataset revision missing")
    cohorts = {}
    for eid, (subset, category) in ARENA_COHORTS.items():
        rows, offset, total = [], 0, None
        while total is None or offset < total:
            q = urllib.parse.urlencode({"dataset": ARENA_DATASET, "config": subset, "split": "latest",
                                        "where": f"\"category\"='{category}'", "offset": offset, "length": 100})
            body = get_json(f"{ARENA_API}?{q}", None)
            if not isinstance(body, dict) or type(body.get("num_rows_total")) is not int or not isinstance(body.get("rows"), list):
                raise SourceError(f"Arena {subset}/{category}: unexpected response")
            total = body["num_rows_total"]
            page = [x.get("row") for x in body["rows"]]
            if not page and offset < total:
                raise SourceError(f"Arena {subset}/{category}: short page")
            rows += page
            offset += len(page)
        cohorts[eid] = rows
    # ponytail: datasets-server는 변환본을 서비스한다. revision은 main sha로 기록하며 변환 지연 가능성은 남는다.
    return {"revision": revision, "cohorts": cohorts}, revision, None


def parse_arena(payload):
    obs = []
    for eid, (subset, category) in ARENA_COHORTS.items():
        rows = payload["cohorts"].get(eid)
        if not rows:
            raise SourceError(f"Arena {subset}/{category}: no rows")
        dates = {x.get("leaderboard_publish_date") for x in rows if isinstance(x, dict)}
        if len(dates) != 1 or not isinstance(next(iter(dates)), str):
            raise SourceError(f"Arena {subset}/{category}: expected one publish date, got {sorted(map(str, dates))}")
        date = next(iter(dates))[:10]
        names = [x.get("model_name") for x in rows]
        for x in rows:
            name, rating = x.get("model_name"), x.get("rating")
            if not isinstance(name, str) or type(rating) not in (int, float) or rating != rating:
                raise SourceError(f"Arena {subset}/{category}: invalid row {name!r}")
            if names.count(name) > 1:
                # 원본에 같은 이름의 별개 항목 존재(실측: webdev 'gpt-5.3-codex (codex-harness)').
                # 모집단에는 남기고, 이름만으로는 매칭되지 않게 rank로 구분한다. 검증 후 alias에 이 키를 쓸 수 있다.
                name = f"{name}#rank={x.get('rank')}"
                if name in names:
                    raise SourceError(f"Arena {subset}/{category}: unresolvable duplicate {name!r}")
                names.append(name)
            obs.append({"evidence_id": eid, "cohort_id": f"arena:{subset}:{category}:{date}", "source_model": name,
                        "raw": rating, "metric_version": f"{subset}/{category}@{date}", "scope": "model_proxy",
                        "harness_id": None, "reasoning_effort": None, "published_at": date, "evaluated_at": None})
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
    need(isinstance(b, dict) and all(isinstance(b.get(k), str) and b[k] for k in ("suite", "version", "subset", "metric"))
         and b.get("direction") in ("higher", "lower"), "benchmark {suite, version, subset, metric, direction} required")
    need(b["suite"] == pin["suite"] and b["version"] == pin["version"],
         f"benchmark must be {pin['suite']} {pin['version']} (other versions are separate cohorts; change the pin)")
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
    cohort = f"{doc['evidence_id']}:{b['suite']}:{b['version']}:{b['subset']}:{b['metric']}"
    return [{"evidence_id": doc["evidence_id"], "cohort_id": cohort, "source_model": x["model_id"],
             "raw": x["raw"], "metric_version": b.get("scoring_version", b["version"]), "scope": "exact_profile",
             "harness_id": x["harness_id"], "reasoning_effort": x["reasoning_effort"],
             "published_at": doc.get("published_at"), "evaluated_at": doc.get("evaluated_at"),
             "_lower_is_better": b["direction"] == "lower"} for x in doc["rows"]]


FETCH = {"aa": fetch_aa, "arena": fetch_arena}
PARSE = {"aa": parse_aa, "arena": parse_arena, "swe": parse_import, "tb": parse_import}


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
              scope TEXT NOT NULL, metric_version TEXT, published_at TEXT, evaluated_at TEXT);
            CREATE INDEX obs_snapshot ON observations(snapshot_id);
            PRAGMA user_version = 1;
            """)
    elif v != DB_SCHEMA_VERSION:
        raise r.InputError(f"unsupported DB schema version {v}")
    return db


@contextlib.contextmanager
def refresh_lock(cache_dir):
    with locking.exclusive(Path(cache_dir) / "refresh.lock", LockBusy("another refresh is running")):
        yield


def refresh_source(db, sid, now, force=False, import_doc=None, get_json=None, env=None):
    meta = SOURCES[sid]
    db.execute("INSERT OR IGNORE INTO sources(id) VALUES (?)", (sid,))
    src = db.execute("SELECT * FROM sources WHERE id=?", (sid,)).fetchone()
    if import_doc is None and not force and src["last_success_at"]:
        age_h = (now - datetime.fromisoformat(src["last_success_at"])).total_seconds() / 3600
        if age_h < meta["ttl_hours"]:
            return {"result": "skipped_fresh", "requests": 0}
    budget = {"used": 0, "max": meta.get("max_requests", 0), "max_seconds": SOURCE_MAX_SECONDS,
              "deadline": time.monotonic() + SOURCE_MAX_SECONDS}
    db.execute("UPDATE sources SET last_attempt_at=? WHERE id=?", (_iso(now), sid))
    db.commit()
    try:
        if import_doc is not None:
            payload, revision, published = import_doc, None, import_doc.get("published_at") or import_doc.get("evaluated_at")
        else:
            payload, revision, published = FETCH[sid](lambda url, h: get_json(url, h, budget), env)
        obs = normalize(PARSE[sid](payload))
    except SourceError as e:
        with db:
            db.execute("UPDATE sources SET last_error=?, failure_count=failure_count+1, last_requests=? WHERE id=?",
                       (str(e), budget["used"], sid))
        return {"result": "failed", "error": str(e), "requests": budget["used"],
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
            db.executemany("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                           [(snap_id, o["evidence_id"], o["cohort_id"], o["source_model"], o["harness_id"],
                             o["reasoning_effort"], o["raw"], o["normalized"], o["scope"], o["metric_version"],
                             o["published_at"], o["evaluated_at"]) for o in obs])
        db.execute("UPDATE sources SET last_success_at=?, last_error=NULL, failure_count=0, current_snapshot=?, "
                   "last_requests=? WHERE id=?", (_iso(now), snap_id, budget["used"], sid))
        old = [x["id"] for x in db.execute("SELECT id FROM snapshots WHERE source_id=? ORDER BY fetched_at DESC",
                                           (sid,)).fetchall()[KEEP_PAYLOADS:]]
        for oid in old:
            db.execute("DELETE FROM observations WHERE snapshot_id=?", (oid,))
            db.execute("DELETE FROM snapshots WHERE id=?", (oid,))
    return {"result": "unchanged" if unchanged else "updated", "requests": budget["used"], "snapshot": snap_id}


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


def build_snapshot(db, cfg, mapping, aliases, now):
    sources, cohorts, index, unmatched, ambiguous = {}, {}, {}, {}, []
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
            c = cohorts.setdefault(o["cohort_id"], {"source_id": x["id"], "evidence_id": o["evidence_id"],
                                                    "metric_version": o["metric_version"], "n": 0})
            c["n"] += o["raw"] is not None
            if o["scope"] == "exact_profile":
                canonical = o["source_model"]  # 수동 import는 canonical ID로 작성
            else:
                canonical = aliases.get(x["id"], {}).get(o["source_model"])
                if canonical is None:
                    unmatched.setdefault(x["id"], set()).add(o["source_model"])
                    continue
            o.update(source_id=x["id"], source_revision=x["source_revision"], fetched_at=x["fetched_at"])
            index.setdefault((o["evidence_id"], canonical), []).append(o)

    profiles = {}
    for p in cfg["profile"]:
        ev = {}
        for eid in EVIDENCE_IDS:
            found = index.get((eid, p["model_id"]), [])
            if eid in EXACT_PINS:  # 이름만 같다고 exact가 아님: harness·effort까지 일치
                found = [o for o in found if o["harness_id"] == p["harness_id"]
                         and o["reasoning_effort"] == p["reasoning_effort"] != "unknown"]
            if len(found) > 1:
                ambiguous.append({"profile": p["id"], "evidence_id": eid,
                                  "source_models": sorted(o["source_model"] for o in found)})
            elif found:
                o = found[0]
                ev[eid] = {k: o[k] for k in ("raw", "normalized", "scope", "cohort_id", "metric_version", "source_id",
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


def refresh(cache_dir, cfg, mapping, aliases, now, only=None, force=False, import_doc=None,
            get_json=http_get_json, env=os.environ):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    with refresh_lock(cache_dir):
        db = open_db(cache_dir / "bench-router.db")
        try:
            results = {sid: refresh_source(db, sid, now, force, import_doc, get_json, env)
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
