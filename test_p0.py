"""P0 검증 V01–V10 (06 문서). 실행: python3 -m unittest -v test_p0"""
import contextlib
import io
import json
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
        res = r.evaluate(self.task(), config(ps), MAPPING, None, [], NOW, context=context)
        self.assertEqual((res["status"], res["selected"], len(res["candidates"])), ("ok", None, 1))
        self.assertEqual(res["candidates"][0]["context_facts"]["estimated_cost_usd"], 0.003)
        self.assertEqual(res["excluded"], [{"profile": "b", "reasons": ["context_unknown", "estimated_cost_unknown"]}])
        self.assertEqual(r.pin_selection(res, config(ps), "a")["selected"]["profile"], "a")
        self.assertEqual(r.pin_selection(res, config(ps), "b")["status"], "no_eligible_profile")
        over = r.evaluate(self.task(), config(ps), MAPPING, None, [], NOW,
                          context={**context, "max_estimated_cost_usd": 0.0029})
        self.assertIn("estimated_cost_exceeds_max", over["excluded"][0]["reasons"])
        no_cap = r.evaluate(self.task(), config(ps), MAPPING, None, [], NOW,
                            context=r.validate_context({"schema_version": "1.0", "profiles": {"b": {}}}, ["a", "b"]))
        unknown = next(c for c in no_cap["candidates"] if c["profile"] == "b")
        self.assertEqual((unknown["context_facts"]["estimated_cost_usd"],
                          unknown["context_facts"]["cost_missing_reason"]), (None, "estimate_or_price_missing"))

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
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["--config-dir", str(cfg_dir), "--cache-dir", str(Path(self.cwd) / "cache"),
                             "evaluate", "--task", str(task_file)])
        res = json.loads(out.getvalue())
        self.assertEqual((code, res["status"], res["selected"], len(res["candidates"])), (0, "ok", None, 1))

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
        one.pop("config_hash"), two.pop("config_hash")  # 설정 파일 순서만 다름
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
        self.assertEqual(res["excluded"], [{"profile": "local-codex-example", "reasons": ["disabled"]}])
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


if __name__ == "__main__":
    unittest.main()
