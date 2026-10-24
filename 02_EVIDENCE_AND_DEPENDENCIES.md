# 외부 근거·의존성·확인 한계

원 조사일: 2026-10-12 · 구현 대조 갱신: 2026-10-24. 아래 E1·U 설명은 원 조사 당시의 외부 근거 기록이다. 이번 갱신에서 외부 사이트·계정 응답을 다시 확인하지 않았다. 현재 구현과 이후 검증은 다음 표 및 [구현 상태](docs/implementation-status.md)를 따른다.

| 항목 | 현재 구현 / 확인 범위 |
|---|---|
| 핵심 CLI | Python 3.11+ 표준 라이브러리, 별도 설치 없이 모듈 실행 |
| Arena | revision 고정 Parquet·pyarrow 직접 디코드; 활성 wiki unit 수집 |
| AA / MG | AA pagination, The Model Gap 공개 JSON adapter 구현; 과거 실호출 기록 있음 |
| SWE / TB | 평가 조건이 있는 승인 수동 import; Verified / TB 4.0 고정 |
| 의미 판단 | Jev 또는 native bench-decider의 analysis·벤더별 guidance·benchmark 단계 구현 |
| 실행 | Projects 1.2.1 대화형 / Herdr headless; 현재 회귀 검증은 fake CLI·실제 임시 Git worktree |
| 보조 도구 | uv/mise 선택 설치, CodeBurn 가용성·quota·프로필 discovery 연동 |

공식 가이드의 모델별 원문과 버전은 `bench_router/guidelines.toml`에 고정하며 runtime 웹 조회는 하지 않는다. 정책 6과 기록 버전은 [vendor-guided](docs/vendor-guided-routing.md)에 있다. 2차 자료의 가격·속도·점수 차이를 구현 상수로 사용하지 않는다.

## 근거 수준

- E1: 공식 웹 문서에서 확인.
- E2: 실제 계정 응답·설치 바이너리에서 확인. 아래 원 조사에는 없었으며 이후 AA·Arena·MG와 직접 Herdr 실측 기록은 구현 상태·eval 문서를 참조한다.
- P: 본 handoff가 정한 정책. 외부 성능의 증거 아님.
- U: 추가 검증 필요.

## 재사용 후보

| 도구 | E1로 확인한 관련 기능 | 사용 판단 |
| --- | --- | --- |
| [RouteLLM](https://github.com/lm-sys/RouteLLM) | strong/weak 쌍, 선호도 기반 router, API 호환 서버, calibration/evaluation | 선호도 기반 라우팅 비교 후보. 본 설계의 수집·프로필·herdr 실행을 대체하는 turnkey 구성은 미확인 |
| [Switchyard](https://github.com/NVIDIA-NeMo/Switchyard) | model-pool 라우팅, task/execution/composite 전략, gateway/library 통합, pre-1.0 | README의 현재 범위는 초안보다 넓고 sub-agent 전략도 있음. CLI 프로필+외부 점수+herdr 계약 전체 대체는 별도 검증 |
| [semantic-router](https://github.com/aurelio-labs/semantic-router) | 예시 발화와 vector-space route matching | L2 필요성이 측정되면 로컬 소형 구현과 비용 비교. MVP 의존성으로 추가하지 않음 |
| [Jev 공식 문서](https://docs.typesafe.ai/introduction) | Choice/Score/Noul, 구조화 응답, probability/confidence | L3 선택 부품. typed output이 의미 판단의 정확성을 보장하지는 않음 |
| [herdr 공식 문서](https://herdr.dev/docs/) | terminal/Agent automation | 요구된 실행 백엔드. 현장 설치 버전과 대응 문서 고정 |

RouteLLM이 “하나의 Agent 내부에서만” 쓰인다고 제한하지 않는다. API 호출을 라우팅하는 부품을 상위 Agent 선택에도 응용할 수 있으나, 본 프로젝트의 데이터·프로필·위임 계약을 추가로 연결해야 한다.

## 데이터 소스별 E1 요약과 현장 할 일

### S-AA — Artificial Analysis

공식: [API docs](https://artificialanalysis.ai/data-api/docs)

E1: Free language endpoint는 /api/v2/language/models/free이며 x-api-key 인증을 쓴다. Free quota는 고정 24시간 창당 100회이고 quota scope는 키 하나보다 넓을 수 있다. 응답은 pagination과 data를 갖는다. headline Intelligence/Coding/Agentic 및 가격·median 성능을 제공하지만, Free에는 context window 등 Pro 필드가 빠진다. 문서에서 math 전용 지수는 확인되지 않았다. 공유/표시 시 출처를 남겨야 한다.

현장: 실제 페이지 수, null 처리, index version, Free에서 사용할 필드, rate-limit 헤더, 재배포 조건을 확인한다. 가격은 API 제공 방식의 대리 지표이며 CLI 구독 실비와 동일하다고 간주하지 않는다. 인증 예제·로그에 키를 남기지 않는다.

### S-ARENA — Arena dataset

공식: [dataset card](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset), [files](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/tree/main)

E1: CC BY 4.0, latest/full split, text/vision/document의 style-control subset과 webdev가 있다. 전통 subset의 rating과 Agent Arena subset의 IPS score는 다른 지표다. rating을 모두 “Elo”라 부르지 않는다.

현장: subset/category 목록·실제 파일 구조·컬럼을 확인하고 revision과 publish date를 고정한다. 공개 dataset이라도 다운로드 방식과 요청 수를 검증해야 한다. webdev를 일반 coding 성능으로 확대 해석하지 않는다. Agent Arena가 있다고 하네스가 동일하다고 가정하지 않는다.

### S-TB — Terminal-Bench

공식: [leaderboard](https://www.tbench.ai/)

E1: 현재 공식 화면은 Terminal-Bench 4.0이고 MODEL/AGENT/해결률 등의 열을 구분한다. 페이지의 정적 수집 결과에서는 실제 행이 추출되지 않았다.

U: 안정적인 결과 API나 파일 경로를 확인하지 못했다. 초기에는 출처·기준일·버전·평가 설정이 있는 사용자 승인 수동 스냅샷을 import한다. 2.0 결과가 필요하면 해당 버전의 공식 artifact를 찾고 독립 benchmark ID로 보관한다. 데이터를 없는데 있다고 채우지 않는다.

### S-SWE — SWE-bench

공식: [leaderboards](https://www.swebench.com/)

E1: Verified는 human-filtered 500개 subset이다. 현재 Bash Only 기본 뷰는 mini-SWE-agent 환경을 명시한다. % Resolved를 쓴다.

현장: 공식 결과 파일/저장소의 실제 경로·commit·agent 설정·evaluation split을 확인한다. mini-SWE-agent 점수를 codex-cli 또는 claude-code 직접 점수로 매칭하지 않는다. SWE-bench Pro와 Verified는 서로 다른 출처/버전으로 취급한다. 이 handoff는 Pro 수집 경로를 확정하지 않았다.

## herdr 공식 근거와 해석 경계

공식: [Agent automation](https://herdr.dev/docs/agent-automation/), [CLI reference](https://herdr.dev/docs/cli-reference/), [repository](https://github.com/herdrdev/herdr)

E1: layout 생성과 Agent start는 별개다. Agent는 이름 또는 현재 pane ID로 제어한다. start는 기존 shell pane에서 실행하며 준비를 기다린다. prompt/wait/read와 JSON 스키마 추출을 제공한다. 긴 결과는 파일로 작성시키는 방식을 문서가 제안한다.

E1: prompt --wait는 개별 turn을 추적하지 않는다. working 중 전송하면 기존 turn의 종료가 대기를 만족할 수 있다. idle/done은 입력 준비이고 성공 인증이 아니다. timeout/stalled만으로 미전송을 판단할 수 없다.

현재도 herdr가 작업 단위 exactly-once와 structured result를 전부 제공한다고 해석하지 않는다. wrapper가 receipt와 run-bound result 계약을 유지한다. 원 조사에서 미확정이던 plugin 사용은 이후 Projects 1.2.1 공개 CLI로 구현됐다. 원격 `--machine` 실행은 구현하지 않았다.

## 다음 Agent가 남길 의존성 증거

1. OS, Python 버전, git revision, herdr --version와 server 상태.
2. 설치 버전의 herdr api schema --json과 필요한 --help 출력.
3. 후보 CLI --version, 모델 인자, reasoning 설정, 인증 준비 상태.
4. secret 제거한 실제 source 응답 fixture와 응답 schema/revision/hash.
5. URL, retrieved_at, published/evaluated_at, license/attribution, 요청 수.
6. 각 사실을 E1 → E2로 올린 명령과 결과. 실패/미검증도 그대로 표시.

이 문서의 URL은 출발점이며 고정 API 보증이 아니다. 계정 권한 없이 API가 성공했다고 보고하지 않는다. 연결되지 않은 제3자 Jev 유사 도메인에 키를 보내지 않고 공식 typesafe.ai의 링크로 SDK/endpoint를 확인한다.

