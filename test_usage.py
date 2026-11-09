"""Collector substitution verified against the former CodeBurn 0.9.27 wire contract."""
import json
import unittest
from dataclasses import replace
from functools import partial
from types import SimpleNamespace
from datetime import timedelta
from unittest.mock import patch
from bench_router import usage, codexbar, codeburn, herdr
from test_codexbar import NOW, profile, payload


class CollectorCompatibility(unittest.TestCase):
    def burn(self, used=20, available=True):
        return {"providers": [{"id": "codex", "available": available, "windows": [
            {"label": "5-hour", "usedPct": used}, {"label": "Weekly", "usedPct": 10}]}]}

    def runner(self, raw):
        return lambda cmd, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(raw))

    def test_collectors_give_same_decisions_at_reserve_and_exhaustion_boundaries(self):
        ps = [profile("c", "gpt-6", "codex")]
        for used, expected in ((0, None), (90, None), (91, "codexbar_quota_low"), (100, "codexbar_quota_exhausted")):
            with self.subTest(used=used):
                collectors = [partial(codexbar.collect, runner=self.runner([payload("codex", used)]), which=lambda _: "/tool"),
                              partial(codeburn.collect, runner=self.runner(self.burn(used)), which=lambda _: "/tool")]
                for collect in collectors:
                    out = usage.probe(ps, collector=collect, now=NOW)
                    self.assertEqual(out, {"c": expected})
                    self.assertIn(out.details["c"]["collector"], ("codexbar", "codeburn"))

    def test_codeburn_batches_profiles_and_does_not_invent_usage_credits(self):
        raw = {"providers": [{"id": "claude", "available": True, "plan": "Pro", "windows": [{"label": "Weekly", "usedPct": 10}]}]}
        calls = []
        def run(cmd, **kw):
            calls.append(cmd)
            return self.runner(raw)(cmd, **kw)
        ps = [profile("s"), profile("f", "claude-fable-5")]
        out = usage.probe(ps, collector=partial(codeburn.collect, runner=run, which=lambda _: "/tool"), now=NOW)
        self.assertEqual(out, {"s": None, "f": "codexbar_credits_unverified"})
        self.assertEqual(out.details["f"]["credits"]["capability"], "unsupported")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1:], ["quota", "--format", "json"])

    def test_missing_invalid_and_stale_observations_fail_closed(self):
        ps = [profile("c", "gpt-6", "codex")]
        good = usage.Observation("c", "codex", "gpt-6", "fake", "live", status="ok", binding="ambient_cli",
                                 windows=(usage.Window("weekly", 10, NOW.isoformat(), "live"),))
        for row in (None, replace(good, model="wrong"), replace(good, caps=(object(),)),
                    replace(good, windows=(replace(good.windows[0], observed_at=(NOW-timedelta(hours=1)).isoformat()),)),
                    replace(good, windows=(replace(good.windows[0], used_percent=True),))):
            self.assertIsNotNone(usage.probe(ps, collector=lambda ps, now: {"c": row}, now=NOW)["c"])
        with patch.object(codexbar, "query", side_effect=AssertionError("must not invoke CodexBar")):
            out = usage.probe(ps, collector=lambda ps, now: {"c": good}, now=NOW)
            self.assertEqual(out, {"c": None})

    def test_codeburn_unavailable_and_ambiguous_provider_do_not_pass(self):
        ps = [profile("c", "gpt-6", "codex")]
        for raw in (self.burn(available=False), {"providers": []}, {"providers": self.burn()["providers"] * 2}):
            self.assertEqual(usage.probe(ps, collector=partial(codeburn.collect, runner=self.runner(raw), which=lambda _: "/tool"), now=NOW),
                             {"c": "codexbar_quota_unverified"})

    def test_herdr_substitutes_collector_without_tool_specific_imports(self):
        ps = [profile("c", "gpt-6", "codex")]
        collect = partial(codeburn.collect, runner=self.runner(self.burn()), which=lambda _: "/tool")
        out = herdr.probe_profiles(ps, which=lambda _: "/tool", collector=collect)
        self.assertEqual(out, {"c": None})
        self.assertEqual(out.details["c"]["collector"], "codeburn")

    def test_explicit_backend_choice_and_invalid_names(self):
        ps = [profile("c", "gpt-6", "codex")]
        with patch.dict("os.environ", {"BENCH_ROUTER_USAGE_COLLECTOR": "codeburn"}):
            out = usage.probe(ps, now=NOW, runner=self.runner(self.burn()), which=lambda _: "/tool")
            self.assertEqual(out.details["c"]["collector"], "codeburn")
        with patch.dict("os.environ", {"BENCH_ROUTER_USAGE_COLLECTOR": "unknown"}):
            with self.assertRaises(ValueError):
                usage.probe(ps, now=NOW)

    def test_codeburn_antigravity_shared_pools_stay_separate(self):
        raw = {"providers": [{"id": "antigravity", "available": True, "windows": [
            {"label": "Gemini Models · gemini-weekly", "usedPct": 10},
            {"label": "Claude and GPT · 3p-weekly", "usedPct": 100}]}]}
        ps = [profile("gemini", "gemini-4-argon-high", "agy"), profile("claude", "claude-opus-5-high", "agy")]
        out = usage.probe(ps, collector=partial(codeburn.collect, runner=self.runner(raw), which=lambda _: "/tool"), now=NOW)
        self.assertEqual(out, {"gemini": None, "claude": "codexbar_quota_exhausted"})

    def test_account_and_credit_kind_cannot_be_substituted(self):
        ps = [profile("f", "claude-fable-5")]
        o = usage.Observation("f", "claude", "claude-fable-5", "fake", plan="Pro", status="ok", binding="matched",
            windows=(usage.Window("weekly", 10, NOW.isoformat(), "api", binding="matched", account_key="owner"),),
            balances=(usage.Balance(10, "USD", "api_console_balance", NOW.isoformat(), "api", "matched", "measured", "owner"),),
            account_key="owner")
        self.assertEqual(usage.probe(ps, collector=lambda ps, now: {"f": o}, now=NOW)["f"], "codexbar_credits_unverified")
        o = replace(o, balances=(replace(o.balances[0], kind="claude_usage_credits", account_key="other"),))
        self.assertEqual(usage.probe(ps, collector=lambda ps, now: {"f": o}, now=NOW)["f"], "codexbar_credit_account_mismatch")
