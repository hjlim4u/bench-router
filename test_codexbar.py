"""Pinned CodexBar wire fixtures; all checks offline, no paid agent prompts."""
import json
import os
import select
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from bench_router import codexbar as cb, herdr, routing
from eval import codexbar as report


NOW = datetime(2026, 11, 9, tzinfo=timezone.utc)


def payload(provider="claude", used=10):
    return {"provider": provider, "source": "cli" if provider == "antigravity" else "oauth",
            "usage": {"updatedAt": NOW.isoformat(), "loginMethod": "Claude Pro",
                      "primary": {"usedPercent": used}, "secondary": {"usedPercent": 20}}}


def profile(name, model=None, kind="claude"):
    return {"id": name, "kind": kind, "executable": kind,
            "args": ["--model", model or "claude-sonnet-5-5"]}


def named(key, used, **extra):
    return {"id": key, "window": {"usedPercent": used}, **extra}


class CodexBarTests(unittest.TestCase):
    def check(self, profiles, rows, web=None):
        calls = []
        def run(cmd, **kwargs):
            calls.append(cmd)
            provider, source = cmd[3], cmd[5]
            self.assertEqual(cmd[1:3], ["usage", "--provider"])
            self.assertIn(source, ("oauth", "cli", "web", "auto"))
            row = web if source == "web" else rows.get(provider)
            return SimpleNamespace(returncode=0, stdout=json.dumps([row] if row else []))
        result = cb.availability(profiles, runner=run, which=lambda _: "/tool", now=NOW)
        return result, calls

    def test_shared_caps_and_model_scopes_before_paid_decisions(self):
        p = payload()
        p["usage"]["extraRateWindows"] = [named("claude-weekly-scoped-fable", 100),
                                                 named("claude-routines", 100)]
        p["usage"]["loginMethod"] = "Claude Max"
        got, calls = self.check([profile("sonnet"), profile("fable", "claude-fable-5")], {"claude": p})
        self.assertEqual(got, {"sonnet": None, "fable": "codexbar_quota_exhausted"})
        self.assertEqual(len(calls), 1)
        p["usage"]["secondary"]["usedPercent"] = 100
        self.assertEqual(self.check([profile("sonnet")], {"claude": p})[0]["sonnet"], "codexbar_quota_exhausted")
        p = payload("codex", 100)
        self.assertEqual(self.check([profile("c", "gpt-6", "codex")], {"codex": p})[0]["c"], "codexbar_quota_exhausted")
        for plan in (None, "", "Unknown plan", "Claude Pro"):
            self.assertTrue(cb.needs_credits("claude-fable-5", {"loginMethod": plan}))

    def test_antigravity_family_and_distinct_model_buckets(self):
        p = payload("antigravity")
        p["usage"]["extraRateWindows"] = [named("antigravity-quota-summary-gemini-5h", 10),
            named("antigravity-quota-summary-gemini-weekly", 20),
            named("antigravity-quota-summary-gemini-argon-wtu-weekly", 100),
            named("antigravity-quota-summary-3p-weekly", 100)]
        profiles = [profile("argon", "gemini-4-argon-high", "agy"),
                    profile("flash", "gemini-4-flash-high", "agy"),
                    profile("claude", "claude-opus-5-high", "agy")]
        got, calls = self.check(profiles, {"antigravity": p})
        self.assertEqual(got, {"argon": "codexbar_quota_exhausted", "flash": None,
                               "claude": "codexbar_quota_exhausted"})
        self.assertEqual(len(calls), 1)
        p["usage"]["extraRateWindows"] = [named("antigravity-quota-summary-gemini-weekly", 100, usageKnown=False)]
        self.assertEqual(self.check(profiles[:1], {"antigravity": p})[0]["argon"], "codexbar_quota_unverified")
        p["usage"]["extraRateWindows"] = [named("gpt-6.0-astra", 100), named("gpt-6.1-astra", 10)]
        self.assertEqual(self.check([profile("new", "gpt-6.1-astra-high", "agy")], {"antigravity": p})[0], {"new": None})

    @patch.object(cb, "claude_identity", return_value={"emailAddress": "owner@example.com"})
    def test_fable_requires_fresh_same_account_usage_credits(self, identity):
        p = payload()
        web = payload()
        web["source"] = "web"
        web["usage"].update(accountEmail="owner@example.com", providerCost={
            "balance": 2, "balanceUpdatedAt": NOW.isoformat(), "updatedAt": NOW.isoformat(), "currencyCode": "USD", "used": 1, "limit": 10})
        profiles = [profile("s"), profile("f", "claude-fable-5"), profile("f2", "claude-fable-5")]
        got, calls = self.check(profiles, {"claude": p}, web)
        self.assertEqual(got, {"s": None, "f": None, "f2": None})
        self.assertEqual(len(calls), 2)  # one OAuth request and one web request, regardless of profile count
        for value, reason in [(0, "codexbar_credits_exhausted"), (None, "codexbar_credits_unverified")]:
            web["usage"]["providerCost"]["balance"] = value
            self.assertEqual(self.check(profiles, {"claude": p}, web)[0]["f"], reason)
        web["usage"]["providerCost"].update(balance=2, used=10)
        self.assertEqual(self.check(profiles, {"claude": p}, web)[0]["f"], "codexbar_spend_limit_exhausted")
        web["usage"]["providerCost"]["used"] = 1
        web["usage"]["providerCost"]["balanceUpdatedAt"] = (NOW - timedelta(hours=1)).isoformat()
        self.assertEqual(self.check(profiles, {"claude": p}, web)[0]["f"], "codexbar_credits_unverified")
        self.assertIsNone(self.check(profiles, {"claude": p}, web)[0].details["f"]["credits"]["balance"])
        web["usage"]["accountEmail"] = "other@example.com"
        self.assertEqual(self.check(profiles, {"claude": p}, web)[0]["f"], "codexbar_credit_account_mismatch")
        web["usage"]["accountEmail"] = "owner@example.com"
        web["usage"]["identity"] = ["malformed"]
        web["usage"]["providerCost"] = {"balance": 2, "currencyCode": "USD", "updatedAt": NOW.isoformat()}
        self.assertEqual(self.check(profiles, {"claude": p}, web)[0]["f"], "codexbar_credits_unverified")
        self.assertEqual(self.check(profiles, {"claude": p})[0], {
            "s": None, "f": "codexbar_credits_unverified", "f2": "codexbar_credits_unverified"})
        web["usage"].update(accountEmail="owner@example.com", accountOrganization="Other workspace")
        p["usage"]["accountOrganization"] = "Agent workspace"
        self.assertEqual(self.check(profiles, {"claude": p}, web)[0]["f"], "codexbar_credit_account_mismatch")

    def test_unknown_never_becomes_measured_zero(self):
        bad = []
        for mutate in [lambda p: p.update(error={"code": 1}), lambda p: p.update(diagnostic="last known"),
                       lambda p: p["usage"].update(updatedAt=(NOW - timedelta(hours=1)).isoformat()),
                       lambda p: p["usage"].update(updatedAt=(NOW + timedelta(hours=1)).isoformat()),
                       lambda p: p["usage"].update(primary={"usedPercent": True}, secondary=None),
                       lambda p: p["usage"].update(primary={"usedPercent": float("nan")}, secondary=None),
                       lambda p: p["usage"].update(primary={"usedPercent": 0, "isSyntheticPlaceholder": True}, secondary=None)]:
            p = payload(); mutate(p); bad.append(p)
        for p in bad:
            with self.subTest(p=p):
                self.assertEqual(self.check([profile("p")], {"claude": p})[0], {"p": "codexbar_quota_unverified"})
        self.assertEqual(self.check([profile("p")], {"claude": payload(used=0)})[0], {"p": None})

    def test_cli_failure_missing_binary_and_malformed_payload(self):
        for stdout in ("bad", "null", "{}", '[{"provider":"claude"},{"provider":"claude"}]'):
            run = lambda *a, **k: SimpleNamespace(stdout=stdout, returncode=1)
            self.assertEqual(cb.availability([profile("p")], run, lambda _: "/tool", NOW),
                             {"p": "codexbar_quota_unverified"})
        run = lambda *a, **k: (_ for _ in ()).throw(subprocess.TimeoutExpired("codexbar", 15))
        self.assertEqual(cb.availability([profile("p")], run, lambda _: "/tool", NOW), {"p": "codexbar_quota_unverified"})
        run = unittest.mock.Mock()
        self.assertEqual(cb.availability([profile("p")], run, lambda _: None, NOW), {"p": "codexbar_quota_unverified"})
        run.assert_not_called()

    def test_report_passes_native_options_and_errors_without_new_schema(self):
        with patch.object(report.shutil, "which", return_value="/tool"), \
                patch.object(report.subprocess, "run", return_value=SimpleNamespace(returncode=7)) as run:
            self.assertEqual(report.main(["cost", "--provider", "codex", "--group-by", "project", "--json"]), 7)
            self.assertEqual(run.call_args.args[0][1:], ["cost", "--provider", "codex", "--group-by", "project", "--json"])

    @patch.object(cb, "claude_identity", return_value={"emailAddress": "owner@example.com"})
    def test_web_scoped_limits_and_oauth_spend_cap_are_both_enforced(self, identity):
        base, web = payload(), payload()
        web["source"] = "web"
        web["usage"].update(accountEmail="owner@example.com", providerCost={
            "balance": 2, "currencyCode": "USD", "updatedAt": NOW.isoformat(), "used": 0, "limit": 0})
        ps = [profile("f", "claude-fable-5")]
        web["usage"]["extraRateWindows"] = [named("claude-weekly-scoped-fable", 100)]
        self.assertEqual(self.check(ps, {"claude": base}, web)[0]["f"], "codexbar_quota_exhausted")
        web["usage"]["extraRateWindows"] = []
        base["usage"]["providerCost"] = {"used": 10, "limit": 10, "updatedAt": NOW.isoformat()}
        self.assertEqual(self.check(ps, {"claude": base}, web)[0]["f"], "codexbar_spend_limit_exhausted")

    @patch.object(cb, "worker_email", return_value="owner@example.com")
    def test_passive_web_fallback_and_native_antigravity_auto_are_account_bound(self, identity):
        web = payload();web["source"] = "web";web["usage"]["accountEmail"] = "owner@example.com"
        got, calls = self.check([profile("s")], {}, web)
        self.assertEqual(got, {"s": None})
        self.assertEqual([cmd[5] for cmd in calls], ["oauth", "web"])
        web["usage"]["accountEmail"] = "other@example.com"
        self.assertEqual(self.check([profile("s")], {}, web)[0]["s"], "codexbar_quota_unverified")
        p = payload("antigravity");p["source"] = "oauth";p["usage"]["accountEmail"] = "owner@example.com"
        ps = [profile("a", "gemini-4-argon-high", "agy")]
        got, calls = self.check(ps, {"antigravity": p})
        self.assertEqual(got, {"a": None})
        self.assertEqual(calls[0][5], "auto")
        p["usage"]["accountEmail"] = "other@example.com"
        p["usage"]["primary"]["usedPercent"] = 100
        got, _ = self.check(ps, {"antigravity": p})
        self.assertEqual(got["a"], "codexbar_account_mismatch")
        self.assertEqual(got.details["a"]["windows"], [])

    def test_guard_boundary_pace_and_redacted_output(self):
        p = payload("codex", 90)
        p["usage"]["primary"].update(windowMinutes=300, resetsAt="2026-11-09T03:00:00Z")
        p["pace"] = {"primary": {"stage": "farAhead", "willLastToReset": False, "etaSeconds": 600,
                                  "summary": "PRIVATE MESSAGE"}}
        p["credits"] = {"events": ["PRIVATE CREDIT ID"]}
        ps = [profile("c", "gpt-6", "codex")]
        got, _ = self.check(ps, {"codex": p})
        self.assertEqual(got["c"], None)  # inclusive 10% boundary
        details = got.details["c"]
        self.assertEqual(details["remaining_percent"], 10)
        self.assertEqual(details["windows"][0]["resets_at"], "2026-11-09T03:00:00+00:00")
        self.assertEqual(details["pace"]["primary"]["eta_seconds"], 600)
        self.assertIn("pace_runs_out_before_reset", details["warnings"])
        self.assertNotIn("PRIVATE", json.dumps(details))
        p["usage"]["primary"]["usedPercent"] = 91
        self.assertEqual(self.check(ps, {"codex": p})[0]["c"], "codexbar_quota_low")
        with patch.dict(os.environ, {"BENCH_ROUTER_MIN_REMAINING": "0"}):
            self.assertEqual(self.check(ps, {"codex": p})[0]["c"], None)
            p["usage"]["primary"]["usedPercent"] = 100
            self.assertEqual(self.check(ps, {"codex": p})[0]["c"], "codexbar_quota_exhausted")
        with patch.dict(os.environ, {"BENCH_ROUTER_MIN_REMAINING": "NaN"}):
            with self.assertRaises(routing.InputError):
                self.check(ps, {"codex": p})

    def test_static_constraints_filter_queries_before_network_and_keep_union_for_parallel(self):
        from test_p0 import profile as configured, config
        ps = [configured("a"), configured("b", enabled=False), configured("c", inference_local=True)]
        cfg = config(ps)
        request = routing.validate_task({"schema_version": "1.0", "task_id": "filter", "round": 1,
                                        "summary": "filter candidates", "prompt": "fix", "cwd": "/tmp"})
        request["exclude_profiles"] = ["a"]
        with patch.object(herdr, "probe_profiles", return_value={}) as probe:
            herdr._availability(None, cfg, lambda _: "/tool", herdr.LOCAL_BACKEND, [(request, None)])
            self.assertEqual([p["id"] for p in probe.call_args.args[0]], ["c"])
            other = {**request, "exclude_profiles": ["c"]}
            herdr._availability(None, cfg, lambda _: "/tool", herdr.LOCAL_BACKEND, [(request, None), (other, None)])
            self.assertEqual([p["id"] for p in probe.call_args.args[0]], ["a", "c"])
        calls = unittest.mock.Mock()
        got = herdr.probe_profiles([{**profile("off", "claude-fable-5"), "enabled": False}],
                                  which=lambda _: "/tool", runner=calls)
        self.assertEqual(got, {"off": "disabled"})
        calls.assert_not_called()

    def test_probe_timeout_cleans_owned_children_and_preserves_unrelated_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            with subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"]) as unrelated:
                try:
                    for detached in (False, True):
                        pidfile = Path(tmp) / f"child-{detached}.pid"
                        code = ("import subprocess,sys,time,pathlib,signal; "
                                "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],"
                                f"start_new_session={detached}); "
                                f"pathlib.Path({str(pidfile)!r}).write_text(str(p.pid)); ")
                        if detached:  # Native CodexBar signal handling must get its cleanup opportunity.
                            code += "signal.signal(signal.SIGTERM,lambda *a:(p.terminate(),p.wait(),sys.exit(0))); "
                        code += "time.sleep(30)"
                        with self.assertRaises(subprocess.TimeoutExpired):
                            cb.run_cli([sys.executable, "-c", code], timeout=0.5)
                        pid = int(pidfile.read_text())
                        try:
                            fd = os.pidfd_open(pid)
                        except ProcessLookupError:
                            pass
                        else:
                            try:
                                self.assertTrue(select.select([fd], [], [], 2)[0])
                            finally:
                                os.close(fd)
                        self.assertIsNone(unrelated.poll())
                finally:
                    unrelated.terminate()

    def test_all_evaluation_formats_keep_telemetry_outside_decision_digest(self):
        from test_p0 import profile as configured, config, MAPPING
        from bench_router import decision
        cfg = config([configured("quota-report", model_id="gpt-6.1-sol", reasoning_effort="low")])
        t = routing.validate_task({"schema_version": "1.0", "task_id": "quota-report", "round": 1,
                                   "summary": "fix", "prompt": "fix", "cwd": "/tmp"})
        availability = cb.Availability({"quota-report": None})
        for evaluate in (routing.evaluate_v1, routing.evaluate, decision.evaluate):
            with self.subTest(evaluate=evaluate.__module__ + "." + evaluate.__name__):
                availability.details = {"quota-report": {"remaining_percent": 80}}
                before = evaluate(t, cfg, MAPPING, None, [], NOW, availability=availability)
                availability.details = {"quota-report": {"remaining_percent": 70}}
                after = evaluate(t, cfg, MAPPING, None, [], NOW, availability=availability)
                self.assertEqual(before["preflight"]["quota-report"]["remaining_percent"], 80)
                self.assertEqual(after["preflight"]["quota-report"]["remaining_percent"], 70)
                self.assertEqual(before["assessment_digest"], after["assessment_digest"])


if __name__ == "__main__":
    unittest.main()
