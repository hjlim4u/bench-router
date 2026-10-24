"""벤치마크 Wiki index(index.json) → 작업에 맞는 증거 표. 요청 경로: routing만 import, 네트워크·SQLite 없음.
점수를 합산하지 않는다. unit 표시 순서는 순위가 아니다."""
import re
from pathlib import Path

from . import routing as r

INDEX_SCHEMA_VERSION = "1.0"
BUNDLED_INDEX = Path(__file__).with_name("index.json")
CODE_EXTS = (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".cc", ".cpp", ".h", ".rb", ".php",
             ".cs", ".kt", ".swift", ".sh", ".sql")
FACET_BOUNDARIES = {
    "task:instruction_following": "1 only if explicit output constraints are the main challenge; ordinary requirements are 0.",
    "difficulty:hard_prompts": "Most routine coding, writing or lookup tasks are 0, even when well specified.",
    "domain:software_it": "1 if the subject is software/IT; 0 if code is only a tool for another subject.",
    "task:math": "1 for mathematical derivation/calculation as the main work; incidental arithmetic is 0.",
    "domain:mathematical": "1 only if the subject matter is mathematics.",
    "task:ocr_parse": "1 for converting a scanned/photographed document's text into structured output.",
    "task:vision_ocr": "1 only if an image is attached and its text is needed for the answer.",
}
# script → (유니코드 범위, 알파벳 문자 중 최소 비율)
SCRIPTS = {"hangul": ((0xAC00, 0xD7A3), 0.2), "kana": ((0x3040, 0x30FF), 0.05), "cyrillic": ((0x0400, 0x04FF), 0.2),
           "han": ((0x4E00, 0x9FFF), 0.2)}


def _validate_index(idx):
    if not isinstance(idx, dict) or idx.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise r.InputError("wiki index: unsupported schema")
    r._str(idx.get("wiki_hash"), "wiki index.wiki_hash")
    for key in ("facets", "units", "postings"):
        if not isinstance(idx.get(key), dict):
            raise r.InputError(f"wiki index.{key}: object required")
    for axis, values in idx["facets"].items():
        if not isinstance(values, dict):
            raise r.InputError(f"wiki index.facets.{axis}: object required")
        for value, f in values.items():
            if not isinstance(f, dict):
                raise r.InputError(f"wiki index facet {axis}:{value}: object required")
            for key in ("desc", "detect", "evidence"):
                r._str(f.get(key), f"wiki index facet {axis}:{value}.{key}")
    expected = {}
    for uid, u in idx["units"].items():
        if not isinstance(u, dict) or not isinstance(u.get("facets"), dict):
            raise r.InputError(f"wiki index unit {uid}: object with facets required")
        for key in ("desc", "metric", "status", "adoption", "page"):
            r._str(u.get(key), f"wiki index unit {uid}.{key}")
        for axis, values in u["facets"].items():
            for value in r._str_list(values, f"wiki index unit {uid}.facets.{axis}"):
                if value not in idx["facets"].get(axis, {}):
                    raise r.InputError(f"wiki index unit {uid}: unknown facet {axis}:{value}")
                if u["adoption"] == "active":
                    expected.setdefault(f"{axis}:{value}", set()).add(uid)
    actual = {key: set(r._str_list(ids, f"wiki index.postings.{key}")) for key, ids in idx["postings"].items()}
    if actual != expected:
        raise r.InputError("wiki index: postings disagree with active units")


def load_index(cache_dir):
    """캐시의 index.json(없으면 내장 index.json). 손상되면 None."""
    p = Path(cache_dir) / "index.json"
    try:
        idx = r.load_json_strict(p if p.exists() else BUNDLED_INDEX, 16 * 1024 * 1024)
        _validate_index(idx)
    except r.InputError:
        return None
    return idx


def _share(text, script):
    (lo, hi), _ = SCRIPTS[script]
    letters = [c for c in text if c.isalpha()]
    return sum(lo <= ord(c) <= hi for c in letters) / len(letters) if letters else 0.0


def _kw(k, text):
    """영문 키워드는 ASCII 단어 경계(한글 조사가 붙은 'CI가'도 매칭), 그 외는 부분 문자열."""
    if k.isascii():
        return re.search(r"(?<![A-Za-z0-9_])" + re.escape(k) + r"(?![A-Za-z0-9_])", text, re.I) is not None
    return k in text


def rule_hit(rule, t):
    """wiki facet의 detect = 'rule:<rule>'. 참/거짓, 모르는 규칙은 None. 토큰 0, 결정적."""
    text = t["summary"] + "\n" + t["prompt"]
    files = [f.lower() for f in t["context_files"]]
    if rule == "always":
        return True
    if rule == "round>1":
        return t["round"] > 1
    if (m := re.fullmatch(r"prompt_tokens>(\d+)", rule)):
        return len(t["prompt"]) // 4 > int(m.group(1))  # shortcut: 4자≈1토큰 추정, 토크나이저가 생기면 교체
    if rule == "code_block_or_code_ext":
        return "```" in t["prompt"] or any(f.endswith(CODE_EXTS) for f in files)
    if (m := re.fullmatch(r"ext\((.+)\)", rule)):
        return any(f.endswith(tuple(m.group(1).split(","))) for f in files)
    if (m := re.fullmatch(r"kw\((.+)\)", rule)):
        return any(_kw(k, text) for k in m.group(1).split(","))
    if (m := re.fullmatch(r"script\((hangul|kana|cyrillic|han_only)\)", rule)):
        text = re.sub(r"(?s)(`{3,}|~{3,}).*?(?:\1|$)", "\n", text)
        s = m.group(1)
        if s == "han_only":
            return _share(text, "han") >= SCRIPTS["han"][1] and not _share(text, "kana") and not _share(text, "hangul")
        return _share(text, s) >= SCRIPTS[s][1]
    return None


def task_facets(t, index, *, infer_rules=True):
    """규칙으로 판정되는 facet + Orchestrator가 task.facets에 직접 태그한 값. 어휘 밖의 값은 거부."""
    vocab, out, warnings = index["facets"], {}, []
    for axis, values in sorted(vocab.items()):
        for value, f in sorted(values.items()):
            if not infer_rules or f["detect"] == "self":
                continue
            hit = rule_hit(f["detect"].removeprefix("rule:"), t)
            if hit is None:
                warnings.append(r.warn("unsupported_rule", f"{axis}:{value} {f['detect']}"))
            elif hit:
                out[axis, value] = "rule"
    for axis, values in t["facets"].items():
        if axis not in vocab:
            raise r.InputError(f"task.facets: unknown axis {axis!r}; allowed {sorted(vocab)}")
        for value in values:
            if value not in vocab[axis]:
                raise r.InputError(f"task.facets.{axis}: {value!r} not in {sorted(vocab[axis])}")
            out.setdefault((axis, value), "orchestrator")
    return [{"axis": a, "value": v, "origin": o} for (a, v), o in sorted(out.items())], warnings


def _cell(p, uid, snap, sources, warned):
    sp = snap["profiles"].get(p["id"]) if snap else None
    stale_cfg = sp is not None and sp["fingerprint"] != r.profile_fingerprint(p)
    if stale_cfg or (snap and sp is None):
        warned.add(("stale_config" if stale_cfg else "profile_not_in_snapshot", p["id"]))
    e = sp.get("evidence", {}).get(uid) if sp and not stale_cfg else None
    reason = ("no_snapshot" if snap is None else "profile_not_in_snapshot" if sp is None
              else "stale_config" if stale_cfg else r.unobserved_reason(snap, p["id"], uid) if e is None
              else "null_value" if e.get("normalized") is None
              else "missing_conditions" if e.get("scope") == "exact_profile" and not e.get("conditions")
              else "max_stale_exceeded" if sources[e["source_id"]]["excluded"] else None)
    if reason:
        return {"raw": None, "normalized": None, "missing_reason": reason}
    effort = (e.get("conditions") or {}).get("reasoning_effort")
    known = effort and p["reasoning_effort"] != "unknown"
    conditions = e.get("conditions") or {}
    return {"raw": e["raw"], "normalized": e["normalized"], "scope": e["scope"], "effort": effort,
            "effort_matches": (effort == p["reasoning_effort"]) if known else None,
            "exact_profile": (e["scope"] == "exact_profile" and bool(known) and effort == p["reasoning_effort"]
                              and conditions.get("agent_scaffold") == p["harness_id"]),
            **{k: e.get(k) for k in ("conditions", "source_revision", "metric_version", "fetched_at", "published_at", "evaluated_at")},
            "stale": sources[e["source_id"]]["stale"], "source_id": e["source_id"], "cohort_id": e["cohort_id"],
            "missing_reason": None}


def build(t, cfg, snap, snap_warnings, index, now, max_units=12, profile_ids=None, *, infer_rules=True):
    warnings = list(snap_warnings)
    profiles = sorted((p for p in cfg["profile"] if p["enabled"] and p["id"] not in t.get("exclude_profiles", [])
                       and (profile_ids is None or p["id"] in profile_ids)), key=lambda p: p["id"])
    res = {"schema_version": r.SCHEMA_VERSION, "status": "ok", "task_id": t["task_id"], "round": t["round"],
           "snapshot_id": snap["snapshot_id"] if snap else None, "wiki_hash": (index or {}).get("wiki_hash"),
           "facets": [], "units": [], "omitted_units": 0, "withheld_units": [], "profiles": {p["id"]: {"reasoning_effort": p["reasoning_effort"]}
                                                                          for p in profiles}, "warnings": warnings}
    if index is None:
        warnings.append(r.warn("wiki_index_missing", "no index.json; run `wiki compile` (needs reviewed wiki pages)"))
        return res
    res["facets"], rule_warnings = task_facets(t, index, infer_rules=infer_rules)
    warnings += rule_warnings
    if not index["units"]:
        warnings.append(r.warn("wiki_index_empty", "index.json has no units; wiki pages are not reviewed yet"))
    sources = r.source_status(snap, now) if snap else {}
    for sid, s in sources.items():
        if s["excluded"]:
            warnings.append(r.warn("source_too_stale", "older than max_stale; observations excluded", sid))
        elif s["stale"]:
            warnings.append(r.warn("source_stale", "older than TTL; using last-good", sid))

    matched = {}
    for f in res["facets"]:
        for uid in index["postings"].get(f"{f['axis']}:{f['value']}", []):
            matched.setdefault(uid, []).append(f"{f['axis']}:{f['value']}")
    warned, rows = set(), []
    tasks = {f["value"] for f in res["facets"] if f["axis"] == "task"}
    for uid, facets in matched.items():
        u = index["units"][uid]
        # 언어·난이도만 같다고 다른 작업 유형의 unit을 선택하지 않는다. 공통 agent 신호는 유지한다.
        if (u["facets"].get("task") and not tasks.intersection(u["facets"]["task"])
                and not any(f.startswith("agent_signal:") for f in facets)):
            continue
        cells = {p["id"]: _cell(p, uid, snap, sources, warned) for p in profiles}
        rows.append({"id": uid, "desc": u["desc"], "metric": u["metric"], "status": u["status"], "page": u["page"],
                     "facets": u["facets"], "matched_facets": facets, "profiles": cells,
                     **{k: u[k] for k in ("meaningful_gap", "trust_grade") if k in u}})
    # 표시 순서(순위가 아니다): 작업 유형 일치 → 보조 facet 일치 → 전체 일치 → 점수가 있는 프로필 수 → id.
    # rule:always facet(agent_signal 등)은 모든 작업에 켜지므로 작업 특화 unit을 밀어내지 않게 뒤로 둔다.
    always = {f"{a}:{v}" for a, vs in index["facets"].items() for v, f in vs.items() if f["detect"] == "rule:always"}
    # 범용 unit(task:general 같은 always facet으로만 걸림, agent 신호 제외)은 더 구체적인 facet(작업·언어 등)으로 걸린 unit이 없을 때만 보여 준다.
    # eval/retrieval.py 측정: 상위 12개 무관 unit의 대부분이 범용 unit이었다(nDCG 변화 없음, 정확도 +0.2).
    general = {x["id"] for x in rows if all(f in always and not f.startswith("agent_signal:") for f in x["matched_facets"])}
    if any(not set(x["matched_facets"]) <= always for x in rows):
        res["withheld_units"] = sorted(general)
        rows = [x for x in rows if x["id"] not in general]
    rows.sort(key=lambda x: (-sum(f.startswith("task:") and f not in always for f in x["matched_facets"]),
                             -len([f for f in x["matched_facets"] if f not in always]), -len(x["matched_facets"]),
                             -sum(c["normalized"] is not None for c in x["profiles"].values()), x["id"]))
    res["omitted_units"] = 0 if max_units is None else max(0, len(rows) - max_units)
    res["units"] = rows if max_units is None else rows[:max_units]
    for code, pid in sorted(warned):
        warnings.append(r.warn(code, f"{pid}: profile config changed since snapshot; evidence ignored" if code == "stale_config"
                               else f"{pid}: profile absent from snapshot; run refresh"))
    return res


def _cell_text(c, profile_effort):
    if c["missing_reason"]:
        return "—"
    s = f"{c['raw']:.4g} p{round(c['normalized'] * 100)}"
    if c["effort"]:
        s += f" {c['effort']}" + (f"≠{profile_effort}" if c["effort_matches"] is False else "")
    return s + ("*" if c["stale"] else "")


def table(res):
    """Orchestrator에 넘기는 압축 표. unit 설명은 한 번만, 프로필별 값은 한 줄씩."""
    lines = [f"task {res['task_id']} r{res['round']} · snapshot {(res['snapshot_id'] or '-')[:8]} · wiki {(res['wiki_hash'] or '-')[:8]}",
             "facets: " + (", ".join(f"{f['axis']}:{f['value']}({f['origin']})" for f in res["facets"]) or "-"),
             "units (order = task type matches, then other facet matches, then profiles with a score; not a ranking):"]
    for i, u in enumerate(res["units"], 1):
        extra = "".join(f" {k}={u[k]}" for k in ("meaningful_gap", "trust_grade") if k in u)
        lines.append(f" {i} {u['id']} [{u['metric']}, {u['status']}{extra}] {u['desc']} · {','.join(u['matched_facets'])} · {u['page']}")
    if res["omitted_units"]:
        lines.append(f" … {res['omitted_units']} more matching units omitted (--max-units)")
    if res["withheld_units"]:
        lines.append(f" … general-purpose units withheld because more specific units matched: {', '.join(res['withheld_units'])}")
    lines.append("profiles (raw pPERCENTILE effort; effort≠profile effort means a different effort was measured; — none; * stale source):")
    for pid, meta in res["profiles"].items():
        cells = " · ".join(f"{i}={_cell_text(u['profiles'][pid], meta['reasoning_effort'])}" for i, u in enumerate(res["units"], 1))
        lines.append(f" {pid} ({meta['reasoning_effort']}): {cells or '-'}")
    lines += [f"warning {w['code']}: {w['message']}" + (f" [{w['source_id']}]" if w["source_id"] else "") for w in res["warnings"]]
    return "\n".join(lines)
