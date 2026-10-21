# 공식 가이드 기반 선택 정책

`route`, `explain`, `parallel`, 설치한 Skill의 기본 정책은 `vendor-guided`입니다.
기존 점수식은 `--policy legacy`로 명시적으로 선택합니다. `evaluate`는 선택 없는 사실 조회로 유지합니다.

## 선택 순서

1. 기존 필수 제약으로 실행 가능한 프로필을 정합니다.
2. `analysis`: Jev 또는 native `bench-decider`가 작업 설명·요구사항에서 미확정 facet과 명확성·추론 요구·자율성·완성 기준을 함께 판정합니다. 모델·벤치마크 점수와 파일 본문은 이 요청에 넣지 않습니다. 모호한 facet은 미확정으로 보관합니다.
3. `fit`: 앞선 분석과 원래 요구사항, 정확한 model/effort의 권고만으로 적합 후보를 정합니다. 규칙·출처·공통 지시는 한 번만 제공합니다. 벤치마크 점수는 전달하지 않습니다.
4. 코드가 남은 후보에 한해 관련 facet 평가를 검색합니다. category 평가를 임의로 다시 합치지 않습니다. 제외된 후보의 관측 수가 검색 순서에 영향을 주지 않습니다.
5. 동일 측정 프로토콜의 fresh exact 관측은 raw 값으로 비교합니다. 모델 proxy는 동일 source/cohort/metric version/프로토콜일 때만 모델 단위로 비교하고 `model_proxy_comparison`을 남깁니다. 서로 다른 집단의 percentile이나 exact/proxy를 섞어 순위를 만들지 않습니다.
6. 비교 가능한 평가의 절반을 초과해 우승한 후보가 없을 때만(평가가 1개이거나 과반 우승자가 있으면 코드가 바로 선택) `benchmark` 요청으로 각 평가의 작업 관련도(0·0.5·1)를 받습니다. 코드가 관련도로 가중한 우승 수를 합산하며, 같은 suite의 slice는 한 표를 나눠 갖습니다. 모두 0이면 기권입니다. 이 요청에는 후보명·관측 점수를 넣지 않으며, 평가별 우승 후보는 코드가 계산합니다. 결측은 0점이 아니며 비교할 자료가 없으면 추가 호출 없이 잠정 선택과 불확실성을 남깁니다.
7. `quality`는 비교 가능한 품질 근거, `balanced`는 그 후보들 중 가벼운 cost tier, `cost`는 모든 적합 후보의 fresh 견적이 있을 때 최저 USD를 우선합니다. 실행 직전에 제약과 가용성을 다시 확인합니다.

평가가 필요한 effort는 조건부 후보입니다. `guidelines.toml`의 `evaluation_only_efforts`를 사용하며, 같은 모델·harness의 더 낮은 effort와 동일 workflow 프로토콜에서 실제 개선이 있어야 조건을 해소합니다. baseline은 비교 실험의 대조군으로만 사용하며 실행 후보 검색 순서에 개입하지 않습니다. 증명이 없으면 `workflow_gain_unverified`와 잠정 상태를 보존합니다.

종합 점수나 제공사 공통 effort 척도를 만들지 않습니다. 판단 agent가 의미상 적합성을 판단하며 코드는 그 판단의 진실성을 보증하지 않습니다.
동률은 적합 후보 중 default → fallback_order → ID 순으로 해소합니다. 비용 우선이며 모두 견적이 있으면 최저 견적 후보 안에서 해소합니다.
가이드 미등재 모델도 후보로 유지하고 `guidance_missing`으로 표시합니다. 작업별 평가가 없어도 잠정 선택하며 품질·최저 비용을 보장하지 않습니다.
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
각 단계의 실제 의존성이 바뀌면 그 단계의 응답을 다시 받아야 합니다. snapshot만 바뀐 경우 작업 분석과 적합성 응답은 재사용할 수 있지만 최종 선택 기록은 다시 생성합니다.

## 선택 기록과 호환성

새 `selection` 스키마는 `3.0`이며 기존 profile/digest/policy/reason에 `decision`을 추가합니다.
정책 버전은 `2`입니다. `decision`은 `inputs`, 원래 `task`, 순서가 있는 `stages`, `evaluation`, provider/model, uncertainty를 보관합니다. 각 stage는 request/digest/answers, 실제 provider/model, 보고된 usage와 elapsed_ms(있는 경우)를 보존합니다. `evaluation`에는 공유 unit 정의, 후보별 sparse 관측·결측, 조건부 적합성 검증과 실제 비교 범위가 있습니다.
최종 digest는 이 decision 전체를 묶습니다. 단계별 request digest는 각 요청 내용만 묶으므로 작업 분석을 무관한 snapshot 변경 때문에 다시 호출하지 않습니다.
지나간 시간 수치 자체는 제외하지만 근거·견적이 만료되면 freshness 변경으로 재판단합니다.
`route --selection`에 출력된 기록을 넘길 때 출력 전용 `source`는 제거합니다.
`2.0` 선택 기록과 `--profile`은 기존의 명시적 선택으로 지원하고 새 정책 검증과 구분해 경고합니다.
정책 버전 `1`의 기존 vendor-guided 선택은 새 결정에 재사용하지 않고 다시 판단해야 합니다. 이미 제출한 실행의 receipt 회수는 정책 변경과 무관하게 우선합니다.
기존 실행 회수는 저장된 선택을 사용합니다. 새 가이드나 판단 API 장애 때문에 같은 작업을 재전송하지 않습니다.

## 병렬 실행

`parallel --decision-response responses.json`은 member label → 응답 객체를 받습니다(예: `t1-1`).
작업 분석과 적합성 판단은 request digest로 plan 내에서 재사용합니다. 적합성은 fanout 순서와 독립적이며, 추가 선택에서는 앞서 고른 프로필을 평가 검색과 최종 비교에서 제외합니다. 각 member의 이전 응답들을 유지해 다음 패킷을 해결합니다. 캐시는 plan 호출 동안만 유지하며 파일을 쓰지 않습니다. 각 선택의 stage 기록에는 재사용한 원래 usage가 보존되므로 fanout 기록을 단순 합산해 실제 청구량으로 해석하면 안 됩니다.
모든 선택이 완료되기 전에는 worktree·그룹 파일·worker를 만들지 않습니다.
실행 시작 시 `plan.json`에 선택과 그룹 입력을 저장합니다. 동일 그룹 재실행은 이 선택과 기존 receipts를 회수합니다.
변경된 그룹 입력은 conflict이며, 실행하지 않은 member의 오래된 선택은 전체 사전 검증에서 거부합니다.

## 가이드 갱신

`bench_router/guidelines.toml`은 wiki의 공식 참조 문서에서 추출한 버전 고정 정책 자료입니다.
각 규칙은 정확한 모델 ID·effort·적용 조건·공식 URL·위키 경로와 조사일을 갖습니다.
모델 ID는 prefix나 비슷한 이름으로 매칭하지 않습니다. 목록에 없는 effort도 `guidance_missing`입니다.
이는 지원 가능한 effort 전체 목록이 아니라 검토한 작업별 권고 목록입니다.
가이드 파일의 버전과 내용을 함께 변경해 검토하며 runtime 웹 조회나 draft 위키 자동 승격은 하지 않습니다.
패키지에 포함되므로 wiki 폴더가 없는 복사 설치 Skill도 동일하게 동작합니다.
