# 다중 기준 라우팅 계약 설계

작성일: 2026-10-13. 입력: [확장성 점검 보고서](routing-extensibility-review.md). 상태: 설계안, 구현 전.

## 0. 목표와 비목표

목표: 새 지표(지연, 성공률, 쿼터, 캐시 비용 등)를 추가할 때 **표 한 줄(지표 정의) + 필요하면 함수 하나(제약)** 만 바꾸면 되는 구조. 기존 자동 `route` 결과는 보존.

비목표 (보고서 결론 유지):

- 범용 플러그인 로더, 규칙 엔진, 비용 계산 DSL, 단위 변환표.
- Router 내부 종합 점수. 지표 간 trade-off와 최종 선택은 Orchestrator 소유.
- 가격·쿼터 수집기. 값은 Orchestrator가 공급한다.
- 작업 전체 예산·병렬 예약 관리. Orchestrator 소유 (§5).

책임 경계 한 줄 요약: **Router = 사실 정리 + 필수 제약 검사 + 판단 기록 + 실행.** Orchestrator = 순위·선택·예산.

```
task + config + snapshot + context
          │
          ▼
   assess()  ── facts (지표 정규화·유효성)
          │   ── constraints (통과/탈락, 구조화된 사유)
          │   ── evaluations {"benchmark": ...}   ← 기존 계산, 이름만 붙임
          ▼
   assessment  ──► evaluate 출력 (Orchestrator가 선택)
          │
          └──► legacy_select()  ──► route 출력 (기존 자동 선택, 호환)
```

## 1. 계약 A — 후보 평가와 선택의 분리

### 1.1 구조 변경

현재 `evaluate()`가 `route()`를 호출하고 선택을 지운다. 방향을 뒤집는다.

| 함수 | 역할 | 비고 |
|---|---|---|
| `assess(t, cfg, mapping, snap, snap_warnings, now, availability, context)` | 전 프로필에 대해 facts·constraints·evaluations 계산 | 새 공통 경계. 선택하지 않음 |
| `legacy_select(assessment, t, cfg)` | 기존 `select()` 그대로 적용 | `POLICY`, `lambda_cost`, near-tie, default/fallback 그대로 |
| `route()` | `legacy_select(assess(...))` → 기존 1.0 출력 형태로 변환 | 출력 바이트 단위 호환 목표 |
| `evaluate()` | `assess()` 결과를 2.0 출력으로 반환 | 정렬은 profile ID순 |
| `pin_selection()` | assessment에서 지정 프로필이 제약 통과했는지 확인 | §4 selection 기록 추가 |

### 1.2 평가기 = 이름 붙은 함수

확장점은 후보의 `evaluations` 맵(이름 → 결과)이다. 평가기가 1개인 동안 `assess()`가 `benchmark_evaluation()`을 직접 호출한다. 두 번째 평가기가 생기면 그 호출 옆에 한 줄 추가 (그때 공통 시그니처가 필요하면 dict로). 등록 API·로더 없음.

`benchmark_evaluation`은 현재 `route()` 루프 안의 evidence/coverage/quality 계산을 그대로 옮긴 것. 결과 필드:

```json
"benchmark": {"status": "ok|insufficient|unavailable", "quality": 0.71, "coverage": 0.8,
              "coverage_band": "full", "exact_evidence_weight": 0.6, "evidence": [...],
              "legacy_score": 0.56, "cost_proxy": 0.5}
```

- `coverage`는 **benchmark 근거 충족도**만 뜻한다. 전체 판단 정보의 충족도가 아니다.
- `legacy_score`는 기존 `score`와 같은 값. 이름으로 범위를 드러낸다. 종합 순위 아님.
- 벤치마크가 없어도 후보는 남는다 (`status: "unavailable"`). 탈락은 오직 constraints가 결정.

새 평가기 예 (필요해질 때만): feedback 기록 기반 `history` 성공률 → `EVALUATORS["history"] = ...` 한 줄 + 함수. 평가기는 서로의 결과를 읽지 않는다 (benchmark 점수 불변 보장).

### 1.3 evaluate 출력 2.0

```json
{"schema_version": "2.0", "status": "ok", "task_id": "...", "round": 1,
 "assessment_digest": "sha256:...",           // §4
 "inputs": {"task_hash": "...", "config_hash": "...", "snapshot_id": "...", "context_hash": "...",
            "router_policy_version": "1.0", "metric_registry_version": "1"},
 "task_facts": {"task.complexity": {...}},
 "candidates": [                               // profile ID순, 전 프로필
   {"profile": "a", "profile_fingerprint": "...", "eligible": true,
    "constraints": [ ... §3.2 결과 (통과 항목 포함) ... ],
    "facts": {"cost.estimated_usd": {...}, "latency.p50_ms": {...}},
    "unrecognized_metrics": {"acme.vibe": {...}},
    "evaluations": {"benchmark": {...}}}],
 "classification": {...}, "sources": {...}, "warnings": [...]}
```

결정:

- `candidates`와 `excluded` 분리 대신 단일 목록 + `eligible`. Orchestrator가 탈락 사유의 관측값·기준값을 같은 위치에서 본다.
- `route` 출력은 1.0 그대로 (`score`, `quality`, `coverage`, `cost_proxy`, `excluded`). 의미 변경 없음.
- evaluate 1.0 출력 소비자: `evaluate --format 1` 플래그로 한 버전 동안 유지 후 제거. ponytail: 플래그 하나로 이행, 버전 협상 없음.

## 2. 계약 B — 지표(facts)의 의미·유효성

### 2.1 지표 정의표

새 지표 추가의 **유일한 필수 수정 지점**.

```python
# ponytail: 코드 내 상수. 사용자 튜닝 대상이 아닌 계약이라 TOML로 빼지 않음.
METRIC_REGISTRY_VERSION = "1"
METRICS = {
  # id: (applies_to, kind, unit, max_age_hours | None)
  "tokens.estimated_input":   ("profile", "int",    "tokens", None),
  "tokens.estimated_output":  ("profile", "int",    "tokens", None),
  "tokens.required_context":  ("profile", "int",    "tokens", None),
  "price.input_usd_per_mtok": ("profile", "number", "usd/mtok", 24 * 30),
  "price.output_usd_per_mtok":("profile", "number", "usd/mtok", 24 * 30),
  "cost.estimated_usd":       ("profile", "number", "usd", None),     # Orchestrator 견적 (§3.4)
  "task.complexity":          ("task",    "enum:low|medium|high", None, None),
}
```

| 필드 | 의미 |
|---|---|
| `applies_to` | `task` = 작업 특성 (복잡도). `profile` = 이 작업에 대한 프로필별 관측·추정. 섞어 넣으면 입력 오류 |
| `kind` | `number`, `int`, `bool`, `enum:a\|b`. 검증만 함 |
| `unit` | 정규 단위 1개. 입력 단위가 다르면 **입력 오류**. 변환 안 함 |
| `max_age_hours` | `observed_at` 기준 수명. `None` = 만료 없음. 지표마다 다름 (가격 30일, 지연이라면 1시간 등) |

**선호 방향(“클수록 좋다”)은 정의표에 넣지 않는다.** 그건 정책이다. Router는 순위를 매기지 않으므로 필요 없다.

ponytail: 단위 변환 없음. ms/s 혼용이 실제로 생기면 그 지표만 `unit` 목록 + 배수로 확장.

### 2.2 관측값 형식 (context 2.0)

```json
{"schema_version": "2.0",
 "task_metrics": {"task.complexity": {"value": "high", "source": "orch-classifier@3", "reason": "..."}},
 "max_estimated_cost_usd": 0.05,
 "profiles": {
   "my-codex": {"metrics": {
     "tokens.estimated_input":   {"value": 40000, "unit": "tokens", "source": "orch-estimator@2"},
     "price.input_usd_per_mtok": {"value": 1.25, "unit": "usd/mtok", "source": "vendor-page",
                                  "observed_at": "2026-10-10T00:00:00Z"},
     "latency.p50_ms":           {"status": "missing", "reason": "not_measured", "source": "orch-telemetry"},
     "acme.vibe":                {"value": 3, "unit": "stars", "source": "x"}
   }}}}
```

| 키 | 필수 | 규칙 |
|---|---|---|
| `value` | `status`가 `missing`이 아니면 필수 | `kind` 검사. `null` 금지 — 결측은 `status`로 |
| `unit` | 정의표에 unit이 있으면 필수 | 정의표 값과 정확히 일치 |
| `source` | 필수 | 출처·산출 버전 문자열 (`name@version` 권장) |
| `observed_at` | `max_age_hours`가 있는 지표는 필수 | ISO-8601 UTC |
| `expires_at` | 선택 | 공급자가 더 짧은 수명을 알 때. `max_age_hours`보다 우선하지 않고 더 이른 쪽 적용 |
| `status` | 선택, 기본 `ok` | `ok` \| `missing`. `missing`이면 `reason` 필수 |
| `reason` | 선택 | `task.complexity` 등 설명용 |

Router가 계산해 facts에 붙이는 필드: `freshness: "fresh" | "expired" | "missing"`, `age_hours`.

규칙:

- 결측은 0이 아니다. `missing`/`expired` 값은 계산(예: 비용)에 쓰지 않는다.
- **미등록 지표**는 형식 검사(`value`/`source` 존재, id 네임스페이스) 후 `unrecognized_metrics`로 그대로 전달. 제약·평가에 절대 쓰지 않는다. → Orchestrator는 Router 배포 없이 실험 지표를 흘려 보낼 수 있다.
- 만료·결측 자체로 후보를 제외하지 않는다. 제외 여부는 그 지표를 **쓰는 제약**이 정한다 (§3.2 `on_missing`).
- 핵심 필드(`schema_version`, `profiles`, 지표 항목 키)는 계속 엄격 검증 — 오타 검출 유지. 확장은 `metrics` 맵 안에서만.

### 2.3 1.0 context 호환

`validate_context`가 1.0을 받으면 2.0으로 변환 후 동일 경로 처리:

| 1.0 | 2.0 |
|---|---|
| `complexity {level, reason}` | `task_metrics["task.complexity"] {value: level, reason, source: "context-1.0"}` |
| `estimated_input_tokens` 등 | `tokens.*` |
| `price {input…, output…, source, as_of}` | `price.*`, `observed_at = as_of` |
| `signals[name] {value, unit, source}` | `metrics[name]` (대부분 미등록 → `unrecognized_metrics`) |

`context_hash`는 **변환 후** 2.0 형태로 계산. 1.0 출력의 `context_facts`는 변환 결과에서 역으로 채워 route 1.0 출력 유지.

## 3. 계약 C — 제약 (필수 조건)

### 3.1 제약과 선호의 분리

- Router는 **제약만** 평가한다. 제약 실패는 어떤 점수로도 상쇄되지 않는다.
- 선호(비용 낮을수록, 지연 짧을수록)는 Router 출력에 없다. `legacy_select`의 `priority`/`lambda_cost`는 호환 정책 내부 개념으로 격리.

### 3.2 제약 = 이름 붙은 함수

```python
# ponytail: dict가 확장점. 새 지표로 거르려면 함수 하나 추가.
CONSTRAINTS = {
  "enabled":            ...,  # profile.enabled
  "task_exclusion":     ...,  # task.exclude_profiles
  "cost_tier":          ...,  # task.constraints.max_cost_tier  (legacy proxy, §3.3)
  "context_capacity":   ...,  # max(task.min_context_tokens, tokens.required_context) vs profile.context_tokens
  "capabilities":       ...,
  "local_only":         ...,
  "estimated_cost":     ...,  # context.max_estimated_cost_usd vs cost.estimated_usd (§3.4)
  "availability":       ...,  # live probe 결과
}
# 각 함수: (profile, task, x) -> 실패 결과 목록 ([] = 통과 또는 미적용)
# x = {context, facts, cost(Decimal), availability}
```

구현 상태 (1단계): 실패 결과만 `constraint_failures`에 기록. 통과 결과 기록은 evaluate 2.0(3단계)에서 추가. 1단계에서는 기존 `context_capacity`를 `min_context`(task)와 `required_context`(context) 두 제약으로 유지 — 사유 코드 중복까지 1.0 출력과 동일하게 하기 위함. 3단계에서 하나로 합친다.

결과 형식 (통과도 기록 — explain과 decision이 같은 근거를 보여줌):

```json
{"name": "estimated_cost", "passed": false, "code": "estimated_cost_exceeds_max",
 "metric": "cost.estimated_usd", "observed": 0.20, "limit": 0.05, "on_missing": "exclude"}
```

- `code`는 기존 탈락 사유 문자열을 그대로 쓴다 (`context_insufficient`, `estimated_cost_unknown` 등). route 1.0의 `excluded[].reasons`는 실패한 결과의 `code` 목록 → 호환.
- `on_missing`: 제약이 쓰는 지표가 missing/expired일 때 동작. 각 제약 함수에 상수로 명시 (`exclude` | `pass`). 현재 동작 기준:
  - `estimated_cost`: `exclude` (현재 `estimated_cost_unknown`과 동일).
  - `context_capacity`: 프로필 용량 미설정이면 `exclude` (`context_unknown`, 현재와 동일).
- 제약이 적용되지 않으면 (예: `max_estimated_cost_usd` 미지정) 결과를 남기지 않는다. 쓰지 않는 지표가 없다고 탈락시키지 않는다.

### 3.3 등급 vs 달러 상한

둘 다 독립 제약이며 동시 지정 시 **둘 다** 통과해야 한다 (현재 동작 유지, 문서로 확정).

- `max_cost_tier`는 실제 가격이 없을 때 쓰는 legacy proxy.
- 실제 견적만으로 거르고 싶은 Orchestrator는 `max_cost_tier`를 지정하지 않는다 (기본 `high` = 무제한).
- 자동 대체(“견적이 있으면 등급 무시”)는 하지 않는다. 암묵 규칙이라 3시에 해독해야 할 대상.

### 3.4 비용·토큰 범위

| 개념 | 위치 | Router 처리 |
|---|---|---|
| 컨텍스트 수용량 | profile `context_tokens` (정적 설정) | `context_capacity` 제약 |
| 이번 호출 예상 사용량 | `tokens.estimated_input/output` | 비용 계산 입력 |
| 이번 호출 비용 상한 | `context.max_estimated_cost_usd` | `estimated_cost` 제약 (단건 allowance) |
| 작업 전체 잔여 예산, 병렬 예약, 재시도 누적 | Orchestrator | **처리 안 함.** 필요하면 Orchestrator가 남은 예산을 단건 allowance로 나눠 전달 |
| 계정 쿼터 | — | 유보 (기존 합의) |

`cost.estimated_usd` 결정 순서:

1. Orchestrator가 `cost.estimated_usd`를 직접 주면 그대로 사용 (캐시·부가 비용을 반영한 공급자 견적). `source`에 산출 버전 포함.
2. 없으면 Router가 계산: `(in × price.in + out × price.out) / 1e6`, `source: "router:io2-v1"`. 입력 지표 중 하나라도 missing/expired면 결과도 `missing` (`reason: "estimate_or_price_missing"` 또는 `"price_expired"`).

ponytail: 계산식은 입출력 2요율 한 가지. 캐시 요율이 필요해지면 1번 경로(공급자 견적)로 해결. 계산 항목 추가는 그래도 부족할 때만.

## 4. 계약 D — 판단 기록과 실행 연결

### 4.1 assessment digest

```
assessment_digest = canonical_hash({task_hash, config_hash, snapshot_id, context_hash,
                                    router_policy_version, metric_registry_version})
```

- 기존 해시 재사용. 정적 입력만 포함.
- **포함하지 않음**: `now`, availability, freshness. 시간·환경에 따라 변하는 값은 실행 직전 재검사 대상이지 동일성 비교 대상이 아니다.

### 4.2 selection 입력

`route --profile`에 선택 근거를 함께 받는다.

```bash
bench-router route --task task.json --context context.json --selection selection.json
```

```json
{"schema_version": "2.0", "profile": "my-codex",
 "assessment_digest": "sha256:...",
 "policy": {"id": "orch-cost-latency", "version": "4"},
 "reason": "lowest estimated cost among candidates with benchmark coverage >= 0.5"}
```

실행 시 처리:

1. `assess()` 재실행 (live availability 포함, freshness는 현재 시각 기준).
2. digest 불일치 → `status: "stale_assessment"`, exit 14 (conflict 계열), 실행 안 함. 응답에 새 digest 포함 → Orchestrator는 재평가 후 재선택.
3. 지정 프로필이 제약 실패 → `no_eligible_profile` (현재와 동일) + 실패한 제약 결과.
4. 통과 → `decision.json`에 assessment 전체 + selection 원문 기록 후 실행.

`--profile` 단독 사용은 유지 (selection 없음 → `selection_unrecorded` 경고, digest 검사 생략). 다음 메이저 버전에서 제거 후보.

### 4.3 멱등성 (변경 없음, 명시)

- 같은 `(task_id, round)`는 최초 receipt를 회수한다. 새 context·selection으로 재호출해도 재실행 안 함.
- 새 판단으로 다시 실행하려면 **새 round**.
- 같은 round에 다른 selection이 오면: profile이 다르면 기존 `profile_round_conflict`, 같으면 회수 + selection 차이를 `selection_differs_from_recorded` 경고로 알림.

### 4.4 decision.json

```json
{"schema_version": "2.0", "assessment": {...§1.3...},
 "selection": {...§4.2 원문 또는 {"mode": "legacy_auto", "selection_mode": "benchmark_score"}...},
 "selected": {"profile": "...", "profile_fingerprint": "..."}, "run_id": "..."}
```

자동 `route`도 같은 형식으로 기록 (`selection.mode = "legacy_auto"`). explain은 이 구조만 읽어서 출력 → 사람용 설명과 저장 기록이 같은 근거를 보여줌.

## 5. 계약 E — 병렬 경로

### 5.1 기본 경로 결정

**권장: 다중 기준 선택이 필요한 병렬화는 Orchestrator가 단건 `route --selection`을 여러 번 호출해 수행한다.** group 경로는 worktree 격리·collab 텍스트·deliberate 투표 기능 때문에 유지하되, 선택은 두 모드만 지원:

| group 입력 | 동작 |
|---|---|
| `selections` 없음 | 기존 legacy: `route()` 선택 + 다음 후보 fanout. 단, 후보 순서는 `legacy_score`순 (현재와 동일) |
| task별 `context` + `selections` 배열 | 지정 프로필 그대로 fanout (`fanout` = 배열 길이). 계획·실행 모두 §4.2와 같은 `assess` + digest 검사 |

```json
{"schema_version": "2.0", "group_id": "g1", "cwd": "/repo", "isolation": "isolated",
 "tasks": [{"task": {...}, "context": {...},
            "selections": [{"profile": "a", "assessment_digest": "...", "policy": {...}, "reason": "..."},
                           {"profile": "b", ...}]}]}
```

### 5.2 예산

- 각 worker의 `max_estimated_cost_usd`는 그 호출의 allowance다. 같은 잔여 예산을 모든 worker에 그대로 주면 총합 제한이 안 된다 — 분배는 Orchestrator 책임 (문서에 명시).
- deliberate 후속 round는 프롬프트가 늘어 견적이 바뀐다. Router는 재견적하지 않는다: 후속 round에 `estimate_round1_only` 경고. 정확한 비용 관리가 필요하면 Orchestrator가 round를 직접 진행.

ponytail: 예약→실행→정산 원장 없음. 전체 예산 준수를 Router가 보장해야 하는 요구가 생기면 그때 별도 설계 (보고서 §3 조건 유지).

## 6. 버전과 문서

| 항목 | 값 | 바뀌는 조건 |
|---|---|---|
| task schema | `1.0` 유지 | 변경 없음 |
| context schema | `2.0` 신규, `1.0` 수용 | §2.2 |
| group schema | `2.0` 신규, `1.0` 수용 | §5.1 |
| evaluate 출력 | `2.0` (`--format 1` 한시 유지) | §1.3 |
| route 출력 | `1.0` 유지 + `assessment_digest` 추가 필드 | 추가만, 기존 의미 불변 |
| `POLICY_VERSION` | legacy 선택 정책 버전. 출력에서 `router_policy_version`으로 표기 | `legacy_select` 변경 시 |
| `METRIC_REGISTRY_VERSION` | 정의표 버전 | 기존 지표 의미·단위 변경 시만. 지표 **추가**는 버전 유지 |

`SCHEMA_VERSION` 단일 상수를 입력 종류별 상수로 분리 (`TASK_SCHEMA`, `CONTEXT_SCHEMAS = {"1.0","2.0"}` 등).

문서 정리 (구현과 같은 PR):

- `03_ROUTING_AND_DATA_SPEC.md`의 선택 공식 절 → “legacy 자동 선택 정책” 표기, 규범은 이 문서.
- `docs/orchestrator.md` → context 2.0, selection, evaluate 2.0 예시로 갱신.
- `eval/run.py`의 low-cost-first 비교 → “legacy route baseline” 명시. 외부 정책 유효성 주장에 쓰지 않는다.

## 7. 새 지표 추가 절차 (확장성 검증 기준)

| 하고 싶은 것 | 수정 |
|---|---|
| 지표를 Orchestrator 판단용으로 전달만 | **아무것도 안 함** (미등록 지표로 통과) |
| 단위·수명 검증을 받고 explain에 정식 표시 | `METRICS`에 한 줄 |
| Router가 그 지표로 후보를 거름 | 위 + `CONSTRAINTS`에 함수 1개 + context에 상한 필드 1개 |
| Router가 새 근거로 평가 정보 제공 (예: 과거 성공률) | `EVALUATORS`에 함수 1개 |
| 지표로 순위를 매김 | Router 수정 없음. Orchestrator 정책 |

예: p50 지연 상한.

```python
METRICS["latency.p50_ms"] = ("profile", "number", "ms", 1)
CONSTRAINTS["latency"] = lambda p, t, f, ctx: None if "max_latency_p50_ms" not in ctx else \
    check(f, "latency.p50_ms", "<=", ctx["max_latency_p50_ms"], code="latency_exceeds_max", on_missing="pass")
```

## 8. 구현 순서

각 단계는 독립 커밋, 단계마다 `python3 -m unittest test_p0 test_p1 test_p2 test_p3` 통과.

진행: 1–2단계 완료 (2026-10-13, test_v36·v37).

1. **assess 추출** (`routing.py`): `route()` 루프를 `assess` + `benchmark_evaluation` + `CONSTRAINTS`로 분리, `route`/`evaluate`(1.0 형식) 재구성. 기존 테스트 무수정 통과가 완료 조건.
2. **context 2.0 + METRICS** (`routing.py`): 검증·freshness·1.0 변환·비용 결정 순서.
3. **evaluate 2.0 출력 + explain** (`routing.py`, `cli.py`).
4. **digest + selection + decision 2.0** (`routing.py`, `herdr.py`, `cli.py`).
5. **group 2.0** (`parallel.py`).
6. **문서** (§6).

## 9. 검증 사례

보고서 필수 사례 → 테스트 위치. 명명은 기존 `test_vNN_description` 연번을 이어간다.

| 사례 | 기대 | 파일 |
|---|---|---|
| 벤치마크 없음, 다른 유효 facts 있음 | evaluate에 eligible 후보, `benchmark.status=unavailable` | test_p0 |
| 새 지표 추가 | 기존 `legacy_score`·route 선택 불변 | test_p0 |
| 기존 자동 선택 회귀 | 1단계 전후 route 출력 동일 (기존 fixture 전체) | test_p0 |
| 미등록 지표 | `unrecognized_metrics`로 전달, 제약 미사용 | test_p0 |
| `value: null` / `status: missing` | 전자 입력 오류, 후자 수용·0 아님 | test_p0 |
| 만료 가격 + 비용 상한 | `estimated_cost` 실패, `observed: null`, code `estimated_cost_unknown` | test_p0 |
| 만료 가격, 비용 상한 없음 | 후보 유지, facts에 `expired` | test_p0 |
| 단위 불일치 (`s` vs `ms`) | 입력 오류 | test_p0 |
| 지표 `applies_to` 위반 | 입력 오류 | test_p0 |
| 등급 high + 견적 저렴 + `max_cost_tier=medium` | 탈락 (`cost_tier_exceeds_max`), 문서와 일치 | test_p0 |
| context 1.0 입력 | 2.0과 같은 facts, route 1.0 출력 불변 | test_p0 |
| evaluate 후 config 변경 → route --selection | `stale_assessment`, 실행 안 함 | test_p2 |
| 같은 round 재호출, 다른 selection 같은 profile | 회수 + `selection_differs_from_recorded` | test_p2 |
| decision.json | assessment + selection + digest 기록 | test_p2 |
| group selections + context | 지정 프로필 fanout, 각 dispatch에 context 전달 | test_p3 |
| deliberate 후속 round | `estimate_round1_only` 경고 | test_p3 |

전체 예산(동시 예약·정산) 검증은 해당 기능을 만들 때 추가.

## 10. 결정 요약

| # | 결정 | 대안 / 업그레이드 경로 |
|---|---|---|
| 1 | Router는 순위 없음. 제약 + 사실 + 기존 legacy 선택만 | Orchestrator 정책 공유가 필요해지면 정책을 별도 모듈로 이식 |
| 2 | 지표 정의는 코드 상수 `METRICS` | 외부 팀이 자주 추가하면 TOML |
| 3 | 단위 변환 없음, 불일치 = 오류 | 지표별 배수 목록 |
| 4 | 미등록 지표는 전달만 | — |
| 5 | 등급·달러 상한 모두 독립 제약 | — |
| 6 | 비용 계산식 1개 + 공급자 견적 우선 | 계산 항목 추가 |
| 7 | digest = 정적 입력 해시, 불일치 시 실행 거부 | — |
| 8 | 병렬 다중 기준은 Orchestrator 주도, group은 selections 전달만 | 전체 예산 원장은 요구 시 |
| 9 | evaluate만 2.0, route 1.0 유지 | route 2.0은 legacy 선택 폐기 시 |
