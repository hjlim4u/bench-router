"""parallel: group.json → (task × fanout) agent를 각자 git worktree에서 동시에 위임한다.

isolation 수준:
  isolated   — worktree만 공유하지 않음(완전 격리)
  shared     — 그룹 공용 scratchpad(agent별 노트·실험 결과)를 서로 읽음 → 같은 시행착오 방지
각 worktree를 task.cwd로 넘겨 herdr.dispatch의 receipt·잠금·재전송 방지·결과 계약을 그대로 쓴다.
"""
import json
import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from . import herdr, locking
from . import routing as r

ISOLATION = ("isolated", "shared")
GROUP_KEYS = ("schema_version", "group_id", "cwd", "isolation", "fanout", "max_parallel", "tasks")
GROUP_SCHEMA_VERSION = "2.0"  # tasks[i] = {task, context?, selections[]}: Orchestrator가 고른 프로필로 fanout
MAX_AGENTS = 16
ROUND_KEYS = ("status", "round", "run_id", "result_path", "task_outcome", "worktree", "branch", "receipt_path",
              "delivery_state", "reassignment")


def validate_group(raw):
    if not isinstance(raw, dict):
        raise r.InputError("group: JSON object required")
    v2 = raw.get("schema_version") == GROUP_SCHEMA_VERSION
    unknown = set(raw) - set(GROUP_KEYS) | ({"fanout"} & set(raw) if v2 else set())
    if unknown:
        raise r.InputError(f"group: unknown fields {sorted(unknown)}" + (" (2.0: fanout = selections per task)" if v2 else ""))
    missing = [k for k in ("schema_version", "group_id", "cwd", "tasks") if k not in raw]
    if missing:
        raise r.InputError(f"group: missing fields {missing}")
    if raw["schema_version"] not in (r.SCHEMA_VERSION, GROUP_SCHEMA_VERSION):
        raise r.InputError(f"group.schema_version must be {r.SCHEMA_VERSION!r} or {GROUP_SCHEMA_VERSION!r}")
    if not isinstance(raw["group_id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", raw["group_id"]):
        raise r.InputError("group.group_id: [A-Za-z0-9][A-Za-z0-9_-]{0,63} required")
    g = {"schema_version": raw["schema_version"], "group_id": raw["group_id"],
         "isolation": raw.get("isolation", "isolated"),
         "fanout": r._int(raw.get("fanout", 1), "group.fanout", 1, 8),
         "max_parallel": r._int(raw.get("max_parallel", 4), "group.max_parallel", 1, MAX_AGENTS)}
    if g["isolation"] not in ISOLATION:
        raise r.InputError("group.isolation: " + "|".join(ISOLATION))
    cwd = r._str(raw["cwd"], "group.cwd")
    if not os.path.isabs(cwd) or not os.path.isdir(cwd):
        raise r.InputError("group.cwd: existing absolute directory required")
    g["cwd"] = os.path.realpath(cwd)
    tasks = raw["tasks"]
    if not isinstance(tasks, list) or not tasks:
        raise r.InputError("group.tasks: non-empty array required")
    g["raw_tasks"], g["tasks"], g["contexts"], g["selections"] = [], [], [], ([] if v2 else None)
    for i, rt in enumerate(tasks):
        if not isinstance(rt, dict):
            raise r.InputError(f"group.tasks[{i}]: object required")
        if v2:  # context는 프로필 목록이 필요해 plan에서 검증한다(실행 전)
            if set(rt) - {"task", "context", "selections"} or not isinstance(rt.get("task"), dict):
                raise r.InputError(f"group.tasks[{i}]: task, optional context, selections required")
            sels = rt.get("selections")
            if not isinstance(sels, list) or not 1 <= len(sels) <= 8:
                raise r.InputError(f"group.tasks[{i}].selections: 1..8 selections required")
            sels = [r.validate_selection(x) for x in sels]
            g["selections"].append(sels)
            g["contexts"].append(rt.get("context"))
            rt = rt["task"]
        else:
            g["contexts"].append(None)
        if "cwd" in rt:
            raise r.InputError(f"group.tasks[{i}].cwd: set by group.cwd (each agent gets its own worktree)")
        g["raw_tasks"].append(rt)
        g["tasks"].append(r.validate_task({**rt, "cwd": g["cwd"]}))
    agents = sum(len(x) for x in g["selections"]) if v2 else len(tasks) * g["fanout"]
    if agents > MAX_AGENTS:
        raise r.InputError(f"group: total agents (tasks × fanout) must be <= {MAX_AGENTS}")
    if v2:
        g["fanout"] = max(len(x) for x in g["selections"])
    ids = [t["task_id"] for t in g["tasks"]]
    if len(set(ids)) != len(ids):
        raise r.InputError("group.tasks: duplicate task_id")
    return g


def plan(g, cfg, mapping, snap, snap_warnings, availability, decision_options=None, responses=None):
    """1.0(legacy): task마다 route 1회 → selected 다음 후보 순서로 서로 다른 프로필 fanout개.
    2.0: task마다 단건 route --selection과 같은 평가(evaluate_v1 + 제약 + digest)로 Orchestrator 선택을 검사한다.
    digest 기준은 group 수준 task(cwd=group.cwd, 원래 prompt) — Orchestrator도 그 task로 evaluate한다."""
    now = datetime.now(timezone.utc)
    members, warnings = [], []
    options, responses = dict(decision_options or {}), responses or {}
    # Request digests bind the actual dependencies; analysis is reusable across fanout.
    options["decision_cache"] = {}
    used_labels = set()
    for i, t in enumerate(g["tasks"]):
        if g["selections"] is not None:
            res = r.evaluate_v1(t, cfg, mapping, snap, snap_warnings, now, availability, g["contexts"][i])
            for k, sel in enumerate(g["selections"][i], 1):
                if sel["schema_version"] in ("3.0", "4.0"):
                    chk = r.route(t, cfg, mapping, snap, snap_warnings, now, availability, g["contexts"][i],
                                  selection=sel, **options)
                else:
                    chk = r.apply_selection(res, cfg, None, sel)
                members.append({"label": f"{t['task_id']}-{k}", "index": i, "task_id": t["task_id"],
                                "profile": sel["profile"], "selection": sel, "rounds": [],
                                "status": "planned" if chk["status"] == "selected" else chk["status"]})
            continue
        if options.get("policy", "vendor-guided") == "vendor-guided":
            picked = []
            for k in range(1, g["fanout"] + 1):
                label = f"{t['task_id']}-{k}"
                used_labels.add(label)
                res = r.route(t, cfg, mapping, snap, snap_warnings, now, availability,
                              response=responses.get(label), omit_profiles=picked, **options)
                if res["status"] == "no_eligible_profile" and picked:
                    warnings.append(r.warn("fanout_reduced", f"{t['task_id']}: only {len(picked)} eligible profiles"))
                    break
                selected = res.get("selected")
                sel = res.get("selection") if selected else None
                members.append({"label": label, "index": i, "task_id": t["task_id"],
                                "profile": selected["profile"] if selected else None,
                                "selection": {key: val for key, val in sel.items() if key != "source"} if sel else None,
                                "status": "planned" if selected else res["status"], "rounds": [],
                                "decision": res.get("decision")})
                if not selected:
                    break  # Remaining choices depend on this one; generate their packets on the next invocation.
                picked.append(selected["profile"])
            continue
        res = r.route(t, cfg, mapping, snap, snap_warnings, now, availability, **options)
        if res["status"] != "selected":
            members.append({"label": f"{t['task_id']}-1", "index": i, "task_id": t["task_id"], "profile": None,
                            "status": "no_eligible_profile", "rounds": []})
            continue
        sel = res["selected"]["profile"]
        picks = [sel] + [c["profile"] for c in res["candidates"] if c["profile"] != sel][:g["fanout"] - 1]
        if len(picks) < g["fanout"]:
            warnings.append(r.warn("fanout_reduced", f"{t['task_id']}: only {len(picks)} eligible profile(s)"))
        for k, pid in enumerate(picks, 1):
            members.append({"label": f"{t['task_id']}-{k}", "index": i, "task_id": t["task_id"], "profile": pid,
                            "status": "planned", "rounds": []})
    if set(responses) - used_labels:
        raise r.InputError(f"parallel: unknown or not-yet-requested response labels {sorted(set(responses) - used_labels)}")
    return members, warnings


def _git(cwd, *args):
    p = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", shell=False)
    if p.returncode:
        raise r.InputError(f"git {args[0]}: {(p.stderr or p.stdout).strip()[:300]}")
    return p.stdout.strip()


def _same(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def prepare_repo(cwd):
    """cwd는 git 최상위여야 한다. run/worktree 디렉터리가 diff에 섞이지 않게 info/exclude에 등록."""
    if not _same(_git(cwd, "rev-parse", "--show-toplevel"), cwd):
        raise r.InputError("cwd: must be the top level of a git repository")
    exclude = Path(cwd) / _git(cwd, "rev-parse", "--git-common-dir") / "info" / "exclude"
    text = exclude.read_text("utf-8") if exclude.exists() else ""
    if ".bench-router/" not in text.split():
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text(text + ("" if text.endswith("\n") or not text else "\n") + ".bench-router/\n", "utf-8")
    return bool(_git(cwd, "status", "--porcelain"))


def worktree(cwd, gid, label):
    """Projects starts immediately: prepare the cwd before durable task submission."""
    wt = Path(cwd) / ".bench-router" / "worktrees" / gid / label
    if not wt.exists():
        _git(cwd, "worktree", "add", "-b", f"br/{gid}/{label}", str(wt), "HEAD")
    return wt


def collab_text(g, m, labels, shared):
    s = (f"\n\n---\n[bench-router 병렬 실행 — 그룹 {g['group_id']}, 당신은 {m['label']}, 격리 수준 {g['isolation']}]\n"
         "작업 디렉터리는 당신 전용 git worktree입니다. 커밋하지 말고 변경을 작업 트리에 남기세요"
         "(Orchestrator가 비교·병합합니다).\n")
    if g["isolation"] == "isolated":
        return s
    others = ", ".join(x for x in labels if x != m["label"]) or "(없음)"
    return s + (f"동료 agent: {others}\n공용 scratchpad(절대 경로): {shared}\n"
                f"- 당신은 {shared}/{m['label']}.md 와 {shared}/{m['label']}/ 아래에만 쓰고, 다른 파일은 읽기만 하세요.\n"
                "- 시작 전과 새 접근을 시도하기 전에 동료 노트(*.md)를 읽어 이미 실패한 시도를 반복하지 마세요.\n"
                "- 시도한 접근, 실패 원인, 핵심 발견, 중간 실험 결과(명령·수치)를 짧게 계속 추가하세요.\n"
                "- 동료의 worktree는 수정하지 마세요.\n")


def run_group(g, cfg, mapping, snap, snap_warnings, session=None, runner=subprocess.run, which=shutil.which,
              dry_run=False, decision_options=None, responses=None, wait_ms=None):
    gdir = herdr.bench_dir(g["cwd"]) / "groups" / g["group_id"]
    shared = gdir / "shared"
    availability = None if dry_run else herdr.probe_profiles(cfg["profile"], which)
    # Freeze the original input and selections once, then recover from this plan without new provider calls.
    plan_path = gdir / "plan.json"
    group_hash = r.canonical_hash(g)
    if not dry_run and plan_path.exists():
        saved = r.load_json_strict(plan_path, r.SNAPSHOT_MAX_BYTES)
        if saved["group_hash"] != group_hash:
            return {"schema_version": g["schema_version"], "group_id": g["group_id"], "status": "conflict",
                    "warnings": [r.warn("group_conflict", "group inputs differ from the saved execution plan")]}
        members, warnings = saved["members"], saved["warnings"]
        # Existing receipts are recovered even after guide/config changes. Unstarted members must
        # still pass one group-wide preflight, so stale choices cannot produce a partial new fanout.
        for m in members:
            i = m["index"]
            wt = Path(g["cwd"]) / ".bench-router" / "worktrees" / g["group_id"] / m["label"]
            if any(rc["task_id"] == g["tasks"][i]["task_id"] and rc["round"] == g["tasks"][i]["round"]
                   for rc in herdr.receipts(wt)):
                continue
            sel = m.get("selection")
            if sel and sel["schema_version"] in ("3.0", "4.0"):
                opts = {**(decision_options or {}), "allow_network": False, "policy": "vendor-guided"}
                chk = r.route(g["tasks"][i], cfg, mapping, snap, snap_warnings, datetime.now(timezone.utc),
                              availability, g["contexts"][i], selection=sel, **opts)
            else:
                chk = r.evaluate_v1(g["tasks"][i], cfg, mapping, snap, snap_warnings,
                                    datetime.now(timezone.utc), availability, g["contexts"][i])
                chk = r.apply_selection(chk, cfg, m["profile"], sel, mode="parallel_pinned")
            if chk["status"] != "selected":
                m["status"] = chk["status"]
    else:
        members, warnings = plan(g, cfg, mapping, snap, snap_warnings, availability, decision_options, responses)
    out = {"schema_version": g["schema_version"], "group_id": g["group_id"], "isolation": g["isolation"],
           "fanout": g["fanout"], "shared_dir": None if g["isolation"] == "isolated" else str(shared),
           "members": members, "warnings": warnings}
    labels = [m["label"] for m in members if m["status"] == "planned"]
    for m in members:
        m["worktree"] = str(Path(g["cwd"]) / ".bench-router" / "worktrees" / g["group_id"] / m["label"])
        m["branch"] = f"br/{g['group_id']}/{m['label']}"
    if any(m["status"] == "stale_assessment" for m in members):  # 일부만 옛 판단으로 돌리지 않는다
        return {**out, "status": "stale_assessment", "warnings": warnings + [r.warn(
            "stale_assessment", "a selection's assessment_digest no longer matches; re-evaluate the group's tasks")]}
    pending = next((m["status"] for m in members if m["status"] in ("decision_required", "decision_unavailable")), None)
    if pending:
        return {**out, "status": pending}
    if any(m["status"] != "planned" for m in members):
        return {**out, "status": "no_eligible_profile"}
    if dry_run:
        out["status"] = "selected" if labels else "no_eligible_profile"
        return out

    if prepare_repo(g["cwd"]):
        warnings.append(r.warn("dirty_base", "uncommitted changes in cwd are not in the worktrees (based on HEAD)"))
    shared.mkdir(parents=True, exist_ok=True)

    def run(m):
        rt = g["raw_tasks"][m["index"]]
        try:
            wt = worktree(g["cwd"], g["group_id"], m["label"])
            t = r.validate_task({**rt, "cwd": str(wt), "prompt": rt["prompt"] + collab_text(g, m, labels, shared)})
            # worker task는 구조상 cwd(worktree)·prompt(협업 안내)가 group task와 달라 digest를 다시 비교하지 않는다.
            # 판단 입력 검사는 plan에서 끝났고, context·제약·가용성은 dispatch가 다시 검사한다.
            sel = m.get("selection")
            res = herdr.dispatch(t, cfg, mapping, snap, snap_warnings, session, runner, which,
                                 profile_id=m["profile"],
                                 context=g["contexts"][m["index"]], selection=sel,
                                 selection_mode="orchestrator_pinned" if sel else "parallel_pinned",
                                  check_digest=False, decision_options=decision_options, wait_ms=wait_ms,
                                  availability=availability)
            rnd = {k: res.get(k) for k in ROUND_KEYS}
            rnd["round"] = t["round"]
            if res["status"] != "completed":
                rnd["last_observation"], rnd["warnings"] = res.get("last_observation"), res.get("warnings")
        except (r.InputError, OSError) as e:  # 한 member의 실패가 다른 member 결과를 버리지 않게
            rnd = {"status": "error", "round": rt["round"], "error": str(e)}
        m["rounds"].append(rnd)
        m["status"] = rnd["status"]
        m.update({k: rnd[k] for k in ("worktree", "branch") if rnd.get(k)})  # the agent's work lives in the board's

    def run_all(ms):
        with ThreadPoolExecutor(g["max_parallel"]) as ex:
            list(ex.map(run, ms))

    try:
        with locking.exclusive(gdir / "group.lock", herdr.Busy(f"group {g['group_id']} is already running")):
            if plan_path.exists():
                frozen = r.load_json_strict(plan_path, r.SNAPSHOT_MAX_BYTES)
                if frozen["group_hash"] != group_hash or frozen["members"] != members:
                    return {**out, "status": "conflict", "warnings": warnings + [r.warn(
                        "group_plan_changed", "a different plan was saved concurrently; rerun to recover it")]}
            else:
                r.atomic_write(plan_path, json.dumps({"group_hash": group_hash, "members": members, "warnings": warnings},
                                                    ensure_ascii=False).encode("utf-8"))
            run_all([m for m in members if m["status"] == "planned"])
    except herdr.Busy as e:
        return {**out, "status": "conflict", "warnings": warnings + [r.warn("group_lock", str(e))]}
    out["status"] = "completed" if all(m["status"] == "completed" for m in members) else "partial_failure"
    r.atomic_write(gdir / "group.json", json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8"))
    return out
