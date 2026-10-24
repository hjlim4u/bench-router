"""P1 검증 V11–V18 (06 문서). source 응답은 합성 fixture, 네트워크 없음.
실행: python3 -m unittest -v test_p1"""
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from bench_router import data as d
from bench_router import routing as r
from test_p0 import MAPPING, config, profile

NOW = datetime(2026, 10, 12, tzinfo=timezone.utc)
ENV = {d.AA_KEY_ENV: "SECRET-KEY-XYZ"}


def aa_pages(dup=False):
    p1 = {"tier": "free", "intelligence_index_version": 4.1,
          "pagination": {"page": 1, "page_size": 2, "total_pages": 2, "has_more": True},
          "data": [{"slug": "m-a", "evaluations": {"artificial_analysis_intelligence_index": 50,
                                                   "artificial_analysis_coding_index": 40}},
                   {"slug": "m-b", "evaluations": {"artificial_analysis_intelligence_index": 30,
                                                   "artificial_analysis_coding_index": None}}]}
    p2 = {"tier": "free", "intelligence_index_version": 4.1,
          "pagination": {"page": 2, "page_size": 2, "total_pages": 2, "has_more": False},
          "data": [{"slug": "m-a" if dup else "m-c",
                    "evaluations": {"artificial_analysis_intelligence_index": 40,
                                    "artificial_analysis_coding_index": 60}}]}
    return [p1, p2]


class FakeHTTP:
    def __init__(self, pages=None, fail_page=None):
        self.pages, self.fail_page, self.calls = pages or aa_pages(), fail_page, []

    def __call__(self, url, headers, budget=None):
        self.calls.append(url)
        if budget is not None:  # http_get_json 계약: 요청마다 budget 소비
            budget["used"] += 1
        if url.startswith(d.AA_URL):
            assert headers == {"x-api-key": ENV[d.AA_KEY_ENV]}
            page = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["page"][0])
            if page == self.fail_page:
                raise d.SourceError("HTTP 503")
            return self.pages[page - 1]
        if url == d.ARENA_REVISION_URL:
            return {"sha": "rev1", "siblings": [{"rfilename": f"{s}/latest-00000-of-00001.parquet"} for s in
                                                ("text_style_control", "webdev", "document_style_control", "vision_style_control", "agent")]}
        return [{"model_name": f"arena-{i}", "rating": 1000 + i, "category": c, "leaderboard_publish_date": "2026-10-08T00:00:00"}
                for c in ("overall", "math") for i in range(150)]


def tb_import(**kw):
    doc = {"schema_version": "1.0", "evidence_id": "terminal_exact", "source_url": "https://www.tbench.ai/",
           "attribution": "Terminal-Bench", "published_at": "2026-10-01",
           "benchmark": {"suite": "terminal-bench", "version": "4.0", "subset": "core", "metric": "resolved_rate",
                         "direction": "higher", "variant": "default", "dataset_revision": "v4.0.0",
                         "evaluation_harness": "terminal-bench-official", "aggregation": "pass@1_mean_5"},
           "rows": [{"model_id": "model-a", "harness_id": "codex-cli", "reasoning_effort": "high", "raw": 0.6},
                    {"model_id": "model-z", "harness_id": "codex-cli", "reasoning_effort": "high", "raw": 0.4}]}
    doc.update(kw)
    return doc


class P1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self.tmp.name)
        self.ps = [profile("a", model_id="model-a", reasoning_effort="high"), profile("dflt")]
        self.cfg = config(self.ps)
        self.aliases = {"aa": {"m-a": "model-a"}}

    def tearDown(self):
        self.tmp.cleanup()

    def refresh(self, http=None, now=NOW, **kw):
        return d.refresh(self.cache, self.cfg, MAPPING, self.aliases, now, get_json=http or FakeHTTP(), env=ENV,
                         **{"only": "aa", **kw})

    def snap(self):
        return json.loads((self.cache / "snapshot.json").read_text("utf-8"))

    def db_count(self, table):
        db = d.open_db(self.cache / "bench-router.db")
        try:
            return db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        finally:
            db.close()

    def test_v11_aa_pagination(self):
        http = FakeHTTP()
        res = self.refresh(http)
        self.assertEqual((res["status"], res["sources"]["aa"]["result"], len(http.calls)), ("ok", "updated", 2))
        ev = self.snap()["profiles"]["a"]["evidence"]
        self.assertEqual(ev["aa_intelligence"]["normalized"], 1.0)  # 50 > 40(page2) > 30
        self.assertEqual(ev["aa_coding"]["normalized"], 0.0)        # 40 < 60(page2); null은 모집단 제외
        self.assertEqual(ev["aa_coding"]["cohort_id"], "aa:artificial_analysis_coding_index:v4.1")
        self.assertIsNone(ev["aa_coding"]["conditions"]["agent_scaffold"])
        self.assertEqual(self.snap()["unmatched"]["aa"], ["m-b", "m-c"])

    def test_v11_arena_paging_and_schema(self):
        self.aliases = {"arena": {"arena-149": "model-a"}}
        http = FakeHTTP()
        res = self.refresh(http, only="arena")
        self.assertEqual(res["sources"]["arena"]["requests"], 1 + 4)  # revision + config별 parquet 1개(text는 overall/math 공유)
        self.assertTrue(all("/resolve/rev1/" in u for u in http.calls[1:]))  # 파일은 기록한 revision에 고정
        ev = self.snap()["profiles"]["a"]["evidence"]
        self.assertEqual(sorted(ev), sorted(d.ARENA_COHORTS))
        self.assertEqual((ev["arena_text_math"]["normalized"], ev["arena_text_math"]["published_at"]), (1.0, "2026-10-08"))
        self.assertEqual(ev["arena_text_math"]["conditions"]["dataset_revision"], "rev1")
        self.assertEqual(self.snap()["sources"]["arena"]["source_revision"], "rev1")
        bad = {"revision": "x", "cohorts": {e: [{"model_name": "m", "rating": 1, "leaderboard_publish_date": "2026-01-01"},
                                                {"model_name": "n", "rating": 2, "leaderboard_publish_date": "2026-10-08"}]
                                            for e in d.ARENA_COHORTS}}
        with self.assertRaisesRegex(d.SourceError, "publish date"):
            d.parse_arena(bad)
        dup = {"revision": "x", "cohorts": {e: [{"model_name": "m", "rating": r_, "rank": k, "leaderboard_publish_date": "2026-10-08"}
                                                for k, r_ in ((1, 9), (2, 5), (3, 7))] for e in d.ARENA_COHORTS}}
        for row in dup["cohorts"]["arena_webdev"]:
            row["model_name"] = "dup" if row["rank"] < 3 else "solo"
        names = {o["source_model"] for o in d.parse_arena(dup) if o["evidence_id"] == "arena_webdev"}
        self.assertEqual(names, {"dup#rank=1", "dup#rank=2", "solo"})  # 실측 중복: 모집단 유지, 이름 매칭 차단

    def test_v12_partial_failure_keeps_last_good(self):
        self.refresh()
        before = self.snap()["sources"]["aa"]["snapshot"]
        for http in (FakeHTTP(fail_page=2), FakeHTTP(pages=aa_pages(dup=True))):
            res = self.refresh(http, force=True)
            self.assertEqual(res["status"], "failed")
            self.assertTrue(res["sources"]["aa"]["last_good_kept"])
            self.assertEqual(self.snap()["sources"]["aa"]["snapshot"], before)
            self.assertIn("aa_intelligence", self.snap()["profiles"]["a"]["evidence"])
        self.assertEqual(self.db_count("snapshots"), 1)
        st = d.status(self.cache, NOW)
        self.assertEqual(st["sources"]["aa"]["failure_count"], 2)

    def test_v13_same_payload_is_noop(self):
        self.refresh()
        later = NOW + timedelta(hours=30)
        res = self.refresh(now=later)
        self.assertEqual(res["sources"]["aa"]["result"], "unchanged")
        self.assertEqual((self.db_count("snapshots"), self.db_count("observations")), (1, 6))
        self.assertEqual(self.snap()["sources"]["aa"]["last_success_at"], later.isoformat(timespec="seconds"))

    def test_v14_http_errors_bounded_and_secret_free(self):
        def raiser(code):
            return urllib.error.HTTPError("u", code, "x", {"Retry-After": "60"}, io.BytesIO(b""))
        for code, calls in ((401, 1), (403, 1), (429, 1), (503, 3)):
            with mock.patch("urllib.request.urlopen", side_effect=raiser(code)) as m, mock.patch("time.sleep"):
                with self.assertRaises(d.SourceError) as cm:
                    d.http_get_json(d.AA_URL, {"x-api-key": "SECRET-KEY-XYZ"})
                self.assertEqual(m.call_count, calls, code)
                self.assertNotIn("SECRET", str(cm.exception))
        with mock.patch("urllib.request.urlopen", side_effect=TimeoutError()) as m, mock.patch("time.sleep"):
            with self.assertRaises(d.SourceError):
                d.http_get_json(d.AA_URL)
            self.assertEqual(m.call_count, 3)
        budget = {"used": 0, "max": 1}
        with mock.patch("urllib.request.urlopen", side_effect=raiser(503)), mock.patch("time.sleep"):
            with self.assertRaisesRegex(d.SourceError, "budget"):
                d.http_get_json(d.AA_URL, budget=budget)
        # 전체 시간 상한: 느린 서버에서 재시도가 이어져도 마감 후에는 요청하지 않음
        clock = [0.0]
        def slow(req, timeout):
            self.assertLessEqual(timeout, 10 - clock[0] + 1e-9)  # 요청별 timeout도 남은 시간으로 축소
            clock[0] += timeout
            raise TimeoutError()
        budget = {"used": 0, "max": 100, "max_seconds": 10, "deadline": 10.0}
        with mock.patch("urllib.request.urlopen", side_effect=slow) as m,                 mock.patch("time.monotonic", side_effect=lambda: clock[0]),                 mock.patch("time.sleep", side_effect=lambda s: clock.__setitem__(0, clock[0] + s)):
            with self.assertRaisesRegex(d.SourceError, "deadline exceeded"):
                for _ in range(5):
                    d.http_get_json(d.AA_URL, budget=budget)
            self.assertEqual(m.call_count, 1)  # 첫 요청이 10초 전부 사용 → 재시도 없이 종료
        res = d.refresh(self.cache, self.cfg, MAPPING, self.aliases, NOW, only="aa", get_json=FakeHTTP(), env={})
        self.assertIn("not set", res["sources"]["aa"]["error"])
        self.assertNotIn("SECRET", json.dumps(self.refresh(FakeHTTP(fail_page=1), force=True)))

    def test_v15_lock_and_atomic_publish(self):
        with d.refresh_lock(self.cache):
            with self.assertRaises(d.LockBusy):
                self.refresh()
            child = subprocess.run([sys.executable, "-c",
                                    "import sys\nfrom bench_router import data as d\n"
                                    "try:\n with d.refresh_lock(sys.argv[1]): print('acquired')\n"
                                    "except d.LockBusy: print('busy')",
                                    str(self.cache)], capture_output=True, text=True, check=True)
            self.assertEqual(child.stdout.strip(), "busy")
        self.refresh()
        first = self.snap()["snapshot_id"]
        self.refresh(force=True, now=NOW + timedelta(hours=1))
        self.assertEqual(json.loads((self.cache / "snapshot.last-good.json").read_text())["snapshot_id"], first)
        (self.cache / "snapshot.json").write_text('{"truncated": ', "utf-8")  # 손상 → route는 last-good
        snap, warnings = r.load_snapshot(self.cache)
        self.assertEqual(snap["snapshot_id"], first)
        self.assertEqual([w["code"] for w in warnings], ["snapshot_unusable", "snapshot_last_good"])
        self.assertEqual(list(self.cache.glob(".*.tmp")), [])

    @unittest.skipUnless(os.name == "nt", "Windows file sharing")
    def test_v15_reader_does_not_break_atomic_publish(self):
        path = self.cache / "snapshot.json"
        path.write_bytes(b"old")
        started = threading.Event()
        errors = []

        def write():
            started.set()
            try:
                r.atomic_write(path, b"new")
            except OSError as e:
                errors.append(e)

        with path.open("rb"):
            worker = threading.Thread(target=write)
            worker.start()
            self.assertTrue(started.wait(1))
            worker.join(0.1)
            self.assertTrue(worker.is_alive())
        worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(path.read_bytes(), b"new")
        self.assertEqual(list(self.cache.glob(".*.tmp")), [])

    def test_v16_ttl_skip(self):
        self.refresh()
        http = FakeHTTP()
        res = self.refresh(http, now=NOW + timedelta(hours=1))
        self.assertEqual((res["sources"]["aa"]["result"], len(http.calls)), ("skipped_fresh", 0))
        st = d.status(self.cache, NOW + timedelta(hours=200))
        self.assertTrue(st["sources"]["aa"]["too_stale"])

    def test_v17_route_has_no_network_path(self):
        code = ("import sys; from bench_router import cli, routing; "
                "print(any(m in sys.modules for m in ('urllib.request', 'bench_router.data', 'http.client')))")
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=Path(__file__).parent)
        self.assertEqual(out.stdout.strip(), "False", out.stderr)
        snap, _ = r.load_snapshot(self.cache)  # 캐시 없음 → None, 이후 route는 constrained default (test_p0)
        self.assertIsNone(snap)

    def test_v18_alias_and_version_cohorts(self):
        self.refresh()
        self.assertNotIn("aa_intelligence", self.snap()["profiles"]["dflt"]["evidence"])  # alias 없음 → 미매칭
        with self.assertRaisesRegex(r.InputError, "4.0"):
            d.validate_import(tb_import(benchmark={**tb_import()["benchmark"], "version": "2.0"}), "tb")
        with self.assertRaises(r.InputError):
            d.validate_import(tb_import(published_at=None), "tb")  # 날짜 없는 수동 데이터 거부
        with self.assertRaises(r.InputError):
            d.validate_import(tb_import(), "swe")
        d.refresh(self.cache, self.cfg, MAPPING, self.aliases, NOW, only="tb",
                  import_doc=d.validate_import(tb_import(), "tb"), env=ENV)
        ev = self.snap()["profiles"]["a"]["evidence"]["terminal_exact"]
        self.assertEqual((ev["scope"], ev["normalized"]), ("exact_profile", 1.0))
        self.assertEqual((ev["conditions"]["agent_scaffold"], ev["conditions"]["aggregation"]),
                         ("codex-cli", "pass@1_mean_5"))
        # effort unknown 프로필은 exact 매칭 안 됨
        self.cfg = config([profile("a", model_id="model-a"), profile("dflt")])
        self.refresh(force=True, now=NOW + timedelta(minutes=1))
        self.assertNotIn("terminal_exact", self.snap()["profiles"]["a"]["evidence"])

    def test_v18_effort_rows_pick_profile_effort(self):
        pages = aa_pages()
        pages[0]["data"][0]["slug"], pages[0]["data"][1]["slug"] = "m-a-high", "m-a"
        self.cfg = config([profile("a", model_id="model-a", reasoning_effort="high"),
                           profile("lo", model_id="model-a", reasoning_effort="low"), profile("dflt")])
        self.aliases = {"aa": {"m-a-high": "model-a", "m-a": "model-a"}}
        self.refresh(http=FakeHTTP(pages))
        snap = self.snap()
        a, lo = (snap["profiles"][p]["evidence"]["aa_intelligence"] for p in ("a", "lo"))
        self.assertEqual((a["raw"], lo["raw"]), (50, 30))  # 프로필 effort 행, 없으면 effort 표기 없는 행
        self.assertEqual(snap["ambiguous"], [])

    def test_v18_auto_alias_matches_profile_model_names(self):
        k = d.model_key
        self.assertEqual({k(n)[1] for n in ("Claude Opus 5.5 (High)", "claude-opus-5.5-high", "claude-opus-5-5")}, {"claude-opus-5-5"})
        self.assertEqual(k("GPT-6 Luna (xHigh, Codex Harness)")[1], "gpt-6-luna-xhigh-codex-harness")  # 변형은 자동 매칭 안 함
        pages = aa_pages()
        pages[0]["data"][0]["slug"], pages[0]["data"][1]["slug"] = "Model-A-High", "model-b"
        self.cfg = config([profile("a", model_id="model-a", reasoning_effort="high"), profile("dflt")])
        self.aliases = {}
        res = self.refresh(http=FakeHTTP(pages))
        self.assertEqual(self.snap()["profiles"]["a"]["evidence"]["aa_intelligence"]["raw"], 50)  # alias 없이 연결
        self.assertEqual(res["unmatched_counts"]["aa"], 2)  # model-b, m-c는 프로필이 없어 미매칭
        self.aliases = {"aa": {"Model-A-High": "dflt"}}  # 명시 alias가 자동 매칭보다 우선
        self.refresh(http=FakeHTTP(pages), force=True, now=NOW + timedelta(minutes=1))
        self.assertEqual(self.snap()["profiles"]["dflt"]["evidence"]["aa_intelligence"]["raw"], 50)

    def test_v19_import_conditions_separate_cohorts(self):
        doc = tb_import(rows=[{"model_id": "model-a", "harness_id": "codex-cli",
                               "reasoning_effort": "high", "raw": 0.6},
                              {"model_id": "model-z", "harness_id": "other",
                               "reasoning_effort": "high", "raw": 0.4}])
        obs = d.normalize(d.parse_import(d.validate_import(doc, "tb")))
        self.assertNotEqual(obs[0]["cohort_id"], obs[1]["cohort_id"])
        self.assertEqual([o["normalized"] for o in obs], [0.5, 0.5])
        changed = tb_import(benchmark={**doc["benchmark"], "aggregation": "pass@1_mean_3"})
        self.assertNotEqual(obs[0]["cohort_id"], d.parse_import(changed)[0]["cohort_id"])
        with self.assertRaisesRegex(r.InputError, "aggregation"):
            d.validate_import(tb_import(benchmark={k: v for k, v in doc["benchmark"].items()
                                                   if k != "aggregation"}), "tb")

    def test_v19_v1_cache_migrates_without_dropping_observations(self):
        path = self.cache / "legacy.db"
        legacy = sqlite3.connect(path)
        try:
            with legacy:
                legacy.execute("CREATE TABLE observations(snapshot_id TEXT, evidence_id TEXT, cohort_id TEXT, "
                               "source_model TEXT, harness_id TEXT, reasoning_effort TEXT, raw REAL, normalized REAL, "
                               "scope TEXT, metric_version TEXT, published_at TEXT, evaluated_at TEXT)")
                legacy.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                               ("old", "terminal_exact", "old-cohort", "model-a", "codex-cli", "high", 0.6, 1.0,
                                "exact_profile", "4.0", "2026-10-01", None))
                legacy.execute("PRAGMA user_version = 1")
        finally:
            legacy.close()
        db = d.open_db(path)
        try:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 2)
            self.assertEqual(tuple(db.execute("SELECT raw, conditions FROM observations").fetchone()), (0.6, None))
        finally:
            db.close()

    def test_end_to_end_refresh_then_route(self):
        self.refresh()
        d.refresh(self.cache, self.cfg, MAPPING, self.aliases, NOW, only="tb",
                  import_doc=d.validate_import(tb_import(), "tb"), env=ENV)
        snap, warnings = r.load_snapshot(self.cache)
        with tempfile.TemporaryDirectory() as cwd:
            t = r.validate_task({"schema_version": "1.0", "task_id": "e2e", "round": 1,
                                 "summary": "fix the deploy shell", "prompt": "p", "cwd": cwd})
            res = r.evaluate_v1(t, self.cfg, MAPPING, snap, warnings, NOW)
            legacy = json.loads(json.dumps(snap))
            legacy["profiles"]["a"]["evidence"]["terminal_exact"].pop("conditions")
            legacy["snapshot_id"] = r.snapshot_hash(legacy)
            old = r.evaluate_v1(t, self.cfg, MAPPING, legacy, [], NOW)
            invalid = json.loads(json.dumps(snap))
            invalid["profiles"]["a"]["evidence"]["terminal_exact"]["conditions"] = {"variant": "default"}
            invalid["snapshot_id"] = r.snapshot_hash(invalid)
            with self.assertRaisesRegex(r.InputError, "conditions.suite"):
                r.validate_snapshot(invalid)
        self.assertEqual(res["candidates"][0]["profile"], "a")
        a = res["candidates"][0]
        self.assertEqual((a["coverage"], a["exact_evidence_weight"]), (1.0, 0.7))
        old_terminal = next(e for e in old["candidates"][0]["evidence"] if e["id"] == "terminal_exact")
        self.assertEqual(old_terminal["missing_reason"], "missing_conditions")
        self.assertEqual(d.status(self.cache, NOW, r.config_hash(self.cfg, MAPPING))["snapshot"]["config_matches"], True)


MG_BENCH = [{"id": "deepswe", "variants": ["default"]}, {"id": "hle", "variants": ["no_tools", "with_tools"]}]
MG_SCORES = [{"model_id": "mg-a", "benchmark_id": "deepswe", "variant": "default", "value": 40, "harness": "deepswe-official",
              "source_type": "independent", "source_url": "https://x", "date_observed": "2026-09-01", "notes": ""},
             {"model_id": "mg-b", "benchmark_id": "deepswe", "variant": "default", "value": 55.5, "harness": "vendor-self-report",
              "source_type": "self-reported", "source_url": "https://y", "date_observed": "2026-09-02", "notes": ""},
             {"model_id": "mg-a", "benchmark_id": "hle", "variant": "no_tools", "value": 30, "harness": "artificial-analysis",
              "source_type": "independent", "source_url": "https://z", "date_observed": "2026-08-01", "effort": "high", "notes": ""}]


class FakeHTTP2(FakeHTTP):
    """+ The Model Gap, + agent config(score 컬럼). 요청 URL을 기록한다."""

    def __call__(self, url, headers, budget=None):
        if url.startswith(d.MG_URL):
            self.calls.append(url)
            if budget is not None:
                budget["used"] += 1
            return MG_BENCH if url.endswith("benchmarks.json") else MG_SCORES
        body = super().__call__(url, headers, budget)
        if "/agent/latest-" in url:
            body = [{k if k != "rating" else "score": (v / 10000 if k == "rating" else v) for k, v in x.items()} for x in body]
        return body


class P1Sources(unittest.TestCase):
    """wiki unit 수집: arena:* 추가 cohort, Model Gap 어댑터."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self.tmp.name)
        self.cfg = config([profile("a", model_id="model-a"), profile("b", model_id="model-b")])

    def tearDown(self):
        self.tmp.cleanup()

    def test_v62_model_gap_units_and_conditions(self):
        res = d.refresh(self.cache, self.cfg, MAPPING, {"mg": {"mg-a": "model-a", "mg-b": "model-b"}}, NOW,
                        only="mg", get_json=FakeHTTP2(), env=ENV)
        self.assertEqual((res["status"], res["sources"]["mg"]["requests"]), ("ok", 2))
        snap = json.loads((self.cache / "snapshot.json").read_text("utf-8"))
        a, b = (snap["profiles"][p]["evidence"] for p in ("a", "b"))
        self.assertEqual((a["mg:deepswe/default"]["normalized"], b["mg:deepswe/default"]["normalized"]), (0.0, 1.0))
        self.assertEqual(a["mg:hle/no_tools"]["cohort_id"], "mg:hle/no_tools")  # 변형은 별도 cohort
        self.assertEqual((b["mg:deepswe/default"]["conditions"]["source_type"], a["mg:hle/no_tools"]["conditions"]["reasoning_effort"]),
                         ("self-reported", "high"))
        self.assertIsNone(a["mg:deepswe/default"]["conditions"]["agent_scaffold"])  # 평가기관 ≠ 스캐폴드
        bad = {"unknown variant": [{**MG_SCORES[0], "variant": "xhigh"}], "non-number": [{**MG_SCORES[0], "value": "40"}],
               "duplicate": [MG_SCORES[0], MG_SCORES[0]]}
        for name, scores in bad.items():
            with self.subTest(name), self.assertRaises(d.SourceError):
                d.parse_mg({"benchmarks": MG_BENCH, "scores": scores})

    def test_v62_wiki_arena_units_collected_once_with_separate_cohorts(self):
        units = {"arena:agent/overall": {"adoption": "active"}, "arena:text_style_control/math": {"adoption": "candidate"},
                 "arena:text_to_image/overall": {"adoption": "excluded"}, "mg:deepswe/default": {"adoption": "active"}}
        http = FakeHTTP2()
        res = d.refresh(self.cache, self.cfg, MAPPING, {"arena": {"arena-149": "model-a", "arena-0": "model-b"}}, NOW,
                        only="arena", get_json=http, env=ENV, index={"units": units})
        # revision + config(legacy 4 + agent 1)별 parquet 1개. text math는 legacy와 같은 config라 재요청 없음, excluded는 수집 안 함
        self.assertEqual(res["sources"]["arena"]["requests"], 1 + 5)
        self.assertFalse([u for u in http.calls if "text_to_image" in u])
        ev = json.loads((self.cache / "snapshot.json").read_text("utf-8"))["profiles"]["a"]["evidence"]
        self.assertEqual(ev["arena:agent/overall"]["conditions"]["metric"], "score")
        self.assertEqual(ev["arena:text_style_control/math"]["normalized"], ev["arena_text_math"]["normalized"])  # 모집단 이중 계산 없음
        self.assertNotEqual(ev["arena:text_style_control/math"]["cohort_id"], ev["arena_text_math"]["cohort_id"])

    def test_v62_arena_effort_from_model_name(self):
        names = {"Claude Opus 5.5 (High)": "high", "gpt-6.1-sol-max": "max", "GPT-5.4 (High, Codex Harness)": "high",
                 "claude-opus-5.5-medium": "medium", "Gemini 3 Pro": None, "gpt-oss-120b": None}
        self.assertEqual({n: d.effort_from_name(n) for n in names}, names)
        aa = {"claude-opus-5-5-high": "high", "gpt-6-1-sol-xhigh": "xhigh", "gpt-6-sol-non-reasoning": None, "gemini-4-argon": None}
        self.assertEqual({n: d.effort_from_name(n) for n in aa}, aa)  # AA slugs carry the effort as a suffix too
        rows = [{"model_name": n, "rating": 1000 + i, "rank": i, "leaderboard_publish_date": "2026-10-08"}
                for i, n in enumerate(names)]
        payload = {"revision": "r", "cohorts": {e: rows for e in d.ARENA_COHORTS}}
        got = {o["source_model"]: (o["reasoning_effort"], o["conditions"]["reasoning_effort"])
               for o in d.parse_arena(payload) if o["evidence_id"] == "arena_text"}
        self.assertEqual(got, {n: (e, e) for n, e in names.items()})  # column and conditions agree, so snapshots show the effort

    def test_v62_arena_parquet_decode(self):
        try:
            import pyarrow as pa, pyarrow.parquet as pq
        except ImportError:
            self.skipTest("pyarrow not installed")
        buf = io.BytesIO()
        pq.write_table(pa.Table.from_pylist([{"model_name": "m", "rating": 1.5, "rank": 1, "category": "overall"}]), buf)
        self.assertEqual(d._parquet_rows(buf.getvalue()), [{"model_name": "m", "rating": 1.5, "rank": 1, "category": "overall"}])
        with self.assertRaisesRegex(d.SourceError, "invalid parquet"):
            d._parquet_rows(b"not parquet")
        with self.assertRaisesRegex(d.SourceError, "no latest parquet"):  # 목록에 없는 config는 요청 없이 실패
            d._arena_rows(lambda *a: self.fail("requested"), "rev1", ["webdev/full-00000-of-00001.parquet"], "webdev")

    def test_v62_wiki_arena_unit_failure_is_isolated(self):
        def flaky(fail_config):
            http = FakeHTTP2()
            base = http.__call__
            def call(url, headers, budget=None):
                if f"/{fail_config}/latest-" in url:
                    raise d.SourceError("HTTP 500")
                return base(url, headers, budget)
            return call
        spec = {**d.ARENA_COHORTS, "arena:agent/overall": ("agent", "overall")}
        payload, _, _ = d.fetch_arena(flaky("agent"), ENV, spec)
        self.assertEqual((sorted(payload["spec"]), payload["failed"]), (sorted(d.ARENA_COHORTS), {"arena:agent/overall": "HTTP 500"}))
        self.assertEqual({o["evidence_id"] for o in d.parse_arena(payload)}, set(d.ARENA_COHORTS))
        with self.assertRaises(d.SourceError):  # legacy evidence 실패는 기존대로 source 실패 → last-good 유지
            d.fetch_arena(flaky("webdev"), ENV, spec)


def wiki_page(lifecycle, table, rows):
    body = "\n".join(f"[[{table}]]\n" + "\n".join(f"{k} = {json.dumps(v)}" if not isinstance(v, dict) else
                                                  f"{k} = {{ " + ", ".join(f"{a} = {json.dumps(x)}" for a, x in v.items()) + " }"
                                                  for k, v in row.items()) + "\n" for row in rows)
    return f"---\ntitle: >-\n    t\nlifecycle: {lifecycle}\n---\n# t\n\n## Index\n\n```toml\n{body}```\n\n## Sources\n"


def unit(uid, adoption="active", **facets):
    return {"id": uid, "desc": "d", "metric": "elo", "status": "current", "adoption": adoption,
            "facets": facets or {"task": ["coding"]}}


class P1Wiki(unittest.TestCase):
    """Wiki → index.json 컴파일 (wiki/AGENTS.md 계약). 합성 vault, 네트워크 없음."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault, self.cache = Path(self.tmp.name) / "wiki", Path(self.tmp.name) / "cache"
        self.write("AGENTS.md", "schema")
        self.write("concepts/facets/task.md", wiki_page("reviewed", "facet", [
            {"id": "coding", "desc": "d", "detect": "rule:code_block_or_code_ext", "evidence": "official"},
            {"id": "math", "desc": "d", "detect": "self", "evidence": "official"}]))
        self.write("concepts/facets/lang.md", wiki_page("draft", "facet", [
            {"id": "ko", "desc": "d", "detect": "rule:script(hangul)", "evidence": "official"}]))

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def compile(self):
        from bench_router import wiki
        return wiki.compile_wiki(self.vault)

    def test_v61_wiki_draft_pages_excluded_and_postings_active_only(self):
        self.write("entities/benchmarks/a.md", wiki_page("reviewed", "unit", [
            unit("arena:text_style_control/coding"), unit("arena:text_style_control/math", task=["math", "coding"]),
            unit("mg:deepswe/default", "candidate"), unit("hf:x/y", "excluded") | {"facets": {}}]))
        self.write("entities/benchmarks/b.md", wiki_page("draft", "unit", [unit("swe_verified_exact")]))
        idx = self.compile()
        self.assertEqual(set(idx["facets"]), {"task"})  # draft facet 페이지(lang) 제외
        self.assertEqual(set(idx["units"]), {"arena:text_style_control/coding", "arena:text_style_control/math",
                                             "mg:deepswe/default", "hf:x/y"})  # draft 벤치마크 페이지 제외
        self.assertEqual(idx["postings"], {"task:coding": ["arena:text_style_control/coding", "arena:text_style_control/math"],
                                           "task:math": ["arena:text_style_control/math"]})
        self.assertEqual(idx["units"]["mg:deepswe/default"]["page"], "entities/benchmarks/a.md")

    def test_v61_wiki_rejects_invalid_units(self):
        bad = {"unknown facet value": unit("arena:x/y", task=["painting"]),
               "draft facet page value": unit("arena:x/y", lang=["ko"]),
               "unknown id format": unit("nope"),
               "bad adoption": unit("arena:x/y", "maybe"),
               "empty facets": unit("arena:x/y") | {"facets": {}},
               "unknown key": unit("arena:x/y") | {"weight": 0.5}}
        for name, u in bad.items():
            with self.subTest(name):
                self.write("entities/benchmarks/a.md", wiki_page("reviewed", "unit", [u]))
                with self.assertRaises(r.InputError):
                    self.compile()
        with self.subTest("duplicate across pages"):
            self.write("entities/benchmarks/a.md", wiki_page("reviewed", "unit", [unit("arena:x/y")]))
            self.write("entities/benchmarks/b.md", wiki_page("reviewed", "unit", [unit("arena:x/y")]))
            with self.assertRaisesRegex(r.InputError, "duplicate unit"):
                self.compile()

    def test_v61_wiki_cli_check_and_failure_keeps_previous_index(self):
        from bench_router import cli
        self.write("entities/benchmarks/a.md", wiki_page("reviewed", "unit", [unit("arena:x/y")]))
        base = ["--cache-dir", str(self.cache), "wiki", "compile", "--vault", str(self.vault)]
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            self.assertEqual(cli.main(base + ["--check"]), 0)
        self.assertIsNone(json.loads(out.getvalue())["written"])
        self.assertFalse((self.cache / "index.json").exists())
        with mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(base), 0)
        before = (self.cache / "index.json").read_bytes()
        self.write("entities/benchmarks/a.md", wiki_page("reviewed", "unit", [unit("arena:x/y", task=["painting"])]))
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            self.assertEqual(cli.main(base), 2)
        self.assertEqual(json.loads(out.getvalue())["error"]["code"], "validation")
        self.assertEqual((self.cache / "index.json").read_bytes(), before)

    def test_v61_refresh_reports_wiki_error_without_failing(self):
        import argparse
        from bench_router import cli
        args = argparse.Namespace(config_dir=Path(self.tmp.name), cache_dir=self.cache, vault=self.vault,
                                  import_file=None, source=None, force=False)
        with mock.patch.object(cli, "_config", return_value=(None, None)), \
                mock.patch.object(d, "load_aliases", return_value={}), \
                mock.patch.object(d, "refresh", return_value={"status": "ok"}):
            self.write("entities/benchmarks/a.md", wiki_page("reviewed", "unit", [unit("arena:x/y")]))
            self.assertEqual(cli._refresh(args)["wiki_index"]["units"], 1)
            self.write("entities/benchmarks/a.md", wiki_page("reviewed", "unit", [unit("arena:x/y", task=["painting"])]))
            res = cli._refresh(args)
        self.assertEqual((res["status"], res["wiki_index"]["status"]), ("ok", "error"))
        self.assertEqual(len(json.loads((self.cache / "index.json").read_text())["units"]), 1)

    def test_v61_repo_wiki_compiles_when_reviewed(self):
        """저장소 wiki/ 내용 자체의 계약 검사: 전 페이지를 reviewed로 가정해 컴파일."""
        import shutil
        from bench_router import cli, wiki
        shutil.rmtree(self.vault)
        shutil.copytree(cli.WIKI_VAULT, self.vault)
        for p in self.vault.rglob("*.md"):
            p.write_text(p.read_text(encoding="utf-8").replace("\nlifecycle: draft\n", "\nlifecycle: reviewed\n"),
                         encoding="utf-8")
        idx = wiki.compile_wiki(self.vault)
        self.assertEqual(set(idx["facets"]), set(wiki.AXES))
        active = {u for ids in idx["postings"].values() for u in ids}
        self.assertEqual(active, {k for k, u in idx["units"].items() if u["adoption"] == "active"})
        self.assertTrue(set(d.EVIDENCE_IDS) & set(idx["units"]))


if __name__ == "__main__":
    unittest.main()
