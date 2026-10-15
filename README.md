# bench-router

Orchestrator가 위임하기로 결정한 작업을 받아, **외부 벤치마크 근거로 CLI Agent 프로필을 고르고 [herdr](https://herdr.dev)로 실행을 맡긴 뒤 결과를 계약대로 회수하는** 얇은 라우터입니다.

- 위임 여부·작업 분해·결과 검토는 Orchestrator가 맡습니다. Agent 실행·터미널 상태 관찰은 herdr가 맡습니다.
- 라우터는 선택, 실행 접착(receipt·중복 전송 방지), 결과 계약 검사만 합니다.
- 요청 경로(`route`)에서는 벤치마크 API를 호출하지 않습니다. 데이터는 별도 `refresh`가 미리 받아 둔 로컬 snapshot에서 읽습니다.
- Python 3.11+ 표준 라이브러리만 씁니다. 외부 패키지 의존성이 없습니다.

설계 근거와 원래 명세는 [00_START_HERE.md](00_START_HERE.md)부터 [06_VALIDATION_AND_OPEN_ITEMS.md](06_VALIDATION_AND_OPEN_ITEMS.md)까지의 handoff 문서에 있습니다. 구현 중 명세와 달라진 점은 [명세와 다른 점](#명세와-다른-점)에, 진행 기록은 [docs/implementation-status.md](docs/implementation-status.md)에 정리했습니다.

실행은 herdr-projects 공개 CLI로 통합했습니다. [Projects 설정·이전 안내](docs/projects.md)에 따라 프로젝트와 프로필을 준비하세요. `route`/`parallel`의 결과 계약·중복 실행 방지·합산 4개 제한을 유지합니다.

---

## 구성

```text
Orchestrator ── task.json ──▶ bench-router route ──▶ Projects CLI ──▶ herdr ──▶ Agent CLI (claude, codex, …)
     ▲                         │  분류 → 제약 필터 → 점수 → 선택          │
     │                         │  receipt 기록 → 1회 전송 → 결과 계약 검사 │
     └──── JSON 결과 ◀─────────┘◀──────── result.md / result.json ◀────────┘

OS timer / 수동 ── bench-router refresh ──▶ AA API, Arena dataset, 수동 import(TB/SWE)
                                          └▶ SQLite 이력 ──▶ snapshot.json(원자 교체) ──▶ route가 읽기만 함
```

| 모듈 | 역할 |
|---|---|
| `bench_router/routing.py` | 입력·설정·snapshot 검증, 분류(L0/L1/general), 하드 제약, 점수와 선택. 네트워크·파일 쓰기 없음 |
| `bench_router/data.py` | refresh: source 수집·정규화, SQLite 이력, routing snapshot 게시, `status` |
| `bench_router/herdr.py` | live 위임: 가용성 확인, receipt, herdr 호출, 결과 계약 검사, `collect`/`feedback` |
| `bench_router/parallel.py` | 병렬 위임: task × fanout agent를 각자 git worktree에서 동시 실행, 격리/협업 수준 |
| `bench_router/cli.py` | 명령, 입력 검증, 종료 코드 |
| `bench_router/categories.toml` | 카테고리별 evidence 가중치(기본값) |

---

## 요구 사항

- 오프라인 평가·refresh는 Linux/WSL2/Windows에서 동작합니다. Projects live 실행은 Linux/WSL2에서 준비하세요.
- Python 3.11 이상.
- live 위임에는 Herdr, herdr-projects **0.2.34**, Agent CLI 설치·로그인, 열려 있는 Projects 프로젝트가 필요합니다. `BENCH_ROUTER_PROJECT_DIR`에 프로젝트의 절대 경로를 지정합니다.
- AA 데이터를 쓰려면 Artificial Analysis API 키(Free tier로 충분)가 필요합니다.

별도 설치 단계는 없습니다. 저장소 루트에서 모듈로 실행합니다.

```bash
cd /path/to/bench-router-handoff
python3 -m bench_router.cli --help
```

### 여러 Agent에서 Skill 사용

[`skills/bench-router/SKILL.md`](skills/bench-router/SKILL.md)가 유일한 Skill 원본입니다. 각 Agent의 Skill 검색 디렉터리에 이 폴더의 심볼릭 링크(Windows에서는 junction)를 만드세요. 복사본을 배포하면 업데이트가 갈라집니다. 예를 들어 `REPO`와 `AGENT_SKILLS`를 실제 절대 경로로 지정한 뒤 실행합니다.

```bash
ln -s "$REPO/skills/bench-router" "$AGENT_SKILLS/bench-router"
```

```powershell
New-Item -ItemType Junction -Path "$AgentSkills\bench-router" -Target "$Repo\skills\bench-router"
```

Skill의 `scripts/cli.py`는 링크의 실제 저장소 경로를 찾아 어떤 작업 디렉터리에서도 기존 CLI를 실행합니다. 같은 OS 실행 환경의 Agent는 동일 사용자 설정·캐시를 공유합니다. 네이티브 Windows와 WSL은 잠금 구현이 다르므로 둘이 같은 물리 캐시를 동시에 쓰지 마세요. 한 환경으로 실행을 통일하면 사본 없이 공유할 수 있습니다. `route`는 캐시를 갱신하지 않으며, 정기 `refresh`는 사용자당 한 곳에서만 예약하세요. 수동 `refresh`도 동일 잠금과 캐시를 사용합니다. Windows에서는 작업 스케줄러에 이 스크립트의 `refresh` 명령을 한 번 등록할 수 있습니다.

---

## 설정

설정 디렉터리 기본값은 `$XDG_CONFIG_HOME/bench-router`(없으면 `~/.config/bench-router`)이고, `--config-dir`로 바꿀 수 있습니다. 캐시 디렉터리 기본값은 `$XDG_CACHE_HOME/bench-router`(없으면 `~/.cache/bench-router`)이고, `--cache-dir`로 바꿀 수 있습니다.

| 파일 | 필수 | 내용 |
|---|---|---|
| `profiles.toml` | 예 | 라우팅 대상 Agent 프로필 |
| `aliases.toml` | 아니오 | 출처별 모델 문자열 → 프로필 `model_id` 매핑 |
| `categories.toml` | 아니오 | 없으면 내장 `bench_router/categories.toml` 사용 |
| `env` | 아니오 | `ARTIFICIAL_ANALYSIS_API_KEY=...` (권한 600 권장, refresh 시 환경변수로 읽음) |

### profiles.toml

라우팅 단위는 **프로필**(Agent CLI + 모델 + 실행 설정)입니다. 모든 키가 필수이며, 모르는 키가 있으면 오류입니다.

```toml
schema_version = "1.0"
default_profile = "claude-opus-high"                 # 근거가 부족할 때의 기본값 (제약은 동일하게 적용)
fallback_order = ["claude-opus-high", "codex-sol-high"]

[[profile]]
id = "claude-opus-high"                              # [a-z][a-z0-9_-]{0,47}
enabled = true
kind = "claude"                                      # herdr --kind 값. executable과 같아야 함
executable = "claude"
args = ["--model", "claude-opus-5-5", "--effort", "high", "--permission-mode", "auto"]   # argv 배열
model_id = "claude-opus-5-5"                         # aliases.toml이 가리키는 canonical ID
harness_id = "claude-code"                           # exact 벤치마크 매칭용
reasoning_effort = "high"                            # "unknown"이면 exact 매칭 불가
config_revision = "2026-10-12c"                      # 설정을 바꾸면 갱신 → 지문(fingerprint) 변경
cost_tier = "high"                                   # low | medium | high (정책상 상대값, 실제 요금 아님)
inference_local = false
context_tokens = 0                                   # 0 = 모름 → min_context_tokens 요구 시 탈락
capabilities = ["filesystem_write"]

[[profile]]
id = "codex-sol-high"
enabled = true
kind = "codex"
executable = "codex"
args = ["-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=\"high\"", "-s", "workspace-write", "-a", "never"]
model_id = "gpt-6.1-sol"
harness_id = "codex-cli"
reasoning_effort = "high"
config_revision = "2026-10-12"
cost_tier = "medium"
inference_local = false
context_tokens = 0
capabilities = ["filesystem_write"]
```

프로필의 권한 설정은 결과에 직접 영향을 줍니다. 승인 요청이 뜨면 Agent가 `blocked` 상태로 멈추고, 라우터는 결과를 받지 못합니다. 위 두 설정은 자율 실행이 되도록 맞춘 예입니다(claude `--permission-mode auto`, codex `-s workspace-write -a never`).

### aliases.toml

출처마다 모델 이름이 다르므로, **정확한 문자열 → canonical ID**를 수동으로 관리합니다. reasoning effort가 다른 변형은 별개 모델로 취급합니다. 프로필의 effort와 같은 변형만 연결하세요.

```toml
[arena]
"claude-opus-5.5-high" = "claude-opus-5-5"

[aa]
"claude-opus-5-5-high" = "claude-opus-5-5"
"gpt-6-1-sol-high" = "gpt-6.1-sol"
```

매칭되지 않은 이름은 `status`의 `unmatched_count`/`unmatched_sample`로 확인할 수 있습니다.

---

## 명령

모든 명령은 stdout에 **JSON 한 객체**만 출력합니다(`explain`은 예외로 사람이 읽는 텍스트). 로그는 stderr로 나갑니다. 전역 옵션: `--config-dir`, `--cache-dir`, `--herdr-session NAME`(또는 환경변수 `BENCH_ROUTER_HERDR_SESSION`). Projects 실행 파일 경로는 `BENCH_ROUTER_PROJECTS`(기본 `herdr-projects`)로 지정합니다. `--herdr-session`은 프로젝트가 속한 세션과 일치해야 합니다.

| 명령 | 동작 |
|---|---|
| `refresh [--source aa\|arena] [--force]` | 자동 source 수집 → snapshot 게시. TTL 안이면 건너뜀 |
| `refresh --source swe\|tb --import FILE` | 승인된 수동 벤치마크 결과 import |
| `status` | source별 나이·실패 횟수·마지막 오류·미매칭 모델, snapshot/설정 일치 여부 |
| `route --task FILE --dry-run` | 선택만 하고 부작용 없음(네트워크·herdr·파일 쓰기 없음) |
| `explain --task FILE [--context FILE]` | dry-run의 전체 후보·근거·제외 사유와 제약 결과·지표를 텍스트로 출력 |
| `evaluate --task FILE [--context FILE]` | 선택 없이 전 프로필의 지표·제약 결과·benchmark 평가와 `assessment_digest` (Orchestrator용, [docs/orchestrator.md](docs/orchestrator.md)) |
| `route --task FILE --selection FILE` | Orchestrator가 고른 프로필을 선택 근거와 함께 실행. 평가 후 입력이 바뀌었으면 `stale_assessment` |
| `route --task FILE` | 선택 후 herdr로 위임하고, 유한한 시간 안에 대기·회수 |
| `parallel --group FILE [--dry-run]` | 여러 agent를 각자 worktree에서 병렬 위임 ([병렬 위임](#병렬-위임과-협업-수준)) |
| `collect --run-id ID --cwd DIR [--wait-ms N]` | 기존 run을 관찰·회수. **프롬프트를 다시 보내지 않음** |
| `feedback --run-id ID --cwd DIR --outcome success\|partial\|fail [--evaluator X] [--note Y]` | Orchestrator의 검증 결과 기록 |

### 사용 예

```bash
export PATH="$HOME/.local/bin:$PATH"                 # herdr, claude, codex
set -a; . ~/.config/bench-router/env; set +a          # AA 키
BR="python3 -m bench_router.cli"

$BR refresh                       # aa, arena (소스별 최대 180초)
$BR status
$BR route --task task.json --dry-run
$BR explain --task task.json
$BR --herdr-session work route --task task.json      # live 위임
$BR collect --run-id <RUN_ID> --cwd /abs/project --wait-ms 60000
$BR feedback --run-id <RUN_ID> --cwd /abs/project --outcome success --evaluator orchestrator
```

### 종료 코드

| 코드 | 의미 |
|---|---|
| 0 | `selected`(dry-run), `completed`, refresh/status/feedback 정상 |
| 2 | 입력·설정·인자 오류 |
| 10 | `blocked` — Agent가 승인·질문을 기다림 |
| 11 | `timed_out` / `delivery_uncertain` — 실행 중일 수 있음. `collect`로 확인 |
| 12 | `execution_failed` / `result_invalid` |
| 13 | `no_eligible_profile` — 위임하지 않음 |
| 14 | `conflict` — 같은 task/round에 다른 내용, 미해결 run 존재, 또는 잠금 사용 중. `stale_assessment` — `evaluate` 이후 task·설정·snapshot·context가 바뀜 |
| 15 | 내부 저장소·I/O 오류 |
| 16 | refresh 대상 source 일부 또는 전체 실패(정상 데이터 last-good 유지) |

---

## 입력: task.json

```json
{
  "schema_version": "1.0",
  "task_id": "fix-pager-001",
  "round": 1,
  "summary": "Fix an off-by-one bug in pager.paginate.",
  "prompt": "pager.py의 paginate(...)가 첫 페이지를 빠뜨립니다. 고치세요.",
  "cwd": "/home/me/project",
  "context_files": ["pager.py"],
  "categories": {"coding_repo": 1},
  "category_confidence": 0.9,
  "constraints": {"max_cost_tier": "high", "min_context_tokens": 0, "local_only": false,
                  "timeout_ms": 900000, "required_capabilities": ["filesystem_write"]},
  "priority": "balanced",
  "exclude_profiles": []
}
```

- 필수: `schema_version`, `task_id`(`[A-Za-z0-9][A-Za-z0-9_-]{0,63}`), `round`(≥1), `summary`(≤4000자), `prompt`(≤256 KiB), `cwd`(존재하는 절대 경로).
- `categories`가 있으면 `category_confidence`도 있어야 합니다. 카테고리 값: `coding_repo`, `terminal_ops`, `code_gen`, `webdev`, `math_reasoning`, `analysis`, `writing`, `vision_doc`, `general`.
- 모르는 필드, NaN/Infinity, 중복 JSON 키, 잘못된 UTF-8, cwd 밖을 가리키는 `context_files`는 모두 오류(exit 2)입니다.
- live 위임 시 프롬프트와 실행 계약 문구를 합쳐 120 KiB를 넘으면 거부합니다. herdr가 프롬프트를 argv 인자로만 받기 때문입니다.
- **`cwd`는 Agent가 이미 신뢰한 폴더여야 합니다.** 처음 보는 폴더에서는 Claude Code 등이 신뢰 확인 창을 띄워 `blocked`가 됩니다. 라우터는 이 보안 확인에 자동으로 응답하지 않습니다.

---

## 선택 방식

아래는 `route`가 스스로 고르는 **legacy 자동 선택**입니다. 여러 지표(비용·지연 등)를 함께 따지는 선택은 Orchestrator가 `evaluate` 결과로 하고 `route --selection`으로 실행합니다. 계약은 [docs/routing-contracts.md](docs/routing-contracts.md), 사용법은 [docs/orchestrator.md](docs/orchestrator.md).

1. **분류**
   - L0: Orchestrator가 준 `categories`를 `category_confidence ≥ 0.6`일 때 정규화해 사용합니다.
   - L1: 그 외에는 summary 키워드와 `context_files` 확장자 규칙을 씁니다. 한 카테고리에서만 서로 다른 규칙이 2개 이상 맞아야 채택합니다.
   - 나머지는 `general`로 분류하고 `fallback_reason`을 남깁니다.
2. **하드 제약**: `enabled`, `exclude_profiles`, `max_cost_tier`, `min_context_tokens`, `required_capabilities`, `local_only`를 적용합니다. context가 있으면 `tokens.required_context`와 `max_estimated_cost_usd`도 적용합니다(`routing.CONSTRAINTS`). live에서는 herdr kind 지원 여부와 실행 파일 존재도 확인합니다. default 프로필에도 같은 제약을 적용합니다.
3. **근거와 점수**
   - 카테고리 가중치 `w`와 evidence 매핑 `v`로 evidence별 가중치 `a_b = Σ w_c·v_cb`를 구합니다.
   - 같은 cohort 전체를 모집단으로 percentile 정규화(`(평균 rank − 1)/(N − 1)`, N=1이면 0.5)를 합니다.
   - coverage `C`는 관측된 evidence의 가중치 합입니다.
   - 품질 `Q = C·Q_obs + (1−C)·0.5 − 0.1·(1−C)`. 결측에는 사전값 0.5와 페널티 0.1이 붙고, 측정된 0점은 결측이 아닙니다.
   - 점수 `S = Q − λ·cost_proxy`. λ는 quality 0, balanced 0.15, cost 0.30이고, cost_proxy는 low 0, medium 0.5, high 1입니다.
4. **선택**
   - `C ≥ 0.5`인 후보만 순위를 매깁니다.
   - 최고점과 차이가 0.02 미만인 후보끼리는 낮은 cost tier, 그다음 ID 순으로 고릅니다. `quality` 우선순위에서는 비용으로 순서를 뒤집지 않습니다.
   - 순위에 오른 후보가 없으면 제약을 통과한 `default_profile`, 그다음 `fallback_order`로 갑니다. 이때 `selection_mode`는 `default_insufficient_evidence` 또는 `fallback_insufficient_evidence`입니다.
   - 남는 후보가 없으면 `no_eligible_profile`(exit 13)로 끝납니다.

카테고리별 evidence 기본값(`categories.toml`):

| 카테고리 | evidence(가중치) |
|---|---|
| coding_repo | swe_verified_exact 0.6, aa_coding 0.4 |
| terminal_ops | terminal_exact 0.7, aa_coding 0.3 |
| code_gen | aa_coding 1.0 |
| webdev | arena_webdev 0.6, aa_coding 0.4 |
| math_reasoning | arena_text_math 1.0 |
| analysis | aa_intelligence 0.6, arena_text 0.4 |
| writing | arena_text 1.0 |
| vision_doc | arena_document 0.5, arena_vision 0.5 |
| general | aa_intelligence 1.0 |

출력의 `candidates[]`에는 후보별 `score`, `quality`, `coverage`, `coverage_band`, `exact_evidence_weight`, `cost_proxy`가 들어 있고, evidence마다 원값·정규화값·scope·cohort·평가 조건(`conditions`)·출처 revision·날짜·`missing_reason`이 함께 나옵니다. 근거 데이터가 일부만 있거나, 모델 수준 대리 지표뿐이거나, 오래된 경우에는 `warnings`에 표시합니다.

---

## 데이터 수집 (refresh)

| source | 방식 | evidence | TTL / 최대 허용 경과 |
|---|---|---|---|
| `aa` | Artificial Analysis Free API, 전체 페이지 순회 | `aa_intelligence`, `aa_coding` | 24h / 7d |
| `arena` | LMArena `leaderboard-dataset`(CC BY 4.0), HF datasets-server `/filter` JSON | `arena_text`, `arena_text_math`(text_style_control), `arena_webdev`, `arena_document`, `arena_vision` | 24h / 7d |
| `swe` | `--import` 수동 결과, SWE-bench Verified로 고정 | `swe_verified_exact` | 168h / 30d |
| `tb` | `--import` 수동 결과, Terminal-Bench 4.0으로 고정 | `terminal_exact` | 168h / 30d |

- **응답 처리**: 응답 크기 상한 20 MiB, 요청 수 상한(aa 50, arena 60)을 둡니다. 401/403/429는 재시도하지 않고, 5xx와 네트워크 오류는 최대 2회 재시도합니다.
- **시간 상한**: source마다 전체 **180초** 상한이 있습니다. 요청별 timeout과 재시도 대기도 남은 시간에 맞춰 줄어듭니다.
- **실패 시**: 페이지 하나라도 실패하거나 스키마가 다르면 그 source의 새 데이터를 게시하지 않고 last-good을 유지합니다. 원본이 같으면 `unchanged`로 확인 시각만 갱신합니다.
- **저장**: SQLite(`bench-router.db`: sources / snapshots / observations)에 source별 원본을 최근 3개까지 보관합니다. 동시 refresh는 운영체제 파일 잠금으로 막습니다.
- **게시**: `snapshot.json`은 임시 파일에 쓰고 fsync한 뒤 `os.replace`로 교체합니다. 직전 유효본은 `snapshot.last-good.json`으로 옮기고, 재현용 사본은 `snapshots/`에 30일간 보관합니다.
- **route 쪽 처리**: snapshot이 없거나 손상됐으면 last-good을 쓰고, 그것도 없으면 근거 없이 제약을 통과한 default를 선택합니다. route는 refresh를 시작하지 않습니다.
- **Arena 중복 이름**: 원본에 같은 이름의 별개 항목이 있을 수 있습니다(실측 사례 있음). 이런 항목은 모집단에는 포함하되 `이름#rank=N`으로 구분해, 이름만으로 매칭되지 않게 합니다.

수동 import 형식(`--import FILE`):

```json
{"schema_version": "1.0", "evidence_id": "terminal_exact",
 "source_url": "https://www.tbench.ai/", "attribution": "Terminal-Bench",
 "published_at": "2026-10-01",
 "benchmark": {"suite": "terminal-bench", "version": "4.0", "subset": "core",
               "metric": "resolved_rate", "direction": "higher", "variant": "default",
               "dataset_revision": "v4.0.0", "evaluation_harness": "terminal-bench-official",
               "aggregation": "pass@1_mean_5"},
 "rows": [{"model_id": "claude-opus-5-5", "harness_id": "claude-code",
           "reasoning_effort": "high", "raw": 0.61}]}
```

`harness_id`는 모델을 실행하는 에이전트 스캐폴드(예: Claude Code)이며, `evaluation_harness`는 평가 실행·채점 시스템입니다. `model_id`에는 평가한 모델의 정확한 버전을 사용합니다. 벤치마크 버전·데이터셋 개정판·변형·평가 하네스·스캐폴드·추론 노력·집계 방식이 같은 점수끼리만 하나의 정규화 코호트에 넣습니다. `model_id`, `harness_id`, `reasoning_effort`가 프로필과 모두 일치해야 exact evidence로 인정합니다. 새 조건이 없는 기존 캐시의 exact 점수는 재import 전까지 `missing_conditions`로 제외합니다. 자동 수집 지표에서 확인할 수 없는 조건은 `null`로 남기며 모델 수준 대리 근거로만 사용합니다.

### 정기 실행 (예시, 설치하지 않음)

```ini
# ~/.config/systemd/user/bench-router-refresh.service
[Service]
Type=oneshot
WorkingDirectory=/path/to/bench-router-handoff
EnvironmentFile=%h/.config/bench-router/env
ExecStart=/usr/bin/python3 -m bench_router.cli refresh

# ~/.config/systemd/user/bench-router-refresh.timer
[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true
[Install]
WantedBy=timers.target
```

---

## live 위임과 결과 계약

`route`(dry-run 없이)는 다음 순서로 동작합니다.

1. PATH 가용성과 제약을 검사해 프로필을 선택합니다. Projects의 동일 이름 프로필 `agent/args`를 대조하고 설정·session을 고정합니다. 로그인·모델 접근은 실제 Agent에서 확인합니다.
2. `<cwd>/.bench-router/dispatch.lock`을 잡습니다. cwd당 동시에 하나만 위임합니다.
3. 같은 `(task_id, round)`의 receipt가 있으면 처리 방식이 갈립니다. 내용 hash가 같으면 **재전송 없이 collect**로 회수하고, 다르면 `conflict`입니다. 아직 정리되지 않은 다른 run이 있으면 새 위임을 막습니다(`unresolved_run`).
4. `run_id`(UUID)와 128-bit nonce를 만들고 receipt를 원자적으로 기록합니다. 선택 근거는 `decision.json`에 남깁니다.
5. Projects 버전과 이름 있는 프로필의 `agent/args`를 대조하고 `input.txt`를 원자 저장합니다.
6. 제출 **전에** receipt에 `submission_attempted`를 fsync합니다. 그다음 `thread start --kind checkout --repo CWD --task-file FILE`을 **한 번만** 호출하고 반환된 thread ID를 기록합니다.
7. Agent가 idle/done이 되면 결과 계약을 검사합니다. blocked면 화면(`diagnostic_tail`)을 반환합니다. timeout이나 stalled는 재전송하지 않고 `timed_out`/`delivery_uncertain`으로 남깁니다.

프롬프트 끝에는 실행 계약이 붙습니다. Agent는 `<cwd>/.bench-router/runs/<run_id>/`에 다음 두 파일을 써야 합니다.

- `result.md`: 결과·변경·검증·미완료 사항(최대 10 MiB, 비어 있으면 안 됨).
- `result.json`: 마지막에 한 번에 작성(최대 64 KiB).

```json
{"schema_version": "1.0", "run_id": "...", "nonce": "...", "profile_fingerprint": "...",
 "status": "success|partial|fail", "result_file": "result.md",
 "result_sha256": "<sha256 of result.md>",
 "checks": [{"command": "...", "outcome": "passed|failed|not_run", "notes": "..."}]}
```

라우터는 다음을 모두 확인한 뒤에야 `completed`를 반환합니다.
- run_id, nonce, 지문 일치
- 일반 파일이며 run 디렉터리 밖을 가리키는 symlink나 경로가 아님
- 크기 상한, UTF-8, JSON 유효성
- SHA-256 일치

`completed`는 "계약대로 결과를 받았다"는 뜻일 뿐, 작업 성공을 뜻하지 않습니다. 작업 결과는 `task_outcome`(Agent 자기보고)으로 따로 표시합니다. 실제 성공 여부는 Orchestrator가 검증한 뒤 `feedback`으로 기록하세요. 평가 중에 Agent가 `success`라고 보고했지만 실제로는 틀린 사례가 있었습니다.

run 디렉터리에는 `receipt.json`, `decision.json`, `input.txt`, `result.md`, `result.json`, `feedback.jsonl`이 남습니다. 출력의 `project`와 `thread_id`로 Projects에서 상태를 확인합니다. 진행 중인 thread를 정리하면 Agent도 종료될 수 있으므로 효과를 먼저 확인하세요.

## 병렬 위임과 협업 수준

`parallel --group FILE`은 하위작업 여러 개(`tasks`)와 같은 작업을 상위 N개 프로필에 동시에 맡기기(`fanout`)를 한 번에 처리합니다. agent마다 `<cwd>/.bench-router/worktrees/<group_id>/<label>` git worktree(브랜치 `br/<group_id>/<label>`, HEAD 기준)를 만들어 그 안에서 실행합니다. 각 worktree가 그 agent의 `task.cwd`가 되므로 receipt·잠금·재전송 방지·결과 계약은 `route`와 같습니다. 같은 group 파일로 다시 실행하면 기존 receipt를 회수할 뿐 프롬프트를 다시 보내지 않습니다.

```json
{"schema_version": "1.0", "group_id": "fix-pager", "cwd": "/home/me/project",
 "isolation": "shared", "fanout": 2, "max_parallel": 4,
 "tasks": [{"schema_version": "1.0", "task_id": "pager", "round": 1,
            "summary": "Fix paginate off-by-one", "prompt": "..."}]}
```

- `cwd`는 git 저장소 최상위여야 하며, task에는 `cwd`를 넣지 않습니다. `tasks × fanout ≤ 16`, `fanout` 1–8, `max_parallel` 1–16.
- fanout 프로필은 `selected`, 그다음 후보 순위 순으로 서로 다르게 고릅니다. 부족하면 `fanout_reduced` 경고가 붙습니다. label은 `<task_id>-<k>`입니다.
- **메인 repo를 각 Agent CLI에서 먼저 신뢰해야 합니다.** 상위 폴더가 신뢰돼 있어도 새 git repo는 다시 묻고, 그러면 agent start 단계에서 `blocked`가 됩니다(실측). 메인 repo를 한 번 신뢰하면 그 아래 worktree는 claude·codex 모두 다시 묻지 않았습니다.
- 미커밋 변경은 worktree에 들어가지 않습니다(`dirty_base` 경고). Agent에게는 커밋하지 말고 작업 트리에 변경을 남기라고 지시합니다. 비교·병합과 `git worktree remove`·브랜치 정리는 Orchestrator가 맡습니다.

| `isolation` | 동작 |
|---|---|
| `isolated` (기본) | worktree 격리만. 서로의 존재를 모름 |
| `shared` | 공용 scratchpad `<cwd>/.bench-router/groups/<group_id>/shared/`. agent는 자기 `<label>.md`·`<label>/`에만 쓰고 동료 노트를 읽어, 실패한 접근·발견·중간 실험 결과를 공유합니다. 두 설정의 프로필 args에 `--add-dir <repo>/.bench-router/groups`를 미리 설정합니다 |
| `deliberate` | `shared` + 협의 라운드. 1차 `completed` member가 2명 이상이면 각 `result.md`를 `shared/<label>.result.md`로 복사하고, 같은 worktree·프로필로 `round+1`을 보냅니다. 각 agent는 동료 결과를 검토해 자기 안을 고치고 `shared/<label>.vote.json`(`{"best": label, "reason": ...}`)을 씁니다. 라우터는 다수결로 `consensus.winner`를 냅니다(동률이면 `null`) |

출력은 member별 `profile`, `worktree`, `branch`, `rounds[]`(status, run_id, result_path, task_outcome, workspace_id)와 `consensus`이며, `groups/<group_id>/group.json`에도 남습니다. 전부 `completed`면 exit 0, 아니면 `partial_failure`(16), 같은 group이 이미 실행 중이면 `conflict`(14)입니다. 2차 라운드는 새 agent라서 1차 대화 맥락은 없습니다. 상태는 worktree와 scratchpad로 이어집니다.

---

## 테스트

```bash
python3 -m unittest test_p0 test_p1 test_p2 test_p3     # Linux/WSL2/Windows
```

| 파일 | 범위 |
|---|---|
| `test_p0.py` | 선택·입력 계약(V01–V10): 합성 기대값, 결측과 측정된 0, percentile, 결정성, 제약, near-tie 경계 |
| `test_p1.py` | 수집·캐시(V11–V18): 페이지 순회, 부분 실패 시 last-good, 해시 동일 시 no-op, HTTP 오류와 시간 상한, 잠금과 원자 게시, alias와 버전 cohort |
| `test_p3.py` | 병렬 위임(V30–V34): worktree 격리, fanout, shared `--add-dir`, deliberate 투표, 재실행 시 재전송 없음 (git 필요) |
| `test_p2.py` | 위임(V19–V29): argv 전달, 반환 ID 사용, 시작 실패, 전송 직전 상태, 결과 계약·경로 공격, timeout 후 재전송 없음, crash 복구, 충돌·잠금 |

현재 실행 테스트는 Projects 0.2.34 공개 CLI의 JSON 형태를 따르는 fake를 사용합니다. 아래의 직접 Herdr smoke 결과는 이전 실행 경로의 기록이며 Projects live 검증을 의미하지 않습니다. 실측 근거는 `docs/evidence/`에 있습니다(herdr help·API schema·skill, claude/codex `--help`).

---

## 검증 현황 (2026-10-12)

| 항목 | 결과 |
|---|---|
| 오프라인 테스트 | 35/35 통과 |
| AA 실호출 | 성공 (Free tier, index v4.3, 4페이지, 697개 모델) |
| Arena 실호출 | 성공 (revision `e16f9023…`). HF 장애 중에는 180초 상한에서 실패 처리되고 last-good 유지됨 |
| herdr + Claude Code / Codex live 위임 | 성공. 미해결 run 차단, 재전송 없음, 결과 해시 일치, 정리 뒤 collect 확인 |
| 두 후보를 점수로 비교한 live 선택 | general/balanced 작업에서 codex 선택 후 completed |
| `parallel` live (2026-10-13, deliberate, fanout 2: claude + codex) | 두 worktree에서 동시 실행, 2라운드 모두 completed, scratchpad 노트 공유·투표 확인(서로에게 1표씩 → `winner=null`), 메인 작업 트리 깨끗. 약 2분 |
| 작업군 비교 v1 (20 과제 × 2 프로필) | [eval/results/v1.md](eval/results/v1.md), 비용: [v1-cost.md](eval/results/v1-cost.md) |

작업군 비교 v1의 요약은 다음과 같습니다. 과제당 1회 실행이므로 통계적 결론은 아닙니다.

| 정책 | 성공 | 성공 1건당 API 환산 비용 |
|---|---|---|
| 고정 default (claude) | 20/20 | $0.234 |
| 저비용 우선 (codex) | 19/20 | $0.070 |
| bench-router | 20/20 | $0.217 |

과제가 쉬워 성공률이 천장에 붙었고, bench-router는 20개 중 18개에서 default와 같은 선택을 했습니다. 그중 12개는 근거 부족 때문입니다. 비용은 각 CLI 로그의 토큰을 실측해 API 단가로 환산한 값이며, 구독 실제 지출이 아닙니다(`eval/cost.py`).

### 평가 도구

```bash
python3 eval/workset.py            # 자체 검사: 초기 상태는 불합격, 참조 정답은 합격
python3 eval/run.py --tag T        # (작업, 프로필)마다 live 위임 + hidden check (herdr session 'breval')
python3 eval/cost.py --tag T       # 실행별 토큰·API 환산 비용
```

---

## 알려진 한계

- **근거 데이터 coverage가 낮습니다.** 최신 모델의 AA `coding_index`가 null이고, SWE/TB exact 데이터는 수동 import 전까지 없습니다. 그래서 coding_repo, terminal_ops, code_gen, webdev는 대개 default로 갑니다.
- `cost_tier`는 정책상 상대값입니다. 실측 비용으로 보정하지 않았습니다.
- 프로필 지문에는 CLI 버전이 들어가지 않습니다(`unknown`으로 고정).
- 결정·피드백은 SQLite가 아니라 run 디렉터리 파일로 남깁니다. 실행별 토큰 사용량은 라우터에 기록하지 않습니다(평가 도구에서만 측정).
- 원격 실행(`--machine`), 비동기 `--no-wait`, Agent 재사용, 임베딩·LLM 기반 분류(L2/L3)는 구현하지 않았습니다.
- `refresh`·dispatch 잠금은 Linux/macOS(WSL) 전용입니다.
- 프롬프트가 herdr argv로 전달되므로 프로세스 목록에 노출될 수 있습니다.

## 명세와 다른 점

| 명세(handoff 문서) | 구현 | 이유 |
|---|---|---|
| 결과 계약: `result.json`을 원자적으로 기록 | "마지막에 한 번에 작성, `sha256sum` 사용" | 원자적 쓰기 지시 때문에 Agent가 `mv`·검증 스크립트를 시도하다 승인 대기에 걸렸습니다. 라우터는 Agent가 끝난 뒤에만 검사하고 해시도 확인하므로 원자성은 실익이 없습니다 |
| 결정·feedback을 SQLite에 저장 | run 디렉터리의 `decision.json`, `feedback.jsonl` | 집계 요구가 생기기 전까지 파일로 충분합니다 |
| Arena parquet 처리용 의존성 허용 | HF datasets-server JSON API 사용 | 같은 행을 표준 라이브러리만으로 받을 수 있습니다 |
| conditional GET(304) | 원본 해시가 같으면 `unchanged` 처리 | AA/HF 문서에 ETag 관련 언급이 없습니다 |
| refresh 재시도 상한만 규정 | source별 전체 180초 상한 추가 | HF 장애 때 한 번의 refresh가 25분까지 늘어질 수 있었습니다 |

## 라이선스와 출처

- Arena 데이터: LMArena `leaderboard-dataset`, CC BY 4.0. 출처는 snapshot의 `sources.*.attribution`에 남습니다.
- AA 데이터: Artificial Analysis. 공유하거나 표시할 때 출처를 밝혀야 합니다.
- API 키는 설정 파일(`env`, 권한 600)에만 두고, 저장소·로그·출력에는 남기지 않습니다.
