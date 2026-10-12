# 새 CLI 세션의 구현 순서와 운영

## 먼저 환경을 파악한다

실제 머신/저장소가 이 handoff 생성 환경과 같다고 가정하지 않는다.

1. 사용자 작업 디렉터리와 git status를 확인한다. 기존 AGENTS.md·패키지 설정·테스트·라우터 구현을 읽는다.
2. OS, Python, herdr/Agent CLI 설치와 버전을 확인한다. 사용자 변경을 덮어쓰지 않는다.
3. 네트워크/계정 권한, 실제 사용 가능한 프로필, 모델 인자, reasoning 설정을 확인한다.
4. 기존 구현이 있다면 함수·설정·캐시를 재사용하고 문서 계약과 차이를 기록한다.
5. 정보가 없으면 질문을 최소화하고 오프라인 선택/검증부터 진행한다. Agent 실행·API 인증에 필요한 정보는 추측하지 않는다.

검증용 시작 명령(herdr가 설치된 환경에 한함):

```bash
python3 --version
herdr --version
herdr status
herdr api schema --json
herdr agent start --help
herdr agent prompt --help
herdr agent wait --help
herdr agent read --help
```

herdr가 없으면 mock fixture가 live 검증을 대체했다는 보고를 하지 않는다. 버전 설치/키 발급/로그인이 필요한 경우 작업 환경의 권한 규칙을 따른다.

## 초기 코드 구성

필요한 모듈만 만든다. 아래는 권장 최소 구성이고 파일 개수가 acceptance 기준은 아니다.

| 구성 | 역할 |
| --- | --- |
| cli.py | argparse 명령, validation, stdout/stderr, exit mapping |
| routing.py | L0/L1, constraint filter, normalization/coverage/score, explain |
| data.py | SQLite, JSON snapshot, source fetch/refresh/import |
| herdr.py | subprocess argv, receipt, 실행/collect, 결과 검사 |
| 설정 | profiles.toml, categories.toml, aliases.toml |
| 테스트 | 선택/갱신/위임 경계의 fixture와 최소 통합 검증 |

Python 3.11+의 argparse, json, sqlite3, tomllib, pathlib, hashlib, urllib.request, subprocess, tempfile, os, fcntl을 먼저 쓴다. TOML은 읽기만 해도 된다. HTTP pagination을 몇 줄로 처리할 수 있는데 client SDK를 자동 추가하지 않는다.

단, 실제 Arena artifact가 parquet이면 필요에 따라 pyarrow 또는 datasets를 **refresh 경로에만** 추가할 수 있다. source 형식과 의존성 비용을 확인하고 선택 이유를 남긴다. route에 대형 데이터 라이브러리를 import하여 매 호출 cold start를 키우지 않는다.

벡터 검색/ML framework/gateway/server는 P3 전까지 추가하지 않는다. 처음부터 일반적인 Source/Executor plugin framework를 만들지 않는다. 실제 adapter가 늘어났을 때 간단한 함수 registry면 충분하다.

## P0 — 계약과 합성 라우팅

구현:
- 입력·설정 validator, enum, snapshot version 검사.
- synthetic fixture를 읽는 pure selection 함수.
- L0+L1+general 분류, hard filters.
- coverage/Q/S 및 deterministic sort, fallback, warnings.
- route --dry-run, explain.
- task/output JSON schema 문서와 fixtures.

검증: 06의 V01~V10. 계산은 합성 기대값과 일치하고 stdout은 JSON 한 객체다. shell metacharacter가 입력으로 들어와도 실행되지 않는다.

중요: dry-run은 한 번의 선택 재현에 필요한 hash·availability_unverified를 반환한다. offline 테스트를 위해 사용자 머신에 실제 Agent를 띄우지 않는다.

## P1 — 데이터와 운영 캐시

구현:
- SQLite versioned 초기화와 source provenance.
- refresh, 수동 import, status.
- AA pagination adapter, Arena subset schema adapter.
- lock, bounded HTTP, partial failure/304/hash no-op.
- 소스별 last-good, atomic routing snapshot.
- stale/max_stale/default 정책.

먼저 source fixture로 구현하고 실제 인증 호출은 계정이 준비된 뒤 한 번씩 확인한다. 없는 API endpoint를 추측해 scraping하지 않는다.

검증: V11~V18. route 테스트에서 source network 요청은 0회다. source 일부 실패 시 다른 정상 소스를 보존하며, 마지막 정상본의 출처/날짜도 보존된다.

## P2 — herdr 연결과 실행 회수

구현:
- installed schema 기반 응답 parser와 error mapping.
- local fresh workspace/Agent start.
- synchronous route, finite deadline.
- receipt/dispatch lock, task/round idempotency.
- run/nonce-bound result contract.
- collect, feedback.
- 기존 router 작업이 unresolved이면 신규 live dispatch 차단.

검증: V19~V29 fixture → 최소 실환경 smoke 순서. 실제 작업 디렉터리 변경이 없는 작은 파일 산출 작업부터 시작한다.

외부 데이터에 맞는 exact profile observation이 없더라도 제약 만족 default 위임 smoke는 할 수 있다. 이 경우 보고서에 benchmark-selected가 아니라 default-selected임을 분명히 표시한다.

P2가 통과하면 v1 기능 구현 완료다. 실제 성능 우수성은 별도의 작업군 비교가 필요하다.

## P3 — 측정 후 선택적 확장

다음 중 실제 문제가 확인된 것만 추가한다.

| 트리거 | 추가 후보 |
| --- | --- |
| L1 abstain/오분류가 실제 선택 실패를 유발 | multilingual embedding 또는 semantic-router 비교 |
| L2 경계 사례가 비용 대비 큰 영향 | Jev shadow mode 후 활성화 평가 |
| Agent 시작 시간이 전체 지연을 지배 | profile/cwd fingerprint와 lease가 있는 reuse |
| 동기 호출 제약으로 사용자 흐름이 막힘 | --no-wait + collect, receipt 원장 유지 |
| 다른 머신 작업이 실제 필요 | 원격 adapter와 결과 retrieval/path mapping |
| 실제 성공당 비용 데이터가 충분 | 비용/지연 모델 및 가중치 보정 |
| 내부 turn별 모델 교체가 필요 | Switchyard와 end-to-end benchmark 비교 |

학습형 라우터/가중치 자동 변경은 feedback가 있다는 이유만으로 바로 도입하지 않는다. 수동 검증된 라벨과 held-out 작업군을 확보한 뒤 정책 version을 올린다.

## 배포와 refresh 설정

하나의 주기 도구만 사용한다. Linux systemd user timer 또는 cron, macOS launchd 중 현장 것을 선택한다. 기본 주기는 하루 1회이고 소스 TTL이 지나지 않았으면 fetch를 생략한다.

설정에 실행 파일 절대 경로, config/cache 디렉터리, timezone, 로그 경로를 명시한다. API 키를 timer 파일·crontab 명령·로그에 직접 써 넣지 않는다. 실행 중복은 refresh lock으로 차단한다. 기계가 꺼져 있던 기간 이후 실행 정책은 timer 기능을 활용한다.

처음에는 수동 refresh → status → dry-run → 제한된 live smoke 순으로 검증한다. request path에서 빈 캐시를 채우느라 외부 API를 호출하지 않는다.

일별 요청 예산은 페이지 수 × 소스 수 × 최대 재시도 횟수로 계산하고 실제 rate-limit 잔여를 확인한다. AA를 항상 “하루 1 request”라고 설명하지 않는다.

## Deadline와 자원 관리

timeout_ms는 live delegation의 전체 예산이다. 프로세스 내 deadline 계산은 monotonic clock을 사용하고 receipt의 deadline_at은 UTC로 기록한다. collect는 새 요청의 대기 예산을 사용하되 이전 실행을 새로 전송하지 않는다.

herdr start에 줄 남은 예산이 installed 최소 startup timeout보다 작으면 시작하지 않고 timed_out으로 반환한다. local subprocess timeout은 herdr 호출 timeout에 작은 정리 여유만 더하고 무한 대기를 만들지 않는다.

fresh Agent 정책은 pane 수를 늘릴 수 있다. MVP에서 사용자가 정한 owned-live-agent 상한을 확인하고 도달 시 실행을 차단한다. 임의 사용자 pane를 닫지 않는다. smoke test가 만든 자원의 ID를 보고하고 정리 범위를 명확히 한다. 자동 pool 관리자까지 만들지 않는다.

## 새 세션마다 남길 체크포인트

구현 저장소에 docs/implementation-status.md를 유지한다.

- 완료 phase, 현재 git commit/변경 파일.
- 이번에 실행한 명령과 통과/실패/skip.
- actual source fixture와 herdr version/schema.
- 미해결 run_id, Agent/pane, receipt, 결과 경로.
- 설계 변경의 이유와 policy/schema version.
- 다음에 실행할 한 가지 구체 작업.
- 필요한 사용자 정보와 그 정보 없이 진행 가능한 작업.

secret, API key, raw private prompt를 상태 문서에 복사하지 않는다. 긴 대화 기록 대신 이 체크포인트와 버전 관리된 계약을 다음 Agent에게 전달한다.

