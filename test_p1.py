"""P1 검증 V11–V18 (06 문서). source 응답은 합성 fixture, 네트워크 없음.
실행: python3 -m unittest -v test_p1"""
import io
import json
import os
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
            return {"sha": "rev1"}
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        offset = int(q["offset"][0])
        rows = [{"row": {"model_name": f"arena-{i}", "rating": 1000 + i, "category": "x",
                         "leaderboard_publish_date": "2026-10-08T00:00:00"}} for i in range(150)]
        return {"num_rows_total": 150, "rows": rows[offset:offset + 100]}


def tb_import(**kw):
    doc = {"schema_version": "1.0", "evidence_id": "terminal_exact", "source_url": "https://www.tbench.ai/",
           "attribution": "Terminal-Bench", "published_at": "2026-10-01",
           "benchmark": {"suite": "terminal-bench", "version": "4.0", "subset": "core", "metric": "resolved_rate",
                         "direction": "higher"},
           "rows": [{"model_id": "model-a", "harness_id": "codex-cli", "reasoning_effort": "high", "raw": 0.6},
                    {"model_id": "model-z", "harness_id": "other", "reasoning_effort": "high", "raw": 0.4}]}
    doc.update(kw)
    return doc


class P1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self.tmp.name)
        self.ps = [profile("a", model_id="model-a", reasoning_effort="high"), profile("dflt")]
        self.cfg = config(self.ps, default="dflt")
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
        self.assertEqual(self.snap()["unmatched"]["aa"], ["m-b", "m-c"])

    def test_v11_arena_paging_and_schema(self):
        self.aliases = {"arena": {"arena-149": "model-a"}}
        http = FakeHTTP()
        res = self.refresh(http, only="arena")
        self.assertEqual(res["sources"]["arena"]["requests"], 1 + 2 * len(d.ARENA_COHORTS))  # revision + 150행/100
        ev = self.snap()["profiles"]["a"]["evidence"]
        self.assertEqual(sorted(ev), sorted(d.ARENA_COHORTS))
        self.assertEqual((ev["arena_text_math"]["normalized"], ev["arena_text_math"]["published_at"]), (1.0, "2026-10-08"))
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
            d.validate_import(tb_import(benchmark={"suite": "terminal-bench", "version": "2.0", "subset": "core",
                                                   "metric": "resolved_rate", "direction": "higher"}), "tb")
        with self.assertRaises(r.InputError):
            d.validate_import(tb_import(published_at=None), "tb")  # 날짜 없는 수동 데이터 거부
        with self.assertRaises(r.InputError):
            d.validate_import(tb_import(), "swe")
        d.refresh(self.cache, self.cfg, MAPPING, self.aliases, NOW, only="tb",
                  import_doc=d.validate_import(tb_import(), "tb"), env=ENV)
        ev = self.snap()["profiles"]["a"]["evidence"]["terminal_exact"]
        self.assertEqual((ev["scope"], ev["normalized"]), ("exact_profile", 1.0))
        # effort unknown 프로필은 exact 매칭 안 됨
        self.cfg = config([profile("a", model_id="model-a"), profile("dflt")], default="dflt")
        self.refresh(force=True, now=NOW + timedelta(minutes=1))
        self.assertNotIn("terminal_exact", self.snap()["profiles"]["a"]["evidence"])

    def test_end_to_end_refresh_then_route(self):
        self.refresh()
        d.refresh(self.cache, self.cfg, MAPPING, self.aliases, NOW, only="tb",
                  import_doc=d.validate_import(tb_import(), "tb"), env=ENV)
        snap, warnings = r.load_snapshot(self.cache)
        with tempfile.TemporaryDirectory() as cwd:
            t = r.validate_task({"schema_version": "1.0", "task_id": "e2e", "round": 1, "summary": "fix the deploy",
                                 "prompt": "p", "cwd": cwd, "categories": {"terminal_ops": 1},
                                 "category_confidence": 0.9})
            res = r.route(t, self.cfg, MAPPING, snap, warnings, NOW)
        self.assertEqual((res["selected"]["profile"], res["selection_mode"]), ("a", "benchmark_score"))
        a = res["candidates"][0]
        self.assertEqual((a["coverage"], a["exact_evidence_weight"]), (1.0, 0.7))
        self.assertEqual(d.status(self.cache, NOW, r.config_hash(self.cfg, MAPPING))["snapshot"]["config_matches"], True)


if __name__ == "__main__":
    unittest.main()
