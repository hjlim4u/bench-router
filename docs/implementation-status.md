# bench-router 구현 상태

갱신: 2026-10-24 · 대조한 구현: `67d90a9` · 이번 변경은 문서 갱신이다.

## 현재 구현

| 영역 | 구현과 계약 |
|---|---|
| 선택 | vendor-guided 정책 6: analysis → 벤더별 guidance → 필요 시 benchmark. 복수 적합 후보는 상위 선택 |
| 공개 평가 | `evaluate` 기본 schema 2.0, `--format 1` 호환, `--format 3`은 schema 4.0의 의미 적합성·관측·진단 |
| 선택 기록 | 자동 단일 후보 5.0 / `select`의 상위 선택 6.0. 기존 2.0·`--profile`은 명시적 override |
| 가이드 | `guidelines.toml`에 공식 원문·벤더별 시작점·지원 effort·escalation 고정. runtime 웹 조회 없음 |
| 근거 | wiki 컴파일 index와 facet 조회; 모델 선택용 검색은 12 unit 표시 제한 없음; exact/proxy·freshness·비교 조건 구분 |
| 데이터 | AA pagination·Arena revision 고정 Parquet(pyarrow)·The Model Gap JSON·SWE/TB 수동 import |
| 저장 | SQLite sources/snapshots/observations, 소스별 last-good·원자 게시·최근 payload 3개·재현 snapshot 30일 |
| live | Projects 1.2.1 board 대화형 / Herdr worktree의 headless one-shot. 모델·effort args 변환, receipt·결과 계약 |
| 복구·제어 | collect·복수 run 대기·명시적 tell/stop·completed 대화 resume·feedback |
| 병렬 | group 1.0/2.0, 반복 selection·별도 worktree·동결 plan·재회수·member 전달 상태. task 8·group 16·max_parallel 1–4 |
| admission | 공유 활성 최대 4·경로 중첩 방지·소유권·채택 기록. 제출 전 확정 실패는 receipt settle과 슬롯 반환 |
| 가용성·발견 | PATH·agy models·선택적 CodeBurn quota, profiles discover(Claude 가이드/CLI effort·Codex cache·CodeBurn·agy models) |
| 환경 | 핵심 CLI는 Python 3.11+ stdlib. Arena refresh의 pyarrow·선택적 CodeBurn은 uv/mise로 준비 |

가중합 score·비용 차감·near-tie·default/fallback 자동 선택과 `--policy legacy`는 제거됐다. category quality/coverage는 evaluate 1·2 진단으로 남는다. 과거 vendor-guided selection 3.0·4.0은 현재 입력이 아니므로 새 판단이 필요하다. 제출된 기존 receipt는 새 정책과 무관하게 먼저 회수한다.

## 이번 검증 (2026-10-24)

```bash
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
```

164개 실행: **162개 통과, 2개 skip**. skip은 Windows 전용 파일 공유 검사와 pyarrow 미설치 환경의 실제 Parquet 디코드 검사다. Python 3.14에서 SQLite connection의 `ResourceWarning` 하나가 출력됐으며 실패는 없었다. fake source·CLI 및 실제 임시 Git worktree를 사용한다.

문서 18개의 로컬 링크 147개·JSON 예제 14개·코드 블록 쌍과 terminal-demo.svg XML을 검사했다. 임시 설정의 CLI smoke에서 기본 evaluate는 schema 2.0·exit 0, evaluate --format 3은 schema 4.0·decision_required·exit 17, route dry-run은 schema 1.0·decision_required·exit 17을 확인했다. `wiki compile --check`와 `git diff --check`도 통과했다.

현재 Projects 모델·PTY·board ticker와 정책 6의 실작업 품질·비용을 live로 확인한 것은 아니다. 별도 API refresh·유료 판단·Agent 제출은 이번 문서 갱신에서 실행하지 않았다.

## 과거 실측 기록과 해석 범위

| 기록 | 확인된 범위 |
|---|---|
| AA (2026-10-12) | Free API v4.3, 4페이지·697모델 수집. 당시 coding null과 effort별 alias 차이 확인 |
| Arena (2026-10-12) | revision `e16f9023…` 수집·재시도·TTL skip·장애 deadline·last-good 확인 |
| Arena Parquet 전환 (2026-10-21) | 기존 기록상 26요청·600초·wiki unit 47개 누락에서 14요청·14초·누락 0으로 개선 |
| 직접 Herdr 0.9.3 smoke (2026-10-12) | Claude/Codex 실행·blocked·결과 해시·같은 task/round 재회수·재전송 없음 확인. 현재 Projects 경로의 live 증거는 아님 |
| 이전 parallel smoke (2026-10-13) | 두 worktree·2라운드·공유 노트 확인. 당시 deliberate 모드는 제거됨 |
| 작업군 v1 | 20과제 × 2프로필, 고정 default 20/20·저비용 우선 19/20·이전 router 20/20 |

v1의 성공 1건당 API 환산 비용은 $0.234 / $0.070 / $0.217이었다. 토큰 실측·API 환산이며 구독 실지출이 아니다. 과제당 1회·쉬운 과제의 천장 효과가 있고, 이전 router는 18/20에서 default와 같은 선택이었다. 현재 정책의 품질·비용 개선 근거로 쓰지 않는다. 상세 결과: [v1](../eval/results/v1.md), [비용](../eval/results/v1-cost.md). 외부 CLI 증거는 [evidence/herdr-0.9.3](evidence/herdr-0.9.3/skill.md)에 있다.

과거 실환경의 권한 인자·설정 경로·당시 미완료 체크리스트는 현재 운영 설정으로 사용하지 않는다. 현재 interactive 권한은 Projects worker.access, headless 권한은 [reference](reference.md#비대화형-실행)를 따른다.

## 남은 일과 운영 한계

- 현재 Projects 대화형·headless의 실제 Agent smoke와 장애 복구 확인.
- 정책 6과 상위 선택 정책의 held-out 과제 품질·판단 비용·시간 평가. workflow effort 개선도 상위에서 실제 비교 필요.
- 계정별 CLI/model/effort·quota 확인과 비교 가능한 exact 관측 보강. discovery는 호출 성공을 보장하지 않음.
- OS timer 자동 설치 없음. 사용자 설정·키·보존 정책은 운영자가 관리.
- CLI fingerprint 버전은 `unknown`. decisions/feedback은 run 파일이며 라우터에 실행 토큰을 통합 기록하지 않음.
- 원격 실행·자동 agent pool·팀 전체 예산 예약/정산·DAG·투표·패턴 선택은 구현 범위 밖.

현재 사용법은 [README](../README.md), [정책](vendor-guided-routing.md), [상위 연동](orchestrator.md), [Projects](projects.md), [검증 기준](../06_VALIDATION_AND_OPEN_ITEMS.md)을 따른다.
