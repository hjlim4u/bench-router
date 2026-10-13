"""bench-router CLI. stdout에는 JSON 한 객체(explain 제외), 로그는 stderr. 종료 코드는 04 문서."""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import routing as r

EXIT = {"selected": 0, "completed": 0, "ok": 0, "recorded": 0, "blocked": 10, "timed_out": 11, "waiting": 11,
        "delivery_uncertain": 11, "execution_failed": 12, "result_invalid": 12, "no_eligible_profile": 13,
        "conflict": 14, "partial_failure": 16, "failed": 16}
BUNDLED_CATEGORIES = Path(__file__).with_name("categories.toml")


def _xdg(var, fallback):
    return Path(os.environ.get(var) or Path.home() / fallback) / "bench-router"


def _config(args):
    cfg = r.load_profiles(args.config_dir / "profiles.toml")
    cats = args.config_dir / "categories.toml"
    return cfg, r.load_categories(cats if cats.exists() else BUNDLED_CATEGORIES)


def _load(args):
    task = r.validate_task(r.load_json_strict(args.task, r.TASK_MAX_BYTES))
    cfg, mapping = _config(args)
    context = (r.validate_context(r.load_json_strict(args.context, r.TASK_MAX_BYTES),
                                  [p["id"] for p in cfg["profile"]]) if args.context else None)
    snap, snap_warnings = r.load_snapshot(args.cache_dir)
    if args.cmd == "route" and not args.dry_run:
        from . import herdr  # live 경로에서만
        return herdr.dispatch(task, cfg, mapping, snap, snap_warnings, args.herdr_session,
                              profile_id=args.profile, context=context, selection_mode="orchestrator_pinned")
    now = datetime.now(timezone.utc)
    if args.cmd == "evaluate":
        return (r.evaluate_v1 if args.format == "1" else r.evaluate)(task, cfg, mapping, snap, snap_warnings, now,
                                                                     context=context)
    if args.cmd == "route" and args.profile:
        res = r.evaluate_v1(task, cfg, mapping, snap, snap_warnings, now, context=context)
        return r.pin_selection(res, cfg, args.profile)
    res = r.route(task, cfg, mapping, snap, snap_warnings, now, context=context)
    if args.cmd == "explain":  # 선택은 route, 사실·제약 근거는 evaluate 2.0에서
        res["assessment"] = r.evaluate(task, cfg, mapping, snap, snap_warnings, now, context=context)
    return res


def _parallel(args):
    from . import parallel
    g = parallel.validate_group(r.load_json_strict(args.group, r.TASK_MAX_BYTES * 16))
    cfg, mapping = _config(args)
    snap, snap_warnings = r.load_snapshot(args.cache_dir)
    return parallel.run_group(g, cfg, mapping, snap, snap_warnings, args.herdr_session, dry_run=args.dry_run)


def _collect(args):
    from . import herdr
    return herdr.collect_run(args.cwd, args.run_id, args.wait_ms, args.herdr_session)


def _feedback(args):
    from . import herdr
    return herdr.feedback(args.cwd, args.run_id, args.outcome, args.evaluator, args.note)


def _refresh(args):
    from . import data  # refresh 경로에서만 import (route cold start에 영향 없음)
    cfg, mapping = _config(args)
    aliases = data.load_aliases(args.config_dir / "aliases.toml")
    import_doc = None
    if args.import_file:
        if args.source not in data.SOURCES or not data.SOURCES[args.source].get("manual"):
            raise r.InputError("--import requires --source of a manual source: "
                               + ", ".join(s for s, m in data.SOURCES.items() if m.get("manual")))
        import_doc = data.validate_import(r.load_json_strict(args.import_file, 16 * 1024 * 1024), args.source)
    elif args.source and args.source not in data.AUTO_SOURCES:
        raise r.InputError(f"--source must be one of {data.AUTO_SOURCES} (manual sources need --import)")
    try:
        return data.refresh(args.cache_dir, cfg, mapping, aliases, datetime.now(timezone.utc),
                            only=args.source, force=args.force, import_doc=import_doc)
    except data.LockBusy as e:
        return {"schema_version": r.SCHEMA_VERSION, "status": "conflict", "error": {"code": "lock", "message": str(e)}}


def _status(args):
    from . import data
    try:
        cfg_hash = r.config_hash(*_config(args))
    except r.InputError:
        cfg_hash = None
    return data.status(args.cache_dir, datetime.now(timezone.utc), cfg_hash)


def _metric_text(mid, m):
    if m["freshness"] == "missing":
        return f"{mid} MISSING ({m.get('reason')}) src={m['source']}"
    return (f"{mid}={m['value']}" + (f" {m['unit']}" if m.get("unit") else "") + f" src={m['source']} {m['freshness']}"
            + (f" age_h={m['age_hours']}" if "age_hours" in m else "") + (f" ({m['reason']})" if m.get("reason") else ""))


def _assessment_lines(a):
    """evaluate 2.0의 사실·제약 결과. 순위 정보가 아니다."""
    lines = [f"assessment (registry {a['inputs']['metric_registry_version']}, "
             f"max_estimated_cost_usd={a['max_estimated_cost_usd']}):"]
    lines += [f"  task {_metric_text(k, m)}" for k, m in a["task_facts"].items()]
    for c in a["candidates"]:
        lines.append(f"  {c['profile']}: {'eligible' if c['eligible'] else 'EXCLUDED'}")
        for x in c["constraints"]:
            lines.append(f"    constraint {x['constraint']} {'pass' if x['passed'] else 'FAIL ' + x['code']} "
                         f"{x['metric']}={x['observed']} limit={x['limit']}")
        lines += [f"    fact {_metric_text(k, m)}" for k, m in c["facts"].items()]
        lines += [f"    unrecognized {_metric_text(k, m)}" for k, m in c["unrecognized_metrics"].items()]
    return lines


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
    if res.get("assessment"):
        lines += _assessment_lines(res["assessment"])
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
    ap.add_argument("--herdr-session", default=os.environ.get("BENCH_ROUTER_HERDR_SESSION") or None,
                    help="named herdr session (default: herdr's default session)")
    rp = sub.add_parser("route", help="select a profile and delegate via herdr (--dry-run: select only)")
    rp.add_argument("--task", required=True)
    rp.add_argument("--context", help="Orchestrator metrics: estimates, prices, signals (context JSON 1.0|2.0)")
    rp.add_argument("--profile", help="execute this eligible profile selected by the Orchestrator")
    rp.add_argument("--dry-run", action="store_true")
    vp = sub.add_parser("evaluate", help="report facts, constraint results and evaluations for every profile; no selection")
    vp.add_argument("--task", required=True)
    vp.add_argument("--context", help="Orchestrator metrics: estimates, prices, signals (context JSON 1.0|2.0)")
    vp.add_argument("--format", choices=["1", "2"], default="2",
                    help="output schema; 1 = legacy candidate list (deprecated)")
    ep = sub.add_parser("explain", help="human-readable dry-run with all candidates")
    ep.add_argument("--task", required=True)
    ep.add_argument("--context", help="Orchestrator metrics: estimates, prices, signals (context JSON 1.0|2.0)")
    fp = sub.add_parser("refresh", help="fetch sources and publish the routing snapshot")
    fp.add_argument("--source")
    fp.add_argument("--force", action="store_true", help="ignore TTL")
    fp.add_argument("--import", dest="import_file", help="approved manual observations (swe/tb)")
    sub.add_parser("status", help="source age, failures, unmatched models, snapshot/config state")
    pp = sub.add_parser("parallel", help="dispatch tasks × fanout agents concurrently, each in its own git worktree")
    pp.add_argument("--group", required=True)
    pp.add_argument("--dry-run", action="store_true")
    cp = sub.add_parser("collect", help="observe/collect an existing run; never re-sends the prompt")
    cp.add_argument("--run-id", required=True)
    cp.add_argument("--cwd", required=True)
    cp.add_argument("--wait-ms", type=int, default=0, help="wait while the agent is still working")
    bp = sub.add_parser("feedback", help="record the orchestrator's verified outcome")
    bp.add_argument("--run-id", required=True)
    bp.add_argument("--cwd", required=True)
    bp.add_argument("--outcome", required=True, choices=["success", "partial", "fail"])
    bp.add_argument("--evaluator")
    bp.add_argument("--note")
    args = ap.parse_args(argv)

    try:
        res = {"refresh": _refresh, "status": _status, "collect": _collect, "feedback": _feedback,
                "parallel": _parallel}.get(
            args.cmd, _load)(args)
    except r.InputError as e:
        print(json.dumps({"schema_version": r.SCHEMA_VERSION, "status": "error",
                          "error": {"code": "validation", "message": str(e)}}, ensure_ascii=False))
        return 2
    except (OSError, sqlite3.Error) as e:
        print(json.dumps({"schema_version": r.SCHEMA_VERSION, "status": "error",
                          "error": {"code": "io", "message": str(e)}}, ensure_ascii=False))
        return 15

    if args.cmd == "explain":
        print(explain_text(res))
        return EXIT[res["status"]]
    if args.cmd == "route":
        res["candidates_total"] = len(res["candidates"])
        res["candidates"] = res["candidates"][:3]  # top3 요약, 전체는 explain
    print(json.dumps(res, ensure_ascii=False))
    return EXIT[res["status"]]


if __name__ == "__main__":
    sys.exit(main())
