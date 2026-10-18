"""벤치마크 Wiki(wiki/) → index.json 컴파일. 계약은 wiki/AGENTS.md. 요청 경로는 index.json만 읽는다."""
import hashlib
import json
import re
import tomllib
from pathlib import Path

from . import routing as r
from .data import EVIDENCE_IDS
from .evidence import INDEX_SCHEMA_VERSION, load_index  # noqa: F401  (load_index is re-exported for cli)

AXES = ("task", "lang", "domain", "difficulty", "shape", "agent_signal")
COMPILED_LIFECYCLES = ("reviewed", "verified")
METRICS = ("elo", "ips", "pass_pct", "index")
STATUSES = ("current", "saturated", "contaminated")
ADOPTIONS = ("active", "candidate", "archive", "excluded")
EVIDENCE = ("official", "dataset", "name_only")
FACET_KEYS = ({"id", "desc", "detect", "evidence"}, {"arena_rule"})
UNIT_KEYS = ({"id", "desc", "metric", "status", "adoption", "facets"}, {"reason", "evidence", "meaningful_gap", "trust_grade"})
UNIT_ID = re.compile(r"(?:arena|arena-web|mg|hf):[\w.-]+/[\w.-]+")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LIFECYCLE = re.compile(r"^lifecycle:\s*(\S+)\s*$", re.M)
INDEX_BLOCK = re.compile(r"^## Index\s*\n+```toml\n(.*?)^```", re.S | re.M)


def _lifecycle(text, page):
    fm = FRONTMATTER.match(text)
    m = LIFECYCLE.search(fm.group(1)) if fm else None
    if not m:
        raise r.InputError(f"wiki {page}: frontmatter lifecycle required")
    return m.group(1)


def _index_block(text, page, table):
    m = INDEX_BLOCK.search(text)
    if not m:
        raise r.InputError(f"wiki {page}: '## Index' ```toml block required")
    try:
        doc = tomllib.loads(m.group(1))
    except tomllib.TOMLDecodeError as e:
        raise r.InputError(f"wiki {page}: invalid Index TOML ({e})")
    rows = doc.get(table)
    if set(doc) != {table} or not isinstance(rows, list) or not rows:
        raise r.InputError(f"wiki {page}: Index must contain only a non-empty [[{table}]] array")
    return rows


def _keys(row, keys, where):
    req, opt = keys
    if not isinstance(row, dict) or not req <= set(row) or set(row) - req - opt:
        raise r.InputError(f"{where}: keys must be {sorted(req)} plus optional {sorted(opt)}")
    for k in req - {"facets"}:
        r._str(row[k], f"{where}.{k}")


def _pages(vault, sub):
    """(상대 경로, 본문) — reviewed/verified 페이지만."""
    for p in sorted((vault / sub).rglob("*.md")):
        rel, text = p.relative_to(vault).as_posix(), p.read_text(encoding="utf-8")
        if _lifecycle(text, rel) in COMPILED_LIFECYCLES:
            yield rel, text


def compile_wiki(vault):
    """검증에 실패하면 InputError. 조용히 빠뜨리는 항목은 없다(draft 페이지 제외는 계약)."""
    vault = Path(vault)
    if not (vault / "AGENTS.md").is_file():
        raise r.InputError(f"wiki: {vault} is not a benchmark wiki (AGENTS.md missing)")
    digest, facets, units, postings = {}, {}, {}, {}

    for rel, text in _pages(vault, "concepts/facets"):
        axis = Path(rel).stem
        if axis not in AXES or axis in facets:
            raise r.InputError(f"wiki {rel}: facet page name must be one of {list(AXES)}")
        digest[rel] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        facets[axis] = {}
        for i, f in enumerate(_index_block(text, rel, "facet")):
            where = f"wiki {rel} facet[{i}]"
            _keys(f, FACET_KEYS, where)
            if f["id"] in facets[axis]:
                raise r.InputError(f"{where}: duplicate facet {axis}:{f['id']}")
            if f["evidence"] not in EVIDENCE or not (f["detect"] == "self" or f["detect"].startswith("rule:")):
                raise r.InputError(f"{where}: evidence must be one of {list(EVIDENCE)}, detect 'self' or 'rule:...'")
            facets[axis][f["id"]] = {"desc": f["desc"], "detect": f["detect"], "evidence": f["evidence"]}

    for rel, text in _pages(vault, "entities"):
        digest[rel] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        for i, u in enumerate(_index_block(text, rel, "unit")):
            where = f"wiki {rel} unit[{i}]"
            _keys(u, UNIT_KEYS, where)
            if not (UNIT_ID.fullmatch(u["id"]) or u["id"] in EVIDENCE_IDS):
                raise r.InputError(f"{where}: unknown unit id format {u['id']!r}")
            if u["id"] in units:
                raise r.InputError(f"{where}: duplicate unit {u['id']} (also in {units[u['id']]['page']})")
            for k, allowed in (("metric", METRICS), ("status", STATUSES), ("adoption", ADOPTIONS)):
                if u[k] not in allowed:
                    raise r.InputError(f"{where}: {k} must be one of {list(allowed)}")
            if not isinstance(u["facets"], dict) or (not u["facets"] and u["adoption"] != "excluded"):
                raise r.InputError(f"{where}: facets {{axis = [values]}} required unless adoption = 'excluded'")
            for axis, values in sorted(u["facets"].items()):
                if not r._str_list(values, f"{where}.facets.{axis}"):
                    raise r.InputError(f"{where}: facets.{axis} must not be empty")
                unknown = [v for v in values if v not in facets.get(axis, {})]
                if unknown:  # draft facet 페이지의 값도 여기서 걸린다
                    raise r.InputError(f"{where}: facet values {axis}:{unknown} not defined by a reviewed facet page")
                if u["adoption"] == "active":
                    for v in values:
                        postings.setdefault(f"{axis}:{v}", []).append(u["id"])
            units[u["id"]] = {**{k: u[k] for k in ("desc", "metric", "status", "adoption", "facets")},
                              **{k: u[k] for k in UNIT_KEYS[1] if k in u}, "page": rel}

    return {"schema_version": INDEX_SCHEMA_VERSION, "wiki_hash": r.canonical_hash(digest),
            "facets": facets, "postings": {k: sorted(v) for k, v in sorted(postings.items())},
            "units": dict(sorted(units.items()))}


def write_index(cache_dir, index):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "index.json"
    r.atomic_write(path, json.dumps(index, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return path


def summary(index):
    adoption = {}
    for u in index["units"].values():
        adoption[u["adoption"]] = adoption.get(u["adoption"], 0) + 1
    return {"wiki_hash": index["wiki_hash"], "facet_values": sum(map(len, index["facets"].values())),
            "units": len(index["units"]), "adoption": dict(sorted(adoption.items())), "postings": len(index["postings"])}
