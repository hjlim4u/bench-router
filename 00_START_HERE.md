# bench-router 문서 안내와 현재 상태

갱신: 2026-10-24 · Python 3.11+ · 선택 정책: `vendor-guided` 버전 `6`

bench-router는 **위임할 작업에 맞는 CLI Agent 프로필의 근거를 제공하고 선택·실행을 연결하는 라우터**다. 실행 가능한 구현은 `bench_router/`에 있다. Orchestrator가 위임 여부·작업 분해·팀 구성·최종 선택·결과 채택을 맡고, 라우터는 필수 제약·공식 가이드·비교 가능한 벤치마크·선택 기록을 검사한다. 실제 실행은 herdr-projects 1.2.1과 Herdr에 위임한다.

## 먼저 실행할 것

저장소 루트에서 실행한다. 오프라인 CLI에는 별도 설치가 필요 없다.

```bash
python3 -m bench_router.cli --help
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
python3 -m bench_router.cli wiki compile --check
```

설정은 `~/.config/bench-router/profiles.toml`, 캐시는 `~/.cache/bench-router`가 기본이다. `examples/profiles.example.toml`은 모두 비활성인 placeholder다. 직접 편집하거나 `profiles discover`로 생성한다. 기존 설정 교체에는 `--force`가 필요하다. Arena refresh는 `pyarrow`가 필요하므로 `mise install` 후 `mise run setup`을 실행한다.

## 현재 선택·실행 흐름

1. `route --task task.json --host codex --dry-run`으로 오프라인 판단 패킷을 받는다. 호스트는 실제 환경에 맞춘다. `decision_required`와 종료 코드 17은 미완료 판단을 뜻한다.
2. `analysis` → 적격 벤더별 `guidance` → 필요한 경우 `benchmark` 순으로 응답을 모아 `--decision-response`로 전달한다. dry-run과 `evaluate`는 네트워크·Herdr·파일 쓰기를 수행하지 않는다.
3. 복수 적합 후보가 남으면 자동 순위를 만들지 않는다. `evaluate --format 3`의 완료된 평가(schema 4.0)를 바탕으로 상위가 `select`로 selection 6.0을 만든다. 단일 적합 후보이며 미검증 조건이 없을 때는 자동 selection 5.0이 가능하다. CLI의 format 번호와 JSON schema 버전은 다르다.
4. `route --selection selection.json --dry-run`으로 재검증하고, live 실행에는 `--dry-run`을 뺀다. 현재 제약·가용성을 다시 검사한다. 제출된 같은 task/round는 새 판단보다 기존 receipt 회수가 우선한다.
5. `collect`로 결과 계약을 검사하고 상위가 실제 성공 여부를 검토해 `feedback`을 남긴다. `completed`는 결과 수신 상태이며 품질 합격 판정이 아니다.

가중합·near-tie·default/fallback 자동 선택과 `--policy legacy`는 제거됐다. `evaluate` 기본 출력은 2.0의 사실·제약 조회이며, vendor-guided 후보 적합성은 `--format 3`에서 제공한다. 기존 selection 2.0과 `--profile`은 명시적 override로 유지한다.

## 문서별 역할

| 문서 | 내용 |
|---|---|
| [README](README.md) | 설치·빠른 시작·전체 개요 |
| [01 의도와 결정](01_INTENT_AND_DECISIONS.md) | 책임 경계와 설계 이유 |
| [02 외부 근거](02_EVIDENCE_AND_DEPENDENCIES.md) | 외부 의존성과 과거 조사 근거의 확인 범위 |
| [03 데이터와 선택](03_ROUTING_AND_DATA_SPEC.md) | 수집·매칭·신선도·선택 경로 |
| [04 입출력과 실행](04_INTERFACE_AND_HERDR.md) | CLI·task·프로필·결과·복구 계약 |
| [05 개발과 운영](05_IMPLEMENTATION_PLAYBOOK.md) | 모듈 구성·변경 절차·운영 명령 |
| [06 검증과 미결 사항](06_VALIDATION_AND_OPEN_ITEMS.md) | 현재 검증 범위와 남은 검증 |
| [vendor-guided 정책](docs/vendor-guided-routing.md) | 정책 6의 단계·판단 응답·선택 재생 |
| [라우팅 계약](docs/routing-contracts.md) · [상위 연동](docs/orchestrator.md) | context·assessment·selection·group 버전과 사용법 |
| [Projects 실행](docs/projects.md) · [상세 레퍼런스](docs/reference.md) | 실행 백엔드·권한·전체 명령 |
| [책임 경계](docs/orchestration-boundary.md) | 상위 패턴 정책과 단건 라우터의 구분 |
| [구현 상태](docs/implementation-status.md) | 현재 기능·검증 결과·과거 실측 기록 |

## 문서와 증거를 읽는 기준

사용자 요구와 저장소 `AGENTS.md`를 먼저 따른다. 현재 동작은 코드·테스트에 대조하고, 선택의 상세 계약은 vendor-guided 문서, 실행은 Projects 문서를 함께 확인한다. 초기 설계의 가중치나 과거 eval 결과를 현재 선택 정책으로 해석하지 않는다. 조사·분석 문서는 각 확인일 당시의 기록이다.

fixture 통과, 외부 데이터 실호출, live Agent smoke, 작업군 품질·비용 평가는 서로 다른 증거다. 이전 직접 Herdr smoke와 legacy 작업군 비교가 현재 Projects 실행·정책 6을 검증한 것은 아니다. API 키·로그인·특정 모델 사용 가능 여부는 각 운영 환경에서 확인한다.
