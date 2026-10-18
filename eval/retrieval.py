"""벤치마크 탐색 성능 실험(계획: 프롬프트 태깅 · 벤치마크 인덱싱 · 관련 벤치마크 필터링 · LLM 토큰).

gold는 eval/retrieval_cases.json, eval/unit_gold.json (labeled=true만 채점). LLM 호출은 하지 않는다:
packets가 decide 요청을 쓰고, 운영자가 decide.py(Jev) 또는 native bench-decider로 받은 응답을
<case>~<part>.r<N>.json 으로 저장하면 score가 decide.validate_response로 검증한 뒤 채점한다.
응답 파일의 usage {input_tokens, output_tokens}가 실측 토큰이다(subagent는 host 메타데이터에서 옮겨 적는다).

사용:
  python3 eval/retrieval.py index-audit
  python3 eval/retrieval.py filter [--tags gold|rule|DIR:VARIANT:REP] [--threshold 0.5]
  python3 eval/retrieval.py packets --tag T --stage tag|unit|choice [--from rule_llm --rep 1]
  python3 eval/retrieval.py run --tag T --stage tag|unit|choice [--reps 3]   (Jev 호출, env에 JEV_API_KEY 필요)
  python3 eval/retrieval.py score --tag T [--reps 3]
  python3 eval/retrieval.py selftest
"""
import argparse
import copy
import importlib.util
import json
import math
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from workset import TASKS  # noqa: E402

from bench_router import evidence, routing as r  # noqa: E402

_spec = importlib.util.spec_from_file_location("decide", HERE.parent / "skills/bench-router/scripts/decide.py")
decide = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(decide)

OUT = HERE / "results" / "retrieval"
CASES = HERE / "retrieval_cases.json"  # --cases로 교체(보류 검증 세트 등)
KS = (6, 12, 24)
TAG_VARIANTS = ("llm_all", "rule_llm", "rule_llm_axis", "rule_llm_v2")  # (b) 전체, (c) rule이 켠 것 제외, (c) 축별, (c)+경계 사례
# v2: jev1에서 과잉 태깅된 facet에 경계 사례를 붙인다. skills/bench-router/references/decision.md 2항과 같은 문구를 유지한다.
# script 규칙 언어는 결정적이라 묻지 않는다.
BOUNDARY = {
    "task:instruction_following": "1 only if the main challenge is obeying explicit output constraints (exact length, count, "
                                  "ordering, format, forbidden words). 0 for ordinary tasks that merely state requirements.",
    "difficulty:hard_prompts": "Most routine coding, writing, or lookup tasks are 0, even when well specified.",
    "domain:software_it": "1 only if the subject matter is software or IT itself; 0 when code is merely a tool for another subject.",
    "task:math": "1 only if the main work is mathematical derivation or calculation, not incidental arithmetic.",
    "domain:mathematical": "1 only if the subject matter is mathematics.",
    "task:ocr_parse": "1 only if the input is a scanned or photographed document whose text must be converted to structured output.",
    "task:vision_ocr": "1 only if an image is attached and the answer comes from text inside that image.",
}
THRESHOLDS = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)


def _xdg(var, fallback):
    import os
    return Path(os.environ.get(var) or Path.home() / fallback) / "bench-router"


def est_tokens(text):
    return len(text) // 4  # evidence.rule_hit과 같은 근사. 실측 usage와의 오차를 score가 보고한다


# ---------- 데이터 ----------
def load_cases(labeled_only=True):
    ws = {t[0]: t for t in TASKS}
    out = []
    for c in json.loads(CASES.read_text("utf-8"))["cases"]:
        if "workset" in c:
            t = ws[c["workset"]]
            c = {**c, "summary": t[2], "prompt": t[3], "context_files": sorted(t[4])}
        if c["labeled"] or not labeled_only:
            out.append(c)
    return out


def task(c, facets=None):
    return {"task_id": c["id"], "round": 1, "summary": c["summary"], "prompt": c["prompt"],
            "context_files": c["context_files"], "facets": facets or {}}


def to_axes(keys):
    out = {}
    for k in sorted(keys):
        a, v = k.split(":", 1)
        out.setdefault(a, []).append(v)
    return out


def always_facets(index):
    return {f"{a}:{v}" for a, vs in index["facets"].items() for v, f in vs.items() if f["detect"] == "rule:always"}


def gold_index(index):
    """labeled unit의 facets를 gold로 바꾸고 active postings를 다시 만든다."""
    ug = json.loads((HERE / "unit_gold.json").read_text("utf-8"))["units"]
    idx = copy.deepcopy(index)
    for uid, g in ug.items():
        if g["labeled"]:
            idx["units"][uid]["facets"] = g["facets"]
    postings = {}
    for uid, u in sorted(idx["units"].items()):
        for a, vs in u["facets"].items():
            for v in vs:
                if v not in idx["facets"].get(a, {}):
                    raise r.InputError(f"unit_gold {uid}: unknown facet {a}:{v}")
                if u["adoption"] == "active":
                    postings.setdefault(f"{a}:{v}", []).append(uid)
    idx["postings"] = postings
    return idx


# ---------- 지표 ----------
def tag_scores(pred, req, acc):
    """precision = 허용 집합(required∪acceptable) 안 비율, recall = required 포함 비율. 빈 집합은 1."""
    ok = req | acc
    p = len(pred & ok) / len(pred) if pred else 1.0
    rec = len(pred & req) / len(req) if req else 1.0
    return p, rec, (2 * p * rec / (p + rec) if p + rec else 0.0), req <= pred <= ok


def ndcg(ranked, gains, k):
    dcg = sum((2 ** gains.get(u, 0) - 1) / math.log2(i + 2) for i, u in enumerate(ranked[:k]))
    ideal = sorted(gains.values(), reverse=True)[:k]
    idcg = sum((2 ** g - 1) / math.log2(i + 2) for i, g in enumerate(ideal))
    return dcg / idcg if idcg else (1.0 if not ranked[:k] else 0.0)


def retrieval_scores(ranked, gains, k):
    rel = {u for u, g in gains.items() if g > 0}
    top = ranked[:k]
    return {"p": len(set(top) & rel) / len(top) if top else float(not rel),
            "r": len(set(top) & rel) / len(rel) if rel else 1.0,
            "r_all": len(set(ranked) & rel) / len(rel) if rel else 1.0,
            "r2": len(set(top) & core) / len(core) if (core := {u for u, g in gains.items() if g == 2}) else None,
            "ndcg": ndcg(ranked, gains, k), "irrelevant": len(set(top) - rel),
            "buried": len({u for u, g in gains.items() if g == 2} & set(ranked[k:]))}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def mean(xs):
    return statistics.fmean(xs) if xs else float("nan")


# ---------- 태깅 ----------
def rule_tags(c, index):
    facets, _ = evidence.task_facets(task(c), index)
    return {f"{f['axis']}:{f['value']}" for f in facets} - always_facets(index)


def tag_packets(state, index, variant, skip=()):
    """variant → {part: decide 요청}. rule:always는 모든 작업에 켜지므로 묻지 않는다."""
    qs = {}
    for a, vs in sorted(index["facets"].items()):
        for v, f in sorted(vs.items()):
            if f["detect"] == "rule:always" or f"{a}:{v}" in skip:  # rule이 놓친 rule facet(예: 파일 없는 React)도 묻는다
                continue
            if variant == "rule_llm_v2" and f["detect"].startswith("rule:script("):
                continue
            extra = f" {BOUNDARY[f'{a}:{v}']}" if variant == "rule_llm_v2" and f"{a}:{v}" in BOUNDARY else ""
            qs[f"{a}:{v}"] = {"type": "noul", "instructions":
                              f"Does facet {a}:{v} ({f['desc']}) apply to the task as requested? 1 = applies, 0 = not.{extra}"}
    parts = ({"all": qs} if variant != "rule_llm_axis" else
             {a: {k: q for k, q in qs.items() if k.startswith(a + ":")} for a in index["facets"]})
    return {p: decide.validate_request({"state": state, "questions": q}) for p, q in parts.items() if q}


def state_of(c):
    files = f"\ncontext_files: {', '.join(c['context_files'])}" if c["context_files"] else ""
    return f"{c['summary']}\n\n{c['prompt']}{files}"


def read_answers(d, case_id, rep):
    """case의 모든 part 응답을 합친다. 하나라도 없으면 None. → ({facet: noul}, choice, usage 합, 추정 입력 토큰)"""
    reqs = sorted(d.glob(f"{case_id}~*.request.json"))
    if not reqs:
        return None
    answers, usage, est, choice = {}, {"input_tokens": 0, "output_tokens": 0}, 0, None
    for q in reqs:
        resp = q.with_name(q.name.replace(".request.json", f".r{rep}.json"))
        if not resp.exists():
            return None
        req, raw = json.loads(q.read_text("utf-8")), json.loads(resp.read_text("utf-8"))
        for k, a in decide.validate_response(req, raw).items():
            if a["type"] == "noul":
                answers[k] = a["noul"]
            else:
                choice = a["choice"]
        for k in usage:
            usage[k] += int((raw.get("usage") or {}).get(k, 0))
        est += est_tokens(json.dumps(req, ensure_ascii=False))
    return answers, choice, usage, est


# ---------- 커맨드 ----------
def cmd_index_audit(args, index):
    active = {u: x for u, x in index["units"].items() if x["adoption"] == "active"}
    keys = lambda u: {f"{a}:{v}" for a, vs in u["facets"].items() for v in vs}
    sizes = sorted(len(v) for v in index["postings"].values())
    generic = sorted(u for u, x in active.items() if keys(x) <= always_facets(index) | {"task:general"})
    sigs = {}
    for u, x in active.items():
        sigs.setdefault(tuple(sorted(keys(x))), []).append(u)
    dup = [v for v in sigs.values() if len(v) > 1]
    holes = sorted(f"{a}:{v}" for a, vs in index["facets"].items() for v in vs if f"{a}:{v}" not in index["postings"])
    n = len(active)
    lines = [f"# 인덱싱 감사 · wiki {index['wiki_hash'][:8]}", "",
             f"- active unit {n}, postings {len(sizes)}: 크기 min {sizes[0]} · median {statistics.median(sizes)} · max {sizes[-1]}",
             f"- 범용 facet만 가진 unit {len(generic)}/{n}: {', '.join(generic) or '-'}",
             f"- 구별 불가(facet signature 동일) 묶음 {len(dup)}: " + "; ".join(",".join(g) for g in dup),
             f"- active posting 0개인 facet 값 {len(holes)}: {', '.join(holes)}", "",
             "| facet | df | idf |", "|---|---:|---:|"]
    lines += [f"| {k} | {len(v)} | {math.log(n / len(v)):.2f} |" for k, v in sorted(index["postings"].items(), key=lambda kv: len(kv[1]))]
    ug = {u: g for u, g in json.loads((HERE / "unit_gold.json").read_text("utf-8"))["units"].items() if g["labeled"]}
    lines += ["", f"## gold 대비 정확성 (labeled unit {len(ug)})"]
    if ug:
        rows = []
        for u, g in sorted(ug.items()):
            gk = {f"{a}:{v}" for a, vs in g["facets"].items() for v in vs}
            p, rec, f1, _ = tag_scores(keys(index["units"][u]), gk, set())
            miss_task = sorted(k for k in gk - keys(index["units"][u]) if k.startswith("task:"))
            rows.append((u, p, rec, miss_task))
        lines += [f"- 평균 P {mean([x[1] for x in rows]):.3f} · R {mean([x[2] for x in rows]):.3f}",
                  "- 핵심 task facet 누락: " + ("; ".join(f"{u} {m}" for u, _, _, m in rows if m) or "-")]
    print("\n".join(lines))


def predicted_tags(spec, c, index, threshold):
    if spec == "gold":
        return set(c["facets_required"])
    if spec == "rule":
        return rule_tags(c, index)
    d, variant, rep = spec.split(":")  # DIR:VARIANT:REP
    got = read_answers(OUT / d / "tag" / variant, c["id"], int(rep))
    return None if got is None else rule_tags(c, index) | {k for k, v in got[0].items() if v >= threshold}


def run_filter(c, tags, index, gains):
    res = evidence.build(task(c, to_axes(tags)), {"profile": []}, None, [], index, datetime.now(timezone.utc), 10 ** 6)
    ranked = [u["id"] for u in res["units"]]
    nofilter = {u for f in res["facets"] for u in index["postings"].get(f"{f['axis']}:{f['value']}", [])}
    return ranked, {k: retrieval_scores(ranked, gains, k) for k in KS}, retrieval_scores(sorted(nofilter), gains, 10 ** 6)


def cmd_filter(args, index):
    cases = load_cases()
    gidx = gold_index(index)
    print(f"# 필터링 · 태그 {args.tags} · labeled case {len(cases)}\n")
    print("| 태그 | 인덱스 | k | P@k | R@k | R(전체) | nDCG@k | 무관/case | 묻힌 핵심 | 빈 정답 일치 | R(필터 끔) | 후보 수 | R@k(등급2) |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for spec in dict.fromkeys(["gold", args.tags]):
        for iname, idx in (("gold", gidx), ("현행", index)):
            per = []
            for c in cases:
                tags = predicted_tags(spec, c, idx, args.threshold)
                if tags is None:
                    continue
                ranked, sc, nf = run_filter(c, tags, idx, c["units"])
                per.append((c, ranked, sc, nf))
            for k in KS:
                s = [x[2][k] for x in per]
                empty = [not x[1] for x in per if not x[0]["units"]]
                print(f"| {spec} | {iname} | {k} | {mean([x['p'] for x in s]):.3f} | {mean([x['r'] for x in s]):.3f} | "
                      f"{mean([x['r_all'] for x in s]):.3f} | {mean([x['ndcg'] for x in s]):.3f} | "
                      f"{mean([x['irrelevant'] for x in s]):.1f} | {sum(x['buried'] for x in s)} | "
                      f"{sum(empty)}/{len(empty)} | {mean([x[3]['r_all'] for x in per]):.3f} | {mean([len(x[1]) for x in per]):.1f} | "
                      f"{mean([x['r2'] for x in s if x['r2'] is not None]):.3f} |")


def cmd_packets(args, index):
    base = OUT / args.tag / args.stage
    n = 0
    if args.stage == "tag":
        for c in load_cases(labeled_only=False):
            for variant in TAG_VARIANTS:
                skip = rule_tags(c, index) if variant != "llm_all" else ()
                for part, req in tag_packets(state_of(c), index, variant, skip).items():
                    n += write(base / variant / f"{c['id']}~{part}.request.json", req)
    elif args.stage == "unit":  # 역검색: unit 설명만으로 태깅 → unit.facets와 비교
        for uid, u in index["units"].items():
            if u["adoption"] == "active":
                state = (f"Benchmark: {u['desc']} (metric {u['metric']}). Treat a typical prompt of this benchmark as the task: "
                         "which facets does the benchmark measure?")
                req = tag_packets(state, index, "rule_llm_v2")["all"]
                n += write(base / "rule_llm_v2" / f"{uid.replace('/', '__')}~all.request.json", req)
    else:  # choice: 예측 태그의 evidence 표 vs gold 태그의 evidence 표에서 같은 프로필을 고르는가
        cfg = r.load_profiles(args.config_dir / "profiles.toml")
        snap, warns = r.load_snapshot(args.cache_dir)
        ids = sorted(p["id"] for p in cfg["profile"] if p["enabled"])  # shortcut: enabled 전체, evaluate의 eligible로 좁히려면 교체
        criteria = {**{i: None for i in ids}, "abstain": "Evidence is insufficient to choose"}
        for c in load_cases():
            pred = predicted_tags(f"{args.tag}:{args.source}:{args.rep}", c, index, args.threshold)
            for name, tags in (("pred", pred), ("gold", set(c["facets_required"]))):
                if tags is None:
                    continue
                res = evidence.build(task(c, to_axes(tags)), cfg, snap, warns, index, datetime.now(timezone.utc), args.max_units)
                req = decide.validate_request({"state": f"{state_of(c)}\n\n{evidence.table(res)}", "questions": {"profile": {
                    "type": "choice", "instructions": "Choose the profile best supported by the benchmark evidence for this task.",
                    "criteria": criteria}}})
                n += write(base / f"choice_{name}" / f"{c['id']}~all.request.json", req)
    print(f"{n} requests → {base}")


def cmd_run(args, index):
    """저장된 요청을 Jev로 호출해 r<N>.json으로 쓴다. 이미 있는 응답은 건너뛴다(재개 가능)."""
    reqs = sorted((OUT / args.tag / args.stage).rglob("*.request.json"))
    done = failed = 0
    for rep in range(1, args.reps + 1):
        for q in reqs:
            out = q.with_name(q.name.replace(".request.json", f".r{rep}.json"))
            if out.exists():
                continue
            req = json.loads(q.read_text("utf-8"))
            for attempt in range(4):
                res = decide.decide(req)
                if res["status"] == "ok":
                    break
                time.sleep(2 ** attempt)  # 429·일시 오류. decide는 실패 사유를 jev_unavailable로만 알려 준다
            if res["status"] != "ok":
                failed += 1
                print(f"fail {q.relative_to(OUT)} r{rep}: {res.get('reason')}", file=sys.stderr)
                continue
            write(out, {"answers": res["answers"], "usage": res["usage"], "model": res["model"]})
            done += 1
    print(f"{done} responses written, {failed} failed")
    return failed


def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), "utf-8")
    return 1


def cmd_score(args, index):
    base = OUT / args.tag
    cases = load_cases()
    lines = [f"# 태깅·토큰 채점 · {args.tag} · labeled case {len(cases)}", "",
             "| tagger | th | P | R | F1 | 환각률 | 누락률 | exact | Jaccard(반복) | in tok | out tok | 추정/실측 in | 토큰/F1점 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    rule = [tag_scores(rule_tags(c, index), set(c["facets_required"]), set(c["facets_acceptable"])) for c in cases]
    if rule:
        lines.append(f"| rule-only | - | {mean([x[0] for x in rule]):.3f} | {mean([x[1] for x in rule]):.3f} | "
                     f"{mean([x[2] for x in rule]):.3f} | {1 - mean([x[0] for x in rule]):.3f} | {1 - mean([x[1] for x in rule]):.3f} | "
                     f"{sum(x[3] for x in rule)}/{len(rule)} | 1 | 0 | 0 | - | 0 |")
    axis_err = {}
    for variant in TAG_VARIANTS:
        d = base / "tag" / variant
        runs = {(c["id"], rep): read_answers(d, c["id"], rep) for c in cases for rep in range(1, args.reps + 1)}
        runs = {k: v for k, v in runs.items() if v}
        if not runs:
            continue
        byid = {c["id"]: c for c in cases}
        for th in THRESHOLDS:
            sc, tags = [], {}
            for (cid, rep), (ans, _, _, _) in runs.items():
                c = byid[cid]
                pred = (rule_tags(c, index) if variant != "llm_all" else set()) | {k for k, v in ans.items() if v >= th}
                pred -= always_facets(index)
                tags[cid, rep] = pred
                sc.append(tag_scores(pred, set(c["facets_required"]), set(c["facets_acceptable"])))
                if th == args.threshold and variant == "rule_llm_v2":
                    for k in pred ^ set(c["facets_required"]):
                        if k not in c["facets_acceptable"]:
                            axis_err[k.split(":")[0]] = axis_err.get(k.split(":")[0], 0) + 1
            jac = [jaccard(tags[cid, 1], tags[cid, rep]) for cid, rep in tags if rep > 1 and (cid, 1) in tags]
            vin = [u["input_tokens"] for _, _, u, _ in runs.values()]
            vout = [u["output_tokens"] for _, _, u, _ in runs.values()]
            vest = [e for _, _, _, e in runs.values()]
            f1 = mean([x[2] for x in sc])
            lines.append(f"| {variant} | {th} | {mean([x[0] for x in sc]):.3f} | {mean([x[1] for x in sc]):.3f} | {f1:.3f} | "
                         f"{1 - mean([x[0] for x in sc]):.3f} | {1 - mean([x[1] for x in sc]):.3f} | {sum(x[3] for x in sc)}/{len(sc)} | "
                         f"{mean(jac):.3f} | {mean(vin):.0f} | {mean(vout):.0f} | "
                         f"{(sum(vest) / sum(vin)) if sum(vin) else float('nan'):.2f} | "
                         f"{(mean(vin) + mean(vout)) / (100 * f1) if f1 else float('nan'):.1f} |")
    lines += ["", f"rule_llm_v2 축별 오류 수(th {args.threshold}): " + (", ".join(f"{a} {n}" for a, n in sorted(axis_err.items())) or "-")]

    # 표 토큰: Orchestrator/결정 모델에 넘기는 evidence 크기 (gold 태그, 프로필 없이 unit 줄만)
    lines += ["", "| max_units | table 토큰(추정) | JSON 토큰(추정) | nDCG@k(gold 태그) | nDCG 1점당 table 토큰 |", "|---:|---:|---:|---:|---:|"]
    for k in KS:
        tt, jt, nd = [], [], []
        for c in cases:
            res = evidence.build(task(c, to_axes(c["facets_required"])), {"profile": []}, None, [], index,
                                 datetime.now(timezone.utc), k)
            tt.append(est_tokens(evidence.table(res)))
            jt.append(est_tokens(json.dumps(res, ensure_ascii=False)))
            nd.append(ndcg([u["id"] for u in res["units"]], c["units"], k))
        if cases:
            lines.append(f"| {k} | {mean(tt):.0f} | {mean(jt):.0f} | {mean(nd):.3f} | {mean(tt) / mean(nd) if mean(nd) else float('nan'):.0f} |")

    # 최종 결정: 예측 태그 evidence와 gold 태그 evidence에서 같은 프로필을 고르는가
    pairs, abstain, tok, decided = [], 0, [], []
    for c in cases:
        for rep in range(1, args.reps + 1):
            p = read_answers(base / "choice" / "choice_pred", c["id"], rep)
            g = read_answers(base / "choice" / "choice_gold", c["id"], rep)
            if p and g:
                pairs.append(p[1] == g[1])
                if "abstain" not in (p[1], g[1]) or p[1] != g[1]:
                    decided.append((c["id"], p[1], g[1]))
                abstain += p[1] == "abstain"
                tok.append(p[2]["input_tokens"] + p[2]["output_tokens"])
    if pairs:
        lines += ["", f"최종 결정: pred/gold evidence 일치 {sum(pairs)}/{len(pairs)} · pred abstain {abstain} · 호출당 토큰 {mean(tok):.0f}",
                  f"한쪽 이상이 프로필을 고른 경우 {len(decided)}: 일치 {sum(a == b for _, a, b in decided)} · "
                  + ", ".join(f"{i}({a}/{b})" for i, a, b in decided if a != b)]
    lines += unit_reverse(base / "unit" / "rule_llm_v2", index, args.threshold)
    text = "\n".join(lines)
    (HERE / "results" / f"retrieval-{args.tag}.md").write_text(text + "\n", "utf-8")
    print(text)


def unit_reverse(d, index, th):
    """실험 2 역검색: unit 설명만으로 붙인 facet이 unit.facets·gold와 맞는가. lang 축은 설명 언어 잡음이라 뺀다."""
    if not d.exists():
        return []
    ug = json.loads((HERE / "unit_gold.json").read_text("utf-8"))["units"]
    keys = lambda f: {f"{a}:{v}" for a, vs in f.items() for v in vs if a != "lang"}
    rows = []
    for q in sorted(d.glob("*~all.request.json")):
        name = q.name.split("~")[0]
        got = read_answers(d, name, 1)
        if not got:
            continue
        uid = name.replace("__", "/")
        pred = {k for k, v in got[0].items() if v >= th and not k.startswith("lang:")} - always_facets(index)
        cur = keys(index["units"][uid]["facets"]) - always_facets(index)
        gold = keys(ug[uid]["facets"]) - always_facets(index) if ug.get(uid, {}).get("labeled") else None
        task_only = lambda x: {k for k in x if k.startswith("task:")}
        rows.append((uid, tag_scores(pred, cur, set()), gold is not None and tag_scores(pred, gold, set()),
                     tag_scores(task_only(pred), task_only(cur), set()), sorted(cur - pred), got[2]["input_tokens"]))
    if not rows:
        return []
    m = lambda i, j: mean([x[i][j] for x in rows if x[i]])
    out = ["", f"## 역검색: unit 설명만으로 태깅 (active unit {len(rows)}, th {th}, agent_signal 등 always·lang 제외)", "",
           "| 기준 | P | R | F1 |", "|---|---:|---:|---:|",
           f"| 현행 unit.facets | {m(1, 0):.3f} | {m(1, 1):.3f} | {m(1, 2):.3f} |",
           f"| unit_gold | {m(2, 0):.3f} | {m(2, 1):.3f} | {m(2, 2):.3f} |",
           f"| task 축만(현행) | {m(3, 0):.3f} | {m(3, 1):.3f} | {m(3, 2):.3f} |", "",
           f"설명에서 복원되지 않은 facet(설명 보강 후보, 호출당 입력 {mean([x[5] for x in rows]):.0f} 토큰):"]
    out += [f"- {uid}: {', '.join(miss)}" for uid, _, _, _, miss, _ in rows if miss]
    return out


def selftest():
    assert tag_scores({"a", "b"}, {"a"}, {"b"}) == (1.0, 1.0, 1.0, True)
    assert tag_scores({"a", "x"}, {"a", "c"}, set())[:2] == (0.5, 0.5)
    assert tag_scores(set(), set(), set()) == (1.0, 1.0, 1.0, True)
    assert ndcg(["a", "b"], {"a": 2, "b": 1}, 12) == 1.0 and ndcg(["b", "a"], {"a": 2, "b": 1}, 12) < 1.0
    assert ndcg([], {}, 12) == 1.0 and ndcg(["x"], {}, 12) == 0.0
    s = retrieval_scores(["x", "a", "b"], {"a": 2, "b": 2}, 2)
    assert (s["p"], s["r"], s["r_all"], s["irrelevant"], s["buried"], s["r2"]) == (0.5, 0.5, 1.0, 1, 1, 0.5)
    assert jaccard({"a"}, {"a", "b"}) == 0.5
    print("selftest ok")


def main():
    global CASES
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("index-audit", "filter", "packets", "run", "score", "selftest"))
    ap.add_argument("--tag", default="t1")
    ap.add_argument("--cases", type=Path, default=CASES, help="gold 케이스 파일")
    ap.add_argument("--tags", default="rule", help="filter: gold | rule | TAG:VARIANT:REP (packets/score 결과)")
    ap.add_argument("--stage", choices=("tag", "unit", "choice"), default="tag")
    ap.add_argument("--source", default="rule_llm_v2", choices=TAG_VARIANTS, help="choice: 예측 태그를 가져올 tagger")
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--max-units", type=int, default=12)
    ap.add_argument("--config-dir", type=Path, default=_xdg("XDG_CONFIG_HOME", ".config"))
    ap.add_argument("--cache-dir", type=Path, default=_xdg("XDG_CACHE_HOME", ".cache"))
    args = ap.parse_args()
    CASES = args.cases
    if args.cmd == "selftest":
        return selftest()
    index = evidence.load_index(args.cache_dir)
    if index is None:
        sys.exit("index.json invalid; run `python3 -m bench_router.cli wiki compile`")
    sys.exit({"index-audit": cmd_index_audit, "filter": cmd_filter, "packets": cmd_packets, "run": cmd_run,
              "score": cmd_score}[args.cmd](args, index) and 1)


if __name__ == "__main__":
    main()
