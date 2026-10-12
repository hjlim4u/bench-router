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

### P2 — herdr 위임 (fixture + live smoke 통과)
- `bench_router/herdr.py`: herdr CLI argv 호출, live 가용성 probe(herdr kind / executable PATH), cwd별 dispatch lock, receipt(`<cwd>/.bench-router/runs/<run_id>/receipt.json`), 새 workspace → `agent start` → `agent get` 확인 → `submission_attempted` fsync → `agent prompt --wait` 1회 → 결과 계약 검사. collect/feedback.
- CLI: `route`(live), `collect --run-id --cwd [--wait-ms]`, `feedback --run-id --cwd --outcome`, 전역 `--herdr-session`(또는 `BENCH_ROUTER_HERDR_SESSION`). herdr 경로 지정은 `BENCH_ROUTER_HERDR`.
- 실행 디렉터리: `receipt.json`, `decision.json`(선택 근거), `result.md`/`result.json`(Agent 작성), `feedback.jsonl`.

## 재현
```bash
cd /mnt/d/Projects/bench-router-handoff
python3 -m unittest test_p0 test_p1 test_p2   # 34 tests (fcntl → WSL/Linux)
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
- offline: P0+P1+P2 34/34 통과 (WSL). P0만 Windows Python 3.13에서도 통과.
- mutation: P0 정책값 3종 변경 시 P0 테스트 실패. P2에서 결과 검사 무력화(9개 실패), 기존 receipt 무시(3개 실패), timed_out을 settled로 취급(2개 실패)을 각각 잡아냄.
- **Arena live (E2, 2026-10-12)**: 공개 API로 refresh 성공. 요청 17회, revision `e16f9023298691b4596eca61b4e31161dff31200`, cohort N = text_style_control/overall 414, text_style_control/math 400, webdev/overall 141, document_style_control/overall 44 (publish 2026-09-13), vision_style_control/overall 165. datasets-server read timeout 2회는 재시도로 복구됨. 두 번째 실행은 TTL skip(0.1s).
- **Arena live 상한 확인 (2026-10-12 13:33)**: HF datasets-server가 500/502/read timeout을 내던 시점에 `refresh --source arena --force`가 정확히 180초에 실패로 종료(exit 16, 요청 14회). 상한 도입 전에는 같은 상황에서 4분 이상 응답 없이 실행됐다.
- **AA live (E2, 2026-10-12 14:06)**: Free tier, `intelligence_index_version` 4.3, 4 pages × 200, 모델 697개, 요청 4회, 2초. 응답 스키마는 문서(E1)와 일치. 키는 WSL `~/.config/bench-router/env`(600)에 두고 실행 시 `set -a; . ~/.config/bench-router/env`로 읽는다.
  - AA slug는 reasoning effort별로 나뉜다(`claude-opus-5-5-high`, `gpt-6-1-sol-high` 등). 프로필 effort와 같은 변형을 alias로 연결했다.
  - 이 신모델들은 `coding_index`가 null이다 → `aa_coding` 결측 → code_gen은 두 후보 모두 coverage 0 → default.
  - 키가 대화 기록에 노출됐다. 재발급(rotate)을 권장한다.
- **herdr live (E2)**: 0.9.3 설치, named session `brprobe`로 headless 서버 → `workspace create` → `agent start`(claude 미설치) → `agent get`/`prompt`(없는 agent) → `pane read` → `workspace close` → `server stop`까지 실측. 응답 형식은 `docs/evidence/herdr-0.9.3/`과 test_p2 fake에 반영.
- **live Agent smoke: 통과 (2026-10-12 13:51, WSL 사용자 hjlim4u)** — herdr 0.9.3 named session `brsmoke`, Claude Code 2.1.296, 프로필 `claude-opus-high`(default 선택: Arena 데이터 없음 → `default_insufficient_evidence`).
  - round 1 → 미해결(blocked) 상태에서 round 2 시도: `conflict`/`unresolved_run`(exit 14). round 1 collect → Agent 없음 → `execution_failed`로 정리.
  - round 2 live: 25초, `completed`, task_outcome `success`, delivery `activity_observed`. result.json의 run_id/nonce/fingerprint 일치, `result_sha256` = 독립 계산 `0b56510e…9ca5`. run 디렉터리 밖 파일 변경 없음.
  - 같은 round 재호출: `reused_receipt=true`, 같은 run_id. transcript에서 프롬프트 전용 문자열("검증 토큰:")이 1회 → 재전송 없음.
  - collect: completed. workspace `w1` 닫고 서버 정지 후 collect: 저장된 settled 기록(completed) 반환. feedback `success` 기록.
  - run: `~/br-smoke/.bench-router/runs/02c537a0-5e05-476b-a512-0860b83ca2dc/`

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

- **live 2차 (2026-10-12 14:02, Arena 복구 후)**: Arena refresh 성공(66s, 요청 17, 재시도 2, revision `e16f9023…`).
  - A `smoke-002` writing: **`benchmark_score`로 claude-opus-high 선택**(arena_text norm 0.998, coverage 1.0). codex-sol-high는 coverage 0으로 순위 계산에서 빠짐. 33s `completed`/`success`, SHA-256 독립 계산 일치, 재호출 시 재전송 없음(프롬프트 전용 문자열 1회), workspace를 닫은 뒤에도 collect가 completed.
  - B `smoke-003` 같은 작업 + `exclude_profiles=[claude-opus-high]`: **codex-sol-high**(`fallback_insufficient_evidence`). 44s `completed`/`success`, SHA-256 일치, 재전송 없음, 닫은 뒤 collect도 completed. Agent가 자체 보고한 check 하나(`git status`, cwd가 git 저장소가 아님)는 failed였지만 결과와는 무관.
  - 두 run 모두 feedback `success` 기록. 열린 workspace 0, `brsmoke` 서버 정지.
  - codex: 0.162.1(공식 standalone installer, 사용자 범위), ChatGPT 로그인, `codex exec`로 `gpt-6.1-sol` 접근 확인.

- **live 3차: 두 후보를 점수로 비교한 선택 (2026-10-12 14:10)**: `smoke-004` general/balanced. claude Q 0.996 / S 0.846, codex Q 0.977 / S 0.902(둘 다 coverage 1.0, AA intelligence) → **codex-sol-high `benchmark_score`**. 48s `completed`/`success`, SHA-256 일치, 재전송 없음, 닫은 뒤 collect도 completed, feedback 기록.
  - dry-run 매트릭스: general — quality→claude, balanced/cost→codex. analysis — 모두 claude(codex는 Arena 근거가 없어 coverage 0.6, 결측 페널티). writing — claude(codex coverage 0). code_gen — default(coding_index null).

## live smoke에서 드러난 것과 결정
- **위임 cwd는 Claude Code에서 미리 신뢰된 폴더여야 한다.** 처음 보는 폴더는 신뢰 확인 창 → herdr `agent_not_ready` → 라우터 `blocked`(프롬프트 0회). 보안 확인이므로 자동 응답하지 않는다. Orchestrator 전제 조건.
- **결과 계약에서 "원자적 기록" 요구를 뺐다(04 문서와 다름).** 이 문구 때문에 Agent가 `mv`·python 검증을 시도했고, `acceptEdits` 모드에서 권한 승인 대기(blocked)에 걸렸다. 라우터는 settled 이후에만 검사하고 해시까지 확인하므로 원자성은 실익이 없다. 지금은 "마지막에 한 번에 작성, 해시는 `sha256sum result.md`"로 지시한다.
- 프로필 args에 `--allowedTools Bash(sha256sum:*)`를 추가했다(해시 계산 외 Bash는 승인 필요).
- codex 프로필은 `-s workspace-write -a never`로 둔다(cwd 안에서만 쓰기, 승인 요청 없음, 실패는 모델에 반환). bypass 옵션은 쓰지 않는다.
- Arena의 codex 모델은 `gpt-6.1-sol-max`(effort max)만 있다. 프로필 effort가 `high`이므로 alias로 연결하지 않았다(effort가 다르면 별도 cohort). 그래서 codex는 현재 evidence가 없다.
- 프롬프트 이후 blocked면 `pane read --source visible` 화면을 `diagnostic_tail`로 반환한다. blocked 상태에서 `agent read --lines 2000`은 `agent_not_idle`로 거부된다.
- `pane read`/`agent read`는 JSON이 아닌 텍스트를 출력한다(초기 fake가 틀렸던 부분, 수정함).
- 진행 중 run의 workspace를 닫으면 Agent도 종료된다. smoke 정리는 completed일 때만 한다.

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
- 실제 프로필 설정: WSL `~/.config/bench-router/{profiles.toml,aliases.toml}`(사용자 hjlim4u).
  - claude-opus-high: `--model claude-opus-5-5 --effort high --permission-mode auto`, cost high, alias Arena `claude-opus-5.5-high` / AA `claude-opus-5-5-high`.
  - codex-sol-high: `-m gpt-6.1-sol -c model_reasoning_effort="high" -s workspace-write -a never`, cost medium, alias AA `gpt-6-1-sol-high`.
- 라우팅 효과 평가(06 문서: baseline 대비 작업군 성공률·비용·지연)는 하지 않았다. 지금까지의 live run은 모두 합성 smoke 작업이다.
- `cost_tier`(claude high, codex medium)는 정책 proxy다. 실제 요금·구독 비용은 측정하지 않았다.
- OS timer 미설치(systemd 예시 참조. `EnvironmentFile=%h/.config/bench-router/env`).

## 작업군 비교 v1 (2026-10-12, `eval/results/v1.md`)
- 과제 20개(8개 카테고리) × 프로필 2개, 쌍당 1회. 성공 기준은 라우터 completed **그리고** hidden check 통과. 과제·check는 `eval/workset.py`, 실행 전 `ee3faa0`에 고정. 초기 상태에서는 불합격, 참조 정답(`eval/reference.py`)에서는 합격하는지 자체 검사함.
- fixed-default(claude) 20/20, low-cost-first(codex) 19/20, bench-router 20/20. 평균 시간 38.6 / 83.9 / 40.9초. cost proxy 20 / 10 / 19(정책값, 실제 비용 아님).
- 천장 효과 때문에 성공률은 판별 불가. bench-router는 18/20에서 default와 같은 선택을 했고, 그중 12개는 근거 부족 때문이다. 한계는 evidence coverage다.
- pilot에서 claude `acceptEdits` 프로필이 자체 테스트 실행 중 승인 대기로 blocked → 권한 설정 차이를 재는 비교가 되므로 claude 프로필을 `--permission-mode auto`로 변경(config_revision 2026-10-12c).

## 다음 한 가지 작업
coding_repo·terminal_ops의 evidence coverage 보강: SWE-bench Verified / Terminal-Bench 4.0 공식 결과에서 claude-code·codex-cli 하네스와 effort가 일치하는 행을 찾아 `refresh --import`. 그다음 판별력 있는 작업군 v2(어려운 과제, 반복 실행).

## 사용자에게 필요한 정보
- 실제 사용할 프로필(CLI/모델 ID/reasoning/cost tier/context/capability)과 그에 맞는 aliases.
- AA API 키(환경변수로만).
