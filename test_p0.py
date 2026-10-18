"""P0 검증 V01–V10 (06 문서). 실행: python3 -m unittest -v test_p0"""
import contextlib
import io
import json
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
        return r.route(t, config(profiles, **cfg_kw), MAPPING, snapshot(ev, profiles), [], NOW)

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
        self.assertEqual(r.route(t, config(ps), MAPPING, None, [], NOW)["status"], "no_eligible_profile")
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
        legacy = r.route(t, config(ps), MAPPING, snap, [], NOW, context=ctx)
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
        res = r.route(t, config(ps, default="dflt"), MAPPING, s, [], NOW)
        self.assertEqual(res["selected"]["profile"], "dflt")
        self.assertIn("source_too_stale", [w["code"] for w in res["warnings"]])
        changed = [profile("a", args=["-m", "other"]), profile("dflt")]  # 설정 변경 → 기존 점수 무효
        res = r.route(t, config(changed, default="dflt"), MAPPING, snapshot(ev, ps), [], NOW)
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
            "units": {"u/coding": unit("coding prefs", {}), "u/both": unit("both", {}), "u/repo": unit("repo", {}),
                      "u/general": unit("general", {}), "u/ko": unit("korean", {})}}


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
        self.assertEqual((len(capped["units"]), capped["omitted_units"]), (2, 2))

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


if __name__ == "__main__":
    unittest.main()
