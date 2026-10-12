"""참조 정답. check 자체의 정확성 검증용(Agent에게 제공하지 않음)."""

SOLUTIONS = {
    "pager": {"pager.py": '''def paginate(items, page, per_page):
    start = (page - 1) * per_page
    return items[start:start + per_page] if page >= 1 else []
'''},
    "users": {"users.py": '''def create_user(name, age):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name")
    if type(age) is not int or not 0 <= age <= 150:
        raise ValueError("age")
    return {"name": name.strip(), "age": age}
'''},
    "csvline": {"csvline.py": '''import csv

def parse_line(line):
    return next(csv.reader([line]))
'''},
    "timeout": {"settings.py": '''import warnings

def get_timeout(cfg):
    if "timeout_s" in cfg:
        return cfg["timeout_s"]
    if "timeout" in cfg:
        warnings.warn("timeout is deprecated; use timeout_s", DeprecationWarning, stacklevel=2)
        return cfg["timeout"]
    return 30
'''},
    "bigfiles": {"bigfiles.sh": '''#!/usr/bin/env bash
set -euo pipefail
cd "$1"
find . -type f -size +"$2"k -printf '%P\\n' | LC_ALL=C sort
'''},
    "rotate": {"rotate.sh": '''#!/usr/bin/env bash
set -euo pipefail
dry=0
if [ "$1" = "--dry-run" ]; then dry=1; shift; fi
dir=$1 keep=$2
ls -1t "$dir"/*.log 2>/dev/null | tail -n +$((keep + 1)) | while IFS= read -r f; do
  if [ $dry = 1 ]; then basename "$f"; else rm -- "$f"; fi
done
'''},
    "units": {
        "bench-refresh.service": "[Unit]\nDescription=refresh\n\n[Service]\nType=oneshot\nEnvironmentFile=%h/.config/bench-router/env\nExecStart=/usr/bin/python3 -m bench_router.cli refresh\n",
        "bench-refresh.timer": "[Unit]\nDescription=daily\n\n[Timer]\nOnCalendar=*-*-* 06:00:00\nPersistent=true\n\n[Install]\nWantedBy=timers.target\n"},
    "roman": {"roman.py": '''import re
V = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
     (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]

def to_roman(n):
    if type(n) is not int or not 1 <= n <= 3999:
        raise ValueError(n)
    out = ""
    for v, s in V:
        while n >= v:
            out, n = out + s, n - v
    return out

def from_roman(s):
    if not isinstance(s, str) or not re.fullmatch(r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})", s) or not s:
        raise ValueError(s)
    n, i = 0, 0
    for v, sym in V:
        while s.startswith(sym, i):
            n, i = n + v, i + len(sym)
    return n
'''},
    "lru": {"lru.py": '''from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError(capacity)
        self.cap, self.d = capacity, OrderedDict()

    def get(self, key, default=None):
        if key not in self.d:
            return default
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        self.d[key] = value
        self.d.move_to_end(key)
        if len(self.d) > self.cap:
            self.d.popitem(last=False)

    def __len__(self):
        return len(self.d)
'''},
    "intervals": {"intervals.py": '''def merge(intervals):
    if any(s > e for s, e in intervals):
        raise ValueError("start > end")
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out
'''},
    "form": {"index.html": '''<!doctype html><html lang="ko"><body>
<form id="signup">
<label for="email">이메일</label><input id="email" type="email" required>
<label for="password">비밀번호</label><input id="password" type="password" minlength="8" required>
<button type="submit">가입</button>
</form></body></html>
'''},
    "table": {"table.html": '''<!doctype html><html><body><table>
<caption>상품</caption>
<thead><tr><th scope="col">Name</th><th scope="col">Price</th><th scope="col">Qty</th></tr></thead>
<tbody><tr><td>Keyboard</td><td>49000</td><td>2</td></tr><tr><td>Mouse</td><td>25000</td><td>5</td></tr>
<tr><td>Monitor</td><td>320000</td><td>1</td></tr></tbody></table></body></html>
'''},
    "math1": {"answer.json": '{"a": 249, "b": 76127}\n'},
    "math2": {"answer.json": '{"p": "5/12", "e": "6"}\n'},
    "sales": {"summary.json": '{"totals": {"north": 268.5, "south": 158.0, "east": 185.5}, "top_product": "gadget"}\n'},
    "logs": {"report.json": '{"counts": {"INFO": 2, "WARN": 2, "ERROR": 6}, "top_errors": ["db timeout", "cache miss storm", "auth failed"]}\n'},
    "release": {"RELEASE.md": '''# v2.3.0 릴리스 노트

## 새 기능
- route에 부작용 없는 `--dry-run` 옵션을 추가했습니다.
- 지연된 결과를 회수하는 `collect` 명령을 추가했습니다.

## 버그 수정
- 재시도 시 프롬프트가 중복 전송되던 문제를 고쳤습니다 (#412).
- 오래된 스냅샷이 마지막 정상본으로 돌아가지 않던 문제를 고쳤습니다 (#418).

## 호환성
- Python 3.11 이상이 필요합니다.
'''},
    "email": {"email.txt": "안녕하세요, 고객님.\n주문번호 A-1029의 배송이 지연되어 불편을 드린 점 진심으로 사과드립니다.\n요청하신 환불은 10월 20일까지 처리될 예정입니다.\n추가로 궁금하신 점이 있으면 언제든 회신 부탁드립니다.\n감사합니다.\n"},
    "checklist": {"checklist.md": "- [ ] 금요일까지 대시보드 권한 정리 (민지)\n- [ ] 로그 보존 기간 초안 작성 (준호)\n- [ ] 다음 주 고객 인터뷰 3건 일정 잡기 (서연)\n- [ ] 장애 회고 문서 공유 (태현)\n"},
    "translate": {"README_ko.md": '''# 빠른 시작

도구를 설치하고 첫 작업을 실행합니다.

## 설치

```bash
pip install example-tool==1.4.2
```

## 실행

옵션은 [사용자 가이드](https://example.com/guide)를 참고하세요.

```bash
example-tool run --config ./job.toml
```
'''},
}
