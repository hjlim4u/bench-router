# 다중 기준 라우팅 계약

갱신: 2026-10-24. 구현: `routing.py`, `decision.py`, `cli.py`, `herdr.py`, `parallel.py`. 초기 2026-10-13 설계의 후보 평가·지표·제약 경계를 유지하며, 제거된 legacy 자동 선택 절차는 현재 계약에 포함하지 않는다.

## 0. 목표와 책임

Router는 사실 정리·필수 제약·공식 가이드 적합성·비교 가능한 평가·선택 기록·실행을 제공한다. 상위 Orchestrator는 작업 분해·팀 구성·최종 선택·전체 예산·결과 채택을 결정한다. 범용 플러그인 로더·규칙 엔진·단위 변환 DSL·workflow scheduler는 없다.

기본 선택은 [vendor-guided 정책 6](vendor-guided-routing.md)이다. 복수 적합 후보는 상위 선택을 요구하고, 가중합·near-tie·default/fallback 순위로 줄이지 않는다.

## 1. 계약 A — 후보 평가와 선택의 분리

### 1.1 공통 경계

| 함수 / CLI | 책임 |
|---|---|
| `routing.assess()` | ID순 전 프로필 facts·제약·선택적 benchmark 평가. 선택하지 않음 |
| `routing.evaluate()` / `evaluate --format 2` | 기본 schema 2.0의 사실·제약·category benchmark quality/coverage |
| `routing.evaluate_v1()` / `evaluate --format 1` | schema 1.0의 candidates/excluded 호환 형태 |
| `decision.evaluate()` / `evaluate --format 3` | schema 4.0의 단계별 의미 판단·후보 적합성·관측·비교·진단 |
| `decision.bind()` / `select` | 완료된 format 3 평가에서 상위 선택 기록 6.0 생성 |
| `routing.route()` → `decision.route()` | 정책 6의 판단 패킷·제한된 단일 후보 선택 5.0·선택 재생 |
| `routing.apply_selection()` | selection 2.0 또는 `--profile`의 명시적 override; 현재 제약 검사 |

CLI `--format 3`은 JSON schema 버전 `4.0`과 다르다. `select`는 format 1·2 결과를 받지 않는다. 모든 evaluate 형식은 오프라인이며 worker 실행·파일 쓰기·판단 API 호출을 하지 않는다.

### 1.2 기본 benchmark 평가

`assess()`는 제약을 통과한 후보에만 `benchmark_evaluation()`을 직접 호출한다. 평가 결과는 `status: ok|insufficient|unavailable`, `quality`, `coverage`, `exact_evidence_weight`, `evidence`다. 출력 변환 시 `coverage_band`를 붙인다. 근거가 없어도 후보는 남으며 하드 탈락은 제약이 결정한다.

coverage는 benchmark 근거 충족도이며 전체 판단의 확신도가 아니다. category 가중치·percentile·quality 식은 [데이터 명세](../03_ROUTING_AND_DATA_SPEC.md)에 있다. `score`, `legacy_score`, `cost_proxy`는 출력하지 않고 후보 순서는 profile ID순이다. 다른 평가기를 실제 추가할 때 `evaluations`에 이름 하나와 함수 호출을 추가한다. 별도 `EVALUATORS` registry는 없다.

### 1.3 evaluate 출력 2.0

| 필드 | 의미 |
|---|---|
| `inputs`, `assessment_digest` | task/config/snapshot/context·기본 정책·지표 registry 버전의 정적 입력과 SHA-256 hex |
| `task_facts`, `max_estimated_cost_usd` | task 지표와 호출 allowance |
| `candidates` | 모든 프로필 ID순; eligible·constraints·facts·unrecognized_metrics·evaluations |
| `classification`, `sources`, `warnings` | 기본 category 분류·소스 날짜·경고 |
| `availability_verified` | evaluate에서는 false; live dispatch에서 재검사 |

`evaluations`는 하드 탈락 후보에서 `{}`다. `constraints`는 적용한 통과·실패를 모두 포함한다. format 1은 candidates/excluded 형태를 유지하지만 순위·자동 선택을 제공하지 않는다.

### 1.4 vendor-guided 후보 평가와 선택

format 3은 `analysis → 적격 벤더별 guidance → benchmark(비교가 있을 때)`를 재생한다. 판단 미완료는 `decision_required`(17), 완료된 평가는 `status: ok`다. pending 응답의 최종 `assessment_digest`는 null이며 현재 request digest는 `decision.request_digest`다.

완료된 schema 4.0은 전 프로필의 hard eligibility·suitability·facts·sparse observations/missing·후보별 diagnostics를 제공한다. 공유 `evidence`에는 unit 정의·comparisons·comparison_scopes·relevance·prefiltered_units·auxiliary_units를 둔다. 선택용 검색에는 표 표시용 12 unit 제한을 적용하지 않는다. `decision`은 재생 원본, `recommendation`은 제한된 단일 후보 추천 또는 기권이다. 자세한 필드와 응답 작성은 [상위 연동](orchestrator.md#vendor-guided-candidate-assessments-and-upstream-choices)을 따른다.

## 2. 계약 B — 지표(facts)의 의미·유효성

### 2.1 지표 정의표

`routing.METRICS`가 등록 지표의 대상·타입·단위·최대 수명을 정의한다. 등록 항목은 tokens.estimated_input/output, tokens.required_context, price.input/output_usd_per_mtok, cost.estimated_usd, task.complexity다. latency.p50_ms 등 다른 namespaced 지표는 현재 미등록이며 전달만 한다.

선호 방향이나 지표 간 가중치는 registry에 없다. 등록 지표의 타입·단위가 다르면 입력 오류이며 자동 단위 변환을 하지 않는다. 미등록 namespaced 지표는 형식만 검사하고 전달하며 제약·평가에 사용하지 않는다.

### 2.2 관측값 형식 (context 2.0)

```json
{"schema_version": "2.0",
 "task_metrics": {"task.complexity": {"value": "high", "source": "orch-classifier@3", "reason": "cross-file change"}},
 "max_estimated_cost_usd": 0.25,
 "profiles": {"my-codex": {"metrics": {
   "tokens.estimated_input": {"value": 40000, "unit": "tokens", "source": "orch-estimator@2"},
   "price.input_usd_per_mtok": {"value": 1.25, "unit": "usd/mtok", "source": "example-price",
                              "observed_at": "2026-10-24T00:00:00Z"},
   "latency.p50_ms": {"status": "missing", "reason": "not_measured", "source": "telemetry"},
   "acme.vibe": {"value": 3, "unit": "stars", "source": "experiment@1"}
 }}}}
```

위 가격은 형식 예시다. 프로필 키는 설정된 ID여야 한다. 지표는 모두 선택적이며 각 관측에는 `source`가 필요하다. 값이 있으면 `value`와 정의된 `unit`, 결측이면 `status: missing`과 `reason`을 쓴다. `value: null`은 거부한다.

수명이 있는 지표는 `observed_at`이 필요하고 `expires_at`으로 더 짧은 수명을 줄 수 있다. 가격은 30일이다. 계산된 facts에는 fresh/expired/missing을 표시한다. 만료·결측은 0이 아니며 계산에서 제외한다. 해당 값을 쓰는 제약이 없으면 결측 자체로 탈락시키지 않는다.

### 2.3 context 1.0 호환

`complexity`, `estimated_*_tokens`, `required_context_tokens`, `price{..., as_of}`, `signals`는 context 2.0으로 변환해 같은 검증 경로를 탄다. `context_hash`와 `decision_context`는 변환 후 형태를 사용한다. 과거 1.0 가격도 30일 만료를 적용한다.

## 3. 계약 C — 제약 (필수 조건)

### 3.1 제약과 선호

제약 실패는 점수·상위 선택·provisional 수용으로 상쇄할 수 없다. 비용·지연 trade-off와 전체 예산은 상위 정책이다. `priority` 입력은 호환상 받지만 자동 비용 차감·near-tie 정렬에 사용하지 않는다.

### 3.2 이름 붙은 검사

`routing.CONSTRAINTS`는 enabled, task_exclusion, cost_tier, context_capacity, capabilities, local_only, availability, estimated_cost다. 검사 함수 `(profile, task, x)`는 적용한 통과·실패 결과 목록을 반환한다. 결과의 검사 이름은 `constraint`다.

```json
{"constraint": "estimated_cost", "passed": false, "code": "estimated_cost_exceeds_max",
 "metric": "cost.estimated_usd", "observed": 0.20, "limit": 0.05, "on_missing": "exclude"}
```

context capacity는 task 최소값과 context 필요값 중 큰 값으로 검사한다. 용량 불명은 양수 요구를 충족하지 않는다. 비용 상한이 있는데 견적이 missing/expired면 `estimated_cost_unknown`으로 탈락한다. 적용하지 않는 제약은 불필요한 결측 실패를 만들지 않는다.

### 3.3 등급과 달러 상한

`max_cost_tier`(low/medium/high)와 `max_estimated_cost_usd`는 독립이며 둘 다 지정하면 둘 다 통과해야 한다. 등급 기본 high는 등록된 모든 등급을 허용한다. 견적이 있다고 등급을 자동 무시하지 않는다.

### 3.4 비용·토큰·quota

1. fresh `cost.estimated_usd` 공급자 견적이 우선이다.
2. 없으면 `(input tokens × input rate + output tokens × output rate) / 1,000,000`으로 계산한다(`source: router:io2-v1`).
3. 입력이 없거나 만료되면 missing과 원인을 반환한다. 캐시·추가 요금은 상위 견적에 반영한다.

예상 토큰은 이번 호출의 비용 입력, profile.context_tokens는 정적 수용량이다. 호출 allowance를 팀 전체 budget이나 실제 요금 보장으로 읽지 않는다. live에서는 CodeBurn의 provider 상태·모든 quota window 소진을 선택적으로 검사한다. Antigravity는 `agy models`의 실제 모델 목록을 검사한다. CodeBurn 실패는 PATH 검사로 폴백하되 agy 모델 검사는 유지한다. N개 worker를 위한 quota 예약은 없다.

## 4. 계약 D — 판단 기록과 실행 연결

### 4.1 digest

format 1·2의 digest는 task_hash·config_hash·snapshot_id·context_hash·router_policy_version·metric_registry_version을 묶는다. now·가용성·freshness는 제외하고 실행 직전 다시 검사한다.

format 3의 schema 4.0 digest는 `canonical_hash({"schema_version":"4.0", "decision":...})`다. decision에는 task·전체 입력·단계별 request/digest/답변·관측·관련성·진단이 있다. 단계별 request digest는 그 단계의 실제 의존성만 묶는다. 시간 경과 값 자체는 제외하지만 만료에 따른 freshness 변경은 재검증 대상이다. 파일 본문 전체를 hash하는 계약은 아니다.

### 4.2 selection 입력

| schema | 생성과 검증 |
|---|---|
| 2.0 | format 1·2의 digest + profile·외부 policy·reason. 의미 판단 override로 `selection_legacy` 경고 |
| 5.0 | 정책 6의 자동 단일 후보 + 전체 decision. 추천 profile에 고정 |
| 6.0 | 완료된 format 3 평가에서 `select`로 생성. 외부 policy·reason·accept_provisional·전체 decision |

6.0은 documented 후보 또는 명시적 수용이 있는 provisional/alternative 후보를 선택한다. unsuitable·미평가·hard 탈락은 거부한다. 수용은 pending 조건을 해소하지 않는다. `select` 출력은 `selection` 객체를 감싼 schema 1.0 응답이므로 그 객체만 `--selection` 파일에 저장한다.

`--selection`과 `--profile`은 배타적이며 `--decision-response`도 함께 쓸 수 없다. `--profile`은 기록 없는 override로 `selection_unrecorded`를 경고한다. 기존 vendor-guided schema 3.0·4.0이나 정책 1–5 기록은 새 판단에 재사용하지 않는다.

5.0·6.0 실행은 provider를 새로 호출하지 않고 저장된 단계를 재생하며 현재 제약·가용성을 검사한다. 근거 입력이 달라지면 `stale_assessment`(14), 잘못된 입력 형식·미지원 schema는 validation(2)다. 5.0의 profile만 바꿔 재사용할 수 없다.

### 4.3 멱등성

같은 canonical cwd·task_id·round는 기존 receipt를 먼저 확인한다. 같은 semantic hash면 회수하고 다른 내용은 conflict다. 지정 profile이 다르면 `profile_round_conflict`, 같은 profile의 선택 기록만 다르면 회수와 `selection_differs_from_recorded` 경고다. 의도적 새 실행은 상위가 부분 효과를 검토한 뒤 새 round로 요청한다. timeout은 취소·재전송 허가가 아니다.

### 4.4 decision.json

run의 `decision.json`은 route 응답에 selection과 기본 evaluate 2.0 `assessment`를 더한 형태다. vendor-guided의 원본 근거는 `selection.decision`에도 보존한다. 별도 decision 2.0 wrapper는 없다. 실행 응답에서는 전체 assessment를 제외한다. 출력 전용 `selection.source`는 재입력 전에 제거한다.

## 5. 계약 E — 병렬 경로

group 1.0은 task × fanout으로 정책 6을 반복하고 앞서 고른 profile은 다음 비교에서 제외한다. 복수 적합 후보가 남으면 판단·상위 선택을 요청하며 자동 기본값으로 fanout하지 않는다.

group 2.0은 task별 `context`와 `selections`의 순서 있는 실행 목록을 받는다. selection 2.0·5.0·6.0을 사용할 수 있고 같은 profile도 반복할 수 있다. task당 1–8개·group 전체 최대 16개며 `fanout` 키는 허용하지 않는다. `max_parallel`은 1–4, 사용자 공유 admission도 활성 4개다.

상위는 group.cwd와 원래 prompt로 평가한다. plan 단계에서 모든 선택의 digest를 확인하고 stale 항목 하나면 전체 미실행이다. 모든 선택이 끝나기 전에는 worktree·group 파일·worker를 만들지 않는다. worker의 cwd·협업 문구는 실행 시 달라지므로 내부적으로 이미 검사한 task hash만 조정하고 현재 제약·가용성은 재검사한다.

동결된 plan과 receipts로 같은 group을 회수한다. 입력 변경·목록 재정렬은 conflict다. member rounds는 `delivery_state`·`reassignment`를 보존한다. 반복 selection도 별도 label·worktree·receipt·한도를 사용한다. team budget·집계·채택·재시도는 상위 책임이다.

## 6. 버전과 문서

| 계약 | 현재 값 |
|---|---|
| task / result / route envelope | 1.0 |
| context / group | 2.0, 입력 1.0도 수용 |
| evaluate 기본 / 호환 | schema 2.0 / 1.0 |
| evaluate `--format 3` | schema 4.0 |
| vendor-guided 정책 / selection | policy 6 / 자동 5.0·외부 6.0 |
| 기본 평가·snapshot 정책 / 지표 registry | routing.POLICY_VERSION 1.0 / METRIC_REGISTRY_VERSION 1 |

정책 버전·CLI format 번호·JSON schema 번호는 독립이다. 공식 가이드는 `guidelines.toml`의 별도 버전과 원문으로 고정한다. 상세 운영 예는 [reference](reference.md), 현재 검증은 [implementation-status](implementation-status.md), 상위 사용법은 [orchestrator](orchestrator.md)를 따른다.

## 7. 지표 추가와 검증

전달만 할 namespaced 지표는 registry 수정 없이 사용할 수 있다. 정식 타입·단위·수명이 필요하면 `METRICS`, 필터가 필요하면 `CONSTRAINTS`의 함수·입력 상한·focused fixture를 함께 추가한다. 단순 예시 지연 상한을 실제 지원 입력처럼 문서화하지 않는다. 순위 정책은 상위에서 구현한다.

전체 검증 명령은 `python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn`이다. 현재 선택·stale·재생·부분 실패·중복 방지의 기준은 [검증 문서](../06_VALIDATION_AND_OPEN_ITEMS.md)에 있다. Projects live·workflow 품질·팀 예산 검증은 오프라인 계약 검증과 별도다.
