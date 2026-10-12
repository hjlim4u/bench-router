# bench-router 구현 상태

갱신: 2026-10-12 · 런타임: WSL2 Ubuntu (Python 3.14.4), 커널 6.6.87.2-microsoft-standard-WSL2

## 완료
### P0 — 오프라인 계약·합성 라우팅
- `bench_router/routing.py`: task/profiles/categories/snapshot 검증, L0/L1/general 분류, 하드 제약, percentile, coverage/Q/S, near-tie, default/fallback, stale/max_stale, fingerprint 불일치(stale_config).
- `bench_router/cli.py`: `route --dry-run`, `explain`.
- `bench_router/categories.toml`: 03 문서의 evidence 매핑(P 정책, policy_version 1.0).

### P1 — 데이터·운영 캐시
- `bench_router/data.py`: SQLite(user_version=1; sources/snapshots/observations), AA Free pagination adapter, Arena adapter, TB/SWE 수동 import, fcntl refresh lock, bounded HTTP, 소스별 last-good, 원자 게시 + last-good 승격 + 30일 재현본, 소스별 payload 3개 보관.
- CLI: `refresh [--source ID] [--force] [--import FILE]`, `status`.
- route는 `data`/`urllib.request`를 import하지 않는다(test_v17에서 확인).
- 소스별 refresh 전체 상한 `SOURCE_MAX_SECONDS=180`: 요청·재시도·대기를 모두 포함하고, 요청별 timeout과 재시도 대기는 남은 시간으로 줄인다. 넘으면 해당 소스는 실패 처리되고 last-good을 유지한다. (HF datasets-server가 느릴 때 refresh가 25분까지 늘어질 수 있던 빈틈을 막음.)

### P2 — herdr 위임 (fixture 검증 완료, live smoke 대기)
- `bench_router/herdr.py`: herdr CLI argv 호출, live 가용성 probe(herdr kind / executable PATH), cwd별 dispatch lock, receipt(`<cwd>/.bench-router/runs/<run_id>/receipt.json`), 새 workspace → `agent start` → `agent get` 확인 → `submission_attempted` fsync → `agent prompt --wait` 1회 → 결과 계약 검사. collect/feedback.
- CLI: `route`(live), `collect --run-id --cwd [--wait-ms]`, `feedback --run-id --cwd --outcome`, 전역 `--herdr-session`(또는 `BENCH_ROUTER_HERDR_SESSION`). herdr 경로 지정은 `BENCH_ROUTER_HERDR`.
- 실행 디렉터리: `receipt.json`, `decision.json`(선택 근거), `result.md`/`result.json`(Agent 작성), `feedback.jsonl`.

## 재현
```bash
cd /mnt/d/Projects/bench-router-handoff
python3 -m unittest test_p0 test_p1 test_p2   # 33 tests (fcntl → WSL/Linux)
BR="python3 -m bench_router.cli --config-dir CFG --cache-dir CACHE"
$BR refresh            # aa, arena (TTL 내면 skip; --force)
$BR refresh --source tb --import tb.json
$BR status
$BR route --task task.json --dry-run
$BR explain --task task.json
$BR --herdr-session NAME route --task task.json          # live 위임
$BR collect --run-id RUN --cwd /abs/cwd --wait-ms 60000  # 재전송 없음
$BR feedback --run-id RUN --cwd /abs/cwd --outcome success --evaluator orchestrator
```
herdr는 `~/.local/bin/herdr`(0.9.3). 비로그인 셸에서는 PATH에 없으므로 `export PATH=$HOME/.local/bin:$PATH`가 필요하다.
설정 디렉터리(기본 `~/.config/bench-router`): `profiles.toml`(필수), `aliases.toml`(선택), `categories.toml`(선택, 없으면 내장본).

## 검증 결과
- offline: P0+P1+P2 33/33 통과 (WSL). P0만 Windows Python 3.13에서도 통과.
- mutation: P0 정책값 3종 변경 시 P0 테스트 실패. P2에서 결과 검사 무력화(9개 실패), 기존 receipt 무시(3개 실패), timed_out을 settled로 취급(2개 실패)을 각각 잡아냄.
- **Arena live (E2, 2026-10-12)**: 공개 API로 refresh 성공. 요청 17회, revision `e16f9023298691b4596eca61b4e31161dff31200`, cohort N = text_style_control/overall 414, text_style_control/math 400, webdev/overall 141, document_style_control/overall 44 (publish 2026-09-13), vision_style_control/overall 165. datasets-server read timeout 2회는 재시도로 복구됨. 두 번째 실행은 TTL skip(0.1s).
- **Arena live 상한 확인 (2026-10-12 13:33)**: HF datasets-server가 500/502/read timeout을 내던 시점에 `refresh --source arena --force`가 정확히 180초에 실패로 종료(exit 16, 요청 14회). 상한 도입 전에는 같은 상황에서 4분 이상 응답 없이 실행됐다.
- **AA live: 미검증** — `ARTIFICIAL_ANALYSIS_API_KEY` 없음. 문서(E1) 스키마로 fixture만 통과. 키가 없으면 refresh는 aa 실패로 exit 16(정상 동작, Arena last-good 유지).
- **herdr live (E2)**: 0.9.3 설치, named session `brprobe`로 headless 서버 → `workspace create` → `agent start`(claude 미설치) → `agent get`/`prompt`(없는 agent) → `pane read` → `workspace close` → `server stop`까지 실측. 응답 형식은 `docs/evidence/herdr-0.9.3/`과 test_p2 fake에 반영.
- **live Agent smoke: 미실행** — WSL에 claude CLI가 없다(로그인 필요).

## 실측으로 확인된 사실 (E1 → E2)
- Arena는 parquet이지만 HF datasets-server `/filter` JSON(100행/요청)으로 같은 행을 받음 → pyarrow 불필요. 컬럼: model_name, organization, license, rating, rating_lower/upper, variance, vote_count, rank, category, leaderboard_publish_date. license CC BY 4.0.
- text subset에 `math` category 존재(→ `arena_text_math` 사용 가능). webdev 카테고리: overall/webdev/webdev-html/webdev-react/image_to_webdev.
- **원본에 같은 model_name의 별개 항목 존재**(webdev/overall `gpt-5.3-codex (codex-harness)`, rank 86/101). 처리: 모집단 유지, `name#rank=N`으로 구분해 이름만으로 매칭 안 됨.
- Windows Python에서는 HF TLS 검증 실패(사내 인증서 추정). WSL에서는 정상.

## herdr 0.9.3 실측 사실
- `herdr --session X server`가 headless 서버를 띄운다(소켓 `~/.config/herdr/sessions/X/`). 실험은 named session으로 한다.
- 성공은 stdout `{"id","result":{"type":...}}`. 실패는 stderr `{"error":{"code","message"}}` + exit 1, 문법 오류는 exit 2.
- `workspace create` → `result.{workspace.workspace_id, tab, root_pane.pane_id}`. `agent start` → `agent_started{agent: AgentInfo, argv}`. `agent prompt` → `agent_prompted{agent}`. AgentInfo에는 `name, pane_id, agent_status(idle|working|blocked|done|unknown), cwd, completion_seq, state_change_seq`가 있다.
- 실행 파일이 없으면 `agent start`는 `timeout` 코드를 반환하고 pane에 `command not found`가 남는다. 미설치를 별도 코드로 구분하지 않으므로 사전 probe가 필요하다.
- `agent stop`은 없다. agent 이름 형식은 `[a-z][a-z0-9_-]{0,31}`.
- `agent prompt --wait`은 비작업 상태에서 5초 안에 working/blocked가 관찰되지 않으면 `agent_prompt_stalled`. turn 단위 추적이 아니다. 프롬프트는 positional 인자로만 받는다 → argv 길이 제한(120 KiB) 적용.

## P2에서 정한 것 (문서에 없던 세부)
- 프로필의 `executable`은 `kind`와 같아야 한다(herdr가 canonical executable을 실행). 로그인/모델 접근은 probe하지 않고 `auth_unverified` 경고만 낸다.
- herdr 오류 매핑: start `agent_not_ready` → blocked, 그 외 start 실패 → execution_failed(pane 마지막 20줄을 `diagnostic_tail`로 반환). prompt `agent_blocked` → blocked(전송 안 됨), `timeout` → timed_out, 그 외 → delivery_uncertain. 어느 경우에도 재전송하지 않는다.
- settled(새 dispatch를 막지 않음)는 completed / result_invalid / execution_failed. 나머지 상태는 collect로 정리해야 다음 live dispatch가 가능하다. prompt를 보낸 적 없는 run을 collect하면 execution_failed로 정리된다.
- 전송이 모호한 상태에서 agent가 idle이고 유효한 결과가 없으면 result_invalid가 아니라 delivery_uncertain으로 둔다.
- workspace/pane은 자동으로 닫지 않는다. 출력의 `workspace_id`로 사용자가 정리한다.
- fingerprint의 CLI 버전은 계속 "unknown"이다. 버전 probe를 넣으면 refresh도 같은 입력으로 계산해야 한다.
- decisions/feedback은 SQLite가 아니라 run 디렉터리 파일(`decision.json`, `feedback.jsonl`)에 남긴다. 집계가 필요해지면 DB로 옮긴다.

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
- P2 live smoke: WSL에 Claude Code 설치·로그인 필요. 실제 프로필 설정은 WSL `~/.config/bench-router/{profiles.toml,aliases.toml}`에 작성해 두었다(claude-opus-high: `--model claude-opus-5-5 --effort high --permission-mode acceptEdits`, Arena alias `claude-opus-5.5-high`).

## 다음 한 가지 작업
WSL에서 claude 로그인 → 06의 smoke 절차: `refresh` → `status` → `route --dry-run` → live `route`(task.synthetic 형태, `/tmp/br-smoke`) → 같은 task 재호출(재전송 없음 확인) → `collect` → `feedback` → workspace 정리.

## 사용자에게 필요한 정보
- 실제 사용할 프로필(CLI/모델 ID/reasoning/cost tier/context/capability)과 그에 맞는 aliases.
- AA API 키(환경변수로만).
