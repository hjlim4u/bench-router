# 공식 가이드 기반 선택 정책

`route`, `explain`, `parallel`, 설치한 Skill의 기본 정책은 `vendor-guided`입니다.
기존 점수식은 `--policy legacy`로 명시적으로 선택합니다. `evaluate`는 선택 없는 사실 조회로 유지합니다.

## 선택 순서

1. 기존 필수 제약으로 실행 가능한 프로필을 정합니다.
2. `analysis`: Jev 또는 native `bench-decider`가 작업 설명·요구사항에서 미확정 facet과 명확성·추론 요구·자율성·완성 기준을 함께 판정합니다. 키워드·코드블록·확장자로 얻은 작업 유형은 `rule_hints`이며 의미 분석이 거부할 수 있습니다. 거부한 규칙은 검색에서 다시 적용하지 않습니다. 명시적 task.facets와 언어·입력 길이 등 구조적 사실은 유지합니다. 모델·벤치마크 점수와 파일 본문은 이 요청에 넣지 않습니다. 모호한 facet은 미확정으로 보관합니다.
3. `fit`: 앞선 분석과 원래 요구사항, 정확한 model/effort의 권고만으로 적합 후보를 정합니다. 규칙·출처·공통 지시는 한 번만 제공합니다. 벤치마크 점수는 전달하지 않습니다.
4. 코드가 남은 후보에 한해 검토된 facet 평가를 검색합니다. 모델 선택용 검색에는 상위 12개 표시 제한을 적용하지 않습니다. category 평가를 임의로 다시 합치지 않습니다. 비활성 unit은 인덱스에서 제외되고, 비교 불가·비현행·범용 일치뿐인 unit은 `prefiltered_units`에 이유를 남겨 의미 검사에서 제외합니다. 공통 에이전트 신뢰성은 `auxiliary_units`로 보존합니다. 후보별 결측·관측은 진단을 위해 유지합니다.
5. 동일 측정 프로토콜의 fresh exact 관측은 raw 값으로 비교합니다. 모델 proxy는 동일 source/cohort/metric version/프로토콜일 때만 모델 단위로 비교하고 `model_proxy_comparison`을 남깁니다. 서로 다른 집단의 percentile이나 exact/proxy를 섞어 순위를 만들지 않습니다.
6. 사전 필터를 통과한 비교가 있으면 `benchmark` 요청 하나로 관련성과 근거를 함께 판정합니다. suite별 짧은 측정 설명·facet과 원래 요구사항만 전달하며 후보명·점수·출처 상세·Wiki 본문은 보내지 않습니다. `relevance:<unit>`는 0..1, `basis:<unit>`는 직접 측정하는 핵심 요구의 facet 또는 `__supporting__`·`__unrelated__`·`__unknown__` 중 하나입니다. 관련도 0.8 이상과 핵심 요구 근거를 모두 충족한 unit에 `accepted: true`를 기록합니다. 0.8은 정책 문턱이며 보정된 확률이 아닙니다. unit별 비교 결과와 관련성은 상위 계층에 제공하며 투표하거나 합산하지 않습니다. 결측은 0점이 아닙니다.
7. 적합 후보가 복수이면 `decision_unavailable`(종료 17)과 `upstream_selection_required`를 반환합니다. `quality`·`balanced`·`cost`, 비용 견적, default/fallback 순서로 후보를 자동 축소하지 않습니다. 상위 계층이 `evaluate --format 3` → `select` → `route --selection`으로 최종 선택합니다. 적합 후보가 하나이고 별도의 미검증 조건이 없으면 기존 단건 경로로 선택할 수 있습니다. 비교 근거가 모두 거부되면 이 경우에도 추천을 기권합니다. 실행 직전에 제약과 가용성을 다시 확인합니다.

평가가 필요한 effort는 `guidelines.toml`의 `evaluation_only_efforts`에 따라 `provisional`, `workflow_gain: null`, `workflow_gain_unverified`로 남깁니다. 라우터는 낮은 effort 대조군을 탐색하거나 벤치마크 우세로 적합성을 승격하지 않습니다. 후보가 하나여도 상위 선택이 필요하며 실제 작업에서의 개선 검증·수용은 상위 계층이 담당합니다. `select --accept-provisional`은 미검증 조건을 명시적으로 수용할 뿐 해소하지 않습니다.

종합 점수나 제공사 공통 effort 척도를 만들지 않습니다. 판단 agent가 의미상 적합성을 판단하며 코드는 그 판단의 진실성을 보증하지 않습니다.
동률·벤치마크 간 상충·비용과 품질의 절충은 상위 정책의 판단입니다. 가이드 미등재 모델도 후보로 유지하고 `guidance_missing`으로 표시합니다. 품질·최저 비용을 보장하지 않습니다.
등록된 프로필의 실행 인자를 자동 변경하거나 프로필을 생성하지 않습니다.

## CLI와 오프라인 응답

```bash
python3 -m bench_router.cli route --task task.json --host codex --dry-run
python3 -m bench_router.cli route --task task.json --host codex --decision-response response.json --dry-run
python3 -m bench_router.cli route --task task.json --host codex --decision-response response.json
python3 -m bench_router.cli route --task task.json --policy legacy --dry-run
```

첫 명령은 `decision_required`와 `decision` 패킷을 반환합니다. dry-run은 Jev 키가 있어도 네트워크나 쓰기를 수행하지 않습니다.
호스트가 현재 패킷의 `request`만 native 판단 agent에게 전달합니다. 응답 파일에는 `decision.completed`의 검증된 이전 단계들과 새 응답을 순서대로 넣습니다.

```json
{
  "stages": [
    {
      "request_digest": "<현재 decision.request_digest>",
      "provider": "subagent",
      "model": "<실제 실행 메타데이터의 모델>",
      "answers": {"<현재 단계의 모든 question ID>": {"type": "choice", "choice": "<허용 옵션>"}}
    }
  ]
}
```

같은 명령을 `--decision-response`로 반복해 다음 단계를 해결합니다. `decision.stage`는 `analysis`, `fit`, 필요 시 `benchmark`입니다. 첫 단계는 단일 응답 객체로도 받을 수 있습니다. facet 질문은 `noul` 응답을 사용합니다. 관련 질문을 위해 별도 facet 판단을 먼저 호출할 필요가 없습니다.

호스트에 맞는 `--host`가 필요합니다. 실제 모델이 요청한 모델과 다르면 `decision_unavailable`입니다.
`--decision-response`는 저장된 Jev 응답도 받을 수 있습니다(`provider: "jev"`).
live `route`는 설정된 Jev를 호출할 수 있으며, 키가 없거나 호출이 실패하면 native 패킷을 반환합니다.
`decision_required`와 `decision_unavailable`의 종료 코드는 17입니다. 기권·장애 때 legacy로 전환하지 않습니다.
각 단계의 실제 의존성이 바뀌면 그 단계의 응답을 다시 받아야 합니다. snapshot만 바뀐 경우 작업 분석과 적합성 응답은 재사용할 수 있지만 최종 선택 기록은 다시 생성합니다. 단계 완료 뒤 상위 선택이 필요한 경우에는 같은 응답 파일로 `evaluate --format 3`을 호출해 assessment를 얻습니다. 반환된 `decision`에는 재사용할 `stages`와 후보별 관측·관련성 근거가 있습니다.

## 선택 기록과 호환성

상위 계층이 후보 평가를 받은 뒤 자체 정책으로 프로필을 선택하려면 `evaluate --format 3` → `select` → `route --selection`을 사용합니다. 이 경로의 선택 기록은 **4.0**이며 적합 후보 중 기본 추천과 다른 프로필을 고를 수 있습니다. 잠정 적합성은 `--accept-provisional`로 수용해야 하고, 부적합 후보나 필수 제약 실패는 우회하지 못합니다. [공개 평가·외부 선택 계약](orchestrator.md#vendor-guided-candidate-assessments-and-upstream-choices)을 참조하세요. 기존 2.0 override와 기본 자동 선택의 3.0 재현 의미는 유지합니다.

vendor-guided 단일 후보 선택 기록은 `3.0`이며 기존 profile/digest/policy/reason에 `decision`을 추가합니다. 상위가 format 3 후보 평가에서 선택한 기록은 `4.0`이고, 같은 `decision`에 `accept_provisional`을 추가합니다. 두 형식 모두 정책 버전 `4`의 평가 근거를 보존하지만, 3.0은 라우터의 단일 후보에 고정되고 4.0은 검증된 외부 정책의 선택을 기록합니다.
`decision`은 `inputs`, 원래 `task`, 순서가 있는 `stages`, `evaluation`, provider/model, uncertainty를 보관합니다. 각 stage는 request/digest/answers, 실제 provider/model, 보고된 usage와 elapsed_ms(있는 경우)를 보존합니다. `evaluation`에는 공유 unit 정의, 후보별 sparse 관측·결측, 조건부 적합성 검증과 실제 비교 범위가 있습니다.
최종 digest는 이 decision 전체를 묶습니다. 단계별 request digest는 각 요청 내용만 묶으므로 작업 분석을 무관한 snapshot 변경 때문에 다시 호출하지 않습니다.
지나간 시간 수치 자체는 제외하지만 근거·견적이 만료되면 freshness 변경으로 재판단합니다.
`route --selection`에 출력된 기록을 넘길 때 출력 전용 `source`는 제거합니다.
`2.0` 선택 기록과 `--profile`은 기존의 명시적 선택으로 지원하고 새 정책 검증과 구분해 경고합니다.
`4.0`은 `evaluate --format 3` → `select`가 만든 기록만 허용합니다. 기존 2.0·3.0 기록을 4.0으로 임의 변환하거나, 3.0의 profile만 바꿔 재사용할 수 없습니다.
정책 버전 `1`·`2`·`3`의 기존 vendor-guided 선택은 새 결정에 재사용하지 않고 다시 판단해야 합니다. 이미 제출한 실행의 receipt 회수는 정책 변경과 무관하게 우선합니다.
기존 실행 회수는 저장된 선택을 사용합니다. 새 가이드나 판단 API 장애 때문에 같은 작업을 재전송하지 않습니다.

### 상위 계층용 관련성 근거

`evaluate --format 3`의 `evidence.relevance[unit_id]`와 저장된 `decision.evaluation.relevance`는 같은 근거를 제공합니다. 예:

```json
{"score": 0.9, "accepted": true, "basis": "task:repo_coding",
 "task_requirement": "Resolve an issue in an existing repository with a code patch",
 "reason": "The selected task requirement is judged directly measured by this unit.",
 "matched_facets": ["task:repo_coding"], "comparison_scope": "exact_profile",
 "source_page": "entities/benchmarks/swe-bench-verified-exact.md", "request_digest": "<benchmark request digest>"}
```

원래 요청은 `decision.task`, 측정 대상 설명은 `evidence.units[unit_id].desc`, 실제 측정 조건은 후보별 `observations[unit_id]`에서 참조합니다. 설명을 unit마다 반복 생성하지 않고 선택형 근거로 연결합니다. `benchmark_relevance`는 거부된 unit을 0으로 표시한 관련도이며 투표에 사용하지 않습니다. `relevance.score`는 원래 응답입니다. 상위 계층은 지지 근거·거부 사유·보조 신뢰성·proxy 범위를 구분해 자체 agent/model 배정 정책을 적용할 수 있습니다. 판단 내용은 의미 평가자의 주장이지 실행 성공의 검증이 아닙니다. 근거를 변조하면 digest 또는 실행 시 재생 검증에서 거부됩니다.

## 병렬 실행

`parallel --decision-response responses.json`은 member label → 응답 객체를 받습니다(예: `t1-1`).
복수 적합 후보가 남으면 이 경로도 상위 선택을 요청합니다. 여러 모델을 배정하려면 완료된 assessment에서 selection 4.0을 만들고 group 2.0의 `selections`로 전달합니다. 기본 프로필로 fanout을 자동 완성하지 않습니다.
작업 분석과 적합성 판단은 request digest로 plan 내에서 재사용합니다. 적합성은 fanout 순서와 독립적이며, 추가 선택에서는 앞서 고른 프로필을 평가 검색과 최종 비교에서 제외합니다. 각 member의 이전 응답들을 유지해 다음 패킷을 해결합니다. 캐시는 plan 호출 동안만 유지하며 파일을 쓰지 않습니다. 각 선택의 stage 기록에는 재사용한 원래 usage가 보존되므로 fanout 기록을 단순 합산해 실제 청구량으로 해석하면 안 됩니다.
모든 선택이 완료되기 전에는 worktree·그룹 파일·worker를 만들지 않습니다.
실행 시작 시 `plan.json`에 선택과 그룹 입력을 저장합니다. 동일 그룹 재실행은 이 선택과 기존 receipts를 회수합니다.
변경된 그룹 입력은 conflict이며, 실행하지 않은 member의 오래된 선택은 전체 사전 검증에서 거부합니다.
group 2.0의 `selections`는 순서 있는 실행 인스턴스 목록이므로 동일 profile을 반복할 수 있습니다. 반복 항목도 별도 label·worktree·receipt를 가지며 task당 8개와 group 전체 16개 한도에 포함됩니다. member `rounds`에는 `delivery_state`와 `reassignment`가 보존되므로, 불확실하거나 미완료인 실행은 재배정 전에 `collect_first`를 따릅니다.

## 가이드 갱신

`bench_router/guidelines.toml`은 wiki의 공식 참조 문서에서 추출한 버전 고정 정책 자료입니다.
각 규칙은 정확한 모델 ID·effort·적용 조건·공식 URL·위키 경로와 조사일을 갖습니다.
모델 ID는 prefix나 비슷한 이름으로 매칭하지 않습니다. 목록에 없는 effort도 `guidance_missing`입니다.
이는 지원 가능한 effort 전체 목록이 아니라 검토한 작업별 권고 목록입니다.
가이드 파일의 버전과 내용을 함께 변경해 검토하며 runtime 웹 조회나 draft 위키 자동 승격은 하지 않습니다.
패키지에 포함되므로 wiki 폴더가 없는 복사 설치 Skill도 동일하게 동작합니다.
