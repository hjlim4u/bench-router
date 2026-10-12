"""작업군 비교용 과제 20개 (06 문서 "라우팅 효과 평가").

각 과제 = Orchestrator가 줄 summary/categories/prompt + 초기 파일 + hidden acceptance check.
check는 Agent 작업 디렉터리에 복사하지 않고, Agent 종료 후 하네스가 실행한다.
acceptance 기준은 실행 전에 고정한다(이 파일의 git revision이 기준).
"""
import configparser
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path


def _load(d, name):
    spec = importlib.util.spec_from_file_location(f"m_{uuid.uuid4().hex}", Path(d) / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _raises(fn, *a, exc=ValueError):
    try:
        fn(*a)
    except exc:
        return True
    except Exception:
        return False
    return False


def _hangul_ratio(text):
    letters = [c for c in text if c.isalpha()]
    return sum("가" <= c <= "힣" for c in letters) / max(1, len(letters))


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.text = [], []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def _html(path):
    p = _Tags()
    p.feed(Path(path).read_text("utf-8"))
    return p


# ---------- checks ----------

def c_pager(d):
    m = _load(d, "pager")
    items = list(range(10))
    got = [m.paginate(items, p, 3) for p in (1, 2, 3, 4, 5)]
    return got == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9], []], f"pages={got}"


def c_users(d):
    m = _load(d, "users")
    ok = m.create_user("  Kim ", 30) == {"name": "Kim", "age": 30}
    ok &= m.create_user("Lee", 0)["age"] == 0 and m.create_user("Park", 150)["age"] == 150
    bad = [("", 3), ("   ", 3), (None, 3), ("a", -1), ("a", 151), ("a", 3.5), ("a", True), ("a", "3")]
    fails = [b for b in bad if not _raises(m.create_user, *b)]
    return ok and not fails, f"not rejected={fails}"


def c_csvline(d):
    m = _load(d, "csvline")
    cases = {'a,"b,c","d""e",': ["a", "b,c", 'd"e', ""], "x": ["x"], '"",1': ["", "1"], "1,2,3": ["1", "2", "3"]}
    got = {k: m.parse_line(k) for k in cases}
    return got == cases, f"got={got}"


def c_timeout(d):
    import warnings
    m = _load(d, "settings")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        old = m.get_timeout({"timeout": 7})
        warned = any(issubclass(x.category, DeprecationWarning) for x in w)
    with warnings.catch_warnings(record=True) as w2:
        warnings.simplefilter("always")
        new = m.get_timeout({"timeout_s": 5})
        silent = not any(issubclass(x.category, DeprecationWarning) for x in w2)
    both = m.get_timeout({"timeout_s": 5, "timeout": 7})
    return (new, old, warned, silent, both, m.get_timeout({})) == (5, 7, True, True, 5, 30), \
        f"new={new} old={old} warned={warned} silent={silent} both={both}"


def _sh(d, *args):
    return subprocess.run(["bash", str(Path(d) / args[0]), *args[1:]], capture_output=True, text=True, timeout=30)


def c_bigfiles(d):
    with tempfile.TemporaryDirectory() as t:
        tp = Path(t)
        (tp / "sub dir").mkdir()
        for rel, size in (("a.bin", 3000), ("small.txt", 100), ("sub dir/b c.dat", 2049), ("sub dir/edge", 2048)):
            (tp / rel).write_bytes(b"x" * size)
        os.symlink(tp / "a.bin", tp / "link")
        r = _sh(d, "bigfiles.sh", t, "2")
    got = r.stdout.splitlines()
    return r.returncode == 0 and got == ["a.bin", "sub dir/b c.dat"], f"rc={r.returncode} out={got} err={r.stderr[-200:]}"


def c_rotate(d):
    import time
    with tempfile.TemporaryDirectory() as t:
        tp = Path(t)
        now = time.time()
        for i in range(5):
            f = tp / f"app{i}.log"
            f.write_text("x")
            os.utime(f, (now - (5 - i) * 100, now - (5 - i) * 100))  # app4 최신
        (tp / "keep.txt").write_text("x")
        dry = _sh(d, "rotate.sh", "--dry-run", t, "2")
        after_dry = sorted(p.name for p in tp.iterdir())
        real = _sh(d, "rotate.sh", t, "2")
        after = sorted(p.name for p in tp.iterdir())
    ok = (dry.returncode == 0 and len(after_dry) == 6 and all(f"app{i}.log" in dry.stdout for i in range(3))
          and real.returncode == 0 and after == ["app3.log", "app4.log", "keep.txt"])
    return ok, f"dry_rc={dry.returncode} after_dry={len(after_dry)} after={after}"


def c_units(d):
    s = configparser.ConfigParser(strict=False, interpolation=None)
    s.optionxform = str
    s.read(Path(d) / "bench-refresh.service")
    tm = configparser.ConfigParser(strict=False, interpolation=None)
    tm.optionxform = str
    tm.read(Path(d) / "bench-refresh.timer")
    ok = (s.get("Service", "Type", fallback="") == "oneshot"
          and s.get("Service", "ExecStart", fallback="").strip() == "/usr/bin/python3 -m bench_router.cli refresh"
          and s.get("Service", "EnvironmentFile", fallback="").strip() == "%h/.config/bench-router/env"
          and tm.get("Timer", "OnCalendar", fallback="").strip() == "*-*-* 06:00:00"
          and tm.get("Timer", "Persistent", fallback="").strip().lower() == "true"
          and tm.get("Install", "WantedBy", fallback="").strip() == "timers.target")
    return ok, f"service={dict(s.items('Service')) if s.has_section('Service') else None} timer={dict(tm.items('Timer')) if tm.has_section('Timer') else None}"


def c_roman(d):
    m = _load(d, "roman")
    rt = all(m.from_roman(m.to_roman(n)) == n for n in range(1, 4000))
    known = m.to_roman(1994) == "MCMXCIV" and m.to_roman(3999) == "MMMCMXCIX"
    bad = [f for f in (lambda: m.to_roman(0), lambda: m.to_roman(4000), lambda: m.from_roman("IIII"),
                       lambda: m.from_roman("IC"), lambda: m.from_roman(""), lambda: m.from_roman("VX"))
           if not _raises(f)]
    return rt and known and not bad, f"roundtrip={rt} known={known} unrejected={len(bad)}"


def c_lru(d):
    m = _load(d, "lru")
    c = m.LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    first = c.get("a")
    c.put("c", 3)  # b 제거
    c.put("a", 10)  # 갱신, 크기 유지
    ok = (first, c.get("b"), c.get("b", "zz"), c.get("a"), c.get("c"), len(c)) == (1, None, "zz", 10, 3, 2)
    return ok and _raises(m.LRUCache, 0), f"state={(first, c.get('b'), c.get('a'), c.get('c'), len(c))}"


def c_merge(d):
    m = _load(d, "intervals")
    cases = [([(1, 3), (2, 6), (8, 10), (15, 18)], [(1, 6), (8, 10), (15, 18)]), ([(1, 2), (2, 3)], [(1, 3)]),
             ([(5, 7), (1, 2)], [(1, 2), (5, 7)]), ([], []), ([(1, 10), (2, 3)], [(1, 10)])]
    got = [[tuple(x) for x in m.merge(i)] for i, _ in cases]
    return got == [o for _, o in cases] and _raises(m.merge, [(3, 1)]), f"got={got}"


def c_form(d):
    p = _html(Path(d) / "index.html")
    by_id = {a.get("id"): (t, a) for t, a in p.tags if a.get("id")}
    labels = {a.get("for") for t, a in p.tags if t == "label"}
    email, pw, form = by_id.get("email"), by_id.get("password"), by_id.get("signup")
    ok = (form and form[0] == "form" and email and email[1].get("type") == "email" and "required" in email[1]
          and pw and pw[1].get("type") == "password" and pw[1].get("minlength") == "8" and "required" in pw[1]
          and {"email", "password"} <= labels
          and any(t == "button" and a.get("type") == "submit" for t, a in p.tags))
    return bool(ok), f"ids={sorted(k for k in by_id)} labels={labels}"


def c_table(d):
    p = _html(Path(d) / "table.html")
    tags = [t for t, _ in p.tags]
    ths = [a for t, a in p.tags if t == "th"]
    text = " ".join(p.text)
    ok = ("caption" in tags and len(ths) >= 3 and all(a.get("scope") == "col" for a in ths[:3])
          and tags.count("tr") >= 4 and all(w in text for w in ("Keyboard", "Mouse", "Monitor", "49000", "25000", "320000")))
    return ok, f"tags={tags.count('tr')} tr, th={len(ths)}"


def c_math1(d):
    a = json.loads((Path(d) / "answer.json").read_text("utf-8"))
    return (a.get("a"), a.get("b")) == (249, 76127), f"answer={a}"


def c_math2(d):
    a = json.loads((Path(d) / "answer.json").read_text("utf-8"))
    try:
        ok = Fraction(str(a.get("p"))) == Fraction(5, 12) and Fraction(str(a.get("e"))) == 6
    except (ValueError, ZeroDivisionError):
        ok = False
    return ok, f"answer={a}"


SALES = """region,product,qty,price
north,widget,3,9.50
south,gadget,1,120.00
north,gadget,2,120.00
east,widget,10,9.50
south,widget,4,9.50
east,doohickey,2,45.25
"""


def c_sales(d):
    s = json.loads((Path(d) / "summary.json").read_text("utf-8"))
    want = {"north": 268.5, "south": 158.0, "east": 185.5}
    tot = s.get("totals", {})
    ok = set(tot) == set(want) and all(abs(float(tot[k]) - v) < 0.01 for k, v in want.items()) and s.get("top_product") == "gadget"
    return ok, f"summary={s}"


LOG = "\n".join([
    "2026-10-01T10:00:00 INFO start",
    "2026-10-01T10:00:01 ERROR db timeout",
    "2026-10-01T10:00:02 WARN slow request /api/a",
    "2026-10-01T10:00:03 ERROR db timeout",
    "2026-10-01T10:00:04 ERROR cache miss storm",
    "2026-10-01T10:00:05 INFO ok",
    "2026-10-01T10:00:06 ERROR db timeout",
    "2026-10-01T10:00:07 ERROR auth failed",
    "2026-10-01T10:00:08 ERROR cache miss storm",
    "2026-10-01T10:00:09 WARN slow request /api/b",
]) + "\n"


def c_logs(d):
    r = json.loads((Path(d) / "report.json").read_text("utf-8"))
    ok = r.get("counts") == {"INFO": 2, "WARN": 2, "ERROR": 6} and r.get("top_errors") == ["db timeout", "cache miss storm", "auth failed"]
    return ok, f"report={r}"


def c_release(d):
    t = (Path(d) / "RELEASE.md").read_text("utf-8")
    heads = all(h in t for h in ("# v2.3.0 릴리스 노트", "## 새 기능", "## 버그 수정", "## 호환성"))
    terms = [x for x in ("--dry-run", "#412", "#418", "Python 3.11", "collect") if x not in t]
    return heads and not terms and _hangul_ratio(t) > 0.5 and len(t) <= 1500, \
        f"heads={heads} missing={terms} hangul={_hangul_ratio(t):.2f} len={len(t)}"


def c_email(d):
    t = (Path(d) / "email.txt").read_text("utf-8")
    need = [x for x in ("A-1029", "10월 20일") if x not in t]
    apology = any(x in t for x in ("죄송", "사과"))
    return not need and apology and t.rstrip().endswith("감사합니다.") and len(t) <= 600 and _hangul_ratio(t) > 0.7, \
        f"missing={need} apology={apology} end={t.rstrip()[-8:]!r} len={len(t)}"


def c_checklist(d):
    lines = [l for l in (Path(d) / "checklist.md").read_text("utf-8").splitlines() if l.startswith("- [ ] ")]
    owners = ["(민지)", "(준호)", "(서연)", "(태현)"]
    return len(lines) == 4 and all(any(o in l for l in lines) for o in owners), f"items={lines}"


README_EN = """# Quick start

Install the tool and run your first job.

## Install

```bash
pip install example-tool==1.4.2
```

## Run

Use the [user guide](https://example.com/guide) for options.

```bash
example-tool run --config ./job.toml
```
"""


def c_translate(d):
    t = (Path(d) / "README_ko.md").read_text("utf-8")
    blocks = re.findall(r"```.*?```", README_EN, re.S)
    ok = (all(b in t for b in blocks) and "https://example.com/guide" in t
          and len(re.findall(r"^#{1,6} ", t, re.M)) == len(re.findall(r"^#{1,6} ", README_EN, re.M))
          and _hangul_ratio(re.sub(r"```.*?```", "", t, flags=re.S)) > 0.5)
    return ok, f"blocks_ok={all(b in t for b in blocks)} heads={len(re.findall(r'^#{1,6} ', t, re.M))}"


# ---------- 과제 ----------
# (id, category, summary, prompt, files, check)
TASKS = [
    ("pager", "coding_repo", "Fix an off-by-one bug in pager.paginate (1-indexed pages).",
     "pager.py의 paginate(items, page, per_page)는 1부터 시작하는 페이지 번호를 받아야 하는데 첫 페이지 항목이 빠집니다. 버그를 고치세요. 시그니처는 유지하고, 범위를 벗어난 페이지는 빈 리스트를 반환하게 하세요.",
     {"pager.py": 'def paginate(items, page, per_page):\n    """Return the items on the 1-indexed page."""\n    start = page * per_page\n    return items[start:start + per_page]\n'}, c_pager),
    ("users", "coding_repo", "Add input validation to users.create_user.",
     "users.py의 create_user(name, age)에 입력 검증을 추가하세요. name은 앞뒤 공백을 제거한 뒤 비어 있지 않은 문자열이어야 하고, age는 0 이상 150 이하의 int여야 합니다(bool·float·문자열 불가). 위반 시 ValueError를 내세요. 반환 형식 {\"name\", \"age\"}은 유지하고 name은 공백 제거값으로 저장하세요.",
     {"users.py": 'def create_user(name, age):\n    return {"name": name, "age": age}\n'}, c_users),
    ("csvline", "coding_repo", "Make csvline.parse_line handle RFC 4180 quoted fields.",
     "csvline.py의 parse_line(line)은 단순히 쉼표로 나눕니다. 큰따옴표로 감싼 필드(내부 쉼표 포함)와 이스케이프된 따옴표(\"\")를 RFC 4180대로 처리하도록 고치세요. 표준 라이브러리 csv를 써도 됩니다. 문자열 리스트를 반환하세요.",
     {"csvline.py": 'def parse_line(line):\n    return line.split(",")\n'}, c_csvline),
    ("timeout", "coding_repo", "Rename config key timeout to timeout_s with a deprecation path.",
     "settings.py의 get_timeout(cfg)가 읽는 설정 키를 \"timeout\"에서 \"timeout_s\"로 바꾸세요. 기존 \"timeout\" 키만 있으면 그 값을 쓰되 DeprecationWarning을 내고, 둘 다 있으면 timeout_s가 우선입니다(이때 경고 불필요). 둘 다 없으면 기본값 30입니다.",
     {"settings.py": 'def get_timeout(cfg):\n    return cfg.get("timeout", 30)\n'}, c_timeout),
    ("bigfiles", "terminal_ops", "Write a bash script listing files larger than N KiB.",
     "bigfiles.sh를 작성하세요. 사용법: bash bigfiles.sh DIR SIZE_KB. DIR 아래(하위 디렉터리 포함)의 일반 파일 중 크기가 SIZE_KB KiB(1024바이트 단위)를 초과하는 파일만, DIR 기준 상대 경로로 한 줄에 하나씩 사전순 출력하세요. 심볼릭 링크는 제외하고, 공백이 들어간 경로도 처리해야 합니다.",
     {}, c_bigfiles),
    ("rotate", "terminal_ops", "Write a log rotation bash script keeping the newest N logs.",
     "rotate.sh를 작성하세요. 사용법: bash rotate.sh [--dry-run] DIR N. DIR 바로 아래의 *.log 파일 중 수정 시각 기준 최신 N개만 남기고 나머지를 삭제합니다. --dry-run이면 삭제하지 않고 삭제할 파일 이름만 한 줄씩 출력합니다. *.log가 아닌 파일은 건드리지 마세요.",
     {}, c_rotate),
    ("units", "terminal_ops", "Write a systemd user service and timer for a daily refresh.",
     "systemd user unit 두 개를 작성하세요. bench-refresh.service: Type=oneshot, EnvironmentFile=%h/.config/bench-router/env, ExecStart=/usr/bin/python3 -m bench_router.cli refresh. bench-refresh.timer: 매일 06:00(OnCalendar=*-*-* 06:00:00), Persistent=true, [Install] WantedBy=timers.target. 설치나 활성화는 하지 말고 파일만 작성하세요.",
     {}, c_units),
    ("roman", "code_gen", "Implement Roman numeral conversion in both directions.",
     "roman.py에 to_roman(n)과 from_roman(s)를 구현하세요. 범위는 1~3999이고, 범위 밖 정수나 표준 표기가 아닌 문자열(예: IIII, IC, VX, 빈 문자열)은 ValueError입니다.",
     {}, c_roman),
    ("lru", "code_gen", "Implement an LRU cache class.",
     "lru.py에 LRUCache(capacity) 클래스를 구현하세요. get(key, default=None), put(key, value), len()을 지원합니다. 용량을 넘으면 가장 오래 사용하지 않은 항목을 제거하고, get과 put 모두 사용으로 칩니다. capacity가 1 미만이면 ValueError입니다.",
     {}, c_lru),
    ("intervals", "code_gen", "Implement interval merging.",
     "intervals.py에 merge(intervals)를 구현하세요. (start, end) 쌍의 리스트를 받아 겹치거나 맞닿은 구간을 합친 뒤 시작값 순으로 반환합니다. start > end인 구간이 있으면 ValueError입니다.",
     {}, c_merge),
    ("form", "webdev", "Build an accessible signup form in index.html.",
     "index.html에 id가 signup인 회원가입 form을 만드세요. 이메일 입력(id=email, type=email, required)과 비밀번호 입력(id=password, type=password, minlength=8, required)이 있어야 하고, 각각 for 속성으로 연결된 label과 type=submit 버튼이 필요합니다. 외부 리소스는 쓰지 마세요.",
     {}, c_form),
    ("table", "webdev", "Build an accessible product table in table.html.",
     "table.html에 상품 표를 만드세요. caption이 있어야 하고, 열 머리글 Name, Price, Qty는 th scope=\"col\"로 작성합니다. 행: Keyboard 49000 2 / Mouse 25000 5 / Monitor 320000 1. 외부 리소스는 쓰지 마세요.",
     {}, c_table),
    ("math1", "math_reasoning", "Answer two number theory questions in answer.json.",
     "다음 두 질문의 답을 answer.json에 정수로 쓰세요: {\"a\": 1000!의 끝자리 0의 개수, \"b\": 1000 미만 소수의 합}.",
     {}, c_math1),
    ("math2", "math_reasoning", "Answer two probability questions in answer.json.",
     "다음 두 질문의 답을 answer.json에 기약분수 문자열로 쓰세요: {\"p\": 공정한 주사위 두 개의 합이 소수일 확률, \"e\": 공정한 주사위를 6이 나올 때까지 던질 때 던지는 횟수의 기댓값}. 예: \"1/3\", \"6\".",
     {}, c_math2),
    ("sales", "analysis", "Summarize regional revenue from sales.csv.",
     "sales.csv를 분석해 summary.json을 작성하세요. totals: 지역별 매출 합계(qty×price, 숫자), top_product: 전체 매출이 가장 큰 상품명.",
     {"sales.csv": SALES}, c_sales),
    ("logs", "analysis", "Summarize log levels and top errors from app.log.",
     "app.log를 분석해 report.json을 작성하세요. counts: 레벨별(INFO/WARN/ERROR) 줄 수, top_errors: ERROR 메시지(타임스탬프·레벨 제외)를 빈도 내림차순으로 정렬한 상위 3개 리스트(동률이면 먼저 나온 순).",
     {"app.log": LOG}, c_logs),
    ("release", "writing", "Write Korean release notes from an English changelog.",
     "아래 변경 내역으로 RELEASE.md에 한국어 릴리스 노트를 쓰세요. 첫 줄은 \"# v2.3.0 릴리스 노트\"이고, \"## 새 기능\", \"## 버그 수정\", \"## 호환성\" 섹션이 있어야 합니다. 식별자(옵션명·이슈 번호·버전)는 원문 그대로 두고, 전체 1500자 이내로 쓰세요.\n\n- Added --dry-run to route (no side effects)\n- Added collect command for delayed result retrieval\n- Fixed duplicate prompt on retry (#412)\n- Fixed stale snapshot not falling back to last-good (#418)\n- Requires Python 3.11 or newer",
     {}, c_release),
    ("email", "writing", "Write a polite Korean refund reply email.",
     "고객에게 보낼 환불 안내 답장을 email.txt에 한국어로 쓰세요. 주문번호 A-1029의 배송 지연을 사과하고, 환불은 10월 20일까지 처리된다고 안내합니다. 600자 이내로 쓰고 마지막 문장은 \"감사합니다.\"로 끝내세요.",
     {}, c_email),
    ("checklist", "general", "Extract action items from meeting notes into a checklist.",
     "아래 회의록에서 실행 항목만 골라 checklist.md에 \"- [ ] 할 일 (담당자)\" 형식으로 한 줄씩 쓰세요. 실행 항목이 아닌 내용은 넣지 마세요.\n\n회의록: 지난 분기 지표는 목표 대비 5% 높았다. 민지는 금요일까지 대시보드 권한을 정리한다. 배포 일정은 그대로 유지하기로 했다. 준호가 로그 보존 기간 초안을 작성한다. 서연은 고객 인터뷰 3건을 다음 주에 잡는다. 점심 메뉴는 따로 정하기로 했다. 태현이 장애 회고 문서를 공유한다.",
     {}, c_checklist),
    ("translate", "general", "Translate README_en.md to Korean preserving markdown structure.",
     "README_en.md를 한국어로 번역해 README_ko.md로 저장하세요. 제목 개수와 수준, 링크 URL, 코드 블록 내용은 그대로 유지합니다.",
     {"README_en.md": README_EN}, c_translate),
]


def run_check(task_id, d):
    fn = next(t[5] for t in TASKS if t[0] == task_id)
    try:
        ok, detail = fn(d)
        return bool(ok), detail
    except Exception as e:  # 파일 누락·import 실패 등 = 불합격
        return False, f"{type(e).__name__}: {e}"


def materialize(task, d):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    for name, body in task[4].items():
        (d / name).write_text(body, "utf-8")
    return d


if __name__ == "__main__":
    # 자체 검사: 초기 상태는 불합격, 참조 정답(eval/reference.py)은 합격이어야 check를 믿을 수 있다
    sys.path.insert(0, str(Path(__file__).parent))
    from reference import SOLUTIONS
    assert len({t[0] for t in TASKS}) == 20 and set(SOLUTIONS) == {t[0] for t in TASKS}
    with tempfile.TemporaryDirectory() as root:
        for t in TASKS:
            d = materialize(t, Path(root) / "init" / t[0])
            ok, detail = run_check(t[0], d)
            assert not ok, ("initial state passes", t[0], detail)
            d = materialize(t, Path(root) / "ref" / t[0])
            for name, body in SOLUTIONS[t[0]].items():
                (d / name).write_text(body, "utf-8")
            ok, detail = run_check(t[0], d)
            assert ok, ("reference fails", t[0], detail)
    print("workset self-check ok: 20 tasks fail initially and pass with reference solutions")
