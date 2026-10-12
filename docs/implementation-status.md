# bench-router 구현 상태

갱신: 2026-10-12 · 런타임: WSL2 Ubuntu (Python 3.14.4), 커널 6.6.87.2-microsoft-standard-WSL2

## 완료
### P0 — 오프라인 계약·합성 라우팅
- `bench_router/routing.py`: task/profiles/categories/snapshot 검증, L0/L1/general 분류, 하드 제약, percentile, coverage/Q/S, near-tie, default/fallback, stale/max_stale, fingerprint 불일치(stale_config).
- `bench_router/cli.py`: `route --dry-run`, `explain`. live `route`는 exit 2(P2 미구현).
- `bench_router/categories.toml`: 03 문서의 evidence 매핑(P 정책, policy_version 1.0).

### P1 — 데이터·운영 캐시
- `bench_router/data.py`: SQLite(user_version=1; sources/snapshots/observations), AA Free pagination adapter, Arena adapter, TB/SWE 수동 import, fcntl refresh lock, bounded HTTP, 소스별 last-good, 원자 게시 + last-good 승격 + 30일 재현본, 소스별 payload 3개 보관.
- CLI: `refresh [--source ID] [--force] [--import FILE]`, `status`.
- route는 `data`/`urllib.request`를 import하지 않는다(test_v17에서 확인).

## 재현
```bash
cd /mnt/d/Projects/bench-router-handoff
python3 -m unittest test_p0 test_p1          # 21 tests
BR="python3 -m bench_router.cli --config-dir CFG --cache-dir CACHE"
$BR refresh            # aa, arena (TTL 내면 skip; --force)
$BR refresh --source tb --import tb.json
$BR status
$BR route --task task.json --dry-run
$BR explain --task task.json
```
설정 디렉터리(기본 `~/.config/bench-router`): `profiles.toml`(필수), `aliases.toml`(선택), `categories.toml`(선택, 없으면 내장본).

## 검증 결과
- offline: P0+P1 21/21 통과 (WSL). P0만 Windows Python 3.13에서도 통과.
- mutation: near_tie_epsilon/missing_penalty/coverage_threshold 변경 시 P0 테스트 실패 확인.
- **Arena live (E2, 2026-10-12)**: 공개 API로 refresh 성공. 요청 17회, revision `e16f9023298691b4596eca61b4e31161dff31200`, cohort N = text_style_control/overall 414, text_style_control/math 400, webdev/overall 141, document_style_control/overall 44 (publish 2026-09-13), vision_style_control/overall 165. datasets-server read timeout 2회는 재시도로 복구됨. 두 번째 실행은 TTL skip(0.1s).
- **AA live: 미검증** — `ARTIFICIAL_ANALYSIS_API_KEY` 없음. 문서(E1) 스키마로 fixture만 통과. 키가 없으면 refresh는 aa 실패로 exit 16(정상 동작, Arena last-good 유지).
- herdr/Agent: 미실행.

## 실측으로 확인된 사실 (E1 → E2)
- Arena는 parquet이지만 HF datasets-server `/filter` JSON(100행/요청)으로 같은 행을 받음 → pyarrow 불필요. 컬럼: model_name, organization, license, rating, rating_lower/upper, variance, vote_count, rank, category, leaderboard_publish_date. license CC BY 4.0.
- text subset에 `math` category 존재(→ `arena_text_math` 사용 가능). webdev 카테고리: overall/webdev/webdev-html/webdev-react/image_to_webdev.
- **원본에 같은 model_name의 별개 항목 존재**(webdev/overall `gpt-5.3-codex (codex-harness)`, rank 86/101). 처리: 모집단 유지, `name#rank=N`으로 구분해 이름만으로 매칭 안 됨.
- Windows Python에서는 HF TLS 검증 실패(사내 인증서 추정). WSL에서는 정상.

## P1에서 정한 것 (문서에 없던 세부)
- evidence ↔ cohort: `aa_intelligence`/`aa_coding` = AA Free 해당 index(metric_version = intelligence_index_version; coding은 별도 버전 없음). `arena_text`=text_style_control/overall, `arena_text_math`=text_style_control/math, `arena_webdev`=webdev/overall, `arena_document`=document_style_control/overall, `arena_vision`=vision_style_control/overall. 바꾸면 `data.ARENA_COHORTS`와 policy version.
- exact pin: `terminal_exact`=terminal-bench 4.0, `swe_verified_exact`=swe-bench verified. 다른 버전 import는 거부.
- 수동 import 형식: `{schema_version, evidence_id, source_url, attribution, published_at|evaluated_at, benchmark{suite,version,subset,metric,direction[,scoring_version]}, rows[{model_id, harness_id, reasoning_effort, raw}]}`. model_id는 canonical(alias 미적용). exact 매칭은 model_id+harness_id+reasoning_effort 일치, effort "unknown"이면 불가.
- alias는 snapshot 빌드 시 적용(alias 변경은 재수집 없이 다음 refresh에 반영). 같은 canonical로 2개 이상 매칭되면 evidence 없음 + `ambiguous` 보고.
- conditional GET(304) 미구현 — AA/HF 문서에 ETag 언급 없음. payload hash 동일 시 `unchanged`(last_success_at만 갱신)로 대체.
- refresh lock 사용 중 → exit 14(`conflict`).
- source 수준 published_at: Arena는 cohort마다 날짜가 달라 source에는 null, evidence별 published_at에 기록.

## 미완료
- AA live 확인(키 필요).
- OS timer 미설치. 예(systemd user, WSL에서 systemd 활성 필요):
  ```ini
  # ~/.config/systemd/user/bench-router-refresh.service
  [Service]
  Type=oneshot
  WorkingDirectory=/mnt/d/Projects/bench-router-handoff
  EnvironmentFile=%h/.config/bench-router/env   # ARTIFICIAL_ANALYSIS_API_KEY=... (chmod 600)
  ExecStart=/usr/bin/python3 -m bench_router.cli refresh
  # ~/.config/systemd/user/bench-router-refresh.timer
  [Timer]
  OnCalendar=*-*-* 06:00:00 Asia/Seoul
  Persistent=true
  [Install]
  WantedBy=timers.target
  ```
- WSL 기본 사용자 계정 미생성(현재 root로 실행). `wsl -d Ubuntu`로 한 번 실행해 생성 권장.
- JSON Schema 파일(task/output): 런타임 validator가 계약을 강제하므로 생략.
- P2: herdr 연결 전체. herdr 미설치.

## 다음 한 가지 작업
herdr 설치 확인(`herdr --version`, `herdr api schema --json`) → P2 adapter fixture(V19–V29)부터.

## 사용자에게 필요한 정보
- 실제 사용할 프로필(CLI/모델 ID/reasoning/cost tier/context/capability)과 그에 맞는 aliases.
- AA API 키(환경변수로만).
- herdr 설치 여부/버전.
