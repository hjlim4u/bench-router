# 개발·운영 절차

갱신: 2026-10-24. 초기 P0–P3 구현은 완료됐다. 새 구현을 시작하는 대신 현재 모듈과 계약을 재사용한다.

## 모듈 구성

| 파일 | 책임 |
|---|---|
| `bench_router/cli.py` | argparse·설정 로드·명령별 출력·종료 코드 |
| `routing.py` | task/profile/context 검증, facts·필수 제약, 기본 benchmark quality/coverage, selection 호환 |
| `decision.py` / `decision_provider.py` | 정책 6의 단계별 판단·적합성·평가 비교·digest·선택 재생 / Jev·native 응답 계약 |
| `guidelines.toml` | 버전 고정 벤더별 가이드 원문·시작점·평가 후 escalation |
| `data.py` | AA/Arena/MG 수집·수동 import·SQLite·snapshot 게시 |
| `wiki.py` / `evidence.py` | 검토된 wiki 컴파일 / facet별 근거 조회 |
| `herdr.py` | 프로필 discovery·가용성 probe, Projects 대화형·Herdr headless 실행, receipt·collect·tell·stop·resume·결과 검사 |
| `parallel.py` | group 검증·선택 사전 검사·worktree·동결 plan·병렬 실행과 회수 |
| `coordination.py` / `locking.py` | 사용자 공유 admission·경로 중첩 방지 / OS별 파일 잠금 |
| `eval/` | 비교 과제·토큰/비용 분석·CodeBurn 보조 도구 |
| `skills/bench-router/` | 설치 가능한 Skill과 CLI·판단 진입 스크립트 |

## 변경을 시작할 때

1. `git status`와 적용되는 `AGENTS.md`를 확인하고 사용자 변경을 보존한다.
2. 변경하려는 계약과 호출자를 코드에서 확인한다. 선택은 [vendor-guided](docs/vendor-guided-routing.md), context·selection은 [routing-contracts](docs/routing-contracts.md), 실행은 [Projects](docs/projects.md)를 함께 읽는다.
3. 동작 변경이면 해당 `test_p*.py` 또는 coordination/codeburn 테스트에 합성 fixture를 추가한다. live 서비스로 단위 테스트하지 않는다.
4. 문서·CLI 예시·버전 영향도 함께 갱신한다. 기존 선택 버전을 재해석하거나 task/round의 회수 우선순위를 바꾸지 않는다.
5. 전체 오프라인 suite와 관련 문서 검사를 통과시킨다. 테스트·실데이터·live 검증을 구분해 보고한다.

```bash
python3 -m bench_router.cli --help
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
python3 -m bench_router.cli wiki compile --check
```

## 설치와 설정

핵심 CLI는 Python 3.11+ 표준 라이브러리로 동작한다. Arena refresh는 pyarrow가 필요하며 CodeBurn CLI는 선택적 가용성·사용량 도구다.

```bash
mise install
mise run setup   # uv sync --extra arena
mise run test
# 실제 네트워크 수집이 필요할 때만:
mise run refresh # 전체 source --force
```

사용자 설정·키는 저장소에 커밋하지 않는다. `examples/profiles.example.toml`을 복사해 활성화하거나 `profiles discover`로 생성한다. discovery는 설치된 CLI 모델 정보·Codex cache·가이드·CodeBurn 모델을 사용하며 계정의 실제 호출 성공을 보장하지 않는다. 기존 설정을 바꾸려면 `--force`를 명시한다.

## 선택부터 회수까지

```bash
BR="python3 -m bench_router.cli"
$BR status
$BR route --task task.json --host codex --dry-run
$BR evaluate --format 3 --task task.json --host codex --decision-response responses.json
$BR select --assessment assessment.json --profile PROFILE \
  --policy-id team-policy --policy-version 1 --reason "작업별 후보 검토 결과"
```

`responses.json`은 현재 단계까지의 검증된 응답 배열이다. 미완료 응답은 종료 17이므로 `status`를 확인해 다음 패킷을 해결한다. 완료된 `evaluate --format 3` 전체를 assessment 파일로 저장하고, `select` 출력에서는 `selection` 객체만 추출한다. 자세한 응답 형식은 [상위 연동](docs/orchestrator.md)을 따른다.

live 실행은 Linux/WSL2, Projects 1.2.1, Herdr와 대상 CLI의 설치·로그인이 필요하다. `cwd`는 커밋이 있는 Git 최상위여야 한다. 미커밋 변경은 worker에 전달되지 않는다.

```bash
$BR route --task task.json --selection selection.json --dry-run
$BR --herdr-session work route --task task.json --selection selection.json --wait-ms 0
$BR collect --run-id RUN --cwd /abs/project --wait-ms 60000
$BR feedback --run-id RUN --cwd /abs/project --outcome success --evaluator orchestrator
```

`--wait-ms 0`도 제출 자체는 수행한다. 반환된 `timed_out`은 취소가 아니므로 collect로 관찰한다. 재요청은 동일 task/round를 회수하며 새 prompt를 보내지 않는다. 의도적인 재실행은 부분 효과·정지 여부를 확인한 뒤 새 round로 요청한다.

## 병렬 실행과 자원 관리

상위가 만든 group 2.0의 `selections`는 순서 있는 실행 목록이다. 같은 프로필 반복도 별도 worker로 실행하며 task당 8개·group 전체 16개 한도에 포함한다. `max_parallel`은 1–4이며 공유 admission도 활성 4개를 제한한다. 모든 선택 검증이 끝나기 전에는 worktree·group 파일·worker를 만들지 않는다.

실행 시 plan을 저장하고 동일 group은 이를 회수한다. `delivery_state`·`reassignment`를 확인하고 `collect_first`를 따른다. 단순 `partial_failure`만 보고 자동 재시도하지 않는다. 패턴·DAG·투표·최종 채택·전체 예산은 상위 책임이다.

`completed`이면 관리 대상 pane을 반환하며 `resume`은 같은 대화를 다시 연다. `tell`·`stop`은 명시적 지시로만 호출한다. 제출 전 확정 실패는 receipt를 settle하고 admission을 반환한다. 실행 여부가 불확실하면 정지 확인 전에는 슬롯을 자동 해제하지 않는다. 필요한 경우 `coordination release --confirmed-stopped --note ...`로 기록한다.

## 데이터 운영과 체크포인트

refresh는 수동 또는 운영자가 별도로 등록한 timer에서 실행한다. 키·절대 실행 경로·config/cache·timezone을 현장에 맞추고, 예약 파일에 키를 직접 넣지 않는다. 요청 경로에서 빈 캐시를 채우지 않는다. [reference의 timer 예시](docs/reference.md#정기-실행-예시-설치하지-않음)를 참고한다.

상태 문서에는 구현 revision, 변경 파일, 검증 명령·결과, source 기준일·revision, 미해결 run·receipt, 계약 버전과 남은 검증을 남긴다. secret이나 개인 prompt를 복사하지 않는다. 현재 체크포인트는 [implementation-status](docs/implementation-status.md)에 있다.
