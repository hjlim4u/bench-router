# 검증 범위·완료 기준·미결 사항

갱신: 2026-10-24. 현재 테스트는 초기 V01–V40 시나리오를 확장했으며, 제거된 legacy 선택 규칙의 기대값을 현재 계약으로 사용하지 않는다.

## 오프라인 검증

```bash
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
python3 -m bench_router.cli wiki compile --check
```

| 파일 | 현재 검증 범위 |
|---|---|
| `test_p0.py` | 입력·context 지표·제약·percentile·quality/coverage·기본 평가, facet 규칙·wiki/evidence, vendor-guided 단계·가이드·관련성·공개 평가·선택 6.0 |
| `test_p1.py` | AA pagination, Arena/MG fixture, malformed payload 격리, 부분 실패·last-good, alias·effort·평가 조건, deadline·잠금·원자 게시 |
| `test_p2.py` | Projects 및 headless 실행, argv·receipt·결과 경로/nonce/hash, blocked·timeout·불확실 전송, 회수·명시적 제어·선택 재검증 |
| `test_p3.py` | worktree 격리·공유 scratchpad, group 선택·동결 plan·재회수, 반복 selection, 전달 상태·한도 |
| `test_coordination.py` | 공유 admission 4개, 경로 중첩·소유권·정지 확인·결과 채택, Projects 연동 |
| `test_codeburn.py` | CodeBurn 가용성·quota·사용량 및 프로필 discovery fixture |

외부 CLI는 fake/mock으로 대체하고 Git worktree는 임시 저장소에서 실제로 만든다. 오프라인 테스트는 실제 모델·PTY·board ticker·계정 quota의 동작을 증명하지 않는다. 이번 실행 결과와 날짜는 [구현 상태](docs/implementation-status.md)에 기록한다.

## 현재 선택 계약의 주요 검증 기준

- 하드 제약 실패는 선택·실행 불가다. 벤치마크 결측 자체는 하드 탈락이 아니며 0점과 구분한다.
- `evaluate` 기본 2.0은 facts·제약·quality/coverage이며 선택하지 않는다. `score`·`legacy_score`·`cost_proxy`를 출력하지 않는다.
- 정책 6은 analysis → 적격 벤더별 guidance → 필요한 경우 benchmark 순이다. 벤더별 공식 가이드와 모델 ID·effort 매핑을 따르고 다른 벤더 원칙을 공통화하지 않는다.
- 판단 요청에는 해당 단계에 필요한 정보만 보낸다. 가이드에 없는 구성은 `guidance_missing` 등으로 잠정 상태를 남긴다.
- 비교 가능한 측정 조건과 fresh raw 값만 비교한다. exact/proxy나 서로 다른 cohort의 percentile을 섞어 종합 점수·다수결을 만들지 않는다.
- 복수 적합 후보는 `upstream_selection_required`다. 단일 적합 후보도 미검증 조건 또는 관련성 기권이 있으면 자동 선택하지 않는다.
- 완료된 format 3 평가(schema 4.0)에서 `select`가 selection 6.0을 만든다. provisional·alternative는 명시적 수용이 필요하고 unsuitable·hard 탈락은 우회할 수 없다.
- selection 5.0은 라우터의 단일 추천에 묶인다. 6.0은 다른 적합 후보를 상위 정책으로 선택할 수 있다. 2.0·`--profile`은 별도 override 경고를 유지한다. 과거 selection 3.0·4.0은 재평가해야 한다.
- 입력·근거·정책 변경은 재평가 대상으로 처리한다. 단계 digest는 실제 의존성만 묶으며 과거 정책 1–5 기록은 새 선택에 재사용하지 않는다.
- dry-run·evaluate·explain·evidence는 네트워크·Herdr·파일 쓰기가 없다. 판단 패킷·기권은 종료 17이며 legacy로 자동 전환하지 않는다.

## 실행·복구의 주요 기준

- 같은 task/round와 같은 semantic hash는 기존 receipt를 회수한다. 다른 내용·프로필 충돌은 실행하지 않는다. 정책·판단 API 변경도 이미 제출한 prompt를 재전송하는 이유가 아니다.
- 제출 의도는 호출 전에 기록한다. 응답 유실·timeout·crash 뒤에는 전달 상태를 보존하고 `collect_first`를 따른다.
- `completed`에는 올바른 run ID·nonce·fingerprint·상태·UTF-8·크기·경로·SHA-256 검사가 필요하다. `checks`는 worker의 주장이고 라우터가 자동 실행하지 않는다.
- 제출 전 확정 실패는 receipt와 admission을 정리한다. 실행 불확실 슬롯은 worker 정지 확인 전 자동 해제하지 않는다.
- group 2.0은 반복 profile도 별도 실행 인스턴스로 센다. task당 8·group당 16·`max_parallel` 1–4 한도를 지킨다. stale 선택 하나면 전체 미실행이며 모든 선택 완료 전 실행 자원을 만들지 않는다.
- 실행 이후 일부 실패는 보존하고 group 재호출은 plan과 receipts를 회수한다. `delivery_state`·`reassignment`를 member rounds에 전달한다.

## live smoke와 효과 평가는 별도

운용 환경에서 승인된 작은 Git 프로젝트·프로필로 Projects 버전·Herdr 세션·CLI 로그인·모델 인자·권한을 확인한다. 먼저 offline selection을 검증한 뒤 live 실행, 동일 task/round 재회수, collect, 결과 해시·브랜치 확인, feedback 순으로 진행한다. 미커밋 변경은 worker에 전달되지 않음을 확인한다.

현재 Projects 1.2.1 경로의 live 검증과 정책 6의 작업군 품질·비용 평가는 이번 문서 갱신에서 수행하지 않았다. 과거 직접 Herdr smoke와 20개 과제 결과는 [eval/results/v1.md](eval/results/v1.md), [비용 기록](eval/results/v1-cost.md)에 있으며 현재 정책의 효과를 입증하지 않는다.

효과 평가는 고정 프로필·저비용 우선·현재 상위 선택 정책을 같은 과제·환경·예산·acceptance check로 비교해야 한다. verified success/partial/fail, 시간, 판단 호출 비용, 실제 토큰과 비용 proxy 구분, abstain·결측·제약 위반·중복 전송을 기록한다. 과제당 한 번·20개 정도의 탐색으로 통계적 우수성을 주장하지 않는다.

## 남은 검증과 운영 선택

| 항목 | 현재 상태 / 필요한 일 |
|---|---|
| Projects 대화형·headless live | fake CLI와 실제 임시 worktree 검증; 실제 모델·PTY·복구 smoke는 운영 환경에서 별도 확인 |
| 정책 6의 작업별 품질·비용 | 공식 가이드 적합성과 비교 근거를 제공할 뿐 성공·최저 비용을 보장하지 않음; held-out 작업군 평가 필요 |
| workflow effort 개선 | `workflow_gain_unverified` 유지; 상위가 실제 작업 대조 평가 후 수용 |
| 계정·모델·quota | discovery·CodeBurn은 사전 정보; 실행 가능성과 팀 전체 잔여 budget 보장은 아님 |
| exact 데이터 | model/harness/effort/평가 조건이 일치하는 행만 인정; 결측을 proxy로 채우지 않음 |
| OS timer·보존 정책 | timer 자동 설치 없음; snapshot 30일과 사용자 로그 보존은 운영자가 조정 |
| 전체 팀 예산·패턴 선택 | 상위 책임; router에 예약·정산·DAG·투표 엔진 없음 |
| 별도 JSON Schema·format 1 제거 | 런타임 validator가 계약을 강제; 제거 시점은 별도 결정 |

보고에는 변경 파일·계약 버전·재현 명령·fixture/live 구분·실제 검증 결과·한계를 남긴다. `completed`와 최종 품질 합격을 구분한다.
