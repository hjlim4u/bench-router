# bench-router 구현·검증 Handoff

문서 버전: 1.0 · 작성일: 2026-10-12 (Asia/Seoul) · 대상: 별도 CLI 환경의 새 Agent 세션

## 새 Agent에게 주는 첫 지시

사용자가 원하는 것은 **위임할 작업에 맞는 CLI Agent 프로필을 외부 벤치마크 근거로 선택하는 얇은 라우터**다. Orchestrator가 위임 여부와 전달 프롬프트를 결정한다. bench-router는 캐시를 읽고 프로필을 선택하여 herdr에 전달한다. 실제 실행·터미널 상태 관찰·출력 수집은 herdr에 맡긴다.

이 묶음에는 실행 가능한 라우터 구현이 없다. 설계, 계약, 구현 순서, 검증 시나리오와 합성 예제만 있다. 이 세션에서는 실제 API 키, 사용자 머신, herdr 바이너리, 운용할 모델 목록을 확인하지 못했다. 문서에 등장하는 프로필은 비활성 예제이며 실제 사용 가능한 모델을 뜻하지 않는다.

아래 순서로 읽고, 기존 저장소가 있다면 그 저장소의 AGENTS.md 및 현재 코드를 먼저 확인한다. 기존 구현이 있으면 재사용하고, 없다면 Python 3.11+ 표준 라이브러리 중심의 최소 CLI를 구현한다. 임베딩·Jev·원격 실행·Agent 재사용은 첫 구현의 필수 조건이 아니다.

## 전달할 컨텍스트 유형과 파일

| 유형 | 새 세션에서 필요한 이유 | 파일 |
| --- | --- | --- |
| 부트스트랩·현 상태 | 무엇을 읽고 무엇부터 실행할지, 구현 여부 | 이 파일 |
| 사용자 의도·범위·결정 근거 | 구현 범위를 임의로 확장하거나 축소하는 실수 방지 | [01_INTENT_AND_DECISIONS.md](01_INTENT_AND_DECISIONS.md) |
| 외부 의존성·근거·불확실성 | 초안의 API·명령·수치를 사실로 오인하지 않기 | [02_EVIDENCE_AND_DEPENDENCIES.md](02_EVIDENCE_AND_DEPENDENCIES.md) |
| 데이터·분류·선택 정책 | 캐시와 점수 계산을 재현 가능하게 구현 | [03_ROUTING_AND_DATA_SPEC.md](03_ROUTING_AND_DATA_SPEC.md) |
| 입력·출력·실행 계약 | Orchestrator/herdr 연결, 중복 위임·잘못된 완료 방지 | [04_INTERFACE_AND_HERDR.md](04_INTERFACE_AND_HERDR.md) |
| 구현 순서·운영 방법 | 환경 정보가 없어도 독립 작업을 진행하기 | [05_IMPLEMENTATION_PLAYBOOK.md](05_IMPLEMENTATION_PLAYBOOK.md) |
| 검증·완료 기준·미결 항목 | 통과 여부를 객관적으로 보고하고 다음 세션에 이어주기 | [06_VALIDATION_AND_OPEN_ITEMS.md](06_VALIDATION_AND_OPEN_ITEMS.md) |
| 합성 예제·기대값 | API와 실제 Agent 없이 계약·계산 검증 | [examples/task.synthetic.json](examples/task.synthetic.json), [examples/profiles.example.toml](examples/profiles.example.toml), [examples/scoring.synthetic.json](examples/scoring.synthetic.json) |

## 읽는 순서

1. 00 → 01 → 02를 읽어 목적과 근거 수준을 이해한다.
2. 03 → 04를 읽고 계약을 먼저 구현한다.
3. 05의 P0 → P1 → P2 순서로 진행한다. 통과 기준은 06에 있다.
4. examples의 파일을 실제 운용 설정으로 복사할 때 placeholder를 현장 값으로 바꾼다. 비활성 예제 설정을 그대로 운용하지 않는다.
5. 종료 전 06의 완료 보고 템플릿과 체크포인트를 작성한다.

## 문서의 권위와 변경 원칙

- 사용자 요구가 최우선이다. 새 세션에서 받은 추가 지시는 이 문서보다 우선한다.
- 본문에서 **확정 원칙**은 사용자 요구를 구현하기 위한 경계다.
- **v1 기본값**은 이 handoff가 정한 재현 가능한 시작 정책이다. 검증된 최적값이 아니다.
- **현장 검증**은 설치 버전·실제 계정·실제 데이터에서 확인해야 한다.
- **보류** 항목은 MVP에 자동으로 넣지 않는다.
- 다중 기준 라우팅(후보 평가와 선택의 분리, 지표·제약, 선택 기록, 병렬 선택)의 현재 규범은 `docs/routing-contracts.md`다. 03의 점수 계산·선택 절은 **legacy 자동 route 정책**으로 유지되며 최종 선택의 규범이 아니다. Orchestrator 연동 사용법은 `docs/orchestrator.md`.
- 문서 간 모순을 발견하면 인터페이스는 04, 계산은 03을 기준으로 해결하고 변경 이유를 기록한다. 사용자 요구를 변경하는 해석이면 사용자에게 확인한다.
- 웹 자료는 확인 시점의 사실이며 설치된 바이너리와 계정 응답을 대신하지 않는다.

## 새 세션에 붙여 넣을 프롬프트

> bench-router-handoff/00_START_HERE.md부터 순서대로 읽고 벤치마크 기반 Agent 라우터의 구현과 검증을 이어가세요. 기존 저장소와 AGENTS.md를 먼저 확인하세요. 문서의 확정 원칙·v1 기본값·현장 검증·보류를 구별하세요. P0/P1의 오프라인 계약과 합성 검증부터 진행하고, 실제 프로필과 herdr를 확인한 뒤 P2 위임 smoke test를 수행하세요. 요청 경로의 벤치마크 API 호출, 별도 Agent 실행 엔진, 무조건적인 prompt 재전송을 만들지 마세요. 실제 API/herdr 검증을 못하면 fixture 통과와 실환경 미검증을 분리해 보고하세요. 완료 시 변경 파일, 재현 명령, 테스트 결과, 한계, 다음 작업을 남기세요.

## 현재 완료·미완료

완료: 사용자 요구 정리, 제공된 타 AI 초안의 주요 가정 점검, 공식 웹 문서 확인, 설계 보완, 합성 기대값 및 handoff 구성.

미완료: 라우터 구현, 실제 소스 인증 호출, 실제 데이터 파싱, herdr 설치 버전 고정, 실제 CLI 모델 인자 검증, live Agent 실행, 작업군별 성능 측정. 이 묶음을 이 항목들이 완료된 증거로 사용하면 안 된다.

묶음 자체검사: Markdown 내부 파일 링크·코드 블록 쌍, JSON/TOML 파싱, 합성 coverage/Q/S 및 priority별 선택 기대값, 합성 결과 파일 SHA-256, ZIP 내부 바이트 일치를 확인했다. 이는 문서·예제 검증이며 라우터 구현 테스트가 아니다.

## 운반 방법

묶음 전체를 새 환경의 작업 디렉터리에 풀고 위 프롬프트와 상대 경로를 전달하면 된다. 현재 세션의 scratch 절대 경로, ChatGPT 전용 도구, 숨은 대화 기록은 필요하지 않다. ZIP 내부 MANIFEST.sha256은 전달 중 파일 변경 여부를 확인하는 용도다.

