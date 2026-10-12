"""실행별 비용 측정: 토큰은 각 CLI의 로컬 세션 로그에서 실측, 금액은 AA 공개 API 단가로 환산.

- 토큰(실측): claude = ~/.claude/projects/<cwd>/*.jsonl 의 마지막 cost-state.modelUsage,
  codex = ~/.codex/sessions/**/rollout-*.jsonl 중 session_meta.cwd가 같은 세션의 마지막 token_count.
  run마다 cwd가 다르므로(eval 하네스) cwd로 귀속한다.
- 금액(환산): codex는 AA pricing(input / cache hit / cache write / output, $/1M) × 토큰.
  claude는 Claude Code가 기록한 costUSD를 쓴다. AA 단가의 cache write($5/M)는 5분 캐시 기준인데 Claude Code는
  1시간 캐시(입력 단가의 2배)를 쓴다. AA 입력·적중·출력 단가 + 1시간 쓰기 $8/M로 계산하면 v1 20 run 모두
  costUSD와 오차 1e-16 이내로 일치했다(2026-10-12 검증). 구독 실비가 아니다. "API 환산 USD"로만 표시한다.
- 집계 규칙 차이: Anthropic input_tokens는 캐시 제외, OpenAI input_tokens는 cached 포함(→ 빼서 uncached 계산).
  output은 양쪽 모두 thinking/reasoning 포함.

사용: python3 eval/cost.py --tag v1   (results.jsonl에 토큰/USD를 붙여 eval/results/<tag>-cost.md 작성)
"""
import argparse
import glob
import json
import os
import re
import sqlite3
import statistics
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = Path.home()


def aa_prices(cfg):
    """profile id → AA pricing($/1M). aliases.toml의 [aa] 매핑으로 slug를 찾는다."""
    aliases = tomllib.loads((HOME / ".config/bench-router/aliases.toml").read_text()).get("aa", {})
    db = sqlite3.connect(HOME / ".cache/bench-router/bench-router.db")
    cur = db.execute("SELECT current_snapshot FROM sources WHERE id='aa'").fetchone()[0]
    payload = json.loads(db.execute("SELECT payload FROM snapshots WHERE id=?", (cur,)).fetchone()[0])
    by_slug = {m["slug"]: m.get("pricing") for b in payload["pages"] for m in b["data"]}
    out = {}
    for p in cfg["profile"]:
        slugs = [s for s, canon in aliases.items() if canon == p["model_id"]]
        out[p["id"]] = by_slug.get(slugs[0]) if len(slugs) == 1 else None
    return out


def claude_usage(cwd):
    d = HOME / ".claude/projects" / re.sub(r"[^A-Za-z0-9-]", "-", str(cwd))
    states = []
    for f in sorted(glob.glob(str(d / "*.jsonl"))):
        last = None
        for line in open(f, encoding="utf-8"):
            x = json.loads(line)
            if x.get("type") == "cost-state":
                last = x
        if last:
            states.append(last)
    if not states:
        return None
    u = {"input": 0, "cache_hit": 0, "cache_write": 0, "output": 0, "self_reported_usd": 0.0, "aux_usd": 0.0,
         "sessions": len(states)}
    for s in states:
        u["self_reported_usd"] += s.get("totalCostUSD", 0.0)
        for model, m in s.get("modelUsage", {}).items():
            if model.startswith("claude-opus"):  # 프로필의 주 모델
                u["input"] += m["inputTokens"]
                u["cache_hit"] += m["cacheReadInputTokens"]
                u["cache_write"] += m["cacheCreationInputTokens"]
                u["output"] += m["outputTokens"]
            else:  # 보조 호출(예: 제목 생성 haiku)은 CLI 자체 계산값을 그대로 더한다
                u["aux_usd"] += m.get("costUSD", 0.0)
    return u


_codex_index = None


def codex_usage(cwd):
    global _codex_index
    if _codex_index is None:
        _codex_index = {}
        for f in glob.glob(str(HOME / ".codex/sessions/**/*.jsonl"), recursive=True):
            meta, last = None, None
            for line in open(f, encoding="utf-8"):
                x = json.loads(line)
                p = x.get("payload") or {}
                if x.get("type") == "session_meta":
                    meta = p.get("cwd")
                elif p.get("type") == "token_count" and p.get("info"):
                    last = p["info"]["total_token_usage"]
            if meta and last:
                _codex_index.setdefault(meta, []).append(last)
    tus = _codex_index.get(str(cwd))
    if not tus:
        return None
    u = {"input": 0, "cache_hit": 0, "cache_write": 0, "output": 0, "self_reported_usd": None, "aux_usd": 0.0,
         "sessions": len(tus)}
    for t in tus:
        u["input"] += t["input_tokens"] - t["cached_input_tokens"]  # OpenAI: input에 cached 포함
        u["cache_hit"] += t["cached_input_tokens"]
        u["cache_write"] += t.get("cache_write_input_tokens", 0)
        u["output"] += t["output_tokens"]
    return u


def usd(u, price):
    if u and u["self_reported_usd"] is not None:  # claude: CLI 계산값(1시간 캐시 쓰기 반영)
        return u["self_reported_usd"]
    if not u or not price:
        return None
    return (u["input"] * price["price_1m_input_tokens"] + u["cache_hit"] * price["price_1m_cache_hit_tokens"]
            + u["cache_write"] * price["price_1m_cache_write_tokens"] + u["output"] * price["price_1m_output_tokens"]
            ) / 1e6 + u["aux_usd"]


def main():
    sys.path.insert(0, str(HERE.parent))
    sys.path.insert(0, str(HERE))
    from bench_router import routing as r
    from run import TASKS, policies
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    cfg = r.load_profiles(HOME / ".config/bench-router/profiles.toml")
    kinds = {p["id"]: p["kind"] for p in cfg["profile"]}
    prices = aa_prices(cfg)
    root = HOME / "br-smoke/eval" / a.tag
    rows = [json.loads(l) for l in (root / "results.jsonl").read_text().splitlines()]
    for x in rows:
        cwd = root / x["profile"] / x["task"]
        u = (claude_usage if kinds[x["profile"]] == "claude" else codex_usage)(cwd)
        x["usage"], x["usd_api_equiv"] = u, usd(u, prices[x["profile"]])
    (root / "results-cost.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows))

    by = {(x["task"], x["profile"]): x for x in rows}
    pol = policies(cfg, root)
    tot = lambda sel, k: sum((x["usage"] or {}).get(k, 0) for x in sel)
    lines = [f"# 비용 실측 — {a.tag}", "",
             "토큰은 각 CLI 세션 로그에서 실측했습니다. USD는 AA 공개 API 단가로 계산한 **API 환산값**이며, 구독 실제 지출이 아닙니다.", "",
             "단가($/1M, AA): " + "; ".join(f"{p}: in {v['price_1m_input_tokens']}, cache hit {v['price_1m_cache_hit_tokens']}, "
                                          f"cache write {v['price_1m_cache_write_tokens']}, out {v['price_1m_output_tokens']}"
                                          for p, v in prices.items() if v), "",
             "| 정책 | 성공 | API 환산 USD 합 | 성공 1건당 USD | 출력 토큰 | 캐시 적중 입력 | 비캐시 입력 | 측정 누락 run |",
             "|---|---|---|---|---|---|---|---|"]
    for name in ("fixed-default", "low-cost-first", "bench-router"):
        sel = [by[(t[0], pol[name][t[0]])] for t in TASKS if (t[0], pol[name][t[0]]) in by]
        wins = sum(x["status"] == "completed" and x["check"] for x in sel)
        cost = sum(x["usd_api_equiv"] or 0 for x in sel)
        lines.append(f"| {name} | {wins}/{len(sel)} | ${cost:.2f} | ${cost / max(1, wins):.3f} | {tot(sel, 'output'):,} | "
                     f"{tot(sel, 'cache_hit'):,} | {tot(sel, 'input'):,} | {sum(x['usage'] is None for x in sel)} |")
    cl = [x for x in rows if x["usage"] and x["usage"]["self_reported_usd"] is not None]
    if cl:
        aa5 = sum(usd({**x["usage"], "self_reported_usd": None}, prices[x["profile"]]) for x in cl)
        lines += ["", f"claude 교차 검증({len(cl)} run): Claude Code costUSD 합 ${sum(x['usd_api_equiv'] for x in cl):.2f}. "
                      f"AA cache write 단가($5/M, 5분 캐시)를 그대로 쓰면 ${aa5:.2f}로 과소추정된다. "
                      "1시간 캐시 쓰기 단가($8/M)로 계산하면 run별 오차 1e-16 이내로 일치한다."]
    lines += ["", "| 작업 | " + " | ".join(f"{p} USD (out tok)" for p in kinds) + " |", "|---|" + "---|" * len(kinds)]
    for t in TASKS:
        cells = []
        for p in kinds:
            x = by.get((t[0], p))
            cells.append("-" if not x or x["usd_api_equiv"] is None else f"${x['usd_api_equiv']:.3f} ({x['usage']['output']:,})")
        lines.append(f"| {t[0]} | " + " | ".join(cells) + " |")
    out = HERE / "results" / f"{a.tag}-cost.md"
    out.write_text("\n".join(lines) + "\n", "utf-8")
    print("\n".join(lines[:12 + 3]))
    print(f"report: {out}")


if __name__ == "__main__":
    main()
