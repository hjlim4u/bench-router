"""bench-router CLI. stdout에는 JSON 한 객체(explain 제외), 로그는 stderr. 종료 코드는 04 문서."""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import routing as r

EXIT = {"selected": 0, "no_eligible_profile": 13}
BUNDLED_CATEGORIES = Path(__file__).with_name("categories.toml")


def _xdg(var, fallback):
    return Path(os.environ.get(var) or Path.home() / fallback) / "bench-router"


def _load(args):
    task = r.validate_task(r.load_json_strict(args.task, r.TASK_MAX_BYTES))
    cfg = r.load_profiles(args.config_dir / "profiles.toml")
    cats = args.config_dir / "categories.toml"
    mapping = r.load_categories(cats if cats.exists() else BUNDLED_CATEGORIES)
    snap, snap_warnings = r.load_snapshot(args.cache_dir)
    return r.route(task, cfg, mapping, snap, snap_warnings, datetime.now(timezone.utc))


def explain_text(res):
    cls = res["classification"]
    lines = [f"task {res['task_id']} round {res['round']} · policy {res['policy_version']} · snapshot {res['snapshot_id']}",
             f"classification: {cls['stage']} {cls['categories']} confidence={cls['self_reported_confidence']}"
             + (f" fallback={cls['fallback_reason']}" if cls["fallback_reason"] else "")
             + (f" rules={cls['matched_rules']}" if cls["matched_rules"] else ""),
             f"selected: {res['selected']['profile'] if res['selected'] else '-'} ({res['selection_mode']})",
             "candidates:"]
    for c in res["candidates"]:
        lines.append(f"  {c['profile']}: score={c['score']} quality={c['quality']} coverage={c['coverage']} "
                     f"({c['coverage_band']}) exact={c['exact_evidence_weight']} cost_proxy={c['cost_proxy']}")
        for e in c["evidence"]:
            lines.append(f"    {e['id']} w={e['weight']} norm={e['normalized']} raw={e['raw']} scope={e['scope']} "
                         f"src={e['source_id']}@{e['source_revision']} published={e['published_at'] or 'unknown'}"
                         + (" STALE" if e["stale"] else "") + (f" missing={e['missing_reason']}" if e["missing_reason"] else ""))
    lines += ["excluded:"] + [f"  {x['profile']}: {', '.join(x['reasons'])}" for x in res["excluded"]]
    lines += ["warnings:"] + [f"  {w['code']}: {w['message']}" + (f" [{w['source_id']}]" if w["source_id"] else "")
                              for w in res["warnings"]]
    lines += ["sources:"] + [f"  {sid}: last_success={s['last_success_at']} age_h={s['age_hours']} "
                             f"published={s['published_at'] or 'unknown'} stale={s['stale']} excluded={s['excluded']}"
                             for sid, s in res["sources"].items()]
    return "\n".join(lines)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):  # WSL은 이미 UTF-8; Windows 콘솔 대비
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="bench-router")
    ap.add_argument("--config-dir", type=Path, default=_xdg("XDG_CONFIG_HOME", ".config"))
    ap.add_argument("--cache-dir", type=Path, default=_xdg("XDG_CACHE_HOME", ".cache"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("route", help="select a profile (--dry-run only until P2)")
    rp.add_argument("--task", required=True)
    rp.add_argument("--dry-run", action="store_true")
    ep = sub.add_parser("explain", help="human-readable dry-run with all candidates")
    ep.add_argument("--task", required=True)
    args = ap.parse_args(argv)

    try:
        if args.cmd == "route" and not args.dry_run:
            raise r.InputError("live route is not implemented yet (P2); use --dry-run")
        res = _load(args)
    except r.InputError as e:
        print(json.dumps({"schema_version": r.SCHEMA_VERSION, "status": "error",
                          "error": {"code": "validation", "message": str(e)}}, ensure_ascii=False))
        return 2
    except OSError as e:
        print(json.dumps({"schema_version": r.SCHEMA_VERSION, "status": "error",
                          "error": {"code": "io", "message": str(e)}}, ensure_ascii=False))
        return 15

    if args.cmd == "explain":
        print(explain_text(res))
    else:
        res["candidates_total"] = len(res["candidates"])
        res["candidates"] = res["candidates"][:3]  # top3 요약, 전체는 explain
        print(json.dumps(res, ensure_ascii=False))
    return EXIT[res["status"]]


if __name__ == "__main__":
    sys.exit(main())
