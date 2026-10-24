"""bench-router CLI. stdout에는 JSON 한 객체(explain 제외), 로그는 stderr. 종료 코드는 04 문서."""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import routing as r

EXIT = {"selected": 0, "completed": 0, "ok": 0, "recorded": 0, "sent": 0, "stop_sent": 0, "blocked": 10, "timed_out": 11, "waiting": 11,
        "delivery_uncertain": 11, "execution_failed": 12, "result_invalid": 12, "no_eligible_profile": 13,
        "conflict": 14, "stale_assessment": 14, "partial_failure": 16, "failed": 16,
        "decision_required": 17, "decision_unavailable": 17}
BUNDLED_CATEGORIES = Path(__file__).with_name("categories.toml")
WIKI_VAULT = Path(__file__).resolve().parent.parent / "wiki"


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
    selection = (r.validate_selection(r.load_json_strict(args.selection, r.SNAPSHOT_MAX_BYTES))
                 if getattr(args, "selection", None) else None)
    response = (r.load_json_strict(args.decision_response, r.SNAPSHOT_MAX_BYTES)
                if getattr(args, "decision_response", None) else None)
    from . import evidence
    options = {"host": getattr(args, "host", None),
               "response": response, "index": evidence.load_index(args.cache_dir),
               "env": r.env_with_dotenv(args.config_dir, task["cwd"])}
    if response is not None and (selection or getattr(args, "profile", None)):
        raise r.InputError("--decision-response cannot be combined with --selection or --profile")
    snap, snap_warnings = r.load_snapshot(args.cache_dir)
    if args.cmd == "route" and not args.dry_run:
        from . import herdr  # live 경로에서만
        return herdr.dispatch(task, cfg, mapping, snap, snap_warnings, args.herdr_session,
                              profile_id=args.profile, context=context, selection_mode="orchestrator_pinned",
                              selection=selection, decision_options={**options, "allow_network": True},
                              wait_ms=args.wait_ms)
    now = datetime.now(timezone.utc)
    if args.cmd == "evaluate":
        if args.format == "3":
            from . import decision
            return decision.evaluate(task, cfg, mapping, snap, snap_warnings, now, context=context, **options)
        if response is not None:
            raise r.InputError("--decision-response requires evaluate --format 3")
        return (r.evaluate_v1 if args.format == "1" else r.evaluate)(task, cfg, mapping, snap, snap_warnings, now,
                                                                     context=context)
    if args.cmd == "route" and (args.profile or selection):
        if selection and selection["schema_version"] in r.GUIDED_SELECTIONS:
            return r.route(task, cfg, mapping, snap, snap_warnings, now, context=context,
                           selection=selection, **options)
        res = r.evaluate_v1(task, cfg, mapping, snap, snap_warnings, now, context=context)
        return r.apply_selection(res, cfg, args.profile, selection)
    res = r.route(task, cfg, mapping, snap, snap_warnings, now, context=context, **options)
    if args.cmd == "explain":  # 선택은 route, 사실·제약 근거는 evaluate 2.0에서
        res["assessment"] = r.evaluate(task, cfg, mapping, snap, snap_warnings, now, context=context)
    return res


def _select(args):
    from . import decision
    assessment = r.load_json_strict(args.assessment, r.SNAPSHOT_MAX_BYTES)
    selection = decision.bind(assessment, args.profile, {"id": args.policy_id, "version": args.policy_version},
                              args.reason, args.accept_provisional)
    return {"schema_version": r.SCHEMA_VERSION, "status": "ok", "selection": selection}


def _parallel(args):
    from . import parallel
    g = parallel.validate_group(r.load_json_strict(args.group, r.TASK_MAX_BYTES * 16))
    cfg, mapping = _config(args)
    snap, snap_warnings = r.load_snapshot(args.cache_dir)
    from . import evidence
    responses = (r.load_json_strict(args.decision_response, r.SNAPSHOT_MAX_BYTES) if args.decision_response else {})
    if not isinstance(responses, dict):
        raise r.InputError("parallel decision response: object keyed by member label required")
    return parallel.run_group(g, cfg, mapping, snap, snap_warnings, args.herdr_session, dry_run=args.dry_run, wait_ms=args.wait_ms,
                              decision_options={"host": args.host,
                                                "index": evidence.load_index(args.cache_dir),
                                                "allow_network": not args.dry_run,
                                                "env": r.env_with_dotenv(args.config_dir, g["cwd"])},
                              responses=responses)


def _collect(args):
    from . import herdr
    if args.run:
        if args.cwd or args.run_id:
            raise r.InputError("collect: use either --cwd/--run-id or repeated --run CWD RUN_ID")
        return herdr.collect_many([tuple(x) for x in args.run], args.wait_ms, args.until, args.herdr_session)
    if not (args.cwd and args.run_id):
        raise r.InputError("collect: --cwd and --run-id required (or repeated --run CWD RUN_ID)")
    return herdr.collect_run(args.cwd, args.run_id, args.wait_ms, args.herdr_session)


def _stop(args):
    from . import herdr
    return herdr.stop_run(args.cwd, args.run_id)


def _wait_ms(v):
    if int(v) < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return int(v)


def _tell(args):
    from . import herdr
    if (args.message is None) == (args.message_file is None):
        raise r.InputError("tell: exactly one of --message or --message-file required")
    text = args.message
    if text is None:
        path = Path(args.message_file)
        if path.stat().st_size > herdr.MAX_PROMPT_ARG_BYTES:
            raise r.InputError(f"message file over {herdr.MAX_PROMPT_ARG_BYTES} bytes")
        text = path.read_text("utf-8")
    return herdr.tell_run(args.cwd, args.run_id, text)


def _resume(args):
    from . import herdr
    try:
        return {**herdr.resume_run(args.cwd, args.run_id), "status": "ok"}
    except herdr.Busy as e:
        return {"schema_version": r.SCHEMA_VERSION, "status": "conflict", "run_id": args.run_id,
                "warnings": [r.warn("dispatch_lock", str(e))]}


def _feedback(args):
    from . import herdr
    return herdr.feedback(args.cwd, args.run_id, args.outcome, args.evaluator, args.note)


def _coordination(args):
    from . import coordination as co
    try:
        if args.action == "status":
            return co.inspect()
        if not args.key or not args.note:
            raise r.InputError("coordination mutation requires --key and --note")
        if args.action == "release":
            if not args.confirmed_stopped:
                raise r.InputError("release requires --confirmed-stopped after inspecting worker and effects")
            rec = co.resolve(args.key, args.note)
        else:
            rec = co.feedback(args.key, args.input_hash, args.decision, args.note)
        return {"schema_version": "1.0", "status": "recorded", "record": rec}
    except co.Conflict as e:
        return {"schema_version": "1.0", "status": "conflict", "error": {"code": "coordination", "message": str(e)}}


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
    from . import wiki
    try:  # Wiki 오류는 snapshot 갱신을 막지 않는다. 이전 index.json을 그대로 두고 그 수집 대상을 쓴다
        idx = wiki.compile_wiki(args.vault)
        wiki_status = {"status": "ok", **wiki.summary(idx)}
    except r.InputError as e:
        idx, wiki_status = wiki.load_index(args.cache_dir), {"status": "error", "error": {"code": "validation", "message": str(e)}}
    try:
        res = data.refresh(args.cache_dir, cfg, mapping, aliases, datetime.now(timezone.utc),
                           only=args.source, force=args.force, import_doc=import_doc, index=idx,
                           env=r.env_with_dotenv(args.config_dir))
    except data.LockBusy as e:
        return {"schema_version": r.SCHEMA_VERSION, "status": "conflict", "error": {"code": "lock", "message": str(e)}}
    if wiki_status["status"] == "ok":
        wiki.write_index(args.cache_dir, idx)
    res["wiki_index"] = wiki_status
    return res


def _evidence(args):
    from . import evidence
    if args.max_units < 1:
        raise r.InputError("--max-units must be >= 1")
    t = r.validate_task(r.load_json_strict(args.task, r.TASK_MAX_BYTES))
    return evidence.build(t, r.load_profiles(args.config_dir / "profiles.toml"), *r.load_snapshot(args.cache_dir),
                          evidence.load_index(args.cache_dir), datetime.now(timezone.utc), args.max_units)


def _wiki(args):
    from . import wiki
    if args.action == "facets":  # 자동 판정 규칙이 있어도 Orchestrator가 직접 지정할 수 있다.
        from . import evidence
        idx = evidence.load_index(args.cache_dir)
        if idx is None:
            raise r.InputError("no index.json; run `wiki compile`")
        facets = {a: {v: f for v, f in vs.items() if f"{a}:{v}" in idx["postings"]}
                  for a, vs in idx["facets"].items()}
        return {"schema_version": r.SCHEMA_VERSION, "status": "ok", "wiki_hash": idx["wiki_hash"],
                "facets": {a: {v: f["desc"] for v, f in vs.items()} for a, vs in facets.items()},
                "detection": {a: {v: f["detect"] for v, f in vs.items()} for a, vs in facets.items()}}
    idx = wiki.compile_wiki(args.vault)
    path = None if args.check else str(wiki.write_index(args.cache_dir, idx))
    return {"schema_version": r.SCHEMA_VERSION, "status": "ok", "written": path, **wiki.summary(idx)}


def _status(args):
    from . import data
    try:
        cfg_hash = r.config_hash(*_config(args))
    except r.InputError:
        cfg_hash = None
    return data.status(args.cache_dir, datetime.now(timezone.utc), cfg_hash)


def _profiles(args):
    from . import herdr
    path = args.config_dir / "profiles.toml"
    if path.exists() and not args.force:
        raise r.InputError(f"{path} exists; use profiles discover --force to replace it")
    profiles = herdr.discover_profiles()
    path.parent.mkdir(parents=True, exist_ok=True)
    r.atomic_write(path, herdr.profiles_toml(profiles).encode("utf-8"))
    return {"schema_version": r.SCHEMA_VERSION, "status": "ok", "written": str(path),
            "profiles": [p["id"] for p in profiles]}


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
             f"classification: {cls['stage']} {cls['categories']}"
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
    if res.get("decision"):
        lines += ["decision: " + json.dumps(res["decision"], ensure_ascii=False)]
    if res.get("selection"):
        lines += ["selection: " + json.dumps(res["selection"], ensure_ascii=False)]
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
                    help="record this Herdr session with each run and require it on collect")
    rp = sub.add_parser("route", help="select a profile and delegate via Projects (--dry-run: select only)")
    rp.add_argument("--task", required=True)
    rp.add_argument("--context", help="Orchestrator metrics: estimates, prices, signals (context JSON 1.0|2.0)")
    pin = rp.add_mutually_exclusive_group()
    pin.add_argument("--selection", help="Orchestrator selection record (JSON: profile, assessment_digest, policy, reason)")
    pin.add_argument("--profile", help="execute this eligible profile without a selection record (warns)")
    rp.add_argument("--dry-run", action="store_true")
    rp.add_argument("--wait-ms", type=_wait_ms, help="after submission, wait at most this long (0: return at once; collect later)")
    vp = sub.add_parser("evaluate", help="report facts, constraint results and evaluations for every profile; no selection")
    vp.add_argument("--task", required=True)
    vp.add_argument("--context", help="Orchestrator metrics: estimates, prices, signals (context JSON 1.0|2.0)")
    vp.add_argument("--format", choices=["1", "2", "3"], default="2",
                    help="output schema; 3 = staged vendor-guided candidate assessment (offline)")
    selp = sub.add_parser("select", help="record an upstream choice from an evaluate --format 3 assessment; no dispatch")
    selp.add_argument("--assessment", required=True)
    selp.add_argument("--profile", required=True)
    selp.add_argument("--policy-id", required=True)
    selp.add_argument("--policy-version", required=True)
    selp.add_argument("--reason", required=True)
    selp.add_argument("--accept-provisional", action="store_true")
    ep = sub.add_parser("explain", help="human-readable dry-run with all candidates")
    ep.add_argument("--task", required=True)
    ep.add_argument("--context", help="Orchestrator metrics: estimates, prices, signals (context JSON 1.0|2.0)")
    xp = sub.add_parser("evidence", help="benchmark evidence for the task's facets, per profile; no selection")
    xp.add_argument("--task", required=True)
    xp.add_argument("--max-units", type=int, default=12)
    xp.add_argument("--format", choices=["json", "table"], default="json")
    fp = sub.add_parser("refresh", help="fetch sources and publish the routing snapshot")
    fp.add_argument("--source")
    fp.add_argument("--force", action="store_true", help="ignore TTL")
    fp.add_argument("--import", dest="import_file", help="approved manual observations (swe/tb)")
    fp.add_argument("--vault", type=Path, default=WIKI_VAULT, help="benchmark wiki compiled into index.json")
    wp = sub.add_parser("wiki", help="compile reviewed benchmark wiki pages into index.json, or list taggable facets")
    wp.add_argument("action", choices=["compile", "facets"])
    wp.add_argument("--vault", type=Path, default=WIKI_VAULT)
    wp.add_argument("--check", action="store_true", help="validate only; do not write index.json")
    sub.add_parser("status", help="source age, failures, unmatched models, snapshot/config state")
    profiles = sub.add_parser("profiles", help="create profiles.toml from CodeBurn-observed models")
    profiles.add_argument("action", choices=["discover"])
    profiles.add_argument("--force", action="store_true", help="replace an existing profiles.toml")
    pp = sub.add_parser("parallel", help="dispatch tasks × fanout agents concurrently, each in its own git worktree")
    pp.add_argument("--group", required=True)
    pp.add_argument("--dry-run", action="store_true")
    pp.add_argument("--wait-ms", type=_wait_ms, help="per member, wait at most this long after submission; rerun the group to collect")
    for parser in (rp, ep, pp, vp):
        parser.add_argument("--host", choices=["antigravity", "codex", "claude"], help="native decision agent host")
        parser.add_argument("--decision-response", help="saved ordered stages array of responses (digest, provider, actual model, answers); parallel: keyed by member label")
    cp = sub.add_parser("collect", help="observe/collect an existing run; never re-sends the prompt")
    cp.add_argument("--run-id")
    cp.add_argument("--cwd")
    cp.add_argument("--run", nargs=2, action="append", metavar=("CWD", "RUN_ID"),
                    help="repeatable: collect several runs, returning when --until is met")
    cp.add_argument("--until", choices=["any", "all"], default="any", help="with --run: first settled/blocked, or all")
    cp.add_argument("--wait-ms", type=_wait_ms, default=0, help="wait while the agent is still working")
    stp = sub.add_parser("stop", help="stop a live run: board stop, or close a headless run's pane; logged, never automatic")
    stp.add_argument("--cwd", required=True, help="run cwd; a parallel member's router worktree when --run-id is omitted")
    stp.add_argument("--run-id", help="defaults to the only unsettled run under --cwd")
    sp = sub.add_parser("resume", help="reopen a completed run's agent in the same conversation; sends nothing")
    sp.add_argument("--run-id", required=True)
    sp.add_argument("--cwd", required=True)
    tp = sub.add_parser("tell", help="relay one explicit message to a live run's agent (board tell); logged, never automatic")
    tp.add_argument("--cwd", required=True, help="run cwd; a parallel member's worktree when --run-id is omitted")
    tp.add_argument("--run-id", help="defaults to the only unsettled run under --cwd")
    tp.add_argument("--message")
    tp.add_argument("--message-file")
    bp = sub.add_parser("feedback", help="record the orchestrator's verified outcome")
    bp.add_argument("--run-id", required=True)
    bp.add_argument("--cwd", required=True)
    bp.add_argument("--outcome", required=True, choices=["success", "partial", "fail"])
    bp.add_argument("--evaluator")
    bp.add_argument("--note")
    cc = sub.add_parser("coordination", help="shared admission records and explicit post-inspection resolution")
    cc.add_argument("action", choices=["status", "release", "feedback"])
    cc.add_argument("--key")
    cc.add_argument("--confirmed-stopped", action="store_true")
    cc.add_argument("--note")
    cc.add_argument("--input-hash")
    cc.add_argument("--decision", choices=["accepted", "withheld", "rejected"])
    args = ap.parse_args(argv)

    try:
        res = {"refresh": _refresh, "status": _status, "profiles": _profiles, "collect": _collect, "resume": _resume, "tell": _tell, "stop": _stop, "feedback": _feedback,
                "parallel": _parallel, "select": _select, "coordination": _coordination, "wiki": _wiki,
                "evidence": _evidence}.get(
            args.cmd, _load)(args)
    except r.InputError as e:
        print(json.dumps({"schema_version": r.SCHEMA_VERSION, "status": "error",
                          "error": {"code": "validation", "message": str(e)}}, ensure_ascii=False))
        return 2
    except (OSError, sqlite3.Error) as e:
        print(json.dumps({"schema_version": r.SCHEMA_VERSION, "status": "error",
                          "error": {"code": "io", "message": str(e)}}, ensure_ascii=False))
        return 15

    if args.cmd == "evidence" and args.format == "table":
        from . import evidence
        print(evidence.table(res))
        return 0
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
