"""작업군 비교 하네스. (작업, 프로필) 쌍을 한 번씩 live 위임하고 hidden check로 채점한 뒤 정책별로 집계한다.

정책: fixed-default(설정의 default_profile), low-cost-first(cost tier가 가장 낮은 프로필), bench-router(dry-run 선택).
세 정책은 같은 (작업, 프로필) 실행 결과 행렬에서 계산한다 — 같은 작업·환경·예산, 쌍당 표본 1개.

사용: python3 eval/run.py --tag NAME [--only id,id] [--workers 2]   (WSL, herdr session 'breval')
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from workset import TASKS, materialize  # noqa: E402

from bench_router import routing as r  # noqa: E402

SESSION = "breval"
TIER = {"low": 0, "medium": 1, "high": 2}


def cli(*args, timeout=None):
    p = subprocess.run([sys.executable, "-m", "bench_router.cli", "--herdr-session", SESSION, *args],
                       capture_output=True, text=True, cwd=HERE.parent, timeout=timeout)
    try:
        return json.loads(p.stdout), p.returncode
    except ValueError:
        return {"status": "harness_error", "stderr": p.stderr[-500:], "stdout": p.stdout[-500:]}, p.returncode


def task_json(t, cwd, exclude):
    tid, cat, summary, prompt = t[:4]
    return {"schema_version": "1.0", "task_id": tid, "round": 1, "summary": summary, "prompt": prompt, "cwd": str(cwd),
            "categories": {cat: 1}, "category_confidence": 0.9, "priority": "balanced",
            "constraints": {"timeout_ms": 600000, "required_capabilities": ["filesystem_write"]},
            "exclude_profiles": exclude}


def check(tid, d):
    code = ("import json,sys; sys.path.insert(0, sys.argv[1]); from workset import run_check; "
            "print(json.dumps(run_check(sys.argv[2], sys.argv[3])))")
    try:
        p = subprocess.run([sys.executable, "-c", code, str(HERE), tid, str(d)], capture_output=True, text=True, timeout=90)
        return tuple(json.loads(p.stdout.strip().splitlines()[-1]))
    except Exception as e:  # 무한 루프·크래시 = 불합격
        return False, f"check crashed: {type(e).__name__}"


def run_pair(t, pid, profiles, root):
    d = materialize(t, root / pid / t[0])
    spec = root / "tasks" / f"{t[0]}--{pid}.json"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(json.dumps(task_json(t, d, [p for p in profiles if p != pid]), ensure_ascii=False), "utf-8")
    t0 = time.monotonic()
    out, code = cli("route", "--task", str(spec), timeout=900)
    secs = round(time.monotonic() - t0, 1)
    ok, detail = check(t[0], d)
    if out.get("workspace_id"):  # 쌍마다 새 workspace; 결과를 회수했으면 정리
        subprocess.run(["herdr", "--session", SESSION, "workspace", "close", out["workspace_id"]], capture_output=True)
    return {"task": t[0], "category": t[1], "profile": pid, "status": out.get("status"), "exit": code,
            "selection_mode": out.get("selection_mode"), "task_outcome": out.get("task_outcome"),
            "delivery_state": out.get("delivery_state"), "run_id": out.get("run_id"), "seconds": secs,
            "check": ok, "check_detail": str(detail)[:300], "diagnostic_tail": (out.get("diagnostic_tail") or "")[-600:],
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def policies(profiles_cfg, root):
    """정책별 작업→프로필. bench-router는 실제 라우터 dry-run(제외 없음)."""
    ids = [p["id"] for p in profiles_cfg["profile"] if p["enabled"]]
    cheapest = min(ids, key=lambda i: (TIER[next(p for p in profiles_cfg["profile"] if p["id"] == i)["cost_tier"]], i))
    out = {"fixed-default": {}, "low-cost-first": {}, "bench-router": {}}
    for t in TASKS:
        spec = root / "tasks" / f"{t[0]}--dryrun.json"
        spec.write_text(json.dumps(task_json(t, root, []), ensure_ascii=False), "utf-8")
        res, _ = cli("route", "--task", str(spec), "--dry-run")
        out["fixed-default"][t[0]] = profiles_cfg["default_profile"]
        out["low-cost-first"][t[0]] = cheapest
        out["bench-router"][t[0]] = res["selected"]["profile"]
        out.setdefault("_mode", {})[t[0]] = res["selection_mode"]
    return out


def ok(x):
    return bool(x) and x["status"] == "completed" and x["check"]


def report(rows, pol, cfg, tag):
    by = {(x["task"], x["profile"]): x for x in rows}
    tier_proxy = {p["id"]: r.POLICY["tier_proxy"][p["cost_tier"]] for p in cfg["profile"]}
    lines = [f"# 작업군 비교 결과 — {tag}", "",
             f"생성: {datetime.now(timezone.utc).isoformat(timespec='seconds')} · 작업 {len(TASKS)}개 × 프로필 "
             f"{len({x['profile'] for x in rows})}개 · 쌍당 1회 실행 · priority balanced · hidden acceptance check로 채점", "",
             "성공 = 라우터 `completed` **그리고** hidden check 통과 (blocked 등은 Orchestrator가 결과를 받지 못하므로 실패).", "",
             "| 정책 | 성공 | 성공률 | check만 통과 | 평균 시간(s) | 중앙값(s) | cost proxy 합 | 자기보고 success인데 check 실패 |",
             "|---|---|---|---|---|---|---|---|"]
    for name in ("fixed-default", "low-cost-first", "bench-router"):
        sel = [by.get((t[0], pol[name][t[0]])) for t in TASKS]
        sel = [x for x in sel if x]
        secs = [x["seconds"] for x in sel]
        win = sum(ok(x) for x in sel)
        lines.append(f"| {name} | {win}/{len(sel)} | {win / max(1, len(sel)):.0%} | {sum(x['check'] for x in sel) - win} | "
                     f"{statistics.mean(secs):.1f} | {statistics.median(secs):.1f} | "
                     f"{sum(tier_proxy[x['profile']] for x in sel):.1f} | "
                     f"{sum(x['task_outcome'] == 'success' and not x['check'] for x in sel)} |")
    oracle = sum(any(ok(by.get((t[0], p))) for p in tier_proxy) for t in TASKS)
    lines += ["", f"참고 상한(작업마다 통과한 프로필이 하나라도 있으면 성공): {oracle}/{len(TASKS)}", "",
              "## 작업별", "", "| 작업 | 카테고리 | bench-router 선택 (mode) | " + " | ".join(tier_proxy) + " |",
              "|---|---|---|" + "---|" * len(tier_proxy)]
    for t in TASKS:
        cells = []
        for p in tier_proxy:
            x = by.get((t[0], p))
            cells.append("-" if not x else f"{'OK' if ok(x) else 'FAIL'} ({x['status']}, check {'pass' if x['check'] else 'fail'}) {x['seconds']}s")
        lines.append(f"| {t[0]} | {t[1]} | {pol['bench-router'][t[0]]} ({pol['_mode'][t[0]]}) | " + " | ".join(cells) + " |")
    fails = [x for x in rows if not ok(x)]
    if fails:
        lines += ["", "## 실패 상세", ""] + [f"- {x['task']} / {x['profile']}: status={x['status']} outcome={x['task_outcome']} "
                                          f"— {x['check_detail']}" for x in fails]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    cfg = r.load_profiles(Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "bench-router" / "profiles.toml")
    profiles = [p["id"] for p in cfg["profile"] if p["enabled"]]
    root = Path.home() / "br-smoke" / "eval" / a.tag
    root.mkdir(parents=True, exist_ok=True)
    res_file = root / "results.jsonl"
    done = {(x["task"], x["profile"]) for x in map(json.loads, res_file.read_text().splitlines())} if res_file.exists() else set()
    only = set(filter(None, a.only.split(",")))
    todo = {p: [t for t in TASKS if (not only or t[0] in only) and (t[0], p) not in done] for p in profiles}

    def worker(pid):
        for t in todo[pid]:
            row = run_pair(t, pid, profiles, root)
            with open(res_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"[{row['at'][11:19]}] {t[0]:10} {pid:17} {row['status']:18} check={'PASS' if row['check'] else 'FAIL'} {row['seconds']}s", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(worker, profiles))
    rows = list(map(json.loads, res_file.read_text().splitlines()))
    pol = policies(cfg, root)
    out = HERE / "results" / f"{a.tag}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(report(rows, pol, cfg, a.tag), "utf-8")
    (HERE / "results" / f"{a.tag}.jsonl").write_text(res_file.read_text(), "utf-8")
    print(f"report: {out}")


if __name__ == "__main__":
    main()
