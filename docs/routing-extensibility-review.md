# 다중 기준 라우팅 확장성 점검

점검일: 2026-10-13. 대상은 **당시 작업 트리**의 Router·Orchestrator 연동·병렬 실행·데이터·평가 코드다. 아래 코드 행 링크와 “현재” 표현도 당시 기준이며 현행 API를 설명하지 않는다.

2026-10-24 구현 대조: assess 분리·지표 registry·통과/실패 제약·digest·선택 기록·group 2.0이 구현됐다. 가중합 자동 선택은 제거됐고 evaluate 1·2는 ID순 사실 평가다. 정책 6의 의미 적합성은 evaluate --format 3(schema 4.0), 상위 선택은 selection 6.0으로 공개한다. 현재 규범은 [라우팅 계약](routing-contracts.md)과 [vendor-guided 정책](vendor-guided-routing.md)을 따른다. 이 문서는 설계 변경의 근거 기록으로 보존한다.

## 결론

별도 설계가 필요하다. 현재 구현은 **벤치마크 기반 Router에 외부 판단용 정보와 프로필 지정 실행을 추가한 단계**다. Orchestrator가 최종 선택한다는 기존 합의와는 일치하지만, 모든 실행 경로가 다양한 지표를 종합하는 구조는 아니다.

우선 설계할 부분은 후보 평가와 선택의 분리, 지표의 의미·유효성 계약, 판단 기록과 실행 간 연결이다. 병렬 실행도 같은 경계를 사용해야 한다. 단건 비용 상한을 전체 예산 관리로 해석해서는 안 된다.

기존 벤치마크 계산을 없애거나 범용 플러그인 프레임워크를 만들 필요는 없다. 벤치마크 계산을 하나의 평가기로 유지하고, 외부 정책과 공유할 계약을 작게 정의하는 방향을 권한다. 아래 내용은 설계 제안이며 구현 변경은 하지 않았다.

## 1. 우선: 후보 평가가 기존 선택 정책에 종속됨

근거: [evaluate](../bench_router/routing.py#L675), [route](../bench_router/routing.py#L584), [select](../bench_router/routing.py#L540).

`evaluate()`는 `route()`를 호출한 뒤 선택 결과와 일부 경고만 제거한다. 후보에는 기존 `score`, `quality`, `coverage`, `cost_proxy`가 남고 순서도 기존 점수순이다. `select()`는 벤치마크 coverage 문턱과 비용 등급으로 점수를 만들며, 예상 달러 비용·복잡도·추가 signals는 순위에 반영하지 않는다. 비용 상한은 별도 필터로만 작동한다.

따라서 후보의 첫 항목이나 `score`를 종합 추천으로 읽으면 판단이 어긋난다. 현재 `evaluate`가 벤치마크 없는 후보를 제거한다는 뜻은 아니다. 후보는 반환하지만 기존 점수는 null이고, 자동 `route`는 default/fallback 설정에도 의존한다.

권고:

- 공통 후보 평가 함수에서 사실 수집·파생값 계산·제약 검사를 수행한다. `evaluate`는 이 결과를 반환하고, 기존 `route`는 여기에 기존 선택 함수를 적용한다. 현재 호출 방향을 뒤집는 정도로 시작한다.
- 후보 목록 순서는 안정적인 profile ID순으로 두거나, 정렬 정책을 명시한다. 벤치마크 기반 순위를 종합 순위로 취급하지 않는다.
- 기존 점수는 `benchmark` 평가 결과로 이름과 범위를 명시한다. `benchmark.coverage`와 전체 판단에 필요한 정보의 충족도는 별개다.
- 최종 선택·지표 간 우선순위·fallback 순서는 Orchestrator 소유로 유지한다. 기존 자동 선택은 명시적인 호환 정책으로 남긴다.

회귀 기준: 벤치마크가 없어도 다른 유효 정보가 있는 후보를 반환한다. 새 signal 추가로 기존 benchmark 점수가 바뀌지 않는다. 기존 자동 선택 정책의 결과는 보존한다.

## 2. 우선: 확장 signal은 전달만 가능하고 의미·유효성 계약이 부족함

근거: [validate_context](../bench_router/routing.py#L175), [context_facts](../bench_router/routing.py#L225), [source_status](../bench_router/routing.py#L457).

현재 signal은 프로필별 `{value, unit, source}`이며 value는 유한 숫자만 허용한다. 관측 시각·만료·결측 사유·산출 버전을 표현하지 못한다. 가격에는 `as_of`가 있지만 만료 판정은 없다. 반면 벤치마크에는 source TTL, max-stale, scope, metric version 등이 있다. 같은 판단에 쓰이는 입력들의 신뢰도 계약이 다르다.

지연 시간처럼 빨리 변하는 지표, 아직 측정하지 못한 값, task 수준의 복잡도를 프로필 성능값과 동일하게 취급하면 잘못된 비교가 생긴다. 단위 문자열만으로 milliseconds와 seconds의 호환도 보장되지 않는다.

권고:

- 우선 사용하는 숫자 지표부터 ID별 단위·적용 대상(task/profile)·의미를 정의한다. 확장 영역을 유지하되 인식하지 못하는 지표를 자동으로 판단에 사용하지 않는다.
- 관측값에는 `observed_at` 또는 `as_of`, 필요 시 `expires_at`, 결측 상태와 이유를 표현한다. 결측은 0이 아니다. 가격·지연·신뢰도처럼 수명이 다른 지표에 동일한 TTL을 강제하지 않는다.
- 원자료의 단위·출처·산출 버전과 정책의 선호 방향·변환 규칙을 구분한다. “클수록 좋다”는 규칙도 모든 값에 공통으로 적용할 수 없다.
- 만료·결측 시 제외할지, 보수적 추정으로 계속할지는 해당 제약/정책에 명시한다. 사용하지 않는 선택 지표가 없다고 후보 전체를 제외하지 않는다.
- task 요구와 profile 능력을 구별한다. 복잡도는 작업 특성이고, 그 작업을 처리할 적합도는 정책의 판단 결과다.

가격 API나 계정 쿼터 수집기를 Router에 추가할 필요는 없다. Orchestrator 제공 입력의 계약을 보강하면 된다.

## 3. 우선: 제약·선호·예산의 범위가 겹침

근거: [hard_filter](../bench_router/routing.py#L564), [context_facts](../bench_router/routing.py#L225), [select](../bench_router/routing.py#L540), [비용 사후 계산](../eval/cost.py#L103).

`max_cost_tier`와 `max_estimated_cost_usd`, `min_context_tokens`와 `required_context_tokens`가 서로 다른 입력에 존재한다. 현재는 모두 통과해야 한다. 따라서 실제 추정액이 낮아도 high 등급이면 제외될 수 있다. 이는 독립 제약이라면 타당하지만 실제 가격이 옛 등급을 대체한다고 기대하면 충돌한다.

프로필의 `context_tokens`는 정적 컨텍스트 수용량이다. 남은 실행 토큰 예산이나 계정 사용량이 아니다. `max_estimated_cost_usd`도 한 번의 추정 호출 비용 상한이며, 누적 소비·예약·재시도 비용을 관리하지 않는다. 추정식은 입력/출력 두 요율이고, 사후 비용 도구는 캐시·부가 비용까지 구분하므로 양쪽 값이 다를 수 있다.

권고:

- 필수 제약과 비교 선호를 명확히 분리한다. 필수 제약 실패를 높은 점수로 상쇄하지 않는다.
- 기존 등급은 호환 정책의 proxy로 유지한다. 달러 단위 예산과의 우선순위 및 동시 지정 의미를 문서화한다.
- 토큰은 최소한 컨텍스트 수용량, 호출 예상 사용량, 작업 전체 잔여 예산으로 구분한다. 계정 쿼터 연동은 앞선 합의대로 유보한다.
- Router는 전달된 단건 allowance를 검사하고, Orchestrator가 작업 전체 잔여 예산과 병렬 예약을 소유하도록 한다. 전체 예산 준수를 요구할 때 예약→실행→정산 및 불확실한 실행의 예약 유지 규칙을 별도로 설계한다.
- 예상 비용의 범위를 명시한다. 캐시/부가 비용 지원이 필요해지면 제공자가 산출한 견적과 계산 버전을 전달하거나 계산 항목을 늘리되, 임의 비용 계산 DSL은 만들지 않는다.

## 4. 우선: 평가 당시 판단과 실행 당시 검증을 연결할 계약이 없음

근거: [CLI 로딩](../bench_router/cli.py#L28), [dispatch](../bench_router/herdr.py#L365), [pin_selection](../bench_router/routing.py#L682).

`evaluate` 결과의 snapshot/config/context와 `route --profile` 호출의 입력이 같아야 한다는 연결 검사는 없다. CLI는 매번 현재 파일을 다시 읽는다. 선택 후 설정·컨텍스트·가격이 바뀌어도, 실행 시 현재 제약만 통과하면 진행한다. 반대로 같은 task/round의 재호출은 최초 decision을 반환하므로, 새로운 context를 새 실행 요청으로 해석하지 않는다.

최초 판단 기록을 재사용하는 멱등성은 유지해야 한다. 부족한 것은 Orchestrator가 왜 골랐는지와 무엇을 근거로 골랐는지를 저장하는 계약이다. 현재 `policy_version`은 Router의 정책 버전이고, 외부 정책 ID·버전·선택 이유는 입력되지 않는다. 탈락 후보도 profile과 사유만 남고, 비용/용량의 실제값과 기준값은 해당 후보 항목에 남지 않는다.

권고:

- 결정 기록에 외부 정책 ID/버전, 선택 이유, 선택 profile, 평가 결과를 식별할 digest를 포함한다. 기존 snapshot/config/context hash를 재사용한다.
- 판단에 중요한 정적 입력이 달라지면 재평가를 요구할지 명시한다. 실행 가능성 같은 동적 사실은 실행 직전 다시 검사한다. 시간에 따라 달라지는 출력 전체를 단순 비교하는 방식은 피한다.
- 같은 task/round는 최초 실행 회수라는 기존 규칙을 유지한다. 새 판단으로 재실행하려면 새 round를 사용한다.
- 제약 결과를 code, 관측값, 기준값, 근거 지표로 설명할 수 있게 한다. 범용 규칙 엔진 없이 현재 검사 결과부터 구조화한다.

## 5. 우선: 병렬 경로에는 새 입력·선택 계약이 전달되지 않음

근거: [validate_group](../bench_router/parallel.py#L29), [plan](../bench_router/parallel.py#L70), [run_group](../bench_router/parallel.py#L161).

그룹 입력에는 context나 외부 선택 목록이 없다. `plan()`은 기존 `route()`의 선택과 후보 순서로 fanout을 정하고, 각 dispatch에도 context를 전달하지 않는다. 단건에서는 표현 가능한 가격·용량 제약을 같은 형태로 병렬 경로에 적용할 수 없다.

권고:

- 외부 Orchestrator가 병렬 실행을 이용할 경우 task별 context와 명시적 profile 선택을 전달하는 계약을 정의한다. 계획과 실행 모두 같은 평가/제약 검사를 사용한다.
- Orchestrator가 병렬화를 전담할 경우 기존 group 경로는 호환 기능이라고 명시한다. 어느 경로를 제품의 기본으로 할지 먼저 정하고 중복 정책을 만들지 않는다.
- fanout 전체 예상 비용과 후속 round 재견적은 Orchestrator 책임으로 둔다. 같은 잔여 예산을 각 worker에게 통째로 제공하면 총합 제한이 되지 않는다.

## 6. 다음: 벤치마크 저장 형식을 모든 지표의 형식으로 확대하면 안 됨

근거: [normalize](../bench_router/data.py#L272), [build_snapshot](../bench_router/data.py#L381), [validate_snapshot](../bench_router/routing.py#L417), [load_categories](../bench_router/routing.py#L380).

데이터 경로는 고정 `EVIDENCE_IDS`, cohort percentile, exact-profile/model-proxy, category별 합계 1의 가중치에 맞춰져 있다. 벤치마크에는 적절한 구조다. 가격·잔여 예산·지연·불리언 capability를 모두 여기에 넣으면 불필요한 정규화와 모델 식별 매핑을 강요하게 된다.

권고:

- 이 파이프라인은 benchmark 전용으로 유지한다. category 분류·coverage·proxy scope도 그 내부 개념으로 남긴다.
- 외부 런타임 facts와 benchmark 결과를 후보 평가 경계에서 합친다. 모든 지표를 하나의 저장소나 percentile로 통일하지 않는다.
- 공통 점수가 필요하면 Orchestrator 정책이 지표별 변환과 trade-off를 정한다. USD와 percentile을 의미 정의 없이 더하지 않는다.
- 새 벤치마크 자체를 자주 추가하게 될 때만 고정 ID 목록을 작은 선언형 정의표로 옮긴다. 현재 단계에서 동적 플러그인 로더는 불필요하다.

## 7. 다음: 출력·버전·검증도 함께 전환해야 함

근거: [explain_text](../bench_router/cli.py#L91), [평가 정책](../eval/run.py#L75), [평가 보고서](../eval/run.py#L95), [현재 연동 문서](orchestrator.md).

사람용 explain은 벤치마크와 cost proxy 중심이며 context의 비용·추가 지표를 출력하지 않는다. 평가 도구의 low-cost-first도 cost tier 기준이고, 비교 대상은 기존 자동 route다. 이 결과만으로 외부 다중 기준 정책의 유효성을 주장할 수 없다. task/profile/context/snapshot 등은 공통 `SCHEMA_VERSION`에 묶여 있고 엄격한 필드 검증을 사용하므로 확장 필드 도입 시 호환 전략이 필요하다.

권고:

- explain과 저장된 decision이 같은 사실·제약·정책 이유를 설명하도록 한다.
- wire schema와 정책 버전을 구분한다. context가 독립 진화해야 한다면 그 버전부터 분리한다. core의 오타 검출은 유지하고, 정의된 확장 영역만 추가 지표를 받는다.
- `score` 등 기존 필드 의미를 같은 버전에서 바꾸지 않는다. 호환 필드를 유지하거나 명시적으로 새 계약을 도입한다.
- 기존 평가를 baseline으로 보존하고 외부 정책에 대한 합성 계약 테스트를 추가한다. 실제 성공률·비용 개선 검증은 별도 실험으로 구분한다.
- 구현 전 기존 의도/라우팅/인터페이스 문서와 `docs/orchestrator.md`의 책임 범위를 맞춘다. 기존 설계의 역사적 설명은 남길 수 있지만 현재 규범이 무엇인지 표시한다.

## 최소 설계 산출물과 적용 순서

세 가지 작은 계약 문서면 충분하다. 별도 프레임워크 설계는 필요 없다.

| 계약 | 반드시 결정할 내용 | 구현 영향 |
|---|---|---|
| 후보 평가와 선택 | benchmark 평가 범위, eligibility와 ranking 구분, 외부 정책 소유권, legacy 자동 선택 | routing, CLI, explain |
| facts와 제약 | 지표 ID/단위/대상/유효기간/결측, 비용과 토큰의 범위, 버전 호환 | context 검증, 비용 계산, profile/task 제약 |
| 결정과 실행 | 판단 식별자, 변경 시 재평가, 멱등성, 병렬 전달, 전체 예산 책임 | herdr, parallel, decision 기록, Orchestrator 연동 |

1. 세 계약과 호환 방침을 먼저 확정한다.
2. 공통 후보 평가를 추출하고 기존 자동 선택 결과를 유지한다.
3. facts 및 결정 기록을 보강하고 단건/병렬/설명 출력을 연결한다.
4. 기존 테스트에 다중 기준 계약 검증을 추가한다. 외부 정책의 순위 계산은 Orchestrator에서 검증한다.

필수 검증 사례: 벤치마크 없는 후보, 미지원 지표의 전달, 결측·만료·단위 불일치, 제약과 선호 충돌, 평가 후 설정 변경, 같은 round 회수, 병렬 context 전달, 후속 round 재견적. 전체 예산을 구현한다면 동시 예약과 불확실한 실행 정산도 검증한다.

## 이번 점검에서 확인한 동작

현재 코드와 기존 test fixture를 사용한 오프라인 합성 입력으로 확인했다. 네트워크·실제 agent 호출은 없었다.

| 입력 | 관측 결과 |
|---|---|
| 같은 cost tier, priority=cost, A 예상 $0.20 / B 예상 $0.002, A의 benchmark 우세 | 자동 route는 A 선택. 예상액은 순위식에 미반영 |
| 가격 as_of=2000-01-01 | 수용. 만료 정책 없음 |
| signal.value=null | 입력 오류. 결측 상태 표현 불가 |
| signal에 as_of 추가 | 입력 오류. 현 계약은 value/unit/source만 허용 |
| benchmark 없음, default/fallback 없음, 유효 후보 2개 | route는 no_eligible_profile, evaluate는 두 후보 반환 |

이 결과는 기존 계약 위반을 뜻하지 않는다. 새 정책을 적용할 때 구분해야 할 기존 동작을 보여준다. 리뷰 중 제품 코드 수정 및 전체 회귀 테스트 재실행은 하지 않았다. 실제 Orchestrator의 정책 구현과 herdr 운영 동작은 검증하지 않았다.
