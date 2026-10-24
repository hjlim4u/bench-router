# 사용자 의도와 설계 결정

갱신: 2026-10-24. 현재 동작과 계약은 [문서 안내](00_START_HERE.md), [vendor-guided 정책](docs/vendor-guided-routing.md), [Projects 실행](docs/projects.md)을 따른다.

## 설계의 출발점

사용자는 구현 전에 기존 OSS/도구의 활용 가능성을 조사하고, 타 AI 답변과 객관적으로 교차 검증한 설계를 원했다. 초기 문서는 다른 CLI Agent가 구현을 이어갈 handoff로 작성됐고, 현재는 구현된 라우터의 설계 결정 기록이다.

아래 사용자 요구는 초기 목표를 보존한다. 구현 과정에서 가중합 자동 선택은 제거됐고, 공식 가이드 기반 평가와 상위 최종 선택으로 구체화됐다. 과거 외부 도구 조사는 확인일 당시의 기록이며 현재 버전의 전면 비교가 아니다.

## 사용자 요구

1. Orchestrator가 프롬프트 복잡도와 위임 필요성을 판단한다.
2. 위임 시 컨텍스트와 subagent용 프롬프트를 구성해 스크립트를 호출한다.
3. 스크립트가 관련 리더보드·벤치마크를 API/캐시에서 얻어 적절한 Agent를 선택한다.
4. 선택된 Agent에 프롬프트를 전달한다.
5. 완료 후 결과를 Orchestrator에 반환하여 추가 라운드·종료를 결정하게 한다.
6. 빈번한 데이터 API 호출과 프롬프트-벤치마크 검색 비용을 줄인다.
7. subagent 호출·결과·상태 추적은 herdr 기능을 최대한 이용하여 직접 구현 범위를 줄인다.
8. 기존 도구가 요구를 충족한다면 불필요한 별도 구현을 피한다.

## 핵심 경계

| 주체 | 책임 |
| --- | --- |
| Orchestrator | 위임 판단, 작업 분해·팀 구성, task/facets·컨텍스트, 복수 후보 최종 선택, 결과 검토·추가 라운드·예산 |
| bench-router | 스냅샷 수집·정규화, 제약, 공식 가이드 적합성·비교 근거·선택 기록, 실행 연결·결과 계약 검사 |
| herdr-projects / herdr | worktree·pane와 Agent 실행, 입력 전달, 실제 상태 관찰·복구 |
| Subagent | 작업 수행, 실행별 결과 파일 작성, 수행·미수행·오류 정보 보고 |
| 주기 실행 도구 | 정기 refresh 실행; cron/systemd/launchd 중 현장 하나를 사용 |

결과 파일 검사와 중복 전송 방지를 위한 작은 로컬 receipt는 필수 접착 코드다. 별도 worker queue, heartbeat, 자체 terminal detector, lifecycle 서버를 만들라는 뜻이 아니다.

## 설계 결정 기록

| ID | 결정 | 이유 | 지위 |
| --- | --- | --- | --- |
| D01 | 라우팅 단위는 프로필(Agent CLI+모델+설정) | 모델이 같아도 하네스·reasoning effort·도구·버전이 다름 | 확정 원칙 |
| D02 | route는 벤치마크 API를 호출하지 않음 | 사용자 요청 지연과 API 부담 제거 | 확정 원칙 |
| D03 | refresh는 별도 명령과 OS 주기 작업 | 상시 서비스·Redis 없이 충분 | v1 기본값 |
| D04 | SQLite 이력 + 작은 JSON snapshot | 표준 라이브러리, 읽기 경로 단순화, 근거 재현 | v1 기본값 |
| D05 | 기본 평가는 L1 규칙 → general; vendor-guided는 의미 analysis 사용 | 초기 L0 categories 입력은 제거됐고 명시 작업 특성은 task.facets 사용 | 구현 |
| D06 | Jev 또는 native bench-decider로 제한된 단계별 판단, 임베딩은 미도입 | 작업 분석·벤더별 가이드 시작점·평가 관련성을 구조화 | 구현 |
| D07 | herdr-projects 공개 CLI를 subprocess argv로 호출 (2026-10-15) | 프로젝트 실행 계층 재사용. 결과 계약·admission은 Router 유지 | 확정 원칙 |
| D08 | Projects approval/done 또는 headless 종료 확인 + 실행별 결과 계약 | 실행 종료는 작업 성공 인증이 아님 | 확정 원칙 |
| D09 | 단일 머신·새 worker, wait-ms/collect·명시적 resume 지원 | 원격 실행·자동 세션 pool은 미구현 | 구현 |
| D10 | 선택·수집·실행을 별도 함수로 유지 | dry-run·fixture 검증 가능; 플러그인 프레임워크는 만들지 않음 | v1 기본값 |
| D11 | 결과 최적성은 실제 작업으로 비교 검증 | 외부 순위는 개별 작업 성공확률이 아님 | 확정 원칙 |
| D12 | API 응답/CLI 스키마를 버전 고정하여 기록 | 동적 데이터·문서와 설치 버전 차이를 통제 | 확정 원칙 |
| D13 | 최종 선택·지표 간 trade-off·예산은 Orchestrator, Router는 사실 정리·필수 제약·선택 기록·실행 (2026-10-13) | 지표가 늘어도 Router 정책을 바꾸지 않고, USD와 percentile 같은 단위를 의미 없이 섞지 않음. 근거: docs/routing-extensibility-review.md | 확정 원칙 |
| D14 | 새 지표 = `METRICS` 한 줄(+거를 때만 `CONSTRAINTS` 함수 하나), 미등록 지표는 전달만 (2026-10-13) | 플러그인 프레임워크·규칙 엔진 없이 확장. 계약: docs/routing-contracts.md | v1 기본값 |
| D15 | 정책 6: analysis → 벤더별 guidance → 필요 시 benchmark; 복수 적합 후보는 상위 선택 | 가이드 원칙을 벤더 사이에 일반화하거나 서로 다른 평가를 합산하지 않음 | 구현 |
| D16 | 후보 평가 schema 4.0(`--format 3`), 자동 selection 5.0, 외부 selection 6.0 | CLI 형식 번호·JSON schema·선택 정책 버전을 분리 | 구현 |
| D17 | group 2.0 반복 selection 허용, max_parallel 1–4, 합산 admission 4 | 실행 인스턴스별 worktree·receipt를 유지 | 구현 |

## 타 AI 초안에서 유지하는 부분

- 요청/갱신 경로 분리, 로컬 캐시, 마지막 정상 스냅샷, 원자적 JSON 교체.
- 닫힌 카테고리와 Orchestrator 힌트, 강제 제약을 먼저 적용하는 결정적 선택.
- 모델명 alias 정규화와 agent+model 결과의 구분.
- herdr start/prompt/wait/read 활용과 결과 파일 반환.
- dry-run/explain, 선택 근거·기준일·feedback 기록.
- 임베딩·결정 모델을 선택적 고도화로 두는 방향.

## 초기 초안 검토 기록 (당시 기준)

아래 coverage 수축·default·결정성 설명은 초기 설계 비교다. 현재 quality/coverage는 기본 평가 진단으로만 남고 비용 차감·default/fallback·near-tie 자동 선택은 제거됐다. 의미 판단은 저장된 단계 응답과 digest로 재생한다.

| 초안 가정 | handoff 기준선 |
| --- | --- |
| AA 전체 목록 단일 호출·math index | 실제 pagination을 순회; 현재 Free 스키마에 math 지수 가정 금지 |
| LMArena code = 일반 코딩 | webdev는 웹 개발 proxy; 저장소 수정이나 모든 코드 생성의 직접 점수로 쓰지 않음 |
| Terminal-Bench 2.0/최신 자동 혼용 | benchmark version을 고정; 현재 공식 사이트는 4.0 표시, 2.0 행과 섞지 않음 |
| 하네스 누락 시 모델 점수 × 0.9 | 그 값은 검증된 하네스 보정이 아님; MVP에서 다른 평가의 점수 대입 금지 |
| 빠진 점수 가중치 재분배만 수행 | coverage와 결측 수축을 함께 사용; 부분 데이터가 유리해지지 않게 함 |
| 7일 오래된 route가 자동 refresh 실행 | v1 route는 경고만 반환; refresh는 별도 timer/명시 호출이 담당 |
| 캐시 없음 → default 무조건 위임 | default에도 동일 하드 제약; 없거나 부적합하면 후보 없음으로 종료 |
| idle Agent는 이름만 같으면 재사용 | MVP는 재사용 안 함; 이후 cwd·config fingerprint·소유권·lock 모두 확인 |
| idle/done + 결과 파일 존재 = 완료 | run ID·nonce·프로필·결과 해시·경로·manifest 상태까지 확인 |
| 같은 입력이면 항상 같음 | task+snapshot+config+명시적 가용성 snapshot이 같을 때 결정적 |
| 사람이 고른 Agent와 70% 일치 = 성공 | 참고 지표; baseline 대비 실제 성공률·성공당 비용·지연으로 판단 |
| Switchyard 0.2만 기준 | 확인된 공식 README는 0.3.0과 sub-agent 전략도 언급; 범위를 단정하지 않음 |
| L0 비용 정확히 0, 임베딩 5–20ms 보장 | 분석 재사용으로 추가 호출을 없앰; 토큰/지연은 실제 측정 |
| Jev 가격·영어 중심을 확정 | 공식 접근성·계약·가격·다국어 적합성은 현장 확인, 기본 비활성 |

## 구현 필요성 판단

검토한 RouteLLM·Switchyard·semantic-router는 재사용할 수 있는 라우팅 부품이다. 제공 자료와 확인한 공식 문서만으로 **외부 벤치마크 수집 → 실제 CLI 프로필 매칭 → herdr 위임** 전체를 즉시 대체하는 구성을 확인하지 못했다. 이것이 시장 전체에 대체 도구가 없다는 증명은 아니다.

따라서 최소 수집·선택·herdr 접착 코드를 구현한다. 구현 도중 기존 저장소/도구가 같은 계약을 충족함을 확인하면 대체하고, 어떤 기능과 검증을 재사용했는지 기록한다.

## 범위 밖

자체 Agent 런타임, agent 내부 매 turn 모델 교체, 자동 가중치 학습, vector DB, 웹 대시보드, Kubernetes, 자동 원격 파일 동기화, herdr 플러그인 자동 설치는 범위 밖이다. 구현된 병렬 실행 어댑터는 패턴·DAG·투표·예산 scheduler가 아니다. 벤치마크 태스크 자체를 매일 재실행하지 않는다.

Python은 권장 기본값이다. 현장 저장소가 다른 언어로 충분히 구현되어 있으면 재작성보다 계약 준수를 우선한다.

