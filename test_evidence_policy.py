"""Refresh, last-good and same-vendor proxy regressions; no network."""
import argparse
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

from bench_router import cli, data, decision, evidence, routing as r
from test_p0 import NOW, MAPPING, config, profile, snapshot, index_fixture
from test_p1 import FakeHTTP, ENV


class EvidencePolicy(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ps = [profile("target", model_id="gpt-6-luna", reasoning_effort="medium"),
                   profile("near", model_id="gpt-6-luna", reasoning_effort="low"),
                   profile("far", model_id="gpt-6-astra", reasoning_effort="medium"),
                   profile("other", model_id="claude-opus-5-5", reasoning_effort="medium")]
        self.cfg = config(self.ps)
        self.task = r.validate_task({"schema_version": "1.0", "task_id": "policy", "round": 1,
                                    "cwd": str(self.root), "summary": "fix", "prompt": "fix",
                                    "facets": {"task": ["coding"]}, "priority": "cost"})
        self.snap = snapshot({"target": {}, "near": {"u/coding": .4},
                              "far": {"u/coding": .9}, "other": {"u/coding": .99}}, self.ps)
        for pid, sp in self.snap["profiles"].items():
            for row in sp["evidence"].values():
                row["conditions"] = {"suite": "test", "subset": "coding", "metric": "rate",
                                     "direction": "higher", "reasoning_effort": next(
                                         p["reasoning_effort"] for p in self.ps if p["id"] == pid)}

    def cell(self, pid="target", now=NOW):
        table = evidence.build(self.task, self.cfg, self.snap, [], index_fixture(), now)
        return next(u for u in table["units"] if u["id"] == "u/coding")["profiles"][pid]

    def test_nearby_same_model_precedes_stronger_or_cross_vendor_score(self):
        cell = self.cell()
        self.assertEqual(cell["raw"], .4)
        self.assertEqual(cell["proxy"]["donor_profile"], "near")
        self.assertEqual(cell["proxy"]["measured_effort"], "low")
        self.assertFalse(cell["exact_profile"])
        self.assertFalse(cell["effort_matches"])
        self.assertEqual(cell["scope"], "model_proxy")
        self.assertEqual(cell["conditions"], self.snap["profiles"]["near"]["evidence"]["u/coding"]["conditions"])

    def test_missing_requires_recent_check_but_failed_refresh_keeps_last_good(self):
        now = NOW + timedelta(hours=1)
        self.assertEqual(self.cell(now=now)["missing_reason"], "no_observation")
        self.snap["sources"]["syn"].update(last_attempt_at=now.isoformat(), last_error="HTTP 503")
        cell = self.cell(now=now)
        self.assertEqual(cell["raw"], .4)
        self.assertTrue(cell["stale"])
        self.assertEqual(cell["proxy"]["refresh_result"], "failed")
        self.assertEqual(self.cell(now=NOW + timedelta(days=8))["missing_reason"], "no_observation")

    def test_no_cross_vendor_or_unknown_vendor_proxy(self):
        for pid in ("near", "far"):
            self.snap["profiles"][pid]["evidence"] = {}
        self.assertEqual(self.cell()["missing_reason"], "no_observation")
        p = self.ps[0]
        p["model_id"] = "private-model"
        self.snap["profiles"][p["id"]]["fingerprint"] = r.profile_fingerprint(p)
        self.assertEqual(self.cell()["missing_reason"], "no_observation")

    def test_nearby_model_and_nearest_measured_effort_are_explicit_proxies(self):
        self.snap["profiles"]["near"]["evidence"] = {}
        self.assertEqual(self.cell()["proxy"]["donor_model"], "gpt-6-astra")
        donor = profile("close-effort", model_id="gpt-6-luna", reasoning_effort="high")
        self.ps.append(donor)
        self.snap["profiles"][donor["id"]] = {
            "fingerprint": r.profile_fingerprint(donor),
            "evidence": {"u/coding": {**self.snap["profiles"]["far"]["evidence"]["u/coding"],
                                      "conditions": {"reasoning_effort": "high"}}}}
        self.ps[0]["reasoning_effort"] = "xhigh"
        self.snap["profiles"]["target"]["fingerprint"] = r.profile_fingerprint(self.ps[0])
        self.snap["profiles"]["near"]["evidence"]["u/coding"] = {
            **self.snap["profiles"][donor["id"]]["evidence"]["u/coding"],
            "conditions": {"reasoning_effort": "low"}}
        self.assertEqual(self.cell()["proxy"]["donor_profile"], "close-effort")

    def test_measured_zero_is_never_imputed(self):
        self.snap["profiles"]["target"]["evidence"]["u/coding"] = {
            **self.snap["profiles"]["near"]["evidence"]["u/coding"], "raw": 0, "normalized": 0}
        cell = self.cell()
        self.assertEqual(cell["raw"], 0)
        self.assertNotIn("proxy", cell)

    def test_stale_observed_value_remains_until_max_stale(self):
        self.assertIsNone(self.cell("near", NOW + timedelta(hours=1))["missing_reason"])
        self.assertEqual(self.cell("near", NOW + timedelta(days=8))["missing_reason"], "max_stale_exceeded")

    def test_partial_protocol_group_survives_missing_candidate(self):
        fits = {p["id"]: {"status": "documented"} for p in self.ps}
        ev = decision.evaluations(self.task, {"facets": [{"axis": "task", "value": "coding"}]},
                                  fits, self.cfg, self.snap, [], index_fixture(), NOW + timedelta(hours=1))
        self.assertEqual(ev["comparisons"]["u/coding"], ["other"])
        self.assertNotIn("target", ev["units"]["u/coding"]["comparison_profiles"])
        self.assertEqual(ev["missing"]["target"]["u/coding"], "no_observation")
        row = ev["observations"]["near"]["u/coding"]
        incompatible = {**row, "conditions": {**row["conditions"], "subset": "different"}}
        self.assertFalse(decision._model_comparable(row, incompatible))
        ev["benchmark_relevance"] = {"u/coding": .9}
        self.assertNotIn("task_specific_evaluation_missing", decision.candidate_diagnostics({"evaluation": ev}, "near", {}))
        self.assertIn("task_specific_evaluation_missing", decision.candidate_diagnostics({"evaluation": ev}, "target", {}))

    def test_refresh_failure_metadata_survives_snapshot_and_status(self):
        cfg = config([profile("p", model_id="model-a")])
        data.refresh(self.root, cfg, MAPPING, {"aa": {"m-a": "model-a"}}, NOW,
                     only="aa", get_json=FakeHTTP(), env=ENV)
        later = NOW + timedelta(hours=25)
        report = data.refresh(self.root, cfg, MAPPING, {"aa": {"m-a": "model-a"}}, later,
                              only="aa", get_json=FakeHTTP(fail_page=1), env=ENV)
        self.assertEqual(report["status"], "failed")
        snap, _ = r.load_snapshot(self.root)
        source = r.source_status(snap, later)["aa"]
        self.assertEqual(source["refresh_result"], "failed")
        self.assertTrue(source["stale"])
        self.assertFalse(source["excluded"])
        status = data.status(self.root, later)["sources"]["aa"]
        for key, value in source.items():
            self.assertEqual(status[key], value, key)
        db = data.open_db(self.root / "bench-router.db")
        self.addCleanup(db.close)
        db.execute("INSERT INTO sources(id,last_attempt_at,last_error) VALUES ('mg',?,?)", (later.isoformat(), "failed"))
        db.commit()
        never = data.status(self.root, later)["sources"]["mg"]
        self.assertTrue(never["excluded"])
        self.assertEqual(never["refresh_result"], "failed")

    def test_refresh_boundary_is_fresh(self):
        cfg = config([profile("p")])
        data.refresh(self.root, cfg, MAPPING, {}, NOW, only="aa", get_json=FakeHTTP(), env=ENV)
        http = FakeHTTP()
        report = data.refresh(self.root, cfg, MAPPING, {}, NOW + timedelta(hours=24),
                              only="aa", get_json=http, env=ENV)
        self.assertEqual(report["sources"]["aa"]["result"], "skipped_fresh")
        self.assertEqual(http.calls, [])
        self.assertFalse(data.status(self.root, NOW + timedelta(hours=24))["sources"]["aa"]["stale"])

    def test_explicit_refresh_precedes_snapshot_read_and_cannot_change_replay(self):
        args = argparse.Namespace(task="task", context=None, selection=None, decision_response=None,
                                  config_dir=self.root, cache_dir=self.root, refresh=False,
                                  cmd="evaluate", format="2")
        with mock.patch.object(r, "load_json_strict", return_value=self.task), \
             mock.patch.object(r, "validate_task", return_value=self.task), \
             mock.patch.object(cli, "_config", return_value=(self.cfg, MAPPING)), \
             mock.patch.object(r, "load_snapshot", return_value=(None, [])) as load, \
             mock.patch.object(data, "refresh", return_value={"status": "partial_failure"}) as refresh:
            cli._load(args)
            refresh.assert_not_called()
            args.refresh = True
            refresh.side_effect = lambda *a, **kw: (load.reset_mock() or {"status": "partial_failure"})
            result = cli._load(args)
            load.assert_called_once()
            self.assertEqual(result["benchmark_refresh"]["status"], "partial_failure")
            args.decision_response = "response"
            with self.assertRaisesRegex(r.InputError, "initial assessment"):
                cli._load(args)
            self.assertEqual(refresh.call_count, 1)
            args.decision_response = None
            refresh.side_effect = data.LockBusy("refresh busy")
            load.reset_mock()
            self.assertEqual(cli._load(args)["status"], "conflict")
            load.assert_not_called()

    def test_priority_reaches_vendor_analysis(self):
        request = decision.analysis_request(self.task, index_fixture(), {})
        answers = {k: {"choice": "unknown"} for k in decision.WORKLOADS}
        self.assertEqual(decision._analysis(self.task, request, answers)["requirements"]["priority"], "cost")

    def test_interactive_guide_conditions_are_sent_with_the_starting_point(self):
        guide = decision.load_guidelines()
        request = decision.guidance_request({"requirements": {"priority": "balanced"}}, "openai", guide)
        criteria = request["questions"]["guidance:openai"]["criteria"]
        self.assertEqual(criteria["gpt-6-luna:medium"], "Software engineering; Balanced: Fix a well-scoped bug")
        self.assertIn("Higher quality outputs", criteria["gpt-6-luna:high"])

    def test_model_gap_effort_is_available_for_profile_matching(self):
        rows = data.parse_mg({"benchmarks": [{"id": "test", "variants": ["main"]}],
                              "scores": [{"benchmark_id": "test", "variant": "main", "model_id": "gpt-6-luna",
                                          "value": .4, "effort": "high", "date_observed": NOW.isoformat()}]})
        self.assertEqual(rows[0]["reasoning_effort"], "high")
        self.assertEqual(rows[0]["conditions"]["reasoning_effort"], "high")
