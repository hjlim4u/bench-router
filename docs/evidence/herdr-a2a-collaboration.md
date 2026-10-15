# herdr-a2a 도입 재검증

검증일: 2026-10-15. 결론: 현재 bench-router의 기본 실행 경로는 기존 Herdr CLI를 유지한다. A2A 실험 구현은 `experiment/herdr-a2a-adapter` 브랜치의 `e9f8540` 커밋에 보존했다. 이번 변경에서 main의 CLI, dispatch, collect, 테스트는 도입 전 상태(`9da24ca`)로 복원했다.

## 검증 대상과 경계

- 원본: [IsaiasZc/herdr-a2a, b94d60f](https://github.com/IsaiasZc/herdr-a2a/tree/b94d60f1c255d63e5c69d8fd3f8f288b81922057). 해당 커밋의 수정하지 않은 소스를 `npm ci --ignore-scripts`와 `npm run build`로 준비했다. 소스 작업 트리는 깨끗하다.
- 실행: [eval/herdr_a2a_collaboration.mjs](../../eval/herdr_a2a_collaboration.mjs). 실제 gateway, SDK 클라이언트, HTTP/SSE, delegation service, spawn manager, reuse policy, task service를 사용했다.
- 대체한 부분: worker/Herdr 응답, relay 실행 결과, layout, 메모리 저장소. 실제 agent, PTY 입출력, SQLite 영속성, 모델 호출은 사용하지 않았다.
- 원시 결과: [herdr-a2a-collaboration.json](herdr-a2a-collaboration.json). 프로세스 종료 코드 0은 관측 결과가 스크립트의 assertion과 일치한다는 뜻이다. 도입 조건 통과를 뜻하지 않는다.

## 관측 결과

| 순서 | 작업 | 결과 |
| --- | --- | --- |
| 1 | writer 초안 → reviewer 검토 → writer 재작성 | 모두 completed, SSE 상태·artifact 수신 |
| 2 | 완료 후 같은 contextId로 새 작업 생성 | contextId 유지, 새 task ID, 유휴 상태의 첫 writer 재사용 |
| 3 | 첫 writer를 working으로 표시하고 별도 대화 작업 요청 | 두 번째 writer 생성 |
| 4 | 첫 writer가 다시 idle인 상태에서 원래 contextId로 재작성 요청 | 더 최근에 생성된 두 번째 writer 선택 |
| 5 | 위 요청에 이전 task ID들을 referenceTaskIds로 제공 | relay에는 새 요청 본문만 전달됨; 이전 결과 자동 주입 없음 |

4·5번은 같은 대화 식별자가 같은 물리 worker나 대화 기억을 보장한다는 가정을 반증한다. 스크립트의 `failed_same_writer_affinity`는 이 가정을 요구하는 도입 조건의 실패다. A2A 규격 자체의 위반이나 모든 협업 방식의 실패를 의미하지 않는다. 이번 프로브는 동시 요청의 경합을 재현하지 않고, 두 worker가 생긴 뒤의 선택 정책을 검증한다.

근거 소스: [executor.ts](https://github.com/IsaiasZc/herdr-a2a/blob/b94d60f1c255d63e5c69d8fd3f8f288b81922057/src/a2a/executor.ts)는 새 작업에 contextId와 텍스트를 넘기며 referenceTaskIds를 relay 입력으로 확장하지 않는다. [reuse-policy.ts](https://github.com/IsaiasZc/herdr-a2a/blob/b94d60f1c255d63e5c69d8fd3f8f288b81922057/src/spawn/reuse-policy.ts)는 실행 조건과 상태가 맞는 후보 중 가장 최근 인스턴스를 고른다. [delegation-service.ts](https://github.com/IsaiasZc/herdr-a2a/blob/b94d60f1c255d63e5c69d8fd3f8f288b81922057/src/core/delegation-service.ts)는 새 작업 본문을 relay로 전달한다.

## 판단과 다음 조건

후속 구현에서 [선택적 협업 규약](../hybrid-collaboration.md), 공유 skill 진입점, [패턴·기록 예제](../../examples/hybrid-collaboration.json)를 추가했다. 새로운 router backend나 커스텀 플러그인 API는 추가하지 않았다.

확장 프로브는 11회 요청(질문과 답변은 같은 task이므로 고유 task는 10개)에서 다음을 확인했다. `hybrid_protocol`은 실제 공개 gateway/SDK를 통과한 모의 worker 검증이고 `example_checks`는 상위 agent가 따를 fixture의 일관성 검사다.

- worker가 교체된 뒤에도 이전 결과를 포함한 요청 본문이 그대로 전달된다.
- 병렬 검토 중 하나가 실패해도 성공한 검토의 artifact는 보존된다.
- input-required 이후 같은 task·worker에 답변을 전달해 completed로 진행한다.
- completed task의 이어가기는 거부되며, 후속 검토는 새 task로 생성된다.
- 입력 해시와 의존 단계, 오래된 검토 보류, 전달 불확실 시 재제출 금지, 완료와 채택 구분 예제가 일관된다.

이 검사는 코드 구현 품질, 실제 질문/인증 감지, PTY, SQLite, 전송 유실 후 자동 복구를 검증하지 않는다. 특히 fixture 검사는 중복 실행 방지나 채택 판정을 수행하는 실행기가 존재한다는 뜻이 아니다. 기존 `adoption_gate: failed_same_writer_affinity`는 동일 worker 보장 가정의 반증으로 유지한다. 명시적 입력 전달을 사용하는 협업 흐름의 프로토콜 검사는 통과했다.

공개 A2A 경로에는 표준 메시지와 SSE를 통한 상태·결과 전달이라는 실질적 기능이 있다. 하지만 기존 실험은 이를 `/bench-router/v1` 커스텀 API와 별도 폴링으로 대체했고, 그 유지 비용을 정당화할 실제 품질·비용·복구 개선을 입증하지 못했다. 현재 기본 경로로 채택할 근거는 부족하다.

협업 확장 시에는 요구 계약부터 구분해야 한다. 같은 worker의 기억이 필요한 작업은 명시적인 affinity가 필요하다. 다른 worker로 옮길 수 있는 작업은 필요한 초안·검토 내용·제약을 요청 본문이나 검증 가능한 artifact로 전달해야 한다. contextId와 referenceTaskIds만으로 이를 대체하지 않는다. input-required 상태의 동일 task 이어가기는 이번의 완료 후 새 task 생성과 별도 시나리오다.

현재 단계에서는 추가 adapter나 자체 세션 관리 계층을 만들지 않는다. 재도입 판단에는 실제 agent로 작성→검토→수정 결과의 정확성, 재전달/중복 실행 여부, 실패 후 복구를 기존 CLI와 비교한 증거가 필요하다. 시간과 비용도 실제 관측값이 있을 때만 비교한다.

## 실행 및 제한

```powershell
node eval/herdr_a2a_collaboration.mjs .bench-router/herdr-a2a-patch-check
python -m unittest test_p0 test_p1 test_p2 test_p3
```

프로브 실행 전 지정한 원본 checkout에 `npm ci --ignore-scripts`와 `npm run build`가 필요하다. checkout과 node_modules는 저장소에 포함하지 않는다. bench-router 실행에는 Node나 플러그인이 필요하지 않다.

기존 Python 테스트는 총 53개 중 52개 통과, `test_v25_path_and_size_attacks` 1개가 Windows의 심볼릭 링크 생성 권한 부족(`WinError 1314`)으로 오류를 냈다. 해당 보안 검사를 생략하거나 성공으로 처리하지 않았다. Linux/WSL2 전체 통과는 이번에 확인하지 않았다.

실제 Herdr 기본 세션 검증은 미실행이다. 사용자는 직접 실행을 지시했으나 lean-ctx의 명령 허용 목록이 `herdr`를 차단했다. 해당 차단을 우회하지 않았다. 실제 모델 품질·속도·비용, PTY 결과 추출, 영속성 기반 장애 복구, 취소, 실제 input-required/auth-required 감지와 이어가기는 검증하지 않았다. 확장 프로브의 동시 두 요청은 모의 relay를 사용하며 실제 Herdr 동시 경합을 검증하지 않는다.

## 공통 조정 Adapter 구현

이후 충돌 검토를 반영해 Python 공통 admission과 원본 공개 CLI 기반 검토 Adapter를 추가했다. `route`/`parallel`도 같은 조정 계층을 사용한다. 작업 키는 cwd/task_id/round에 고정되며 backend 전환·입력 변경·합산 4개 초과·쓰기 범위 중첩을 차단한다. review는 버전별 역할 이름, 프로필 지문, 운영자가 확인한 설정 파일 해시와 공개 catalog/task identity를 검사한다. 이 해시는 실제 gateway의 실행 argv를 증명하지 않는다.

`python -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination`은 69개 중 68개 통과, 기존 Windows symlink 권한 오류 1개다. 새 Adapter 검사 16개는 모두 통과했다. 테스트는 독립 임시 조정 디렉터리와 fake CLI를 사용하며 실제 agent를 실행하지 않는다. 동시 admission, backend 중복, 응답 유실·질문 이어가기 중복 차단, 실패/취소 슬롯 보존, 입력 해시·채택 분리, session 고정, CLI 명령 연결을 검사했다.

원본 Node 프로브도 통과했다. `stock_cli_contract`는 원본 CLI 함수의 실제 gateway 응답과 SDK 상태 값·target/runtime/instance 형태가 Adapter의 전제와 일치함을 검사한다. worker·relay는 여전히 모의 처리다. 운영 gateway 설정, 실제 모델 품질·자원 절감, plugin 내부 재시도의 중복 가능성은 미검증이다. [설정·명령·제한](../hybrid-collaboration.md)에 따라 선택적으로 사용한다.
