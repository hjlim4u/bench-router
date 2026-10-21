"""P0 검증 V01–V10 (06 문서). 실행: python3 -m unittest -v test_p0"""
import contextlib
import io
import json
import os
import re
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from bench_router import cli
from bench_router import routing as r

EX = Path(__file__).parent / "examples"
NOW = datetime(2026, 10, 12, tzinfo=timezone.utc)
MAPPING = r.load_categories(cli.BUNDLED_CATEGORIES)


def profile(pid, tier="medium", **kw):
    p = {"id": pid, "enabled": True, "kind": "codex", "executable": "codex", "args": ["-m", pid],
         "model_id": pid, "harness_id": "codex-cli", "reasoning_effort": "unknown", "config_revision": "t",
         "cost_tier": tier, "inference_local": False, "context_tokens": 0, "capabilities": ["filesystem_write"]}
    return {**p, **kw}


def config(profiles, default=None, fallback=()):
    return {"schema_version": "1.0", "default_profile": default, "fallback_order": list(fallback), "profile": profiles}


def guided_reply(packet, chosen, **overrides):
    """Synthetic response to one stage, retaining the validated predecessor stages."""
    request = packet["decision_request"]
    answers = {}
    for key, q in request["questions"].items():
        if q["type"] == "noul":
            answers[key] = {"type": "noul", "noul": overrides.get(key, 0)}
            continue
        choice = "unknown"
        if key.startswith("fit:"):
            pid = key[4:]
            rules = [x for x in q["criteria"] if not x.startswith("__")]
            choice = rules[0] if rules else "__provisional__"
            if chosen not in ("__tie__", pid):
                choice = "__unsuitable__"
        elif key == "benchmark":
            choice = "__tie__"
        answers[key] = {"type": "choice", "choice": overrides.get(key, choice)}
    response = {"request_digest": packet["assessment_digest"], "provider": "subagent", "model": "gpt-6-luna", "answers": answers}
    return {"stages": [*packet.get("decision", {}).get("completed", []), response]}


def guided_responses(packet, reroute, chosen, **overrides):
    for _ in range(3):
        response = guided_reply(packet, chosen, **overrides)
        packet = reroute(response)
        if packet["status"] != "decision_required":
            return response
    raise AssertionError("decision did not finish within three stages")


def snapshot(evidence_by_profile, profiles, last_success="2026-10-11T00:00:00+00:00"):
    """evidence_by_profile: {pid: {evidence_id: normalized|None}} → 검증 가능한 snapshot."""
    fps = {p["id"]: r.profile_fingerprint(p) for p in profiles}
    s = {"schema_version": "1.0", "generated_at": "2026-10-11T00:00:00+00:00", "policy_version": r.POLICY_VERSION,
         "config_hash": "test", "cohorts": {},
         "sources": {"syn": {"last_success_at": last_success, "ttl_hours": 24, "max_stale_hours": 168}},
         "profiles": {pid: {"fingerprint": fps[pid], "evidence": {
             b: {"normalized": n, "raw": n, "scope": "model_proxy", "cohort_id": f"syn-{b}",
                 "metric_version": "1", "source_id": "syn", "source_revision": "r1", "fetched_at": last_success}
             for b, n in ev.items()}} for pid, ev in evidence_by_profile.items()}}
    s["snapshot_id"] = r.snapshot_hash(s)
    return r.validate_snapshot(s)


class P0(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def task(self, **kw):
        raw = {"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "general question",
               "prompt": "p; rm -rf / $(whoami)", "cwd": self.cwd,
               "categories": {"general": 1}, "category_confidence": 0.9}
        raw.update(kw)
        return r.validate_task({k: v for k, v in raw.items() if v is not None})

    def run_route(self, t, profiles, ev, **cfg_kw):
        return r.route_legacy(t, config(profiles, **cfg_kw), MAPPING, snapshot(ev, profiles), [], NOW)

    def test_v11_orchestrator_facts_and_budget(self):
        ps = [profile("a", context_tokens=8000), profile("b", context_tokens=0)]
        context = r.validate_context({"schema_version": "1.0", "complexity": {"level": "high", "reason": "multiple files"},
            "max_estimated_cost_usd": 0.003, "profiles": {
                "a": {"estimated_input_tokens": 1000, "estimated_output_tokens": 1000, "required_context_tokens": 2000,
                      "price": {"input_usd_per_million_tokens": 1, "output_usd_per_million_tokens": 2,
                                "source": "test", "as_of": "2026-10-13T00:00:00+00:00"},
                      "signals": {"orchestrator.latency": {"value": 4, "unit": "seconds", "source": "test"}}},
                "b": {"required_context_tokens": 2000}}}, [p["id"] for p in ps])
        res = r.evaluate_v1(self.task(), config(ps), MAPPING, None, [], NOW, context=context)
        self.assertEqual((res["status"], res["selected"], len(res["candidates"])), ("ok", None, 1))
        self.assertEqual(res["candidates"][0]["context_facts"]["estimated_cost_usd"], 0.003)
        self.assertEqual(res["excluded"], [{"profile": "b", "reasons": ["context_unknown", "estimated_cost_unknown"]}])
        self.assertEqual(r.pin_selection(res, config(ps), "a")["selected"]["profile"], "a")
        self.assertEqual(r.pin_selection(res, config(ps), "b")["status"], "no_eligible_profile")
        over = r.evaluate_v1(self.task(), config(ps), MAPPING, None, [], NOW,
                          context={**context, "max_estimated_cost_usd": 0.0029})
        self.assertIn("estimated_cost_exceeds_max", over["excluded"][0]["reasons"])
        no_cap = r.evaluate_v1(self.task(), config(ps), MAPPING, None, [], NOW,
                            context=r.validate_context({"schema_version": "1.0", "profiles": {"b": {}}}, ["a", "b"]))
        unknown = next(c for c in no_cap["candidates"] if c["profile"] == "b")
        self.assertEqual((unknown["context_facts"]["estimated_cost_usd"],
                          unknown["context_facts"]["cost_missing_reason"]), (None, "estimate_or_price_missing"))

    def test_v36_assess_separates_constraints_from_selection(self):
        ps = [profile("c", context_tokens=1000), profile("b"), profile("a")]
        t = self.task(constraints={"min_context_tokens": 4000})
        ps[1]["context_tokens"] = ps[2]["context_tokens"] = 8000
        asmt = r.assess(t, config(ps), MAPPING, None, [], NOW)
        self.assertEqual([c["profile"] for c in asmt["candidates"]], ["a", "b", "c"])
        failed = [x for x in asmt["candidates"][2]["constraints"] if not x["passed"]]
        self.assertEqual(failed, [{"passed": False, "code": "context_insufficient", "metric": "min_context_tokens",
                                   "observed": 1000, "limit": 4000, "on_missing": "exclude",
                                   "constraint": "context_capacity"}])
        self.assertEqual([x["constraint"] for x in asmt["candidates"][0]["constraints"]],
                         ["enabled", "cost_tier", "context_capacity"])
        self.assertIsNone(asmt["candidates"][0]["evaluations"]["benchmark"]["quality"])
        self.assertEqual(asmt["candidates"][2]["evaluations"], {})
        # benchmark 없음 + default/fallback 없음: 자동 선택은 실패해도 평가는 유효 후보를 돌려준다
        self.assertEqual(r.route_legacy(t, config(ps), MAPPING, None, [], NOW)["status"], "no_eligible_profile")
        self.assertEqual([c["profile"] for c in r.evaluate_v1(t, config(ps), MAPPING, None, [], NOW)["candidates"]],
                         ["a", "b"])

    def test_v37_context_v2_metric_contract(self):
        def m(v, unit="tokens", **kw):
            return {"value": v, "unit": unit, "source": "orch@1", **kw}
        fresh = "2026-10-11T00:00:00+00:00"
        prices = {"price.input_usd_per_mtok": m(1, "usd/mtok", observed_at=fresh),
                  "price.output_usd_per_mtok": m(2, "usd/mtok", observed_at=fresh)}
        ctx = lambda metrics, **top: {"schema_version": "2.0", "profiles": {"a": {"metrics": metrics}}, **top}
        ps = [profile("a")]
        ev = lambda c: r.evaluate_v1(self.task(), config(ps), MAPPING, None, [], NOW, context=c)
        tokens = {"tokens.estimated_input": m(1000), "tokens.estimated_output": m(1000)}
        # 같은 사실의 1.0 입력과 2.0 입력은 같은 결과
        v1 = {"schema_version": "1.0", "max_estimated_cost_usd": 0.01, "profiles": {"a": {
            "estimated_input_tokens": 1000, "estimated_output_tokens": 1000,
            "price": {"input_usd_per_million_tokens": 1, "output_usd_per_million_tokens": 2,
                      "source": "orch@1", "as_of": fresh}}}}
        v2 = ctx({"tokens.estimated_input": {**m(1000), "source": "context-1.0"},
                  "tokens.estimated_output": {**m(1000), "source": "context-1.0"}, **prices}, max_estimated_cost_usd=0.01)
        self.assertEqual(ev(v1)["context_hash"], ev(v2)["context_hash"])
        self.assertEqual(ev(v2)["candidates"][0]["context_facts"]["estimated_cost_usd"], 0.003)
        # 미등록 지표는 전달만, 결측은 0이 아님
        res = ev(ctx({**tokens, **prices, "acme.vibe": m("good", "label"),
                      "latency.p50_ms": {"status": "missing", "reason": "not_measured", "source": "tel"}}))
        self.assertEqual(set(res["candidates"][0]["context_facts"]["signals"]), {"acme.vibe", "latency.p50_ms"})
        # 만료 가격: 상한 있으면 탈락(estimated_cost_unknown), 없으면 후보 유지
        old = {k: {**v, "observed_at": "2026-01-01T00:00:00+00:00"} for k, v in prices.items()}
        self.assertEqual(ev(ctx({**tokens, **old}, max_estimated_cost_usd=1))["excluded"][0]["reasons"],
                         ["estimated_cost_unknown"])
        kept = ev(ctx({**tokens, **old}))["candidates"][0]["context_facts"]
        self.assertEqual((kept["estimated_cost_usd"], kept["cost_missing_reason"]), (None, "price_expired"))
        asmt = r.assess(self.task(), config(ps), MAPPING, None, [], NOW, context=ctx({**tokens, **old}))
        self.assertEqual(asmt["candidates"][0]["metrics"]["price.input_usd_per_mtok"]["freshness"], "expired")
        # Orchestrator 견적이 계산보다 우선
        quoted = ev(ctx({**tokens, **prices, "cost.estimated_usd": m(0.5, "usd")}))
        self.assertEqual(quoted["candidates"][0]["context_facts"]["estimated_cost_usd"], 0.5)
        for bad in (ctx({"tokens.estimated_input": m(1, "k")}),                         # 단위 불일치
                    ctx({"tokens.estimated_input": m(None)}),                           # null 결측
                    ctx({"tokens.estimated_input": {"status": "missing", "source": "x"}}),  # 사유 없는 결측
                    ctx({"price.input_usd_per_mtok": m(1, "usd/mtok")}),                # observed_at 없는 가격
                    ctx({"task.complexity": {"value": "high", "source": "x"}}),        # task 지표를 profile에
                    ctx({"acme.vibe": m([1], "x")}),                                    # 스칼라 아님
                    ctx({}, task_metrics={"task.complexity": {"value": "huge", "source": "x"}})):
            with self.subTest(bad=bad), self.assertRaises(r.InputError):
                r.validate_context(bad, ["a"])
        norm = r.validate_context(v1, ["a"])
        self.assertEqual(r.validate_context(norm, ["a"]), norm)  # 정규형은 다시 넣어도 그대로

    def test_v38_evaluate_v2_reports_facts_constraints_and_benchmark(self):
        ps = [profile("b", "high"), profile("a")]
        ev = {"b": {"swe_verified_exact": 0.9, "aa_coding": 0.9}, "a": {"swe_verified_exact": 0.4, "aa_coding": 0.6}}
        t = self.task(categories={"coding_repo": 1}, constraints={"max_cost_tier": "medium"})
        fresh = "2026-10-11T00:00:00+00:00"
        ctx = {"schema_version": "2.0", "max_estimated_cost_usd": 0.01, "profiles": {"a": {"metrics": {
            "tokens.estimated_input": {"value": 1000, "unit": "tokens", "source": "o"},
            "tokens.estimated_output": {"value": 1000, "unit": "tokens", "source": "o"},
            "price.input_usd_per_mtok": {"value": 1, "unit": "usd/mtok", "source": "o", "observed_at": fresh},
            "price.output_usd_per_mtok": {"value": 2, "unit": "usd/mtok", "source": "o", "observed_at": fresh},
            "acme.vibe": {"value": 3, "unit": "stars", "source": "x"}}}}}
        snap = snapshot(ev, ps)
        res = r.evaluate(t, config(ps), MAPPING, snap, [], NOW, context=ctx)
        self.assertEqual((res["schema_version"], [c["profile"] for c in res["candidates"]]), ("2.0", ["a", "b"]))
        a, b = res["candidates"]
        self.assertEqual(a["facts"]["cost.estimated_usd"]["value"], 0.003)
        self.assertEqual(a["facts"]["cost.estimated_usd"]["source"], r.ROUTER_COST_SOURCE)
        self.assertEqual(set(a["unrecognized_metrics"]), {"acme.vibe"})
        cost_check = next(x for x in a["constraints"] if x["constraint"] == "estimated_cost")
        self.assertEqual((cost_check["passed"], cost_check["observed"], cost_check["limit"]), (True, 0.003, 0.01))
        # 탈락 후보도 목록에 남고, 실패 근거(관측값·기준값)를 함께 보인다. 상한 둘 다 독립 제약.
        self.assertFalse(b["eligible"])
        self.assertEqual({x["code"] for x in b["constraints"] if not x["passed"]},
                         {"cost_tier_exceeds_max", "estimated_cost_unknown"})
        self.assertEqual(b["evaluations"], {})
        # legacy_score는 route 1.0의 score와 같다. 미등록 지표가 늘어도 benchmark 결과는 불변.
        legacy = r.route_legacy(t, config(ps), MAPPING, snap, [], NOW, context=ctx)
        self.assertEqual(a["evaluations"]["benchmark"]["status"], "ok")
        self.assertIsNotNone(a["evaluations"]["benchmark"]["legacy_score"])
        self.assertEqual(a["evaluations"]["benchmark"]["legacy_score"], legacy["candidates"][0]["score"])
        ctx["profiles"]["a"]["metrics"]["acme.other"] = {"value": 1, "source": "x"}
        again = r.evaluate(t, config(ps), MAPPING, snap, [], NOW, context=ctx)
        self.assertEqual(again["candidates"][0]["evaluations"], a["evaluations"])
        self.assertNotEqual(again["inputs"]["context_hash"], res["inputs"]["context_hash"])
        text = cli.explain_text({**legacy, "assessment": res})
        self.assertIn("constraint estimated_cost pass cost.estimated_usd=0.003 limit=0.01", text)
        self.assertIn("FAIL cost_tier_exceeds_max", text)

    def test_v12_context_rejects_invalid_cost_facts(self):
        base = {"schema_version": "1.0", "max_estimated_cost_usd": 1, "profiles": {"a": {}}}
        for bad in ({**base, "max_estimated_cost_usd": float("nan")},
                    {**base, "profiles": {"missing": {}}},
                    {**base, "profiles": {"a": {"price": {"input_usd_per_million_tokens": 1}}}},
                    {**base, "profiles": {"a": {"signals": {"latency": {"value": 1, "unit": "s", "source": "x"}}}}}):
            with self.subTest(bad=bad), self.assertRaises(r.InputError):
                r.validate_context(bad, ["a"])

    def test_v13_evaluate_cli_returns_full_candidate_list(self):
        cfg_dir = Path(self.cwd) / "cfg"
        cfg_dir.mkdir()
        example = (EX / "profiles.example.toml").read_text("utf-8")
        (cfg_dir / "profiles.toml").write_text(example.replace("enabled = false", "enabled = true"), "utf-8")
        task_file = Path(self.cwd) / "task.json"
        task_file.write_text(json.dumps({"schema_version": "1.0", "task_id": "t1", "round": 1,
                                         "summary": "s", "prompt": "p", "cwd": self.cwd}), "utf-8")
        def run(*extra):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cli.main(["--config-dir", str(cfg_dir), "--cache-dir", str(Path(self.cwd) / "cache"),
                                 "evaluate", "--task", str(task_file), *extra])
            return code, json.loads(out.getvalue())
        code, res = run()
        self.assertEqual((code, res["schema_version"], res["status"]), (0, "2.0", "ok"))
        self.assertEqual(sum(c["eligible"] for c in res["candidates"]), 2)
        code, res = run("--format", "1")
        self.assertEqual((code, res["status"], res["selected"], len(res["candidates"])), (0, "ok", None, 2))

    def test_v01_synthetic_fixture(self):
        fx = json.loads((EX / "scoring.synthetic.json").read_text("utf-8"))
        a, exp = fx["evidence_weights"], fx["expected"]
        self.assertEqual(r.POLICY["tier_proxy"], {k: float(v) for k, v in fx["policy"]["tier_proxy"].items()})
        for prio, winner in exp["winner"].items():
            cands = []
            for p in fx["profiles"]:
                cov, q = r.coverage_quality(a, p["scores"])
                self.assertAlmostEqual(cov, exp["coverage"][p["id"]], delta=1e-9)
                self.assertAlmostEqual(q, exp["quality"][p["id"]], delta=1e-9)
                cands.append({"profile": p["id"], "cost_tier": p["cost_tier"], "coverage": cov, "quality": q})
            self.assertEqual(r.select(cands, prio, None, []), (winner, "benchmark_score"), prio)
            if prio == "balanced":
                for c in cands:
                    self.assertAlmostEqual(c["score"], exp["balanced_scores"][c["profile"]], delta=1e-9)

    def test_v02_missing_vs_zero(self):
        a = {"b1": 0.6, "b2": 0.4}
        self.assertAlmostEqual(r.coverage_quality(a, {"b1": 0.0, "b2": None})[0], 0.6)
        cov, q = r.coverage_quality(a, {"b1": 0.0, "b2": 0.0})
        self.assertEqual((cov, q), (1.0, 0.0))
        self.assertEqual(r.coverage_quality(a, {}), (0.0, None))

    def test_v03_percentile(self):
        self.assertEqual(r.percentile_ranks({"x": 7}), {"x": 0.5})
        self.assertEqual(r.percentile_ranks({"a": 10, "b": 20, "c": 20, "d": 30}),
                         {"a": 0.0, "b": 0.5, "c": 0.5, "d": 1.0})
        self.assertEqual(r.percentile_ranks({"fast": 1, "slow": 9}, higher_is_better=False),
                         {"fast": 1.0, "slow": 0.0})

    def test_v04_deterministic(self):
        ps = [profile("a", "high"), profile("b", "low"), profile("c")]
        ev = {"a": {"aa_intelligence": 0.9}, "b": {"aa_intelligence": 0.9}, "c": {"aa_intelligence": 0.5}}
        t = self.task()
        one = self.run_route(t, ps, ev)
        two = self.run_route(t, list(reversed(ps)), ev)
        for k in ("config_hash", "assessment_digest"):  # 설정 파일 순서만 다름(digest는 config_hash에서 파생)
            one.pop(k), two.pop(k)
        self.assertEqual(json.dumps(one), json.dumps(two))
        self.assertEqual(one["selected"]["profile"], "b")  # 최고 score

    def test_v05_no_eligible_cli_exit13(self):
        cfg_dir, cache_dir = Path(self.cwd) / "cfg", Path(self.cwd) / "cache"
        cfg_dir.mkdir()
        cfg_dir.joinpath("profiles.toml").write_text(
            (EX / "profiles.example.toml").read_text("utf-8"), "utf-8")  # 예제는 enabled=false
        task_file = Path(self.cwd) / "task.json"
        fx = json.loads((EX / "task.synthetic.json").read_text("utf-8"))
        task_file.write_text(json.dumps({**fx, "cwd": self.cwd}), "utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["--config-dir", str(cfg_dir), "--cache-dir", str(cache_dir),
                             "route", "--task", str(task_file), "--dry-run"])
        res = json.loads(out.getvalue())
        self.assertEqual((code, res["status"], res["selected"]), (13, "no_eligible_profile", None))
        self.assertEqual(res["excluded"], [{"profile": p, "reasons": ["disabled"]}
                                           for p in ("local-agy-example", "local-codex-example")])
        self.assertIn("snapshot_unusable", [w["code"] for w in res["warnings"]])

    def test_v06_default_obeys_constraints(self):
        ps = [profile("dflt", inference_local=False), profile("loc", inference_local=True)]
        t = self.task(constraints={"local_only": True})
        res = self.run_route(t, ps, {}, default="dflt", fallback=["dflt", "loc"])
        self.assertEqual(res["selected"]["profile"], "loc")
        self.assertEqual(res["selection_mode"], "fallback_insufficient_evidence")
        self.assertIn({"profile": "dflt", "reasons": ["not_local_inference"]}, res["excluded"])
        res = self.run_route(t, ps, {}, default="dflt", fallback=["dflt"])
        self.assertEqual(res["status"], "no_eligible_profile")
        # 기타 하드 제약도 default에 동일 적용
        t = self.task(exclude_profiles=["dflt"], constraints={"max_cost_tier": "low", "min_context_tokens": 1,
                                                               "required_capabilities": ["vision"]})
        res = self.run_route(t, [profile("dflt")], {}, default="dflt")
        self.assertEqual(res["excluded"][0]["reasons"], ["excluded_by_task", "cost_tier_exceeds_max",
                                                         "context_unknown", "missing_capability:vision"])

    def test_v07_low_coverage_uses_default(self):
        # analysis = aa_intelligence 0.6 + arena_text 0.4; arena_text만 관측 → C=0.4
        ps = [profile("a"), profile("dflt")]
        t = self.task(categories={"analysis": 1})
        res = self.run_route(t, ps, {"a": {"arena_text": 1.0}}, default="dflt")
        self.assertEqual((res["selected"]["profile"], res["selection_mode"]), ("dflt", "default_insufficient_evidence"))
        a = next(c for c in res["candidates"] if c["profile"] == "a")
        self.assertEqual((a["score"], a["coverage_band"]), (None, "insufficient"))
        self.assertIn("insufficient_evidence", [w["code"] for w in res["warnings"]])

    def test_v08_input_validation(self):
        t = self.task(categories={"analysis": 2, "writing": 2})
        self.assertEqual(r.classify(t)["categories"], {"analysis": 0.5, "writing": 0.5})
        bad = [dict(categories={"cooking": 1}), dict(categories={"general": -1}), dict(categories={"general": 0}),
               dict(unknown_field=1), dict(constraints={"budget_usd": 5}), dict(priority="fast"),
               dict(round=0), dict(round=True), dict(task_id="../x"), dict(cwd="relative"),
               dict(context_files=["../outside.txt"]), dict(summary=""),
               dict(constraints={"timeout_ms": 999})]
        for kw in bad:
            with self.assertRaises(r.InputError, msg=str(kw)):
                self.task(**kw)
        with self.assertRaises(r.InputError):
            self.task(category_confidence=None)  # categories 있으면 confidence 필수
        f = Path(self.cwd) / "t.json"
        for text in ('{"a": NaN}', '{"a": 1, "a": 2}', '{"a": Infinity}'):
            f.write_text(text, "utf-8")
            with self.assertRaises(r.InputError, msg=text):
                r.load_json_strict(f, r.TASK_MAX_BYTES)
        f.write_bytes(b'{"a": "\xff"}')
        with self.assertRaises(r.InputError):
            r.load_json_strict(f, r.TASK_MAX_BYTES)

    def test_v09_l1_rules(self):
        low = dict(category_confidence=0.3)
        cls = r.classify(self.task(summary="Fix the bug in the React frontend", **low))
        self.assertEqual((cls["stage"], cls["fallback_reason"]), ("fallback", "rule_conflict"))
        cls = r.classify(self.task(summary="Run pytest", **low))
        self.assertEqual((cls["stage"], cls["fallback_reason"]), ("fallback", "no_rule_match"))
        cls = r.classify(self.task(summary="Refactor the repository module", context_files=["src/a.py"], **low))
        self.assertEqual((cls["stage"], cls["categories"]), ("L1", {"coding_repo": 1.0}))
        cls = r.classify(self.task(summary="저장소의 버그를 고쳐줘", categories=None, category_confidence=None))
        self.assertEqual(cls["categories"], {"coding_repo": 1.0})
        cls = r.classify(self.task(summary="SQL", **low))
        self.assertEqual(cls["stage"], "fallback")

    def test_v10_near_tie_boundary(self):
        def pick(q_b, prio):
            cands = [{"profile": "a", "cost_tier": "high", "coverage": 1.0, "quality": 0.9},
                     {"profile": "b", "cost_tier": "low", "coverage": 1.0, "quality": q_b}]
            return r.select(cands, prio, None, [])[0]
        self.assertEqual(pick(0.731, "balanced"), "b")  # 0.75 vs 0.731: gap 0.019 → near-tie, 낮은 tier
        self.assertEqual(pick(0.73, "balanced"), "a")   # gap 0.020 → near-tie 아님
        self.assertEqual(pick(0.899, "quality"), "a")   # quality: 비용으로 뒤집지 않음
        self.assertEqual(pick(0.9, "quality"), "a")     # 정확 동점 → ID

    def test_snapshot_staleness_and_fingerprint(self):
        ps = [profile("a"), profile("dflt")]
        ev = {"a": {"aa_intelligence": 0.9}}
        t = self.task()
        s = snapshot(ev, ps, last_success="2026-10-01T00:00:00+00:00")  # 11일 > max_stale 7일
        res = r.route_legacy(t, config(ps, default="dflt"), MAPPING, s, [], NOW)
        self.assertEqual(res["selected"]["profile"], "dflt")
        self.assertIn("source_too_stale", [w["code"] for w in res["warnings"]])
        changed = [profile("a", args=["-m", "other"]), profile("dflt")]  # 설정 변경 → 기존 점수 무효
        res = r.route_legacy(t, config(changed, default="dflt"), MAPPING, snapshot(ev, ps), [], NOW)
        self.assertEqual(res["selected"]["profile"], "dflt")
        self.assertIn("stale_config", [w["code"] for w in res["warnings"]])
        tampered = dict(snapshot(ev, ps), generated_at="x")
        with self.assertRaises(r.InputError):
            r.validate_snapshot(tampered)


def index_fixture():
    """wiki compile 결과와 같은 모양의 합성 index."""
    f = lambda detect: {"desc": "d", "detect": detect, "evidence": "official"}
    unit = lambda d, facets: {"desc": d, "metric": "elo", "status": "current", "adoption": "active", "facets": facets,
                              "page": "entities/benchmarks/x.md"}
    return {"schema_version": "1.0", "wiki_hash": "w" * 64,
            "facets": {"task": {"coding": f("rule:code_block_or_code_ext"), "repo_coding": f("self"), "general": f("rule:always"),
                                "terminal_ops": f("rule:kw(bash,CI,빌드)")},
                       "lang": {"ko": f("rule:script(hangul)")}, "shape": {"multi_turn": f("rule:round>1")}},
            "postings": {"task:coding": ["u/coding", "u/both"], "task:repo_coding": ["u/both", "u/repo"],
                         "task:general": ["u/general"], "lang:ko": ["u/ko"]},
            "units": {"u/coding": unit("coding prefs", {"task": ["coding"]}),
                      "u/both": unit("both", {"task": ["coding", "repo_coding"]}),
                      "u/repo": unit("repo", {"task": ["repo_coding"]}),
                      "u/general": unit("general", {"task": ["general"]}), "u/ko": unit("korean", {"lang": ["ko"]})}}


class P0Evidence(unittest.TestCase):
    """evidence: facet 판정(규칙 + Orchestrator 태그), 역색인 조회, 프로필별 증거 표. 점수 합산 없음."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = lambda **kw: r.validate_task({"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "fix it",
                                               "prompt": "p", "cwd": self.tmp.name, **kw})

    def tearDown(self):
        self.tmp.cleanup()

    def snap(self, ps, ev, **kw):
        """ev: {pid: {uid: (raw, normalized, effort)}}"""
        s = snapshot({pid: {} for pid in ev}, ps, **kw)
        for p in ps:
            s["profiles"][p["id"]]["evidence"] = {
                uid: {"raw": raw, "normalized": n, "scope": "model_proxy", "cohort_id": f"c-{uid}", "metric_version": "1",
                      "conditions": {"reasoning_effort": eff}, "source_id": "syn", "source_revision": "r", "fetched_at": "x"}
                for uid, (raw, n, eff) in ev[p["id"]].items()}
        s["snapshot_id"] = r.snapshot_hash(s)
        return r.validate_snapshot(s)

    def test_v62_rules_are_deterministic(self):
        from bench_router import evidence as ev
        t = self.t(prompt="```py\nx\n```", summary="CI가 깨짐 한국어 요청입니다", round=2, context_files=[])
        hit = lambda rule, task=t: ev.rule_hit(rule, task)
        self.assertEqual([hit("always"), hit("round>1"), hit("code_block_or_code_ext"), hit("script(hangul)"), hit("kw(bash,CI,빌드)"),
                          hit("script(cyrillic)"), hit("prompt_tokens>500"), hit("nonsense")],
                         [True, True, True, True, True, False, False, None])
        long_ = self.t(prompt="x" * 2100)
        self.assertEqual((hit("prompt_tokens>500", long_), hit("ext(.tsx,.css)", long_)), (True, False))
        self.assertTrue(hit("script(han_only)", self.t(summary="修复登录错误并提交")))
        self.assertFalse(hit("script(han_only)", self.t(summary="ログインの修正です 修复")))  # 가나가 있으면 일본어

    def test_v62_terminal_ops_ignores_plain_build_verb(self):
        from bench_router import evidence as ev
        rule = re.search(r'id = "terminal_ops".*?detect = "rule:(.+?)"', (Path(__file__).parent / "wiki/concepts/facets/task.md").read_text(), re.S).group(1)
        hit = lambda **kw: ev.rule_hit(rule, self.t(**kw))
        self.assertFalse(hit(summary="Build React dashboard component", prompt="Build a responsive dashboard page in React."))
        self.assertTrue(hit(summary="Fix flaky CI", prompt="docker compose up fails in the pipeline"))

    def test_v63_rules_scan_tail_and_language_ignores_code(self):
        from bench_router import evidence as ev
        self.assertTrue(ev.rule_hit("kw(docker)", self.t(prompt="context " * 400 + "fix docker pipeline")))
        for fence in ("```", "~~~"):
            with self.subTest(fence=fence):
                t = self.t(prompt=fence + "python\n" + "variable = 1\n" * 300 + fence + "\n한국어로 오류를 수정해주세요")
                self.assertTrue(ev.rule_hit("script(hangul)", t))
        t = self.t(summary="Fix the bug", prompt="```\n" + "한국어 주석\n" * 300 + "```\nFix this function")
        self.assertFalse(ev.rule_hit("script(hangul)", t))

    def test_v62_facets_from_rules_and_orchestrator(self):
        from bench_router import evidence as ev
        idx = index_fixture()
        facets, warns = ev.task_facets(self.t(prompt="```x```", summary="CI 실패", facets={"task": ["repo_coding"]}), idx)
        self.assertEqual({(f["axis"], f["value"]): f["origin"] for f in facets},
                         {("task", "coding"): "rule", ("task", "general"): "rule", ("task", "terminal_ops"): "rule",
                          ("lang", "ko"): "rule",
                          ("task", "repo_coding"): "orchestrator"})
        for bad in ({"task": ["painting"]}, {"colour": ["red"]}):  # 어휘 밖의 값은 조용히 무시하지 않는다
            with self.assertRaises(r.InputError):
                ev.task_facets(self.t(facets=bad), idx)
        with self.assertRaises(r.InputError):
            self.t(facets=["task"])

    def test_v62_evidence_table_has_effort_missing_and_no_score(self):
        from bench_router import evidence as ev
        ps = [profile("a", reasoning_effort="high"), profile("b", reasoning_effort="high")]
        snap = self.snap(ps, {"a": {"u/both": (1500.0, 0.98, "high"), "u/coding": (1400.0, 0.5, "max")},
                              "b": {"u/both": (1300.0, 0.2, "max")}})
        res = ev.build(self.t(prompt="```x```", facets={"task": ["repo_coding"]}), config(ps), snap, [], index_fixture(), NOW)
        self.assertEqual([u["id"] for u in res["units"]][:2], ["u/both", "u/coding"])  # facet 2개 일치가 먼저
        both = res["units"][0]["profiles"]
        self.assertEqual((both["a"]["effort_matches"], both["b"]["effort_matches"], res["units"][1]["profiles"]["b"]["missing_reason"]),
                         (True, False, "no_observation"))
        self.assertNotIn("score", json.dumps(res))
        text = ev.table(res)
        self.assertIn("1300 p20 max≠high", text)
        self.assertIn("a (high): 1=1500 p98 high · 2=1400 p50 max≠high", text)
        self.assertIn("b (high): 1=1300 p20 max≠high · 2=—", text)
        capped = ev.build(self.t(prompt="```x```", facets={"task": ["repo_coding"]}), config(ps), snap, [], index_fixture(), NOW, max_units=2)
        self.assertEqual((len(capped["units"]), capped["omitted_units"], capped["withheld_units"]), (2, 1, ["u/general"]))

    def test_v62_evidence_without_index_or_with_stale_config(self):
        from bench_router import evidence as ev
        ps = [profile("a")]
        none = ev.build(self.t(), config(ps), None, [], None, NOW)
        self.assertEqual((none["status"], none["units"], [w["code"] for w in none["warnings"]]), ("ok", [], ["wiki_index_missing"]))
        empty = dict(index_fixture(), postings={}, units={})
        self.assertIn("wiki_index_empty", [w["code"] for w in ev.build(self.t(), config(ps), None, [], empty, NOW)["warnings"]])
        snap = self.snap(ps, {"a": {"u/general": (1.0, 0.9, None)}})
        changed = [profile("a", config_revision="v2")]  # 프로필이 바뀌면 이전 snapshot 증거는 쓰지 않는다
        res = ev.build(self.t(), config(changed), snap, [], index_fixture(), NOW)
        self.assertEqual(res["units"][0]["profiles"]["a"]["missing_reason"], "stale_config")
        self.assertIn("stale_config", [w["code"] for w in res["warnings"]])

    def test_v63_task_match_precedes_auxiliary_facets_and_requires_matching_type(self):
        from bench_router import evidence as ev
        idx = index_fixture()
        idx["facets"]["lang"]["en"] = {"desc": "English", "detect": "self", "evidence": "official"}
        for value, detect in (("math", "self"), ("vision", "rule:ext(.png)")):
            idx["facets"]["task"][value] = {"desc": value, "detect": detect, "evidence": "official"}
        for uid, facets in {"u/math": {"task": ["math"]}, "u/vision-en": {"task": ["vision"], "lang": ["en"]},
                            "u/english": {"lang": ["en"], "shape": ["multi_turn"]}}.items():
            idx["units"][uid] = dict(idx["units"]["u/coding"], facets=facets)
            for axis, values in facets.items():
                for value in values:
                    idx["postings"].setdefault(f"{axis}:{value}", []).append(uid)
        task = self.t(round=2, facets={"task": ["math"], "lang": ["en"]})
        build = lambda t, cap: ev.build(t, config([profile("a")]), None, [], idx, NOW, max_units=cap)
        res = build(task, 100)
        ids = [u["id"] for u in res["units"]]
        self.assertEqual(ids[0], "u/math")  # English + multi-turn cannot displace the actual task type.
        self.assertIn("u/english", ids)
        self.assertNotIn("u/vision-en", ids)
        self.assertEqual(build(task, 1)["units"][0]["id"], "u/math")
        self.assertEqual(build(task, 1)["omitted_units"], len(ids) - 1)
        with_image = self.t(round=2, facets=task["facets"], context_files=["image.png"])
        self.assertIn("u/vision-en", [u["id"] for u in build(with_image, 100)["units"]])

    def test_v64_general_units_only_without_task_specific_match(self):
        from bench_router import evidence as ev
        build = lambda t: ev.build(t, config([profile("a")]), None, [], index_fixture(), NOW)
        plain = build(self.t())  # task:general만 켜짐 → 범용 unit이 유일한 증거
        self.assertEqual(([u["id"] for u in plain["units"]], plain["withheld_units"]), (["u/general"], []))
        coding = build(self.t(prompt="```x```"))
        self.assertNotIn("u/general", [u["id"] for u in coding["units"]])
        self.assertEqual(coding["withheld_units"], ["u/general"])
        self.assertIn("withheld because more specific units matched: u/general", ev.table(coding))

    def test_v63_load_index_rejects_structural_corruption(self):
        from bench_router import evidence as ev
        path = Path(self.tmp.name) / "index.json"
        good = index_fixture()
        path.write_text(json.dumps(good))
        self.assertEqual(ev.load_index(self.tmp.name), good)
        bad = [{"schema_version": "1.0"}, dict(good, wiki_hash=None), dict(good, facets=[]),
               dict(good, facets={"task": {"coding": None}}), dict(good, units={"u/coding": None}),
               dict(good, units={"u/coding": {"facets": {}}}),
               dict(good, units={"u/coding": dict(good["units"]["u/coding"], facets={"task": ["unknown"]})}),
               dict(good, postings={"task:coding": ["u/missing"]}), dict(good, postings={"task:coding": None}),
               dict(good, postings={})]
        for idx in bad:
            with self.subTest(index=idx):
                path.write_text(json.dumps(idx))
                loaded = ev.load_index(self.tmp.name)
                self.assertIsNone(loaded)
                res = ev.build(self.t(), config([profile("a")]), None, [], loaded, NOW)
                self.assertEqual([w["code"] for w in res["warnings"]], ["wiki_index_missing"])
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(cli.main(["--cache-dir", self.tmp.name, "wiki", "facets"]), 2)

    def test_v62_evidence_cli_is_read_only(self):
        ps = [profile("a", reasoning_effort="high")]
        home, cache = Path(self.tmp.name) / "cfg", Path(self.tmp.name) / "cache"
        home.mkdir(), cache.mkdir()
        (home / "profiles.toml").write_text('schema_version = "1.0"\n[[profile]]\n' + "\n".join(
            f"{k} = {json.dumps(v)}" for k, v in ps[0].items()) + "\n")
        (cache / "index.json").write_text(json.dumps(index_fixture()))
        fresh = datetime.now(timezone.utc).isoformat(timespec="seconds")  # CLI는 실제 시계를 쓴다
        (cache / "snapshot.json").write_text(json.dumps(self.snap(ps, {"a": {"u/general": (1.0, 0.9, "high")}}, last_success=fresh)))
        tf = Path(self.tmp.name) / "task.json"
        tf.write_text(json.dumps({"schema_version": "1.0", "task_id": "t1", "round": 1, "summary": "s", "prompt": "p", "cwd": self.tmp.name}))
        before = sorted(p.name for p in cache.iterdir())
        for fmt, needle in (("table", "a (high): 1=1 p90 high"), ("json", '"missing_reason": null')):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cli.main(["--config-dir", str(home), "--cache-dir", str(cache), "evidence", "--task", str(tf), "--format", fmt])
            self.assertEqual(code, 0)
            self.assertIn(needle, out.getvalue())
        self.assertEqual(sorted(p.name for p in cache.iterdir()), before)  # 파일 쓰기 없음
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["--config-dir", str(home), "--cache-dir", str(cache), "evidence", "--task", str(tf), "--max-units", "0"]), 2)

    def test_v62_wiki_facets_lists_taggable_vocabulary(self):
        cache = Path(self.tmp.name) / "cache"
        cache.mkdir()
        run = lambda: cli.main(["--cache-dir", str(cache), "wiki", "facets"])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(run(), 0)  # 캐시에 없으면 내장 index.json 사용
        self.assertIn("task", json.loads(out.getvalue())["facets"])
        (cache / "index.json").write_text(json.dumps(index_fixture()))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(run(), 0)
        res = json.loads(out.getvalue())
        self.assertEqual(res["facets"], {"task": {"coding": "d", "repo_coding": "d", "general": "d"},
                                         "lang": {"ko": "d"}, "shape": {}})
        self.assertEqual(res["detection"]["task"]["coding"], "rule:code_block_or_code_ext")
        self.assertEqual(res["detection"]["task"]["repo_coding"], "self")

    def test_v63_explicit_webdev_facet_without_context_files(self):
        from bench_router import evidence as ev
        idx = index_fixture()
        idx["facets"]["task"]["webdev_react"] = {"desc": "React", "detect": "rule:ext(.jsx,.tsx)", "evidence": "official"}
        idx["units"]["u/react"] = dict(idx["units"]["u/coding"], facets={"task": ["webdev_react"]})
        idx["postings"]["task:webdev_react"] = ["u/react"]
        Path(self.tmp.name, "index.json").write_text(json.dumps(idx))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["--cache-dir", self.tmp.name, "wiki", "facets"]), 0)
        self.assertIn("webdev_react", json.loads(out.getvalue())["facets"]["task"])
        task = self.t(prompt="Build a React dashboard", facets={"task": ["webdev_react"]})
        res = ev.build(task, config([profile("a")]), None, [], idx, NOW, max_units=1)
        self.assertEqual(res["units"][0]["id"], "u/react")
        self.assertIn({"axis": "task", "value": "webdev_react", "origin": "orchestrator"}, res["facets"])


class P0Dotenv(unittest.TestCase):
    def test_v65_project_dotenv_precedence_allowlist_and_quotes(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            cfg, proj = Path(tmp) / "cfg", Path(tmp) / "proj"
            cfg.mkdir(), proj.mkdir()
            (cfg / "env").write_text("JEV_API_KEY=from-config\nJEV_MODEL=cfg-model\n")
            (proj / ".env").write_text("# c\nexport JEV_API_KEY='from-project'\nUNRELATED_SECRET=x\nTYPESAFE_API_KEY=\"t\"\nbroken\n")
            with patch.dict(os.environ, {"JEV_MODEL": "from-process"}):
                env = r.env_with_dotenv(cfg, proj)
            self.assertEqual((env["JEV_API_KEY"], env["TYPESAFE_API_KEY"], env["JEV_MODEL"]), ("from-project", "t", "from-process"))
            self.assertNotIn("UNRELATED_SECRET", env)
            with patch.dict(os.environ, {}, clear=True):  # 파일이 없으면 프로세스 환경만
                self.assertEqual(r.env_with_dotenv(Path(tmp) / "none", Path(tmp) / "none"), {})


class P0Decision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import runpy
        cls.helper = runpy.run_path(str(Path(__file__).parent / "skills/bench-router/scripts/decide.py"))

    def setUp(self):
        self.req = {"state": "Fix a bug", "questions": {
            "profile": {"type": "choice", "instructions": "Choose an eligible profile or abstain",
                        "criteria": {"cheap": "Small tasks", "abstain": "Insufficient evidence"}},
            "coding": {"type": "noul", "instructions": "Does this task require code changes?"}}}
        self.reply = {"model": "jev-1.13.0", "answers": {
            "profile": {"type": "choice", "choice": "cheap", "confidence": 0.8},
            "coding": {"type": "noul", "noul": 0.9}}, "usage": {"input_tokens": 100, "output_tokens": 20}}

    def test_v64_without_key_requests_a_cheap_native_subagent(self):
        from unittest.mock import patch
        with patch("urllib.request.urlopen") as post:
            res = self.helper["decide"](self.req, env={})
            self.assertEqual((res["status"], res["model"], res["request"]),
                             ("subagent_required", "cheapest_available", self.req))
            explicit = self.helper["decide"](self.req, env={"BENCH_ROUTER_DECISION_MODEL": "my-cheap-model"})
            self.assertEqual(explicit["model"], "my-cheap-model")
            post.assert_not_called()

    def test_v64_key_calls_jev_and_retains_usage_without_credentials(self):
        from unittest.mock import patch
        for key_name in ("TYPESAFE_API_KEY", "JEV_API_KEY"):
            with self.subTest(key_name=key_name), patch("urllib.request.urlopen") as post:
                post.return_value.__enter__.return_value.read.return_value = json.dumps(self.reply).encode()
                res = self.helper["decide"](self.req, env={key_name: "synthetic-secret", "JEV_MODEL": "jev-1.13.0"}, host="codex")
                req = post.call_args.args[0]
                self.assertEqual(req.full_url, "https://api.typesafe.ai/v1/systemone")
                self.assertEqual(req.get_header("Authorization"), "Bearer synthetic-secret")
                self.assertEqual(json.loads(req.data), {**self.req, "model": "jev-1.13.0"})
                self.assertEqual((res["provider"], res["answers"]["profile"]["choice"], res["usage"]["input_tokens"]),
                                 ("jev", "cheap", 100))
                self.assertNotIn("synthetic-secret", json.dumps(res))

    def test_v64_jev_failure_or_bad_answer_falls_back_without_error_body(self):
        from unittest.mock import patch
        for payload in (None, b'not json', b'{"answers": {}}'):
            with self.subTest(payload=payload), patch("urllib.request.urlopen") as post:
                if payload is None:
                    post.side_effect = TimeoutError("synthetic-secret")
                else:
                    post.return_value.__enter__.return_value.read.return_value = payload
                res = self.helper["decide"](self.req, env={"TYPESAFE_API_KEY": "synthetic-secret"})
                self.assertEqual((res["status"], res["reason"]), ("subagent_required", "jev_unavailable"))
                self.assertNotIn("synthetic-secret", json.dumps(res))
                post.assert_called_once()

    def test_v64_subagent_reply_is_validated_offline(self):
        from unittest.mock import patch
        decide = self.helper["decide"]
        with patch("urllib.request.urlopen") as post:
            res = decide(self.req, env={}, response=self.reply)
            self.assertEqual((res["provider"], res["confidence_kind"]), ("subagent", "self_reported"))
            for bad in ({"answers": {}},
                        {**self.reply, "answers": {**self.reply["answers"], "profile": {"type": "choice", "choice": "ineligible"}}},
                        {**self.reply, "answers": {**self.reply["answers"], "coding": {"type": "noul", "noul": float("nan")}}}):
                with self.subTest(response=bad), self.assertRaises(r.InputError):
                    decide(self.req, env={}, response=bad)
            post.assert_not_called()

    def test_v64_null_reply_cannot_trigger_an_api_call(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            req, reply = Path(tmp) / "request.json", Path(tmp) / "reply.json"
            req.write_text(json.dumps(self.req))
            reply.write_text("null")
            with patch("urllib.request.urlopen") as post, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(self.helper["main"](["--request", str(req), "--response", str(reply)]), 2)
            post.assert_not_called()

    def test_v65_host_specific_native_handoff_and_reply_validation(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {}, clear=True), patch("urllib.request.urlopen") as post, \
                patch("bench_router.routing.env_with_dotenv", side_effect=lambda *a, **k: dict(os.environ)):  # 개발 머신의 실제 .env 차단
            req, reply = Path(tmp) / "request.json", Path(tmp) / "reply.json"
            req.write_text(json.dumps(self.req))
            reply.write_text(json.dumps(self.reply))
            for host, model in (("antigravity", "flash"), ("codex", "gpt-6-luna"), ("claude", "haiku")):
                with self.subTest(host=host):
                    args = ["--host", host, "--request", str(req)]
                    out = io.StringIO()
                    with contextlib.redirect_stdout(out):
                        self.assertEqual(self.helper["main"](args), 0)
                    packet = json.loads(out.getvalue())
                    self.assertEqual((packet["status"], packet["agent"], packet["host"], packet["model"]),
                                     ("subagent_required", "bench-decider", host, model))
                    self.assertEqual(packet["request"], self.req)
                    out = io.StringIO()
                    with contextlib.redirect_stdout(out):
                        self.assertEqual(self.helper["main"](args + ["--response", str(reply)]), 0)
                    result = json.loads(out.getvalue())
                    self.assertEqual((result["status"], result["model"], result["answers"]["profile"]["choice"]),
                                     ("ok", model, "cheap"))
            explicit = self.helper["decide"](self.req, env={"BENCH_ROUTER_DECISION_MODEL": "my-cheap-model"}, host="codex")
            self.assertEqual(explicit["model"], "my-cheap-model")
            with self.assertRaises(r.InputError):
                self.helper["decide"](self.req, env={}, host="unknown")
            post.assert_not_called()

    def test_v66_copied_skill_runs_standalone(self):
        import shutil
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "bench-router"
            shutil.copytree(Path(__file__).parent / "skills/bench-router", copied, symlinks=False)
            self.assertTrue((copied / "bench_router/cli.py").is_file())
            self.assertTrue((copied / "bench_router/index.json").is_file())
            self.assertFalse((copied / "wiki").exists())
            p = subprocess.run([sys.executable, str(copied / "scripts/cli.py"), "--cache-dir", tmp, "wiki", "facets"],
                               cwd=tmp, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(p.stdout)["status"], "ok")


class P0VendorGuidance(unittest.TestCase):
    def setUp(self):
        from bench_router import decision
        self.d = decision
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.task = r.validate_task({"schema_version": "1.0", "task_id": "guided", "round": 1,
            "summary": "Fix one typo", "prompt": "Fix a typo in a comment.", "cwd": self.tmp.name})
        self.ps = [profile("light", model_id="gpt-6-luna", reasoning_effort="low"),
                   profile("strong", model_id="gpt-6-astra", reasoning_effort="xhigh")]
        self.cfg = config(self.ps, default="strong", fallback=["light"])

    def route(self, **kw):
        return r.route(self.task, self.cfg, MAPPING, kw.pop("snap", None), [], kw.pop("now", NOW), host="codex", env={}, **kw)

    def finish(self, chosen="light", **kw):
        response = guided_responses(self.route(**kw), lambda x: self.route(response=x, **kw), chosen)
        return self.route(response=response, **kw)

    def fit_packet(self, **kw):
        return self.route(response=guided_reply(self.route(**kw), "__tie__"), **kw)

    def indexed(self, ids=("u/coding",)):
        from copy import deepcopy
        idx = index_fixture()
        idx["units"] = {uid: deepcopy(idx["units"]["u/coding"]) for uid in ids}
        idx["postings"] = {"task:coding": list(ids)}
        self.task["facets"] = {"task": ["coding"]}
        return idx

    def exact(self, values):
        snap = snapshot(values, self.ps)
        for p in self.ps:
            for row in snap["profiles"].get(p["id"], {}).get("evidence", {}).values():
                row["scope"] = "exact_profile"
                row["conditions"] = {k: "fixture" for k in self.d.PROTOCOL}
                row["conditions"].update(direction="higher", agent_scaffold=p["harness_id"], reasoning_effort=p["reasoning_effort"])
        snap["snapshot_id"] = r.snapshot_hash(snap)
        return snap

    def test_v67_offline_stages_exclude_unrelated_evidence(self):
        from unittest.mock import patch
        with patch("urllib.request.urlopen") as post, patch.object(r, "assess", wraps=r.assess) as assess:
            packet = self.route()
            self.assertEqual((packet["status"], packet["decision"]["stage"], assess.call_count), ("decision_required", "analysis", 1))
            self.assertNotIn("candidates", packet["decision_request"]["state"])
            fit = self.fit_packet()
            self.assertEqual(fit["decision"]["stage"], "fit")
            self.assertNotIn("observations", json.dumps(fit["decision_request"]))
            self.assertNotIn("legacy_score", json.dumps(fit["decision_request"]))
            self.assertTrue(all(c["score"] is None for c in packet["candidates"]))
            self.cfg = config(self.ps[:1])
            self.assertEqual(self.route()["status"], "decision_required")
            post.assert_not_called()

    def test_v68_selection_replays_all_stages_and_rechecks_constraints(self):
        out = self.finish()
        self.assertEqual((out["status"], out["selected"]["profile"]), ("selected", "light"))
        selection = {k: v for k, v in out["selection"].items() if k != "source"}
        self.assertEqual(selection["policy"], self.d.POLICY)
        self.assertEqual([s["stage"] for s in selection["decision"]["stages"]], ["analysis", "fit"])
        self.assertEqual(self.route(selection=selection)["selected"], out["selected"])
        self.ps[0]["enabled"] = False
        self.assertEqual(self.route(selection=selection)["status"], "stale_assessment")

    def test_v69_wrong_rule_stage_digest_and_model_are_rejected(self):
        from copy import deepcopy
        fit = self.fit_packet()
        for response in (guided_reply(fit, "light", **{"fit:light": "gpt-6-astra:xhigh"}),
                         guided_reply(fit, "light", **{"fit:light": "invented"})):
            with self.assertRaises(r.InputError):
                self.route(response=response)
        response = guided_reply(fit, "light")
        bad = deepcopy(response)
        bad["stages"][-1]["request_digest"] = "0" * 64
        with self.assertRaises(r.InputError):
            self.route(response=bad)
        response["stages"][-1]["model"] = "substitution"
        self.assertEqual(self.route(response=response)["status"], "decision_unavailable")

    def test_v70_unknown_configuration_stays_provisional(self):
        for key, value in (("model_id", "gpt-6-luna-new"), ("reasoning_effort", "unknown")):
            old = self.ps[0][key]
            self.ps[0][key] = value
            out = self.finish()
            self.assertIn("guidance_missing", out["selection"]["decision"]["uncertainty"])
            self.ps[0][key] = old

    def test_v71_workload_answers_change_the_next_request(self):
        first = self.route()
        a = self.route(response=guided_reply(first, "light", reasoning="bounded"))
        b = self.route(response=guided_reply(first, "light", reasoning="demanding"))
        self.assertNotEqual(a["assessment_digest"], b["assessment_digest"])
        self.assertEqual(b["decision_request"]["state"]["analysis"]["workload"]["reasoning"], "demanding")
        with self.assertRaises(r.InputError):
            self.route(response={"stages": [*b["decision"]["completed"], guided_reply(a, "light")["stages"][-1]]})

    def test_v72_cost_ties_abstention_and_missing_prices(self):
        self.assertEqual(self.finish("__tie__")["selected"]["profile"], "strong")
        self.assertEqual(self.finish("__abstain__")["status"], "decision_unavailable")
        self.task["priority"] = "cost"
        ctx = {"schema_version": "2.0", "profiles": {pid: {"metrics": {"cost.estimated_usd": {
            "value": value, "unit": "usd", "source": "synthetic"}}} for pid, value in (("light", 0.01), ("strong", 0.1))}}
        self.assertEqual(self.finish("__tie__", context=ctx)["selected"]["profile"], "light")
        self.assertIn("cost_unknown", self.finish("__tie__")["selection"]["decision"]["uncertainty"])


    def test_v73_jev_stages_preserve_usage_and_failure_is_native_handoff(self):
        from unittest.mock import MagicMock, patch
        def respond(request, **kwargs):
            req = json.loads(request.data)
            req.pop("model")
            raw = guided_reply({"decision_request": req, "assessment_digest": r.canonical_hash(req)}, "light")["stages"][-1]
            raw.update(model="jev-1.13.0", usage={"input_tokens": 100, "output_tokens": 10})
            result = MagicMock()
            result.__enter__.return_value.read.return_value = json.dumps(raw).encode()
            return result
        with patch("urllib.request.urlopen", side_effect=respond) as post:
            out = r.route(self.task, self.cfg, MAPPING, None, [], NOW, host="codex", allow_network=True, env={"JEV_API_KEY": "synthetic"})
            self.assertEqual((out["status"], post.call_count), ("selected", 2))
            self.assertEqual([s["usage"]["input_tokens"] for s in out["selection"]["decision"]["stages"]], [100, 100])
        with patch("urllib.request.urlopen", side_effect=TimeoutError("secret")):
            out = r.route(self.task, self.cfg, MAPPING, None, [], NOW, allow_network=True, env={"JEV_API_KEY": "synthetic"})
            self.assertEqual(out["decision"]["reason"], "jev_unavailable")
            self.assertNotIn("secret", json.dumps(out))

    def test_v74_cli_and_copied_skill_use_the_same_staged_policy(self):
        import shutil
        import subprocess
        import sys
        root = Path(self.tmp.name)
        cfg = root / "cfg"
        cfg.mkdir()
        (cfg / "profiles.toml").write_text((EX / "profiles.example.toml").read_text().replace("enabled = false", "enabled = true"))
        task = root / "task.json"
        task.write_text(json.dumps({"schema_version": "1.0", **self.task}))
        argv = ["--config-dir", str(cfg), "--cache-dir", str(root / "cache"), "route", "--task", str(task), "--host", "codex", "--dry-run"]
        response_path = root / "response.json"
        def run(response=None):
            extra = []
            if response is not None:
                response_path.write_text(json.dumps(response))
                extra = ["--decision-response", str(response_path)]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                cli.main([*argv, *extra])
            return json.loads(out.getvalue())
        packet = run()
        pid = packet["candidates"][0]["profile"]
        replies = guided_responses(packet, run, pid)
        self.assertEqual(run(replies)["selected"]["profile"], pid)
        copied = root / "copied"
        shutil.copytree(Path(__file__).parent / "skills/bench-router", copied, symlinks=False)
        proc = subprocess.run([sys.executable, str(copied / "scripts/cli.py"), *argv], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 17, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["assessment_digest"], packet["assessment_digest"])
        self.assertEqual((copied / "bench_router/guidelines.toml").read_bytes(), self.d.GUIDELINES.read_bytes())

    def test_v75_guidance_matches_only_exact_models_and_efforts(self):
        for model, effort in (("claude-sonnet-5-5", "medium"), ("claude-opus-5-5", "medium"),
                              ("gemini-3.8-flash", "high"), ("gemini-4-argon", "medium")):
            self.cfg = config([profile("only", model_id=model, reasoning_effort=effort)])
            packet = self.fit_packet()
            self.assertEqual(packet["decision_request"]["state"]["candidates"][0]["rules"], [f"{model}:{effort}"])
            self.assertEqual(self.finish("only")["status"], "selected")

    def test_v78_freshness_and_profile_measurement_conditions_are_bound(self):
        from datetime import timedelta
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.8}})
        out = self.finish(snap=snap, index=idx)
        row = out["selection"]["decision"]["evaluation"]["observations"]["light"]["u/coding"]
        self.assertTrue(row["exact_profile"])
        selection = {k: v for k, v in out["selection"].items() if k != "source"}
        self.assertEqual(self.route(selection=selection, snap=snap, index=idx, now=NOW + timedelta(hours=1))["status"], "stale_assessment")
        snap["profiles"]["light"]["evidence"]["u/coding"]["conditions"]["reasoning_effort"] = "high"
        changed = self.finish(snap=snap, index=idx)["selection"]["decision"]["evaluation"]
        self.assertFalse(changed["observations"]["light"]["u/coding"]["exact_profile"])
        self.assertFalse(changed["comparisons"])

    def test_v79_tampered_selection_and_budget_changes_are_rejected(self):
        from copy import deepcopy
        out = self.finish()
        selection = {k: v for k, v in out["selection"].items() if k != "source"}
        bad = deepcopy(selection)
        bad["decision"]["stages"].reverse()
        with self.assertRaises(r.InputError):
            self.d.validate_selection(bad)
        ctx = {"schema_version": "2.0", "max_estimated_cost_usd": 0.01, "profiles": {"light": {"metrics": {
            "cost.estimated_usd": {"value": 0.02, "unit": "usd", "source": "quote"}}}}}
        self.assertEqual(self.route(context=ctx)["status"], "no_eligible_profile")
        self.task["facets"] = {"difficulty": ["hard_prompts"]}
        self.assertEqual(self.route(selection=selection)["status"], "stale_assessment")

    def test_v80_excluded_profiles_cannot_displace_eligible_observations(self):
        ids = [f"u/{i:02}" for i in range(12)] + ["u/z-only-eligible"]
        idx = self.indexed(ids)
        self.ps = [profile(f"p{i}", model_id="gpt-6-luna", reasoning_effort="low") for i in range(8)]
        self.cfg = config(self.ps)
        self.task["exclude_profiles"] = [p["id"] for p in self.ps[1:]]
        snap = self.exact({"p0": {ids[-1]: 0.8}, **{p["id"]: {uid: 0.7 for uid in ids[:12]} for p in self.ps[1:]}})
        evaluation = self.finish("p0", snap=snap, index=idx)["selection"]["decision"]["evaluation"]
        self.assertIn(ids[-1], evaluation["observations"]["p0"])
        self.assertEqual(set(evaluation["observations"]), {"p0"})
        self.assertNotIn("aa_intelligence", evaluation["units"])

    def test_v81_numeric_selection_uses_comparable_raw_scores(self):
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.9}, "strong": {"u/coding": 0.6}})
        for pid, normalized in (("light", 0), ("strong", 1)):
            snap["profiles"][pid]["evidence"]["u/coding"].update(normalized=normalized, cohort_id=pid)
        out = self.finish("__tie__", snap=snap, index=idx)
        self.assertEqual(out["selected"]["profile"], "light")
        self.assertEqual(len(out["selection"]["decision"]["stages"]), 2)
        snap["profiles"]["strong"]["evidence"]["u/coding"]["conditions"]["dataset_revision"] = "different"
        self.assertFalse(self.finish("__tie__", snap=snap, index=idx)["selection"]["decision"]["evaluation"]["comparisons"])

    def test_v82_conditional_effort_requires_real_workflow_gain(self):
        idx = self.indexed()
        self.ps = [profile("light", model_id="claude-sonnet-5-5", reasoning_effort="medium"),
                   profile("strong", model_id="claude-sonnet-5-5", reasoning_effort="xhigh")]
        self.cfg = config(self.ps, default="strong")
        proxy = snapshot({"strong": {"u/coding": 0.9}}, self.ps)
        d = self.finish("strong", snap=proxy, index=idx)["selection"]["decision"]
        self.assertIn("workflow_gain_unverified", d["uncertainty"])
        self.assertEqual(d["evaluation"]["fits"]["strong"]["status"], "provisional")
        exact = self.exact({"light": {"u/coding": 0.6}, "strong": {"u/coding": 0.9}})
        d = self.finish("strong", snap=exact, index=idx)["selection"]["decision"]
        self.assertNotIn("workflow_gain_unverified", d["uncertainty"])
        self.assertEqual(d["evaluation"]["fits"]["strong"]["workflow_gain"]["baseline_profile"], "light")

    def test_v83_conflicting_benchmarks_request_relevance_without_scores(self):
        idx = self.indexed(("u/one", "u/two"))
        snap = self.exact({"light": {"u/one": 0.9, "u/two": 0.5}, "strong": {"u/one": 0.5, "u/two": 0.9}})
        fit = self.fit_packet(index=idx, snap=snap)
        packet = self.route(index=idx, snap=snap, response=guided_reply(fit, "__tie__"))
        self.assertEqual(packet["decision"]["stage"], "benchmark")
        self.assertNotIn("raw", json.dumps(packet["decision_request"]))
        self.assertNotIn("model_id", json.dumps(packet["decision_request"]))
        out = self.route(index=idx, snap=snap, response=guided_reply(packet, "__tie__", **{"relevance:u/one": 1}))
        self.assertEqual(out["selected"]["profile"], "light")
        self.assertEqual(self.route(index=idx, snap=snap, response=guided_reply(packet, "__tie__"))["status"], "decision_unavailable")

    def test_v93_relevance_weights_combine_benchmarks_and_suites_share_a_vote(self):
        ids = ("u/a", "u/b", "u/c", "u/d")
        idx = self.indexed(ids)
        snap = self.exact({"light": {"u/a": 0.5, "u/b": 0.5, "u/c": 0.9, "u/d": 0.9},
                           "strong": {"u/a": 0.9, "u/b": 0.9, "u/c": 0.5, "u/d": 0.5}})
        for uid, suite in zip(ids, ("x", "x", "y", "z")):
            for sp in snap["profiles"].values():
                sp["evidence"][uid]["conditions"]["suite"] = suite
        packet = self.route(index=idx, snap=snap, response=guided_reply(self.fit_packet(index=idx, snap=snap), "__tie__"))
        self.assertEqual(packet["decision"]["stage"], "benchmark")
        ones = {f"relevance:{uid}": 1 for uid in ids}
        out = self.route(index=idx, snap=snap, response=guided_reply(packet, "__tie__", **ones))
        # Ungrouped this would be a 2:2 tie resolved to the default "strong".
        self.assertEqual(out["selected"]["profile"], "light")
        self.assertEqual(out["selection"]["decision"]["evaluation"]["benchmark_relevance"]["u/a"], 1)


    def test_v84_model_proxy_can_inform_model_choice_without_effort_claim(self):
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.9}, "strong": {"u/coding": 0.6}})
        for sp in snap["profiles"].values():
            row = sp["evidence"]["u/coding"]
            row.update(scope="model_proxy", cohort_id="same-source-cohort")
            row["conditions"].update(reasoning_effort=None, agent_scaffold=None)
        out = self.finish("__tie__", index=idx, snap=snap)
        self.assertEqual(out["selected"]["profile"], "light")
        self.assertIn("model_proxy_comparison", out["selection"]["decision"]["uncertainty"])
        self.assertIn("task_quality_unverified", out["selection"]["decision"]["uncertainty"])
        snap["profiles"]["strong"]["evidence"]["u/coding"]["cohort_id"] = "other"
        self.assertFalse(self.finish("__tie__", index=idx, snap=snap)["selection"]["decision"]["evaluation"]["comparisons"])

    def test_v85_fanout_reuses_analysis_and_fit_without_provider_calls(self):
        from unittest.mock import patch
        cache = {}
        self.finish("__tie__", decision_cache=cache)
        with patch.object(self.d.provider, "decide", side_effect=AssertionError("must reuse analysis and fit")):
            out = self.route(omit_profiles=["strong"], decision_cache=cache)
        self.assertEqual(out["selected"]["profile"], "light")
        self.assertEqual(len(cache), 2)
        self.assertEqual(set(out["selection"]["decision"]["evaluation"]["fits"]), {"light"})

    def test_v86_forged_observations_and_changed_guides_do_not_replay(self):
        from copy import deepcopy
        from unittest.mock import patch
        out = self.finish()
        selection = {k: v for k, v in out["selection"].items() if k != "source"}
        forged = deepcopy(selection)
        forged["decision"]["evaluation"]["comparisons"] = {"fake": ["light"]}
        forged["assessment_digest"] = r.canonical_hash(forged["decision"])
        self.assertEqual(self.route(selection=forged)["status"], "stale_assessment")
        guide = self.d.load_guidelines()
        with patch.object(self.d, "load_guidelines", return_value={**guide, "hash": "changed"}):
            self.assertEqual(self.route(selection=selection)["status"], "stale_assessment")

    def test_v87_semantic_facets_are_forwarded_and_uncertainty_is_retained(self):
        idx = index_fixture()
        first = self.route(index=idx)
        fit = self.route(index=idx, response=guided_reply(first, "light", **{
            "facet:task:repo_coding": 0.9, "facet:task:coding": 0.5}))
        analysis = fit["decision_request"]["state"]["analysis"]
        self.assertIn("task:coding", analysis["unresolved_facets"])
        self.assertIn({"axis": "task", "value": "repo_coding", "origin": "semantic"}, analysis["facets"])
        out = self.route(index=idx, response=guided_reply(fit, "light"))
        self.assertIn("u/repo", out["selection"]["decision"]["evaluation"]["units"])

    def test_v88_vendor_path_does_not_compute_legacy_benchmark_scores(self):
        from unittest.mock import patch
        with patch.object(r, "benchmark_evaluation", side_effect=AssertionError("legacy benchmark work")):
            self.assertEqual(self.finish()["status"], "selected")

    def test_v89_snapshot_change_reuses_semantics_but_recomputes_the_winner(self):
        from unittest.mock import patch
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.9}, "strong": {"u/coding": 0.6}})
        cache = {}
        first = self.finish("__tie__", index=idx, snap=snap, decision_cache=cache)
        snap["profiles"]["strong"]["evidence"]["u/coding"]["raw"] = 0.99
        snap["snapshot_id"] = r.snapshot_hash(snap)
        with patch.object(self.d.provider, "decide", side_effect=AssertionError("semantics unchanged")):
            second = self.route(index=idx, snap=snap, decision_cache=cache)
        self.assertEqual((first["selected"]["profile"], second["selected"]["profile"]), ("light", "strong"))
        self.assertNotEqual(first["assessment_digest"], second["assessment_digest"])


    def test_v90_direction_and_meaningful_gap_use_raw_metric_units(self):
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.6}, "strong": {"u/coding": 0.9}})
        idx["units"]["u/coding"]["meaningful_gap"] = 0.3
        out = self.finish("__tie__", snap=snap, index=idx)
        self.assertEqual(out["selection"]["decision"]["evaluation"]["comparisons"]["u/coding"], ["light", "strong"])
        idx["units"]["u/coding"]["meaningful_gap"] = 0
        for sp in snap["profiles"].values():
            sp["evidence"]["u/coding"]["conditions"]["direction"] = "lower"
        self.assertEqual(self.finish("__tie__", snap=snap, index=idx)["selected"]["profile"], "light")

    def test_v91_conditional_gain_cannot_use_mismatched_protocol_or_stale_control(self):
        from datetime import timedelta
        idx = self.indexed()
        self.ps = [profile("light", model_id="claude-sonnet-5-5", reasoning_effort="medium"),
                   profile("strong", model_id="claude-sonnet-5-5", reasoning_effort="xhigh")]
        self.cfg = config(self.ps, default="strong")
        snap = self.exact({"light": {"u/coding": 0.6}, "strong": {"u/coding": 0.9}})
        snap["profiles"]["light"]["evidence"]["u/coding"]["conditions"]["dataset_revision"] = "different"
        self.assertIn("workflow_gain_unverified", self.finish("strong", snap=snap, index=idx)["selection"]["decision"]["uncertainty"])
        snap["profiles"]["light"]["evidence"]["u/coding"]["conditions"]["dataset_revision"] = "fixture"
        self.assertIn("workflow_gain_unverified", self.finish("strong", snap=snap, index=idx, now=NOW + timedelta(hours=1))["selection"]["decision"]["uncertainty"])

    def test_v92_majority_winner_skips_benchmark_stage(self):
        ids = ("u/one", "u/two", "u/three")
        idx = self.indexed(ids)
        snap = self.exact({"light": {"u/one": 0.9, "u/two": 0.9, "u/three": 0.5},
                           "strong": {"u/one": 0.5, "u/two": 0.5, "u/three": 0.9}})
        out = self.route(index=idx, snap=snap, response=guided_reply(self.fit_packet(index=idx, snap=snap), "__tie__"))
        self.assertEqual(out["selected"]["profile"], "light")
        self.assertEqual(len(out["selection"]["decision"]["stages"]), 2)
        self.assertIsNone(out["selection"]["decision"]["evaluation"]["benchmark_relevance"])


if __name__ == "__main__":
    unittest.main()
