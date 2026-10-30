"""P0 검증 V01–V10 (06 문서). 실행: python3 -m unittest -v test_p0"""
import contextlib
import io
import json
import os
import re
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timezone
from pathlib import Path

from bench_router import cli
from bench_router import routing as r

EX = Path(__file__).parent / "examples"
NOW = datetime(2026, 10, 12, tzinfo=timezone.utc)
MAPPING = r.load_categories(cli.BUNDLED_CATEGORIES)


# Guidance requests carry no profile IDs; the synthetic responder maps a chosen profile to its guide option through this.
PROFILES = {}


class P0Help(unittest.TestCase):
    def test_v96_all_command_help_is_standalone_and_offline(self):
        parsers = []
        original = cli.argparse.ArgumentParser.parse_args

        def capture(parser, *args, **kwargs):
            parsers.append(parser)
            return original(parser, *args, **kwargs)

        with mock.patch.object(cli.argparse.ArgumentParser, "parse_args", capture):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exited:
                cli.main(["--help"])
        self.assertEqual(exited.exception.code, 0)
        root = parsers[0]
        commands = next(a for a in root._actions if isinstance(a, cli.argparse._SubParsersAction))
        self.assertEqual(set(commands.choices), set(cli.COMMAND_EPILOGS))
        for name, parser in commands.choices.items():
            self.assertTrue(parser.description, name)
            for action in parser._actions:
                self.assertTrue(action.help, (name, action.dest))
        with tempfile.TemporaryDirectory() as tmp:
            for command in [[], *[[name] for name in commands.choices]]:
                for flag in ("-h", "--help"):
                    with self.subTest(command=command, flag=flag):
                        out = io.StringIO()
                        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as exited:
                            cli.main(["--config-dir", tmp, "--cache-dir", tmp, *command, flag])
                        self.assertEqual(exited.exception.code, 0)
                        self.assertIn("BEFORE", out.getvalue())
                        self.assertIn("bench-router", out.getvalue())
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_v96_documented_minimal_task_satisfies_input_contract(self):
        task, _ = json.JSONDecoder().raw_decode(cli.TASK_EPILOG[cli.TASK_EPILOG.index("{"):])
        self.assertEqual(set(task), set(r.TASK_REQUIRED))
        with tempfile.TemporaryDirectory() as tmp:
            task["cwd"] = tmp
            validated = r.validate_task(task)
            self.assertEqual(validated["round"], 1)
        for key in (*r.TASK_REQUIRED, *r.TASK_OPTIONAL, *r.CONSTRAINT_DEFAULTS):
            self.assertIn(key, cli.TASK_EPILOG)


def profile(pid, tier="medium", **kw):
    p = {"id": pid, "enabled": True, "kind": "codex", "executable": "codex", "args": ["-m", pid],
         "model_id": pid, "harness_id": "codex-cli", "reasoning_effort": "unknown", "config_revision": "t",
         "cost_tier": tier, "inference_local": False, "context_tokens": 0, "capabilities": ["filesystem_write"]}
    PROFILES[pid] = {**p, **kw}
    return PROFILES[pid]


def config(profiles):
    return {"schema_version": "1.0", "profile": profiles}


def guided_reply(packet, chosen, **overrides):
    """Synthetic response to one stage, retaining the validated predecessor stages."""
    if packet.get("decision", {}).get("requests"):
        replies = [guided_reply({**packet, "decision_request": item["request"],
                                 "decision": {"request_digest": item["request_digest"]}}, chosen, **overrides)["stages"][-1]
                   for item in packet["decision"]["requests"]]
        return {"stages": [*packet["decision"].get("completed", []), *replies]}
    request = packet["decision_request"]
    answers = {}
    for key, q in request["questions"].items():
        if q["type"] == "noul":
            answers[key] = {"type": "noul", "noul": overrides.get(key, 0)}
            continue
        choice = "unknown"
        if key.startswith("guidance:"):
            choice = guided_choice(key, q, packet, chosen)
        elif key == "benchmark":
            choice = "__tie__"
        elif key.startswith("basis:"):
            bases = [x for x in q["criteria"] if not x.startswith("__")]
            choice = bases[0] if bases else "__unknown__"
        answers[key] = {"type": "choice", "choice": overrides.get(key, choice)}
    response = {"request_digest": packet.get("decision", {}).get("request_digest") or packet["assessment_digest"],
                "provider": "subagent", "model": "gpt-6-luna", "answers": answers}
    return {"stages": [*packet.get("decision", {}).get("completed", []), response]}


def guided_choice(key, q, packet, chosen):
    """Guide option that documents `chosen`; __tie__: one documented profile per vendor; otherwise __none__."""
    from bench_router import decision
    guide = decision.load_guidelines()
    vendor, part = (key.split(":") + [None])[1:3]
    ids = [chosen] if chosen != "__tie__" else sorted(packet.get("fit_profiles") or [c["profile"] for c in packet["candidates"]])
    for pid in ids:
        p = PROFILES.get(pid)
        if not p or guide["models"].get(p["model_id"], {}).get("vendor") != vendor:
            continue
        if part == "model":
            return f"model:{p['model_id']}"
        levels = guide["vendors"][vendor].get("levels", {}).get(p["model_id"], {})
        option = (next((f"effort:{c}" for c, level in levels.items() if level == p["reasoning_effort"]), None) if part == "effort"
                  else f"{p['model_id']}:{p['reasoning_effort']}")
        if option in q["criteria"]:
            return option
    return "__unknown__" if part == "effort" else "__none__"


for _p in r.load_profiles(EX / "profiles.example.toml")["profile"]:
    PROFILES.setdefault(_p["id"], _p)


def guided_responses(packet, reroute, chosen, **overrides):
    for _ in range(10):
        ratings = {key: 1 for key in packet["decision_request"]["questions"] if key.startswith("relevance:")}
        response = guided_reply(packet, chosen, **{**ratings, **overrides})
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
               "prompt": "p; rm -rf / $(whoami)", "cwd": self.cwd}
        raw.update(kw)
        return r.validate_task({k: v for k, v in raw.items() if v is not None})

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
        # benchmark 없음: 평가는 유효 후보를 돌려준다
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
        t = self.task(summary="Fix a repository bug", constraints={"max_cost_tier": "medium"})
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
        # 미등록 지표가 늘어도 benchmark 결과는 불변.
        legacy = r.evaluate_v1(t, config(ps), MAPPING, snap, [], NOW, context=ctx)
        self.assertEqual(a["evaluations"]["benchmark"]["status"], "ok")
        self.assertNotIn("legacy_score", a["evaluations"]["benchmark"])
        self.assertNotIn("score", legacy["candidates"][0])
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
        for p in fx["profiles"]:
            cov, q = r.coverage_quality(a, p["scores"])
            self.assertAlmostEqual(cov, exp["coverage"][p["id"]], delta=1e-9)
            self.assertAlmostEqual(q, exp["quality"][p["id"]], delta=1e-9)

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
        one = r.evaluate_v1(t, config(ps), MAPPING, snapshot(ev, ps), [], NOW)
        two = r.evaluate_v1(t, config(list(reversed(ps))), MAPPING, snapshot(ev, ps), [], NOW)
        for k in ("config_hash", "assessment_digest"):  # 설정 파일 순서만 다름(digest는 config_hash에서 파생)
            one.pop(k), two.pop(k)
        self.assertEqual(json.dumps(one), json.dumps(two))
        self.assertEqual([c["profile"] for c in one["candidates"]], ["a", "b", "c"])  # ID순, 순위 아님

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

    def test_v08_input_validation(self):
        bad = [dict(categories={"analysis": 1}), dict(category_confidence=0.9), dict(unknown_field=1),
               dict(constraints={"budget_usd": 5}), dict(priority="fast"),
               dict(round=0), dict(round=True), dict(task_id="../x"), dict(cwd="relative"),
               dict(context_files=["../outside.txt"]), dict(summary=""),
               dict(constraints={"timeout_ms": 999})]
        for kw in bad:
            with self.assertRaises(r.InputError, msg=str(kw)):
                self.task(**kw)
        f = Path(self.cwd) / "t.json"
        for text in ('{"a": NaN}', '{"a": 1, "a": 2}', '{"a": Infinity}'):
            f.write_text(text, "utf-8")
            with self.assertRaises(r.InputError, msg=text):
                r.load_json_strict(f, r.TASK_MAX_BYTES)
        f.write_bytes(b'{"a": "\xff"}')
        with self.assertRaises(r.InputError):
            r.load_json_strict(f, r.TASK_MAX_BYTES)

    def test_v09_l1_rules(self):
        cls = r.classify(self.task(summary="Fix the bug in the React frontend"))
        self.assertEqual((cls["stage"], cls["fallback_reason"]), ("fallback", "rule_conflict"))
        cls = r.classify(self.task(summary="Run pytest"))
        self.assertEqual((cls["stage"], cls["fallback_reason"]), ("fallback", "no_rule_match"))
        cls = r.classify(self.task(summary="Refactor the repository module", context_files=["src/a.py"]))
        self.assertEqual((cls["stage"], cls["categories"]), ("L1", {"coding_repo": 1.0}))
        cls = r.classify(self.task(summary="저장소의 버그를 고쳐줘"))
        self.assertEqual(cls["categories"], {"coding_repo": 1.0})
        cls = r.classify(self.task(summary="SQL"))
        self.assertEqual(cls["stage"], "fallback")

    def test_snapshot_staleness_and_fingerprint(self):
        ps = [profile("a"), profile("dflt")]
        ev = {"a": {"aa_intelligence": 0.9}}
        t = self.task()
        s = snapshot(ev, ps, last_success="2026-10-01T00:00:00+00:00")  # 11일 > max_stale 7일
        res = r.evaluate_v1(t, config(ps), MAPPING, s, [], NOW)
        self.assertIn("source_too_stale", [w["code"] for w in res["warnings"]])
        changed = [profile("a", args=["-m", "other"]), profile("dflt")]  # 설정 변경 → 기존 점수 무효
        res = r.evaluate_v1(t, config(changed), MAPPING, snapshot(ev, ps), [], NOW)
        self.assertIn("stale_config", [w["code"] for w in res["warnings"]])
        renamed = [profile("a2"), profile("dflt")]  # 새 ID 체계로 재생성된 profiles.toml → refresh 전까지 근거 없음
        res = r.evaluate_v1(t, config(renamed), MAPPING, snapshot(ev, ps), [], NOW)
        self.assertIn("a2: profile absent from snapshot; run refresh", [w["message"] for w in res["warnings"]])
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
        amb = dict(snap, ambiguous=[{"profile": "b", "evidence_id": "u/coding", "source_models": ["m (Low)", "m (Max)"]}])
        res_amb = ev.build(self.t(prompt="```x```", facets={"task": ["repo_coding"]}), config(ps), amb, [], index_fixture(), NOW)
        self.assertEqual(res_amb["units"][1]["profiles"]["b"]["missing_reason"], "ambiguous")  # 소스에 없음과 구분
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
        res = ev.build(self.t(), config([profile("a2")]), snap, [], index_fixture(), NOW)
        self.assertEqual(res["units"][0]["profiles"]["a2"]["missing_reason"], "profile_not_in_snapshot")
        self.assertIn("profile_not_in_snapshot", [w["code"] for w in res["warnings"]])

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
                   profile("strong", model_id="claude-opus-5-5", reasoning_effort="medium")]  # another vendor: both can be documented
        self.cfg = config(self.ps)

    def route(self, **kw):
        return r.route(self.task, self.cfg, MAPPING, kw.pop("snap", None), [], kw.pop("now", NOW), host="codex", env={}, **kw)

    def finish(self, chosen="light", **kw):
        response = guided_responses(self.route(**kw), lambda x: self.route(response=x, **kw), chosen)
        return self.route(response=response, **kw)

    def fit_packet(self, **kw):
        packet = self.route(**kw)
        return self.route(response=guided_reply(packet, "__tie__"), **kw)

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
            self.assertEqual((fit["decision"]["stage"], {q["request"]["state"]["vendor"] for q in fit["decision"]["requests"]}),
                             ("guidance", {"claude", "openai"}))
            self.assertNotIn("observations", json.dumps(fit["decision_request"]))
            self.assertNotIn("legacy_score", json.dumps(fit["decision_request"]))
            self.assertTrue(all("score" not in c for c in packet["candidates"]))
            self.cfg = config(self.ps[:1])
            self.assertEqual(self.route()["status"], "decision_required")
            post.assert_not_called()

    def test_v68_selection_replays_all_stages_and_rechecks_constraints(self):
        out = self.finish()
        self.assertEqual((out["status"], out["selected"]["profile"]), ("selected", "light"))
        selection = {k: v for k, v in out["selection"].items() if k != "source"}
        self.assertEqual(selection["policy"], self.d.POLICY)
        self.assertEqual([s["stage"] for s in selection["decision"]["stages"]], ["analysis", "guidance", "guidance"])
        self.assertEqual(self.route(selection=selection)["selected"], out["selected"])
        self.ps[0]["enabled"] = False
        self.assertEqual(self.route(selection=selection)["status"], "stale_assessment")

    def test_v69_wrong_rule_stage_digest_and_model_are_rejected(self):
        from copy import deepcopy
        fit = self.fit_packet()
        for response in (guided_reply(fit, "light", **{"guidance:openai": "claude-opus-5-5:medium"}),  # another vendor's row
                         guided_reply(fit, "light", **{"guidance:openai": "invented"})):
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

    def test_v72_cost_and_configuration_do_not_resolve_multiple_candidates(self):
        self.assertEqual(self.finish("__abstain__")["status"], "decision_unavailable")
        ctx = {"schema_version": "2.0", "profiles": {pid: {"metrics": {"cost.estimated_usd": {
            "value": value, "unit": "usd", "source": "synthetic"}}} for pid, value in (("light", 0.01), ("strong", 0.1))}}
        self.ps[0]["cost_tier"] = "low"
        for priority in ("quality", "balanced", "cost"):
            self.task["priority"] = priority
            for context in (None, ctx):
                with self.subTest(priority=priority, context=context):
                    out = self.finish("__tie__", context=context)
                    self.assertEqual(out["status"], "decision_unavailable")
                    self.assertIsNone(out["selected"])
                    self.assertIn("upstream_selection_required", out["decision"]["uncertainty"])
        self.assertEqual(self.finish("strong", context=ctx)["selected"]["profile"], "strong")


    def test_v73_jev_stages_preserve_usage_and_failure_is_native_handoff(self):
        from unittest.mock import MagicMock, patch
        from threading import Barrier
        vendor_calls = Barrier(2)
        def respond(request, **kwargs):
            req = json.loads(request.data)
            req.pop("model")
            if req["state"]["stage"] == "guidance":
                vendor_calls.wait(timeout=2)  # sequential vendor calls cannot pass this barrier
            raw = guided_reply({"decision_request": req, "assessment_digest": r.canonical_hash(req)}, "light")["stages"][-1]
            raw.update(model="jev-1.13.0", usage={"input_tokens": 100, "output_tokens": 10})
            result = MagicMock()
            result.__enter__.return_value.read.return_value = json.dumps(raw).encode()
            return result
        with patch("urllib.request.urlopen", side_effect=respond) as post:
            out = r.route(self.task, self.cfg, MAPPING, None, [], NOW, host="codex", allow_network=True, env={"JEV_API_KEY": "synthetic"})
        self.assertEqual((out["status"], post.call_count), ("selected", 3))
        self.assertEqual([s["usage"]["input_tokens"] for s in out["selection"]["decision"]["stages"]], [100, 100, 100])
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
        out = run(replies)  # example profiles carry no guided model/effort: both stay provisional, the caller chooses
        self.assertEqual((out["status"], out["selected"]), ("decision_unavailable", None))
        self.assertIn("upstream_selection_required", out["decision"]["uncertainty"])
        self.assertTrue(all(f["diagnostics"] == ["guidance_missing"] for f in out["decision"]["evaluation"]["fits"].values()))
        copied = root / "copied"
        shutil.copytree(Path(__file__).parent / "skills/bench-router", copied, symlinks=False)
        proc = subprocess.run([sys.executable, str(copied / "scripts/cli.py"), *argv], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 17, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["assessment_digest"], packet["assessment_digest"])
        self.assertEqual((copied / "bench_router/guidelines.toml").read_bytes(), self.d.GUIDELINES.read_bytes())

    def test_v75_guidance_matches_only_exact_models_and_efforts(self):
        for model, effort in (("claude-sonnet-5-5", "medium"), ("claude-opus-5-5", "medium"),
                              ("gemini-3.8-flash", "high"), ("gemini-4-argon", "medium")):
            with self.subTest(model=model, effort=effort):
                self.cfg = config([profile("only", model_id=model, reasoning_effort=effort)])
                out = self.finish("only")
                self.assertEqual(out["status"], "selected")
                fit = out["selection"]["decision"]["evaluation"]["fits"]["only"]
                self.assertEqual((fit["status"], fit["guided"]), ("documented", f"{model}:{effort}"))
        self.cfg = config([profile("only", model_id="claude-sonnet-5-5-preview", reasoning_effort="medium")])
        fit = self.finish("only")["selection"]["decision"]["evaluation"]["fits"]["only"]  # no prefix matching
        self.assertEqual((fit["status"], fit["diagnostics"]), ("provisional", ["guidance_missing"]))

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

    def test_v81_comparable_raw_scores_do_not_select_a_profile(self):
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.9}, "strong": {"u/coding": 0.6}})
        for pid, normalized in (("light", 0), ("strong", 1)):
            snap["profiles"][pid]["evidence"]["u/coding"].update(normalized=normalized, cohort_id=pid)
        out = self.finish("__tie__", snap=snap, index=idx)
        self.assertIsNone(out["selected"])
        self.assertEqual(out["decision"]["evaluation"]["comparisons"]["u/coding"], ["light"])
        self.assertEqual(len(out["decision"]["stages"]), 4)
        snap["profiles"]["strong"]["evidence"]["u/coding"]["conditions"]["dataset_revision"] = "different"
        self.assertFalse(self.finish("__tie__", snap=snap, index=idx)["decision"]["evaluation"]["comparisons"])

    def test_v82_evaluation_gated_effort_stays_alternative_even_with_benchmark_gain(self):
        idx = self.indexed()
        self.ps = [profile("light", model_id="claude-sonnet-5-5", reasoning_effort="medium"),
                   profile("strong", model_id="claude-sonnet-5-5", reasoning_effort="xhigh")]
        self.cfg = config(self.ps)
        exact = self.exact({"light": {"u/coding": 0.6}, "strong": {"u/coding": 0.9}})
        out = self.finish("light", snap=exact, index=idx)
        self.assertEqual(out["selected"]["profile"], "light")  # the guide's starting point, not the higher score
        d = out["selection"]["decision"]
        strong = d["evaluation"]["fits"]["strong"]
        self.assertEqual((strong["status"], strong["workflow_gain"], strong["pending_conditions"]),
                         ("alternative", None, ["workflow_gain_unverified"]))
        self.assertNotIn("strong", d["evaluation"]["observations"])  # alternatives are not searched or compared
        assessment = self.d.evaluate(self.task, self.cfg, MAPPING, exact, [], NOW, host="codex", env={},
                                     index=idx, response={"stages": d["stages"]})
        with self.assertRaisesRegex(r.InputError, "accept_provisional"):
            self.d.bind(assessment, "strong", {"id": "upstream", "version": "1"}, "evaluate separately")
        selection = self.d.bind(assessment, "strong", {"id": "upstream", "version": "1"}, "accept pending evidence", True)
        out = self.route(index=idx, snap=exact, selection=selection)
        self.assertEqual(out["selected"]["profile"], "strong")
        codes = [w["code"] for w in out["warnings"]]
        self.assertIn("workflow_gain_unverified", codes)
        self.assertIn("not_guided_starting_point", codes)

    def test_v83_conflicting_benchmarks_request_relevance_without_scores(self):
        idx = self.indexed(("u/one", "u/two"))
        snap = self.exact({"light": {"u/one": 0.9, "u/two": 0.5}, "strong": {"u/one": 0.5, "u/two": 0.9}})
        fit = self.fit_packet(index=idx, snap=snap)
        packet = self.route(index=idx, snap=snap, response=guided_reply(fit, "__tie__"))
        self.assertEqual(packet["decision"]["stage"], "benchmark")
        self.assertNotIn("raw", json.dumps(packet["decision_request"]))
        self.assertNotIn("model_id", json.dumps(packet["decision_request"]))
        out = self.route(index=idx, snap=snap, response=guided_reply(packet, "__tie__", **{"relevance:u/one": 1}))
        self.assertIsNone(out["selected"])
        self.assertIn("upstream_selection_required", out["decision"]["uncertainty"])
        self.assertEqual(self.route(index=idx, snap=snap, response=guided_reply(packet, "__tie__"))["status"], "decision_unavailable")

    def test_v93_conflicting_suites_are_reported_without_voting(self):
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
        self.assertIsNone(out["selected"])
        self.assertIn("upstream_selection_required", out["decision"]["uncertainty"])
        self.assertEqual(out["decision"]["evaluation"]["comparisons"], {
            "u/a": ["strong"], "u/b": ["strong"], "u/c": ["light"], "u/d": ["light"]})
        self.assertEqual(out["decision"]["evaluation"]["benchmark_relevance"]["u/a"], 1)
        assessment = self.d.evaluate(self.task, self.cfg, MAPPING, snap, [], NOW, host="codex", env={},
                                     index=idx, response={"stages": out["decision"]["stages"]})
        for pid in ("light", "strong"):
            selection = self.d.bind(assessment, pid, {"id": "upstream", "version": "1"}, "task-specific judgment", True)
            self.assertEqual(self.route(index=idx, snap=snap, selection=selection)["selected"]["profile"], pid)


    def test_v84_model_proxy_can_inform_model_choice_without_effort_claim(self):
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.9}, "strong": {"u/coding": 0.6}})
        for sp in snap["profiles"].values():
            row = sp["evidence"]["u/coding"]
            row.update(scope="model_proxy", cohort_id="same-source-cohort")
            row["conditions"].update(reasoning_effort=None, agent_scaffold=None)
        out = self.finish("__tie__", index=idx, snap=snap)
        self.assertIsNone(out["selected"])
        self.assertEqual(out["decision"]["evaluation"]["comparison_scopes"]["u/coding"], "model_proxy")
        self.assertFalse(out["decision"]["evaluation"]["observations"]["light"]["u/coding"]["exact_profile"])
        snap["profiles"]["strong"]["evidence"]["u/coding"]["cohort_id"] = "other"
        self.assertFalse(self.finish("__tie__", index=idx, snap=snap)["decision"]["evaluation"]["comparisons"])

    def test_v85_fanout_reuses_analysis_and_fit_without_provider_calls(self):
        from unittest.mock import patch
        cache = {}
        self.finish("__tie__", decision_cache=cache)
        with patch.object(self.d.provider, "decide", side_effect=AssertionError("must reuse analysis and fit")):
            out = self.route(omit_profiles=["strong"], decision_cache=cache)
        self.assertEqual(out["selected"]["profile"], "light")
        self.assertEqual(len(cache), 3)
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
        with patch.object(self.d, "load_guidelines", return_value={**guide, "hash": "changed", "version": "next"}):
            self.assertEqual(self.route(selection=selection)["status"], "selected")

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

    def test_v89_snapshot_change_reuses_semantics_but_recomputes_unit_comparisons(self):
        from unittest.mock import patch
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.9}, "strong": {"u/coding": 0.6}})
        cache = {}
        first = self.finish("__tie__", index=idx, snap=snap, decision_cache=cache)
        snap["profiles"]["strong"]["evidence"]["u/coding"]["raw"] = 0.99
        snap["snapshot_id"] = r.snapshot_hash(snap)
        with patch.object(self.d.provider, "decide", side_effect=AssertionError("semantics unchanged")):
            second = self.route(index=idx, snap=snap, decision_cache=cache)
        self.assertEqual((first["selected"], second["selected"]), (None, None))
        self.assertEqual(first["decision"]["evaluation"]["comparisons"]["u/coding"], ["light"])
        self.assertEqual(second["decision"]["evaluation"]["comparisons"]["u/coding"], ["strong"])
        self.assertNotEqual(first["assessment_digest"], second["assessment_digest"])


    def test_v90_direction_and_meaningful_gap_use_raw_metric_units(self):
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.6}, "strong": {"u/coding": 0.9}})
        idx["units"]["u/coding"]["meaningful_gap"] = 0.3
        out = self.finish("__tie__", snap=snap, index=idx)
        self.assertEqual(out["decision"]["evaluation"]["comparisons"]["u/coding"], ["light", "strong"])
        idx["units"]["u/coding"]["meaningful_gap"] = 0
        for sp in snap["profiles"].values():
            sp["evidence"]["u/coding"]["conditions"]["direction"] = "lower"
        self.assertEqual(self.finish("__tie__", snap=snap, index=idx)["decision"]["evaluation"]["comparisons"]["u/coding"], ["light"])

    def test_v91_exact_comparison_requires_protocol_and_profile_conditions(self):
        idx = self.indexed()
        for key in ("dataset_revision", "evaluation_harness", "agent_scaffold", "reasoning_effort"):
            with self.subTest(condition=key):
                snap = self.exact({"light": {"u/coding": 0.6}, "strong": {"u/coding": 0.9}})
                snap["profiles"]["strong"]["evidence"]["u/coding"]["conditions"][key] = "different"
                out = self.finish("__tie__", snap=snap, index=idx)
                self.assertFalse(out["decision"]["evaluation"]["comparisons"])
                self.assertIsNone(out["selected"])

    def test_v94_public_assessment_and_external_choice(self):
        from unittest.mock import patch
        self.ps.append(profile("disabled", enabled=False))
        self.cfg = config(self.ps)
        first = self.d.evaluate(self.task, self.cfg, MAPPING, None, [], NOW, host="codex", env={})
        self.assertEqual((first["schema_version"], first["status"], first["assessment_digest"]),
                          ("4.0", "decision_required", None))
        response = guided_reply({**first, "assessment_digest": first["decision"]["request_digest"]}, "__tie__")
        fit = self.d.evaluate(self.task, self.cfg, MAPPING, None, [], NOW, host="codex", env={}, response=response)
        response = guided_reply({**fit, "assessment_digest": fit["decision"]["request_digest"]}, "__tie__")
        effort = self.d.evaluate(self.task, self.cfg, MAPPING, None, [], NOW, host="codex", env={}, response=response)
        assessment = effort
        self.assertEqual(assessment["status"], "ok")
        self.assertEqual([c["profile"] for c in assessment["candidates"]], ["disabled", "light", "strong"])
        self.assertFalse(assessment["candidates"][0]["eligible"])
        self.assertIsNone(assessment["recommendation"]["profile"])
        self.assertIn("upstream_selection_required", assessment["recommendation"]["diagnostics"])
        self.assertNotIn("tie_resolved_by_configuration", assessment["candidates"][1]["diagnostics"])
        self.assertIn("comparable_evaluation_missing", assessment["diagnostics"])
        selection = self.d.bind(assessment, "light", {"id": "team", "version": "1"}, "reserve strong for another role",
                                accept_provisional=True)
        with patch.object(self.d.provider, "decide", side_effect=AssertionError("must replay without calls")):
            out = self.route(selection=selection)
        self.assertEqual((selection["schema_version"], out["status"], out["selected"]["profile"]),
                          ("6.0", "selected", "light"))
        self.assertEqual(out["selection_mode"], "orchestrator_assessed")
        self.assertEqual(self.route(selection=selection, availability={"light": "quota_exhausted"})["status"],
                         "stale_assessment")
        with self.assertRaises(r.InputError):
            self.d.bind(assessment, "disabled", {"id": "team", "version": "1"}, "no")
        self.task["prompt"] += " Changed requirements."
        self.assertEqual(self.route(selection=selection)["status"], "stale_assessment")

    def test_v95_provisional_and_unsuitable_external_choices(self):
        from copy import deepcopy
        self.ps[0]["model_id"] = "unlisted-model"
        decision = self.finish("__tie__")["decision"]
        # Projection is informational: changing it cannot override the embedded fit proof.
        assessment = {"schema_version": "4.0", "status": "ok", "decision": decision,
                      "assessment_digest": self.d.assessment_digest(decision)}
        for pid in decision["evaluation"]["fits"]:
            fit = decision["evaluation"]["fits"][pid]
            if fit["status"] == "provisional":
                with self.assertRaisesRegex(r.InputError, "accept_provisional"):
                    self.d.bind(assessment, pid, {"id": "team", "version": "1"}, "pending")
                self.assertEqual(self.d.bind(assessment, pid, {"id": "team", "version": "1"}, "accepted", True)
                                  ["schema_version"], "6.0")
        unsuitable = self.finish("light")["selection"]["decision"]
        assessment.update(decision=unsuitable, assessment_digest=self.d.assessment_digest(unsuitable))
        with self.assertRaisesRegex(r.InputError, "suitable"):
            self.d.bind(assessment, "strong", {"id": "team", "version": "1"}, "no", True)
        selection = self.d.bind(assessment, "light", {"id": "team", "version": "1"}, "yes", True)
        changed = deepcopy(selection)
        changed["decision"]["evaluation"]["fits"]["strong"]["status"] = "documented"
        with self.assertRaisesRegex(r.InputError, "digest"):
            r.validate_selection(changed)
        changed["assessment_digest"] = self.d.assessment_digest(changed["decision"])
        self.assertEqual(self.route(selection=changed)["status"], "stale_assessment")
        changed = deepcopy(selection)
        changed["decision"]["inputs"]["policy"]["version"] = "3"
        changed["assessment_digest"] = self.d.assessment_digest(changed["decision"])
        with self.assertRaisesRegex(r.InputError, "current vendor-guided policy"):
            self.d.validate_selection(changed)
        selection["schema_version"] = "4.0"
        with self.assertRaises(r.InputError):
            r.validate_selection(selection)

    def test_v96_assessment_with_no_recommendation_retains_candidates(self):
        idx = self.indexed(("u/one", "u/two"))
        snap = self.exact({"light": {"u/one": 0.9, "u/two": 0.5},
                           "strong": {"u/one": 0.5, "u/two": 0.9}})
        packet = self.fit_packet(index=idx, snap=snap)
        packet = self.route(index=idx, snap=snap, response=guided_reply(packet, "__tie__"))
        response = guided_reply(packet, "__tie__")  # all relevance answers are zero
        assessment = self.d.evaluate(self.task, self.cfg, MAPPING, snap, [], NOW, host="codex", env={},
                                     index=idx, response=response)
        self.assertEqual((assessment["status"], assessment["recommendation"]["status"]), ("ok", "abstained"))
        self.assertEqual(assessment["compared_profiles"], ["light", "strong"])
        self.assertEqual(set(assessment["evidence"]["comparisons"]), {"u/one", "u/two"})
        selection = self.d.bind(assessment, "light", {"id": "team", "version": "1"}, "external criterion", True)
        self.assertEqual(self.route(index=idx, snap=snap, selection=selection)["selected"]["profile"], "light")

    def test_v97_cli_assessment_selection_and_offline_execution_check(self):
        from unittest.mock import patch
        root = Path(self.tmp.name)
        cfg = root / "cfg"
        cfg.mkdir()
        (cfg / "profiles.toml").write_text((EX / "profiles.example.toml").read_text().replace("enabled = false", "enabled = true"))
        task = root / "task.json"
        task.write_text(json.dumps({"schema_version": "1.0", **self.task}))
        response_path = root / "response.json"
        args = ["--config-dir", str(cfg), "--cache-dir", str(root / "cache")]
        def run(command):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cli.main([*args, *command])
            return code, json.loads(out.getvalue())
        command = ["evaluate", "--format", "3", "--task", str(task), "--host", "codex"]
        with patch.object(r, "env_with_dotenv", return_value={}), patch("urllib.request.urlopen") as network, \
                patch("bench_router.herdr.dispatch") as dispatch, patch.object(r, "atomic_write") as writes, \
                patch("subprocess.run") as proc, patch("subprocess.Popen") as popen:
            code, assessment = run(command)
            self.assertEqual(code, 17)
            for _ in range(5):
                response_path.write_text(json.dumps(guided_reply(assessment, "__tie__")))
                code, assessment = run([*command, "--decision-response", str(response_path)])
                if code != 17:
                    break
            self.assertEqual((code, assessment["status"]), (0, "ok"))
            path = root / "assessment.json"
            path.write_text(json.dumps(assessment))
            pid = next(c["profile"] for c in assessment["candidates"] if c["eligible"])
            code, result = run(["select", "--assessment", str(path), "--profile", pid, "--policy-id", "team",
                                "--policy-version", "1", "--reason", "role assignment", "--accept-provisional"])
            self.assertEqual((code, result["selection"]["schema_version"]), (0, "6.0"))
            path = root / "selection.json"
            path.write_text(json.dumps(result["selection"]))
            code, result = run(["route", "--task", str(task), "--selection", str(path), "--dry-run"])
            self.assertEqual((code, result["selected"]["profile"]), (0, pid))
            network.assert_not_called()
            dispatch.assert_not_called()
            writes.assert_not_called()
            proc.assert_not_called()  # selection-only works without Herdr, Projects or any agent CLI
            popen.assert_not_called()
            self.assertFalse((root / "cache").exists())

    def test_v92_majority_winner_is_evidence_for_upstream_selection(self):
        ids = ("u/one", "u/two", "u/three")
        idx = self.indexed(ids)
        snap = self.exact({"light": {"u/one": 0.9, "u/two": 0.9, "u/three": 0.5},
                           "strong": {"u/one": 0.5, "u/two": 0.5, "u/three": 0.9}})
        packet = self.route(index=idx, snap=snap, response=guided_reply(self.fit_packet(index=idx, snap=snap), "__tie__"))
        self.assertEqual(packet["decision"]["stage"], "benchmark")
        self.assertEqual(self.route(index=idx, snap=snap, response=guided_reply(packet, "__tie__"))["status"], "decision_unavailable")
        out = self.finish("__tie__", index=idx, snap=snap)
        self.assertIsNone(out["selected"])
        self.assertIn("upstream_selection_required", out["decision"]["uncertainty"])
        self.assertEqual(len(out["decision"]["stages"]), 4)
        self.assertEqual(out["decision"]["evaluation"]["benchmark_relevance"], dict.fromkeys(ids, 1))

    def test_v100_rule_hints_can_be_rejected_without_reappearing_during_retrieval(self):
        from bench_router import evidence
        idx = json.loads(evidence.BUNDLED_INDEX.read_text())
        for prompt, files, hint in (("Explain bash; do not execute commands.", [], "terminal_ops"),
                                    ('Translate the values: ```json\n{"x":"hello"}\n```', [], "coding"),
                                    ("Summarize this text PDF.", ["report.pdf"], "document"),
                                    ("Explain these CSS selectors; do not modify them.", ["style.css"], "webdev_html")):
            with self.subTest(hint=hint):
                self.task.update(summary=prompt, prompt=prompt, context_files=files)
                packet = self.route(index=idx)
                self.assertIn(f"facet:task:{hint}", packet["decision_request"]["questions"])
                fit = self.route(index=idx, response=guided_reply(packet, "__tie__"))
                analysis = fit["decision_request"]["state"]["analysis"]
                self.assertNotIn(hint, [f["value"] for f in analysis["facets"]])
                out = self.route(index=idx, response=guided_reply(fit, "__tie__"))
                evaluation = out["decision"]["evaluation"]
                self.assertFalse(evaluation["comparisons"])
                self.assertTrue(all(hint not in u["facets"].get("task", []) for uid, u in evaluation["units"].items()
                                    if uid not in evaluation["auxiliary_units"]))

    def test_v101_prefilter_does_not_cap_away_comparable_units(self):
        ids = [f"u/{i:02}" for i in range(12)] + ["u/z-valid"]
        idx = self.indexed(ids)
        snap = self.exact({pid: dict.fromkeys(ids, value) for pid, value in (("light", 0.9), ("strong", 0.6))})
        for uid in ids[:12]:
            snap["profiles"]["strong"]["evidence"][uid]["conditions"]["dataset_revision"] = "other"
        fit = self.fit_packet(index=idx, snap=snap)
        packet = self.route(index=idx, snap=snap, response=guided_reply(fit, "__tie__"))
        self.assertEqual(set(packet["decision_request"]["questions"]), {"relevance:u/z-valid", "basis:u/z-valid"})
        out = self.finish("__tie__", index=idx, snap=snap)
        evaluation = out["decision"]["evaluation"]
        self.assertEqual(evaluation["omitted_units"], 0)
        self.assertEqual(evaluation["prefiltered_units"], dict.fromkeys(ids[:12], "no_comparable_observations"))
        self.assertIsNone(out["selected"])

    def test_v102_relevance_basis_threshold_and_upstream_replay(self):
        from copy import deepcopy
        idx = self.indexed()
        snap = self.exact({"light": {"u/coding": 0.9}, "strong": {"u/coding": 0.6}})
        packet = self.route(index=idx, snap=snap, response=guided_reply(self.fit_packet(index=idx, snap=snap), "__tie__"))
        for score, basis in ((0.79, "task:coding"), (1, "__supporting__"), (1, "__unknown__")):
            response = guided_reply(packet, "__tie__", **{"relevance:u/coding": score, "basis:u/coding": basis})
            assessment = self.d.evaluate(self.task, self.cfg, MAPPING, snap, [], NOW, host="codex", env={}, index=idx, response=response)
            self.assertFalse(assessment["evidence"]["relevance"]["u/coding"]["accepted"])
            self.assertEqual(assessment["recommendation"]["status"], "abstained")
        response = guided_reply(packet, "__tie__", **{"relevance:u/coding": 0.8})
        assessment = self.d.evaluate(self.task, self.cfg, MAPPING, snap, [], NOW, host="codex", env={}, index=idx, response=response)
        record = assessment["evidence"]["relevance"]["u/coding"]
        self.assertTrue(record["accepted"])
        self.assertEqual(record["basis"], "task:coding")
        self.assertEqual(record["task_requirement"], idx["facets"]["task"]["coding"]["desc"])
        self.assertEqual(record["request_digest"], packet["assessment_digest"])
        selection = self.d.bind(assessment, "strong", {"id": "team", "version": "1"}, "use this evidence for role allocation", True)
        self.assertEqual(self.route(index=idx, snap=snap, selection=selection)["selected"]["profile"], "strong")
        forged = deepcopy(selection)
        forged["decision"]["evaluation"]["relevance"]["u/coding"]["reason"] = "invented justification"
        forged["assessment_digest"] = self.d.assessment_digest(forged["decision"])
        self.assertEqual(self.route(index=idx, snap=snap, selection=forged)["status"], "stale_assessment")

    def test_v103_agent_signals_remain_auxiliary_and_do_not_consume_semantic_tokens(self):
        idx = self.indexed(("u/coding", "u/agent"))
        idx["facets"]["agent_signal"] = {"overall": {"desc": "Agent reliability", "detect": "rule:always", "evidence": "official"}}
        idx["units"]["u/agent"]["facets"] = {"agent_signal": ["overall"]}
        idx["postings"] = {"task:coding": ["u/coding"], "agent_signal:overall": ["u/agent"]}
        snap = self.exact({"light": {"u/coding": 0.9, "u/agent": 0.1}, "strong": {"u/coding": 0.6, "u/agent": 0.99}})
        out = self.finish("__tie__", index=idx, snap=snap)
        evaluation = out["decision"]["evaluation"]
        self.assertEqual(evaluation["auxiliary_units"], ["u/agent"])
        self.assertEqual(evaluation["prefiltered_units"]["u/agent"], "agent_reliability_only")
        self.assertIn("u/agent", evaluation["observations"]["strong"])
        request = out["decision"]["stages"][-1]["request"]
        self.assertNotIn("u/agent", json.dumps(request))
        self.assertNotIn("raw", json.dumps(request))
        self.assertNotIn("model_id", json.dumps(request))
        self.assertIsNone(out["selected"])

    def test_v104_cost_priority_and_conditional_gain_cannot_bypass_relevance(self):
        idx = self.indexed()
        self.task["priority"] = "cost"
        self.ps = [profile("light", model_id="claude-sonnet-5-5", reasoning_effort="medium"),
                   profile("strong", model_id="claude-sonnet-5-5", reasoning_effort="xhigh")]
        self.cfg = config(self.ps)
        snap = self.exact({"light": {"u/coding": 0.6}, "strong": {"u/coding": 0.9}})
        kw = {"index": idx, "snap": snap}
        response = guided_responses(self.route(**kw), lambda x: self.route(response=x, **kw), "__tie__",
                                    **{"basis:u/coding": "__supporting__"})
        assessment = self.d.evaluate(self.task, self.cfg, MAPPING, snap, [], NOW, host="codex", env={}, index=idx, response=response)
        self.assertEqual([s["stage"] for s in assessment["decision"]["stages"]], ["analysis", "guidance", "benchmark"])
        light, strong = (next(c for c in assessment["candidates"] if c["profile"] == pid) for pid in ("light", "strong"))
        self.assertEqual((light["suitability"]["status"], strong["suitability"]["status"]), ("documented", "alternative"))
        self.assertIsNone(strong["suitability"]["workflow_gain"])
        self.assertIn("workflow_gain_unverified", strong["diagnostics"])
        self.assertIn("task_quality_unverified", light["diagnostics"])  # rejected relevance, whatever the priority
        self.assertEqual(assessment["recommendation"]["status"], "abstained")

    def test_v105_model_revision_and_vendor_guidance_are_isolated(self):
        guide = self.d.load_guidelines()
        profiles = [profile("p-luna", model_id="gpt-6-luna", reasoning_effort="low"),
                    profile("p-haiku", model_id="claude-haiku-5-5", reasoning_effort="low"),
                    profile("p-new", model_id="gpt-7-new", reasoning_effort="low")]
        groups = self.d._guidance_groups(profiles, guide)
        self.assertEqual([(vendor, [p["id"] for p in ps]) for vendor, ps in groups],
                         [("claude", ["p-haiku"]), ("openai", ["p-luna"]), (None, ["p-new"])])
        requests = [self.d.guidance_request({}, vendor, guide) for vendor in ("claude", "openai")]
        claude_sources = {sid for sid in guide["sources"] if sid.startswith("claude")}
        self.assertTrue({"claude_models", "claude_effort", "claude_prompting_sonnet_5_5"} <= claude_sources)
        self.assertEqual([set(req["state"]["sources"]) for req in requests], [claude_sources, {"openai"}])
        text = [json.dumps(req) for req in requests]
        self.assertFalse(any(pid in t for pid in ("p-luna", "p-haiku", "p-new") for t in text))  # no profile IDs
        self.assertNotIn("gpt-6", text[0])  # vendors are isolated
        self.assertNotIn("claude-", text[1])
        self.assertNotIn("lightest", text[0])  # OpenAI's rule stays in OpenAI's request
        self.assertIn("lightest", text[1])
        self.assertEqual(set(requests[0]["state"]["models"]), {"claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"})
        self.assertNotIn("models", requests[1]["state"])  # OpenAI's page has no separate model matrix
        guide_claude = guide["vendors"]["claude"]
        self.assertNotIn("claude-fable-5-1:xhigh", guide_claude["options"])  # a step up, never a starting point
        self.assertIn(("claude-fable-5-1", "xhigh"), guide_claude["escalations"])
        self.assertIn("gpt-6-luna:low", requests[1]["questions"]["guidance:openai"]["criteria"])

    def test_v106_one_guidance_request_per_vendor_and_none_without_guidance(self):
        self.ps = [profile("l-low", model_id="gpt-6-luna", reasoning_effort="low"),
                   profile("l-high", model_id="gpt-6-luna", reasoning_effort="high"),
                   profile("s-med", model_id="claude-sonnet-5-5", reasoning_effort="medium"),
                   profile("s-max", model_id="claude-sonnet-5-5", reasoning_effort="max"),
                   profile("g-high", model_id="gemini-4-argon", reasoning_effort="high"),
                   profile("x-terra", model_id="gpt-5.6-terra", reasoning_effort="low"),
                   profile("x-oss", model_id="gpt-oss-120b", reasoning_effort="medium")]
        self.cfg = config(self.ps)

        def finish(**answers):
            response = guided_responses(self.route(), lambda x: self.route(response=x), "__tie__", **answers)
            return self.route(response=response)["decision"]

        d = finish(**{"guidance:openai": "gpt-6-luna:low"})
        self.assertEqual([(s["stage"], s["request"]["state"].get("vendor")) for s in d["stages"]],
                          [("analysis", None), ("guidance", "claude"), ("guidance", "gemini"), ("guidance", "openai")])
        fits = d["evaluation"]["fits"]
        self.assertEqual({pid: f["status"] for pid, f in fits.items()},
                         {"l-low": "documented", "l-high": "alternative", "s-med": "documented", "s-max": "alternative",
                          "g-high": "documented", "x-terra": "provisional", "x-oss": "provisional"})
        self.assertEqual(fits["s-max"]["pending_conditions"], ["workflow_gain_unverified"])  # escalation, not a start
        self.assertNotIn("pending_conditions", fits["l-high"])
        self.assertEqual(fits["x-oss"]["diagnostics"], ["guidance_missing"])
        self.assertIn("upstream_selection_required", d["uncertainty"])
        fits = finish(**{"guidance:openai": "gpt-6.1-sol:medium", "guidance:claude": "__none__",
                         "guidance:gemini:effort": "__unknown__"})["evaluation"]["fits"]
        self.assertEqual(fits["l-low"]["diagnostics"], ["not_guided_starting_point", "guided_configuration_not_registered"])
        self.assertEqual((fits["l-low"]["status"], fits["s-med"]["status"], fits["s-max"]["status"]),
                         ("alternative", "unsuitable", "unsuitable"))
        self.assertEqual((fits["g-high"]["status"], fits["g-high"]["diagnostics"]), ("provisional", ["guidance_fit_unresolved"]))

    def test_v106_parallel_guidance_accepts_unordered_and_partial_native_responses(self):
        packet = self.fit_packet()
        replies = guided_reply(packet, "__tie__")["stages"]
        expected = self.route(response={"stages": replies})["decision"]
        reversed_result = self.route(response={"stages": [replies[0], *reversed(replies[1:])]})
        self.assertEqual(reversed_result["decision"], expected)
        partial = self.route(response={"stages": [replies[0], replies[-1]]})
        self.assertEqual(len(partial["decision"]["requests"]), 1)
        self.assertEqual(partial["decision"]["requests"][0]["request"]["state"]["vendor"], "claude")
        finished = self.route(response=guided_reply(partial, "__tie__"))
        self.assertEqual(finished["decision"], expected)
        with self.assertRaisesRegex(r.InputError, "duplicate guidance"):
            self.route(response={"stages": [*replies, replies[-1]]})
        wrong = {**replies[-1], "request_digest": "stale"}
        with self.assertRaisesRegex(r.InputError, "current guidance"):
            self.route(response={"stages": [replies[0], wrong]})
        with self.assertRaisesRegex(r.InputError, "request_digest must be a string"):
            self.route(response={"stages": [replies[0], {**wrong, "request_digest": []}]})

    def test_v106_one_failed_vendor_keeps_completed_sibling_and_retries_only_missing(self):
        from bench_router import decision_provider as provider
        original = provider.decide
        calls = []
        def respond(request, **kwargs):
            vendor = request["state"].get("vendor")
            calls.append(vendor)
            if vendor == "openai":
                return original(request, env={}, host="codex")
            raw = guided_reply({"decision_request": request, "assessment_digest": r.canonical_hash(request),
                                "fit_profiles": [p["id"] for p in self.ps]}, "__tie__")["stages"][-1]
            return {**raw, "status": "ok", "provider": "jev", "model": "test-jev", "usage": {"input_tokens": 10}}
        with mock.patch.object(provider, "decide", side_effect=respond):
            packet = r.route(self.task, self.cfg, MAPPING, None, [], NOW, host="codex", allow_network=True,
                             env={"JEV_API_KEY": "test"})
        self.assertCountEqual(calls, [None, "claude", "openai"])
        self.assertEqual(len(packet["decision"]["requests"]), 1)
        self.assertEqual(packet["decision"]["completed"][-1]["usage"], {"input_tokens": 10})
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("offline replay")):
            result = self.route(response=guided_reply(packet, "__tie__"))
        stages = result["decision"]["stages"]
        self.assertEqual([stage["provider"] for stage in stages], ["jev", "jev", "subagent"])
        self.assertEqual([stage["request"]["state"].get("vendor") for stage in stages], [None, "claude", "openai"])

    def test_v107_gemini_thinking_class_follows_each_models_configuration(self):
        levels = self.d.load_guidelines()["vendors"]["gemini"]["levels"]
        self.assertEqual(levels["gemini-3.5-flash-lite"], {"lookup": "minimal", "ordinary": "minimal", "advanced": "high"})
        self.assertEqual(levels["gemini-3.8-flash"], {"lookup": "low", "ordinary": "medium", "advanced": "high"})
        self.assertEqual(levels["gemini-3.1-pro-preview"]["ordinary"], "high")
        self.ps = [profile("f-low", model_id="gemini-3.8-flash", reasoning_effort="low"),
                   profile("f-high", model_id="gemini-3.8-flash", reasoning_effort="high")]
        self.cfg = config(self.ps)
        out = self.finish("f-high")
        self.assertEqual(out["selected"]["profile"], "f-high")
        response = guided_responses(self.route(), lambda x: self.route(response=x), "f-high",
                                    **{"guidance:gemini:effort": "effort:lookup"})
        fits = self.route(response=response)["selection"]["decision"]["evaluation"]["fits"]
        self.assertEqual((fits["f-low"]["status"], fits["f-high"]["status"], fits["f-low"]["guided"]),
                         ("documented", "alternative", "gemini-3.8-flash:low"))

    def test_v109_prompt_guidance_is_quoted_from_the_captured_vendor_pages(self):
        guide = self.d.load_guidelines()
        wiki = Path(__file__).resolve().parent / "wiki"
        flat = lambda s: re.sub(r"\s+", " ", s).strip()
        captures = {}
        for entry in guide["vendors"].values():
            self.assertTrue(entry["prompt_guidance"])
            for row in entry["prompt_guidance"]:
                src = guide["sources"][row["source"]]
                if src["capture"] not in captures:  # strip the blockquote marker of the immutable capture
                    page = (wiki / src["capture"]).read_text("utf-8")
                    captures[src["capture"]] = flat(re.sub(r"(?m)^> ?", "", page))
                for key in ("when", "text"):
                    if key in row:
                        self.assertIn(flat(row[key]), captures[src["capture"]], (row["topic"], key))
        sonnet = self.d.prompt_guidance(guide, "claude-sonnet-5-5")
        self.assertEqual({i["source"]["id"] for i in sonnet["items"]}, {"claude_prompting_sonnet_5_5"})  # one model, one guide
        self.assertEqual(self.d.prompt_guidance(guide, "claude-haiku-5-5")["vendor"], "claude")
        self.assertEqual({i["source"]["id"].split("_")[0] for i in self.d.prompt_guidance(guide, "gpt-6-luna")["items"]}, {"openai"})
        self.assertIsNone(self.d.prompt_guidance(guide, "gpt-7-new"))
        # only the selected model's references: the Gemini 3 page does not reach gemini-4-argon
        self.assertEqual(self.d.prompt_guidance(guide, "gemini-4-argon")["items"], [])
        self.assertTrue(self.d.prompt_guidance(guide, "gemini-3.8-flash")["items"])
        with mock.patch.object(r, "_load_toml", return_value={**r._load_toml(self.d.GUIDELINES)}) as load:
            raw = load.return_value
            raw["vendor"] = {**raw["vendor"], "gemini": {**raw["vendor"]["gemini"], "prompt_guidance": [
                {k: v for k, v in raw["vendor"]["gemini"]["prompt_guidance"][0].items() if k != "models"}]}}
            with self.assertRaisesRegex(r.InputError, "prompt_guidance needs models"):
                self.d.load_guidelines()
        # prompt guidance is output only: it never changes the hashes that selection records bind
        self.assertEqual(guide["vendors"]["claude"]["hash"],
                         r.canonical_hash({k: v for k, v in r._load_toml(self.d.GUIDELINES)["vendor"]["claude"].items()
                                           if k != "prompt_guidance"}))

    def test_v105_removed_default_and_fallback_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "profiles.toml"
            path.write_text('schema_version = "1.0"\ndefault_profile = "a"\n', "utf-8")
            with self.assertRaisesRegex(r.InputError, "default_profile"):
                r.load_profiles(path)

    def test_v110_caller_owned_profiles_2_0(self):
        cli_p, api = profile("a"), {k: v for k, v in profile("api").items() if k not in r.EXECUTION_KEYS}
        # The v1 CLI fingerprint is pinned: existing snapshots and selections must keep matching.
        self.assertEqual(r.profile_fingerprint(cli_p), "9f06ffeab172fb096e59756b929e7e84d9331c7f25e3b2cbf21cf22458d7f2ab")
        self.assertNotEqual(r.profile_fingerprint(api), r.profile_fingerprint({**api, "config_revision": "u"}))
        self.assertEqual(r.profile_fingerprint(api), r.profile_fingerprint({**api, "cost_tier": "high"}))
        toml = lambda version, *ps: f'schema_version = "{version}"\n' + "".join(
            "[[profile]]\n" + "".join(f"{k} = {json.dumps(v)}\n" for k, v in p.items()) for p in ps)
        path = Path(self.tmp.name) / "profiles.toml"
        path.write_text(toml("2.0", cli_p, api), "utf-8")
        cfg = r.load_profiles(path)
        self.assertEqual((cfg["schema_version"], cfg["profile"]), ("2.0", [cli_p, api]))
        for version, p, msg in (("2.0", {**api, "kind": "codex"}, "all together"), ("1.0", api, "keys must be exactly")):
            path.write_text(toml(version, p), "utf-8")
            with self.assertRaisesRegex(r.InputError, msg):
                r.load_profiles(path)
        # Evidence binds to the v2 fingerprint; a new config_revision invalidates it.
        snap = snapshot({"api": {"aa_intelligence": 0.7}}, [api])
        for p, reason in ((api, None), ({**api, "config_revision": "u"}, "stale_config")):
            res = r.evaluate_v1(r.validate_task({"schema_version": "1.0", **self.task}),
                                {"schema_version": "2.0", "profile": [p]}, MAPPING, snap, [], NOW)
            self.assertEqual(res["candidates"][0]["evidence"][0]["missing_reason"], reason)


if __name__ == "__main__":
    unittest.main()
