# 검증 시나리오·완료 기준·미결 사항

## 검증 원칙

테스트 수보다 데이터 결측·중복 위임·잘못된 완료를 실제로 잡는지가 중요하다. 아래 시나리오를 작은 table-driven tests로 묶어도 된다. 구현을 그대로 반복하는 단위 테스트를 무더기로 만들지 않는다.

offline fixture 통과, 실제 API 확인, 실제 herdr smoke, 작업군 효과 측정은 다른 검증 단계다. 미실행 항목은 skip과 이유를 기록한다. 이 handoff 작성 단계에서는 라우터 테스트나 live smoke가 실행되지 않았다.

## P0 선택·입력

| ID | 시나리오 | 기대 결과 |
| --- | --- | --- |
| V01 | 합성 scoring fixture | balanced=c, quality=a, cost=b; 각 Q/S/coverage 일치 |
| V02 | 점수 하나 missing과 측정 0 | missing은 coverage 제외, 0은 coverage 포함 |
| V03 | N=1, 동점, lower-is-better | percentile 0.5, average rank, direction 반영 |
| V04 | 동일 task/config/snapshot/availability | 선택과 설명 순서가 항상 동일 |
| V05 | 후보 모두 제약 탈락 | no_eligible_profile, exit13, prompt 없음 |
| V06 | default가 local_only/context/cost/exclude 위반 | default도 탈락; 무조건 default 실행 금지 |
| V07 | coverage 모두 <0.5 | configured eligible default/fallback_order, 점수 최적 선택이라고 표시하지 않음 |
| V08 | categories 합 !=1, enum 밖, NaN, 중복 key | 합은 normalize; 잘못된 구조는 exit2 |
| V09 | L1 규칙 충돌/unknown confidence | general abstain, 이유 기록 |
| V10 | score gap 0.019/0.020, quality priority | near-tie 경계와 priority별 정렬 계약 준수 |

Q/S float 비교 tolerance는 1e-9로 두고 출력 반올림과 선택 계산을 분리한다. 음수/NaN이 score에 유입되지 않게 한다.

## 다중 기준 계약 (2026-10-13, docs/routing-contracts.md)

| ID | 시나리오 | 기대 결과 |
| --- | --- | --- |
| V36 | benchmark 없음, default/fallback 없음, 유효 후보 있음 | route는 no_eligible_profile, evaluate는 유효 후보 반환; 탈락 사유는 관측값·기준값 포함 |
| V37 | context 2.0 지표: 1.0 동등성, 미등록 지표, 결측, 만료 가격, 공급자 견적, 단위·대상·null 오류 | 결측은 0 아님, 만료는 계산 제외(price_expired), 견적 우선, 잘못된 입력 exit2 |
| V38 | evaluate 2.0 | 전 프로필 ID순, 통과 제약 기록, 등급·달러 상한 독립, legacy_score = route score, 미등록 지표 추가로 benchmark 불변 |
| V39 | route --selection | 선택 기록 저장, 같은 round 회수(재전송 없음), 평가 후 설정 변경 시 stale_assessment |
| V40 | group 2.0 | Orchestrator 순서로 fanout, decision에 context·선택 근거, stale이면 그룹 전체 미실행 |

외부 정책의 순위 계산과 실제 성공률·비용 개선은 Orchestrator 쪽 실험으로 검증한다. 위 사례는 계약 검증이다.

## P1 수집·캐시

| ID | 시나리오 | 기대 결과 |
| --- | --- | --- |
| V11 | AA pagination 2페이지 정상 | 모든 페이지 결과만 한 새 소스 snapshot으로 게시 |
| V12 | 2페이지에서 HTTP 오류/schema 오류 | 부분 데이터 게시 없음; last-good 유지 |
| V13 | 304/동일 hash | 확인시각 갱신, publish date 보존, payload 중복 제거 |
| V14 | 401/403/429/timeout | bounded retry·quota 존중, 상태/exit16, secret 노출 없음 |
| V15 | 두 refresh 동시 실행/게시 중 crash | 단일 writer, route가 완전한 이전/새 JSON만 읽음 |
| V16 | TTL stale/max_stale 초과 | 소스별 stale 경고, 너무 오래된 observation 제외 |
| V17 | 캐시 없음/손상/미지원 schema | last-good 또는 constrained default; route network 0 |
| V18 | 모델 alias 불명/평가 버전 다름 | unmatched 또는 별도 cohort; 점수 혼합 금지 |

최소 source contract fixtures:
- AA: 페이지네이션, null, 필드 누락, 429 응답. 실제 응답과 합성 fixture를 구분.
- Arena: 사용 subset마다 컬럼/metric/version/revision 확인.
- 수동 TB/SWE: source URL, publish/evaluation 날짜, model/harness/config, benchmark version을 필수로 가진 normalized import.

API 키가 없으면 V11~V18 fixture로 개발을 진행하고 actual source E2는 미완료로 남긴다. API를 호출하는 live 검증은 refresh에만 한정한다.

## P2 위임·완료·복구

| ID | 시나리오 | 기대 결과 |
| --- | --- | --- |
| V19 | shell metacharacter/개행 prompt | argv로 정확히 전달; shell 실행 없음 |
| V20 | workspace/start 응답 fixture | 실제 반환 ID를 사용, 이름/ID 추측 없음 |
| V21 | 시작 blocked/timeout/CLI 없음 | prompt 보내지 않음, 사유와 Agent 진단 ID 반환 |
| V22 | prompt 직전 working/다른 session | 전송 중단; 이전 turn 종료를 완료로 사용하지 않음 |
| V23 | idle/done + 올바른 결과 | completed, result 절대경로, task_outcome 분리 |
| V24 | idle/done + 파일 누락/옛 run ID/nonce/hash 불일치 | result_invalid, exit12 |
| V25 | path 탈출/symlink/초대형/빈 결과 | 계약 거부, 임의 파일 읽기/성공 처리 없음 |
| V26 | stalled/timeout 후 Agent가 계속 작업 | uncertain/timed_out, 자동 재전송 없음, collect 가능 |
| V27 | 전송 직전/직후 wrapper crash | receipt가 모호 상태를 보존; 재실행 시 중복 prompt 없음 |
| V28 | 같은 task/round hash 같음/다름, concurrent dispatch | collect 재사용 / conflict14 / lock14 |
| V29 | unknown/Agent 종료/결과 partial/fail | 성공 추정 금지; task_outcome과 orchestration 상태 구별 |

불확실한 전송 경로 테스트에서는 mock의 prompt call count=1 또는 0을 검증한다. 실제 Agent에 실패를 유도하려고 같은 변경 작업을 여러 번 보내지 않는다.

## 실환경 smoke 절차

운용자가 승인한 프로필 하나와 작은 임시 프로젝트를 사용한다. 먼저 version/schema/model args와 인증 준비를 확인한다. default 프로필은 enabled이며 constraints를 만족해야 한다.

1. refresh 또는 날짜 있는 curated snapshot을 만들고 status를 확인한다.
2. dry-run에서 선택 근거·proxy/exact/coverage·날짜를 확인한다.
3. 테스트 작업은 지정 run directory에 짧은 설명 파일과 계약 manifest를 작성하는 것으로 제한한다.
4. live route를 실행하여 idle/done, manifest/hash, cwd, profile fingerprint를 확인한다.
5. 같은 task/round를 다시 호출하고 prompt를 새로 보내지 않는지 확인한다.
6. collect로 동일 결과를 회수한다.
7. 결과 내용을 검토하고 feedback를 기록한다.
8. 생성된 workspace/pane/파일을 보고하고 지정 범위만 정리한다.

금전/시간 사용이 있는 실제 API·Agent 실행은 새 CLI 환경의 사용자 권한과 작업 범위에 따른다. 문서만으로 특정 계정·Agent가 준비됐다고 판단하지 않는다.

## 라우팅 효과 평가

외부 리더보드만으로 라우터의 성공률을 입증할 수 없다. v1 배포 검토 시 같은 작업군에서 다음 baseline과 비교한다.

- 제약을 만족하는 고정 default.
- 저비용 후보 우선 정책.
- bench-router 정책.

작업군에는 저장소 수정, 터미널 작업, 신규 코드, 웹 개발, 한국어 조사/글쓰기, 수학, 문서 이해, 혼합/모호 작업을 포함한다. 각 작업의 acceptance check, capability, context, 예산을 먼저 고정한다. 최소 20개는 탐색용으로 쓸 수 있지만 통계적으로 충분하다고 주장하지 않는다.

기록: verified task success/partial/fail, 성공당 실제 비용 또는 측정 가능한 proxy, wall time, 분류 abstain, fallback 비율, evidence coverage/exact 비중, constraint 위반, invalid result, 중복 전송.

사람의 Agent 선택과 70% 일치는 보조 관찰이고 합격의 단독 기준이 아니다. 각 정책을 가능한 한 같은 작업·환경·예산으로 비교하고 표본 수/불확실성을 함께 보고한다.

latency는 benchmark fetch를 제외한 순수 route 선택과 CLI cold start, Agent start, 전체 완료를 분리한다. “p95 30ms” 등은 실측 머신·프로세스 시작 포함 여부가 없는 보증으로 사용하지 않는다. 비용을 측정하지 못하면 비용 감소를 입증했다고 보고하지 않는다.

## v1 완료 정의

- P0~P2 필수 CLI와 JSON/설정 계약이 구현되어 있다.
- 요청 경로 benchmark source 호출 0, 후보 없는 경우 prompt 0이다.
- 선택 수치/결측/constraint/fallback 정책과 fixture 기대값이 일치한다.
- 부분 갱신·손상 캐시·오래된 데이터에서 명세대로 동작한다.
- installed herdr version/schema와 실제 CLI 인자가 기록되어 있다.
- 최소 1개 실제 프로필의 live smoke가 통과했다.
- result 계약과 timeout/crash idempotency가 통과했다.
- API source live 확인 여부와 라이선스/출처 정보가 기록되어 있다.
- 재현 명령, 알려진 제한, 다음 작업이 남아 있다.

계정/실환경이 없어 마지막 live 검증이 불가능하면 “오프라인 구현 완료, live 검증 대기”로 보고한다. v1 기능 완료와 benchmark router의 품질 우수성 검증은 구분한다.

## 미결 사항과 임시 기본값

| 항목 | 영향 | 현재 기본값 | 새 Agent의 처리 |
| --- | --- | --- | --- |
| 실제 후보 모델/CLI/계정 | live 라우팅 자체 | 비활성 placeholder | 현장 inventory 확보 전 실제 선택 주장 금지 |
| herdr 버전/OS | 명령·schema·locking | Linux/macOS, 설치 버전 확인 | P0/P1 진행, P2 전 확인 |
| Orchestrator 형식 | L0 정확도/비용 | task JSON의 summary+categories | 한 개 실제 예제와 계약 맞춤 |
| task capability/context | 후보 안전한 적합성 | 명시 constraint만 강제 | unknown은 요구 충족으로 보지 않음 |
| 평가 config 정확 매칭 | exact coverage | 엄격 matching | 확인 못한 harness는 missing |
| Arena math/doc subset/category | 특정 카테고리 score | 실제 존재 전 missing | 스키마 확인 또는 default fallback |
| TB/SWE 안정적 수집 artifact | exact 데이터 확보 | 검증된 수동 import | 공식 파일 확인 후 자동화 |
| CLI 구독 비용/Agent 지연 | 경제성 비교 | 고정 tier proxy, latency penalty 0 | 실측 후 정책 version 변경 |
| 임베딩/Jev 적합성 | 한국어 분류·private 데이터 | 비활성 | holdout/shadow 결과 후 추가 |
| 재사용/원격/동시성 | 실행 비용·확장성 | fresh, local, 1 dispatch/cwd | 필요가 확인되면 후속 계약 |
| source redistribution 조건 | 캐시/공유 범위 | 내부 용도, attribution 보존 | 실제 약관/권한 확인 |
| 보존 기간/개인 prompt 로그 | 재현성·노출 | snapshot 30일, 원문 최소 | 사용자 운영 정책으로 조정 |
| 성능 합격 예산/허용 실패율 | 운영 배포 판단 | 하드 제약 위반 0 필수 | 작업군 비교 전에 수치 합의 |

위 모든 질문에 답을 받느라 P0 구현을 중단하지 않는다. 필요한 정보가 없으면 live 단계만 막고 독립적으로 가능한 작업을 완료한다.

## 완료 보고 템플릿

```markdown
# bench-router 구현 결과
- 상태: P0/P1/P2 완료 여부, offline/live 검증 구분
- 구현 commit/변경 파일:
- 설계 변경 및 policy/schema version:
- 실제 환경: OS/Python/herdr/Agent CLI/model/config
- 재현 명령:
- 테스트: 통과/실패/skip, fixture와 live 구분
- 소스: revision/기준일/요청 수/last-good/attribution
- live run: run_id/pane/receipt/result
- 비용·지연: 실측 여부, proxy 구분
- 알려진 한계 및 unresolved execution:
- 다음 한 가지 작업:
- 사용자에게 필요한 정보:
```

