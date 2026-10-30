"""bench-router CLI. stdout에는 JSON 한 객체(explain 제외), 로그는 stderr. 종료 코드는 04 문서."""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import routing as r

EXIT = {"selected": 0, "completed": 0, "ok": 0, "recorded": 0, "sent": 0, "stop_sent": 0, "blocked": 10, "timed_out": 11, "waiting": 11, "handed_off": 11,
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


def _init(args):
    """Create shared defaults offline, preserving existing configuration."""
    defaults = Path(__file__).with_name("defaults")
    args.config_dir.mkdir(parents=True, exist_ok=True)
    created, kept = [], []
    for name in ("profiles.toml", "aliases.toml"):
        content = (defaults / name).read_bytes()
        path = args.config_dir / name
        try:
            with path.open("xb") as f:
                f.write(content)
        except FileExistsError:
            kept.append(str(path))
        else:
            created.append(str(path))
    return {"schema_version": r.SCHEMA_VERSION, "status": "ok", "created": created, "kept": kept}


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
    refresh_report = None
    if getattr(args, "refresh", False):
        if response is not None:
            raise r.InputError("--refresh is only for the initial assessment; replay responses offline")
        from . import data
        try:
            refresh_report = data.refresh(args.cache_dir, cfg, mapping,
                                          data.load_aliases(args.config_dir / "aliases.toml"),
                                          datetime.now(timezone.utc), env=options["env"], index=options["index"])
        except data.LockBusy as e:
            return {"schema_version": r.SCHEMA_VERSION, "status": "conflict",
                    "error": {"code": "lock", "message": str(e)}}
    snap, snap_warnings = r.load_snapshot(args.cache_dir)
    if args.cmd == "route" and not args.dry_run:
        from . import herdr  # live 경로에서만
        return herdr.dispatch(task, cfg, mapping, snap, snap_warnings, args.herdr_session,
                              profile_id=args.profile, context=context, selection_mode="orchestrator_pinned",
                              selection=selection, decision_options={**options, "allow_network": True},
                              wait_ms=args.wait_ms, backend=herdr.resolve_runner(args.runner))
    now = datetime.now(timezone.utc)
    if args.cmd == "evaluate":
        if args.format == "3":
            from . import decision
            result = decision.evaluate(task, cfg, mapping, snap, snap_warnings, now, context=context, **options)
        else:
            if response is not None:
                raise r.InputError("--decision-response requires evaluate --format 3")
            result = (r.evaluate_v1 if args.format == "1" else r.evaluate)(task, cfg, mapping, snap, snap_warnings, now,
                                                                         context=context)
        if refresh_report is not None:
            result["benchmark_refresh"] = refresh_report
        return result
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


def _prompt_guidance(args):
    """Quoted vendor prompting guide that covers the selected model; the router never rewrites a prompt."""
    from . import decision
    model = args.model
    if args.profile:
        profiles = {p["id"]: p for p in _config(args)[0]["profile"]}
        if args.profile not in profiles:
            raise r.InputError(f"profile {args.profile!r} is not in profiles.toml")
        model = profiles[args.profile]["model_id"]
    guidance = decision.prompt_guidance(decision.load_guidelines(), model)
    return {"schema_version": r.SCHEMA_VERSION, "status": "ok", "profile": args.profile, "prompt_guidance": guidance,
            "warnings": [] if guidance and guidance["items"] else [r.warn("prompt_guidance_missing", f"no vendor prompting guide for {model}")]}


def _select(args):
    from . import decision
    assessment = r.load_json_strict(args.assessment, r.SNAPSHOT_MAX_BYTES)
    selection = decision.bind(assessment, args.profile, {"id": args.policy_id, "version": args.policy_version},
                              args.reason, args.accept_provisional)
    return {"schema_version": r.SCHEMA_VERSION, "status": "ok", "selection": selection}


def _parallel(args):
    from . import herdr, parallel
    g = parallel.validate_group(r.load_json_strict(args.group, r.TASK_MAX_BYTES * 16))
    cfg, mapping = _config(args)
    snap, snap_warnings = r.load_snapshot(args.cache_dir)
    from . import evidence
    responses = (r.load_json_strict(args.decision_response, r.SNAPSHOT_MAX_BYTES) if args.decision_response else {})
    if not isinstance(responses, dict):
        raise r.InputError("parallel decision response: object keyed by member label required")
    return parallel.run_group(g, cfg, mapping, snap, snap_warnings, args.herdr_session, dry_run=args.dry_run, wait_ms=args.wait_ms,
                              backend=herdr.resolve_runner(args.runner),
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
        vault = args.vault if args.vault is not None else WIKI_VAULT
        if args.vault is None and not vault.exists():  # installed package has only the compiled index
            idx = wiki.load_index(args.cache_dir)
            if idx is None:
                raise r.InputError("no usable compiled benchmark index")
            wiki_status = {"status": "ok", "source": "compiled_index", **wiki.summary(idx)}
        else:
            idx = wiki.compile_wiki(vault)
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
        lines.append(f"  {c['profile']}: quality={c['quality']} coverage={c['coverage']} "
                     f"({c['coverage_band']}) exact={c['exact_evidence_weight']}")
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


TASK_HELP = 'UTF-8 JSON file; required: schema_version="1.0", task_id, round, summary, prompt, cwd'
TASK_EPILOG = """task file (replace cwd with your existing absolute repository path):
  {"schema_version":"1.0","task_id":"my-task-001","round":1,
   "summary":"Describe the requested change","prompt":"Full task instructions",
   "cwd":"/absolute/path/to/repo"}
  task_id: unique ID using letters/digits/underscore/hyphen (1..64 characters,
  starting with a letter/digit); round: integer >= 1; summary/prompt: nonempty.
  Optional: context_files (paths within cwd), constraints, priority
  (quality|balanced|cost; default balanced), exclude_profiles, facets,
  execution (interactive|headless; default interactive).
  interactive uses a board agent conversation; headless runs a one-shot CLI
  without approval prompts and cannot receive tell messages.
  facets are task tags as {axis: [value]}; obtain allowed values with wiki facets.
  constraints defaults: max_cost_tier=high (low|medium|high),
  min_context_tokens=0, local_only=false, timeout_ms=900000 (1000..3600000),
  required_capabilities=[]. See examples/task.synthetic.json and docs/reference.md.
  Live execution needs a git repository with a commit; worktrees start at HEAD,
  so uncommitted changes are not included. Keep task_id, round and task content
  stable for recovery; inspect previous effects before starting a new round."""
DECISION_EPILOG = """decision responses (offline calls may return exit 17; this is a handoff):
  Read decision_request (also decision.request) and decision.request_digest.
  When decision.requests is present, run ALL its independent vendor requests
  concurrently, one subagent per packet; send only each packet.request.
  Each reply echoes its own packet.request_digest. Preserve completed siblings
  and append the new replies to stages; reply order within guidance is arbitrary.
  Resolve only the current request using the requested decision provider or the
  calling agent's native decision subagent. --host identifies the CALLER, not
  the coding worker. Use the requested model and verify its actual identity;
  never recursively delegate this decision through bench-router.
  Native replies need --host or an explicit BENCH_ROUTER_DECISION_MODEL override.
  Save a response with every supplied question ID and its requested answer type:
    {"request_digest":"<decision.request_digest>","provider":"subagent",
     "model":"<actual model from host metadata>","answers":{...}}
  Answer shapes: {"type":"choice","choice":"<one supplied criteria key>"}
  or {"type":"noul","noul":0.9} (number 0..1), matching the question's type.
  provider is subagent or jev. Preserve decision.completed entries unchanged;
  append the new response in RESPONSE.json as {"stages":[<completed>,<response>]}.
  Rerun the same command with --decision-response RESPONSE.json. Repeat for each
  analysis, vendor guidance and benchmark stage until no request remains.
  Do not invent model metadata, digests or future stages. For provider setup and
  typed answers, see skills/bench-router/references/decision.md (installed skill:
  references/decision.md); docs/reference.md describes the command contracts."""
RECOVERY_EPILOG = """recovery and verification:
  Read JSON status even on a nonzero exit. Retain run_id and the input cwd.
  For timed_out, waiting or delivery_uncertain, collect the existing run;
  it may still be working. Do not resend the prompt with a new task ID.
  For blocked, inspect the reported approval/question. For conflict, inspect
  the warning and existing receipt before retrying. completed means the result
  artifact contract passed; verify the work before recording feedback.
  Example: bench-router collect --cwd /absolute/path/to/repo --run-id RUN --wait-ms 10000"""
CLI_EPILOG = """choose a command:
  evidence                  inspect benchmark observations without selecting
  evaluate --format 3       assess candidates, then choose with select
  route --dry-run           request a decision or validate a saved selection
  route / collect           execute a task / recover its existing result
  explain                   inspect a human-readable routing diagnosis

first use:
  A profile is a named agent CLI + model + effort configuration in profiles.toml.
  Live dispatch needs Herdr/Projects and the target agent CLI configured on
  Linux/WSL2, and a trusted git repository with a commit. See docs/projects.md.
  1. bench-router init
  2. Create task.json; see "bench-router evaluate --help" for a minimal task.
  3. bench-router evaluate --format 3 --task task.json --host codex > assessment.json
     Replace codex with your calling host. If exit 17 requests a decision,
     follow "evaluate --help" and repeat with --decision-response responses.json.
  4. Once assessment status is ok, choose an eligible suitable profile, then:
     bench-router select --assessment assessment.json --profile PROFILE --policy-id caller --policy-version 1 --reason "Reason for choice" > choice.json
     Save ONLY choice.json's selection object as selection.json (not the wrapper).
  5. bench-router route --task task.json --selection selection.json --dry-run
  6. bench-router route --task task.json --selection selection.json --wait-ms 0
  7. bench-router collect --run-id RUN --cwd DIR --wait-ms 10000
     Use route's run_id and task.json's cwd; repeat collect while still working.
  8. Inspect result_path, verify the work, then record success, partial or fail:
     bench-router feedback --run-id RUN --cwd DIR --outcome success
  Benchmark refresh is separate and uses the network; run it when requested:
     bench-router refresh --source mg
  Routing reads cached evidence and never refreshes it automatically.

output and recovery:
  stdout is one JSON object, except explain and evidence --format table.
  Read status even when exit is nonzero. completed requires verification before
  feedback. For timed_out/delivery_uncertain, collect; keep task_id/round stable.

exit codes:
  0 selected/completed/ok/recorded/sent/stop_sent
  2 invalid input   10 blocked (approval/question)
  11 timed_out/waiting/delivery_uncertain/handed_off (collect existing run; may still run)
  12 execution_failed/result_invalid   13 no eligible profile
  14 conflict/stale assessment   15 I/O or storage error
  16 refresh failed/partially failed or parallel partially failed
  17 decision_required (answer current stage) or decision_unavailable
     (inspect reason; multiple candidates need evaluate --format 3 and select)

Put global options BEFORE the command, e.g. bench-router --cache-dir DIR status.
Run "bench-router COMMAND --help" for standalone instructions and examples."""

COMMAND_EPILOGS = {
    "route": """Use --selection with the selection object returned by select, or omit it to
request vendor-guided selection of a sole suitable profile. Multiple suitable
candidates require evaluate --format 3 and an explicit select. --profile is a
legacy explicit pin that bypasses the staged vendor-guided selection workflow.
--decision-response cannot be combined with --selection or --profile.
Example: bench-router route --task task.json --selection selection.json --dry-run
Then omit --dry-run to execute; --wait-ms 0 returns immediately after submission.
The JSON candidate list is capped at three; use explain to inspect all.""",
    "evaluate": """Start with format 3 for caller-owned profile selection:
  bench-router evaluate --task task.json --format 3 --host codex > assessment.json
  # After resolving the current decision request and saving responses.json:
  bench-router evaluate --task task.json --format 3 --host codex --decision-response responses.json > assessment.json
When status is ok, inspect candidates, suitability, observations and diagnostics;
choose a profile and use select --assessment assessment.json (see select --help).
--decision-response requires --format 3; --host is unused for formats 1 and 2.
All formats are offline: no dispatch, network access or file writes by the router.""",
    "select": """Example (replace PROFILE with a candidate ID from the completed assessment):
  bench-router select --assessment assessment.json --profile PROFILE --policy-id caller --policy-version 1 --reason "Fits task requirements" > choice.json
Save only the output's selection object as selection.json, then:
  bench-router route --task task.json --selection selection.json --dry-run
The assessment_digest binds the record to its evidence; preserve the entire
selection object. Changed inputs may require a new assessment.
provisional means vendor guidance is missing; alternative means the vendor's
other configurations. Either requires explicit --accept-provisional.""",
    "explain": """Example: bench-router explain --task task.json --host codex
Prints all candidates, evidence, constraints and any pending decision as text.
Use evaluate --format 3 for a machine-readable assessment to pass to select.
Offline: no dispatch, network access or file writes.""",
    "evidence": """Example: bench-router evidence --task task.json --format table
Uses cached benchmark observations for task facets (tags); display order is
not a profile ranking. Missing/stale evidence appears in warnings.
Offline: no selection, dispatch, network access or file writes.""",
    "refresh": """Examples:
  bench-router refresh --source mg
  bench-router refresh --source swe --import observations.json
Automatic sources: aa = Artificial Analysis (ARTIFICIAL_ANALYSIS_API_KEY needed),
arena = LMArena (pyarrow needed), mg = The Model Gap. Omitting --source refreshes
all automatic sources. Manual sources swe = SWE-bench and tb = Terminal-Bench
require --import; --import requires --source swe or --source tb.
Compiles the wiki index and updates the shared snapshot. Failed sources keep
last-good data; partial_failure means some sources failed. See docs/reference.md
for the manual observation JSON contract. Run network refresh when requested.""",
    "wiki": """Examples:
  bench-router wiki compile --check
  bench-router wiki compile
  bench-router wiki facets
compile validates reviewed wiki pages and writes the cached index.json unless
--check is set. facets reads the existing cached index and returns allowed
task tags and detection rules; --vault and --check have no effect on facets.""",
    "prompt-guidance": """Choose exactly one target: --profile is an ID from profiles.toml; --model is
a model ID without profile lookup. Prints the vendor guide as JSON; a missing
guide is reported in warnings. No model call or prompt rewrite is performed.
Example: bench-router prompt-guidance --model gpt-6.1""",
    "status": """Example: bench-router status
Inspects the shared cache without fetching benchmarks or executing agents.
Check source ages, failures and warnings before relying on cached evidence.""",
    "init": """Example: bench-router init
Creates profiles.toml and aliases.toml under --config-dir, preserving existing
files. Offline; benchmark refresh and live agent setup are separate steps.""",
    "profiles": """Example: bench-router profiles discover
Queries supported local agent CLIs to build profiles.toml. Existing configuration
is preserved unless --force is supplied. This discovers execution profiles,
not benchmark data; init provides bundled defaults without discovery.""",
    "parallel": """Prefer group schema 2.0 with explicit selections from evaluate/select:
  {"schema_version":"2.0","group_id":"group-001","cwd":"/absolute/path/to/repo",
   "tasks":[{"task":<task object without cwd>,"selections":[<selection object>]}]}
Each task may have optional context. Selection count sets fanout (workers per
task, 1..8); profile IDs may repeat. Do not set a top-level fanout in schema 2.0.
Schema 1.0 also accepts tasks directly and top-level fanout (default 1).
For schema 1.0 pending decisions, read members[].decision.request and
request_digest; preserve each member's completed stages in a response file
keyed by its label: {"task-001-1":{"stages":[<completed>,<response>]}}.
Only include labels already requested; later fanout choices depend on earlier
ones. Schema 2.0 replays its supplied selections instead of taking responses.
Optional isolation: isolated (default) or shared (shared scratchpad);
max_parallel defaults to 4 (1..4), with at most 16 workers across the group.
Example: bench-router parallel --group group.json --dry-run
Then omit --dry-run to execute. Rerun the SAME group to recover existing runs.
No workers start while decisions are pending or stale. Review/merge the member
branches yourself. See docs/reference.md for full group contracts.""",
    "collect": """Supply either --cwd DIR AND --run-id RUN, or one or more --run DIR RUN pairs.
Do not mix these forms. --until applies only to --run; both modes stop at the
wait limit even if their requested completion condition is not yet met.
Examples:
  bench-router collect --cwd /absolute/path/to/repo --run-id RUN --wait-ms 10000
  bench-router collect --run /repo/a RUN_A --run /repo/b RUN_B --until all --wait-ms 10000
For a parallel member, cwd is its router worktree from the group output.""",
    "stop": """Example: bench-router stop --cwd /absolute/path/to/repo --run-id RUN
Requests an explicit stop; subsequent collect reports execution_failed.
For a parallel member use its router worktree, not the agent's inner worktree.""",
    "resume": """Example: bench-router resume --cwd /absolute/path/to/repo --run-id RUN
Reopens the completed agent's conversation without sending a message. Use tell
afterwards to provide new instructions. For parallel use the router worktree.""",
    "tell": """Exactly one of --message or --message-file is required.
Example: bench-router tell --cwd /absolute/path/to/repo --run-id RUN --message "Check the edge case too"
The message file must be nonempty UTF-8 text (at most 120 KiB). A settled run needs
resume first. Headless execution does not accept tell.
For parallel use the member's router worktree, not the agent's inner worktree.""",
    "feedback": """Verify the work yourself before choosing success, partial or fail; completed
only confirms the result artifact contract. Writes feedback for an existing run.
Example: bench-router feedback --cwd /absolute/path/to/repo --run-id RUN --outcome partial --note "One requirement remains"
For parallel use the member's router worktree. Admission acceptance is recorded
separately with coordination feedback.""",
    "coordination": """Shared admission records prevent duplicate/overlapping execution.
  status: inspect records to obtain key, request_hash, active and status.
  release: requires --key, --note and --confirmed-stopped AFTER inspecting the
    worker and its effects. Releases admission only; does not stop a worker.
  feedback: requires --key, --note, --input-hash and --decision. Copy input-hash
    from the record's request_hash. accepted requires completed and inactive.
Examples:
  bench-router coordination status
  bench-router coordination release --key KEY --confirmed-stopped --note "Worker stopped; effects inspected"
  bench-router coordination feedback --key KEY --input-hash HASH --decision accepted --note "Result verified"
This acceptance record is separate from per-run feedback --outcome.""",
}


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):  # WSL은 이미 UTF-8; Windows 콘솔 대비
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="bench-router", formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description="Pick an AI coding agent profile for a task from vendor guides and "
                                             "benchmark evidence, run it in an isolated git worktree, and collect its result.",
                                 epilog=CLI_EPILOG)
    ap.add_argument("--config-dir", type=Path, default=_xdg("XDG_CONFIG_HOME", ".config"),
                    help="shared profiles.toml, aliases.toml and optional categories.toml/env; set before command (default: %(default)s)")
    ap.add_argument("--cache-dir", type=Path, default=_xdg("XDG_CACHE_HOME", ".cache"),
                    help="holds the benchmark snapshot and index (default: %(default)s)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ap.add_argument("--herdr-session", default=os.environ.get("BENCH_ROUTER_HERDR_SESSION") or None,
                    help="Herdr session for dispatch; if supplied on collect, must match the run (default: BENCH_ROUTER_HERDR_SESSION, else unset)")
    ap.add_argument("--runner", choices=("auto", "herdr", "local", "external"),
                    default=os.environ.get("BENCH_ROUTER_RUNNER") or "auto",
                    help="live route/parallel executor: herdr board/pane, local one-shot CLI subprocess (headless tasks), "
                         "or external (returns an invocation; you run the agent, then collect). auto = herdr when "
                         "herdr-projects is on PATH, else local. Recorded runs keep theirs (default: %(default)s)")
    rp = sub.add_parser("route", help="select a profile and delegate via Projects (--dry-run: select only)")
    rp.add_argument("--task", required=True, help=TASK_HELP)
    rp.add_argument("--context", help="optional context JSON file (1.0|2.0) of caller-supplied estimates, prices and signals; see docs/routing-contracts.md")
    pin = rp.add_mutually_exclusive_group()
    pin.add_argument("--selection", help="JSON file containing the complete selection object from select, not its output wrapper; mutually exclusive with --profile")
    pin.add_argument("--profile", help="explicit eligible profile ID from profiles.toml; legacy pin without a selection record (warns); exclusive with --selection")
    rp.add_argument("--dry-run", action="store_true", help="select only; no network, herdr or file writes")
    rp.add_argument("--wait-ms", type=_wait_ms, help="nonnegative milliseconds to wait after submission; default: task deadline (constraints.timeout_ms, default 900000); 0: return at once, collect later; unused with --dry-run")
    vp = sub.add_parser("evaluate", help="report facts, constraint results and evaluations for every profile; no selection")
    vp.add_argument("--task", required=True, help=TASK_HELP)
    vp.add_argument("--context", help="optional context JSON file (1.0|2.0) of caller-supplied estimates, prices and signals; see docs/routing-contracts.md")
    vp.add_argument("--refresh", action="store_true", help="check due benchmark sources before the initial assessment; report failures and keep last-good data; omit when replaying decision responses")
    vp.add_argument("--format", choices=["1", "2", "3"], default="2",
                    help="output format: 1 = legacy candidate evidence; 2 = facts, constraints and benchmark evaluations (default); 3 = staged vendor-guided assessment for select; offline unless --refresh")
    selp = sub.add_parser("select", help="record an upstream choice from an evaluate --format 3 assessment; no dispatch")
    selp.add_argument("--assessment", required=True, help="saved output of evaluate --format 3 (status ok)")
    selp.add_argument("--profile", required=True, help="the chosen profile ID from the assessment")
    selp.add_argument("--policy-id", required=True, help="name of the caller's selection policy")
    selp.add_argument("--policy-version", required=True, help="version of that policy")
    selp.add_argument("--reason", required=True, help="why this profile was chosen; stored in the record")
    selp.add_argument("--accept-provisional", action="store_true",
                      help="allow a provisional or alternative (not vendor-documented) profile")
    ep = sub.add_parser("explain", help="human-readable dry-run with all candidates")
    ep.add_argument("--task", required=True, help=TASK_HELP)
    ep.add_argument("--context", help="optional context JSON file (1.0|2.0) of caller-supplied estimates, prices and signals; see docs/routing-contracts.md")
    xp = sub.add_parser("evidence", help="benchmark evidence for the task's facets, per profile; no selection")
    xp.add_argument("--task", required=True, help=TASK_HELP)
    xp.add_argument("--max-units", type=int, default=12, help="maximum benchmark measurement units to show; integer >= 1 (default: %(default)s)")
    xp.add_argument("--format", choices=["json", "table"], default="json", help="output as a JSON object or readable text table (default: %(default)s)")
    fp = sub.add_parser("refresh", help="fetch sources and publish the routing snapshot")
    fp.add_argument("--source", help="aa, arena, mg or tb_auto for automatic collection; swe or tb requires --import FILE (default: all automatic sources)")
    fp.add_argument("--force", action="store_true", help="fetch again even if cached source data has not expired (ignore TTL)")
    fp.add_argument("--import", dest="import_file", help="JSON file of approved manual observations; requires --source swe or --source tb")
    fp.add_argument("--vault", type=Path, help="benchmark wiki to compile; defaults to the clone wiki or installed index")
    wp = sub.add_parser("wiki", help="compile reviewed benchmark wiki pages into index.json, or list taggable facets")
    wp.add_argument("action", choices=["compile", "facets"], help="compile reviewed pages into the cache, or list allowed task facet tags from the cached index")
    wp.add_argument("--vault", type=Path, default=WIKI_VAULT, help="wiki directory for compile only; ignored by facets (default: %(default)s)")
    wp.add_argument("--check", action="store_true", help="compile: validate only, without writing index.json; ignored by facets")
    pgp = sub.add_parser("prompt-guidance", help="the selected model's vendor prompting guide, quoted; offline, rewrites nothing")
    target = pgp.add_mutually_exclusive_group(required=True)
    target.add_argument("--profile", help="profile ID from profiles.toml; look up its model's guide; choose this or --model")
    target.add_argument("--model", help="model ID whose vendor guide to quote; no profile lookup; choose this or --profile")
    sub.add_parser("status", help="source age, failures, unmatched models, snapshot/config state")
    sub.add_parser("init", help="create shared default profiles and aliases offline; keep existing files")
    profiles = sub.add_parser("profiles", help="create profiles.toml from every model each CLI's model flag accepts")
    profiles.add_argument("action", choices=["discover"], help="discover model/effort execution profiles from supported local agent CLIs and write profiles.toml")
    profiles.add_argument("--force", action="store_true", help="replace an existing profiles.toml")
    pp = sub.add_parser("parallel", help="dispatch tasks × fanout agents concurrently, each in its own git worktree")
    pp.add_argument("--group", required=True, help="group JSON file (1.0|2.0) of tasks and worker allocations; schema 2.0 uses selections per task; see example below")
    pp.add_argument("--dry-run", action="store_true", help="plan/validate only; no network, herdr calls, worktrees or file writes")
    pp.add_argument("--wait-ms", type=_wait_ms, help="nonnegative milliseconds to wait per member; default: each task deadline (constraints.timeout_ms, default 900000); 0: return after submission; rerun the same group to collect; unused with --dry-run")
    for parser in (rp, ep, pp, vp):
        parser.add_argument("--host", choices=["antigravity", "codex", "claude"], help="calling agent's host for native decision model selection/verification (not worker profile); default: generic host policy; evaluate: format 3 only")
        parser.add_argument("--decision-response", help='JSON file: {"stages":[responses in request order]} or one response; parallel: keyed by member label; evaluate requires --format 3; see decision workflow below')
    cp = sub.add_parser("collect", help="observe/collect an existing run; never re-sends the prompt")
    cp.add_argument("--run-id", help="existing run ID printed by route; requires --cwd; cannot combine with --run")
    cp.add_argument("--cwd", help="the run's input repository path; requires --run-id; for parallel use the member's router worktree")
    cp.add_argument("--run", nargs=2, action="append", metavar=("CWD", "RUN_ID"),
                    help="repeatable: collect several runs, returning when --until is met")
    cp.add_argument("--until", choices=["any", "all"], default="any", help="with --run only: wait for first settled/blocked run (any) or all runs (all), up to --wait-ms (default: %(default)s)")
    cp.add_argument("--wait-ms", type=_wait_ms, default=0, help="nonnegative milliseconds to observe/wait for existing runs; 0 checks once (default: %(default)s)")
    stp = sub.add_parser("stop", help="stop a live run: board stop, or close a headless run's pane; logged, never automatic")
    stp.add_argument("--cwd", required=True, help="run cwd; a parallel member's router worktree when --run-id is omitted")
    stp.add_argument("--run-id", help="defaults to the only unsettled run under --cwd")
    sp = sub.add_parser("resume", help="reopen a completed run's agent in the same conversation; sends nothing")
    sp.add_argument("--run-id", required=True, help="completed run ID whose agent conversation to reopen")
    sp.add_argument("--cwd", required=True, help="the run's input repository path; for parallel use the member's router worktree")
    tp = sub.add_parser("tell", help="relay one explicit message to a live run's agent (board tell); logged, never automatic")
    tp.add_argument("--cwd", required=True, help="run cwd; a parallel member's worktree when --run-id is omitted")
    tp.add_argument("--run-id", help="defaults to the only unsettled run under --cwd")
    tp.add_argument("--message", help="nonempty text to send (up to 120 KiB); exactly one of --message or --message-file is required")
    tp.add_argument("--message-file", help="UTF-8 text file to send (up to 120 KiB); exactly one of --message or --message-file is required")
    bp = sub.add_parser("feedback", help="record the orchestrator's verified outcome")
    bp.add_argument("--run-id", required=True, help="run ID printed by route")
    bp.add_argument("--cwd", required=True, help="the task's repository root")
    bp.add_argument("--outcome", required=True, choices=["success", "partial", "fail"], help="verified task result")
    bp.add_argument("--evaluator", help="who verified it, e.g. orchestrator")
    bp.add_argument("--note", help="free-text note")
    cc = sub.add_parser("coordination", help="shared admission records and explicit post-inspection resolution")
    cc.add_argument("action", choices=["status", "release", "feedback"], help="inspect admission records, release an inspected stopped worker's admission, or record acceptance")
    cc.add_argument("--key", help="record key from coordination status; required for release and feedback")
    cc.add_argument("--confirmed-stopped", action="store_true", help="release only: required confirmation that the worker stopped and its effects were inspected; does not stop it")
    cc.add_argument("--note", help="nonempty inspection/verification reason; required for release and feedback")
    cc.add_argument("--input-hash", help="feedback only: required request_hash from the inspected record; must match")
    cc.add_argument("--decision", choices=["accepted", "withheld", "rejected"], help="feedback only: required acceptance decision; accepted requires completed and inactive")
    for command in sub._choices_actions:
        parser = sub.choices[command.dest]
        parser.description = command.help
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        sections = [COMMAND_EPILOGS[command.dest]]
        if parser in (rp, ep, pp, vp):
            sections.append(DECISION_EPILOG)
        if parser in (rp, ep, xp, vp):
            sections.append(TASK_EPILOG)
        if parser in (rp, pp, cp):
            sections.append(RECOVERY_EPILOG)
        sections.append("Global options (--config-dir, --cache-dir, --herdr-session, --runner) go BEFORE the command.")
        parser.epilog = "\n\n".join(sections)
    args = ap.parse_args(argv)

    try:
        res = {"init": _init, "refresh": _refresh, "status": _status, "profiles": _profiles, "collect": _collect, "resume": _resume, "tell": _tell, "stop": _stop, "feedback": _feedback,
                "parallel": _parallel, "select": _select, "coordination": _coordination, "wiki": _wiki,
                "evidence": _evidence, "prompt-guidance": _prompt_guidance}.get(
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
