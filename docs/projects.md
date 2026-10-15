# Projects 실행과 협업

현재 실행 경로는 `route` / `parallel` → herdr-projects 공개 CLI → Herdr → Agent CLI다.
상위 agent가 작업 분해·프로필 선택·다음 라운드·결과 채택을 결정한다.
bench-router는 벤치마크 평가, 필수 제약, 실행 기록과 결과 검증을 유지한다.

## 준비

- live 실행은 Linux 또는 WSL2의 같은 사용자·Herdr 세션에서 한다. Projects의 공식 플랫폼은 macOS/Linux이며 네이티브 Windows live 실행을 보장하지 않는다.
- 확인한 공개 계약은 Projects **0.2.34**다. 다른 버전은 제출 전에 거절하며, 진행 중 실행은 처음 기록한 전체 빌드 버전이 바뀌어도 보류한다.
- 플러그인 설치와 사용자 설정은 운영자가 한다. Router는 설치·로그인·권한 설정을 변경하지 않는다.
- 기존 작업을 먼저 회수하고 실제 worker와 부분 변경을 확인한다. 기존 조정 기록이나 receipt를 지워 backend를 전환하지 않는다.

```bash
herdr plugin install eliasstravik/herdr-projects --ref v0.2.34
herdr-projects configure
herdr-projects new bench --repo /absolute/repo
herdr-projects open bench --session NAME
export BENCH_ROUTER_PROJECT_DIR="$HOME/.herdr-projects/bench"
# 선택: export BENCH_ROUTER_PROJECTS=/absolute/path/to/herdr-projects
python -m bench_router.cli --herdr-session NAME route --task task.json
```

명령은 설치 예시다. 설치 버전을 `herdr-projects --version`으로 확인한다.
project 디렉터리에 `PROJECT.md`와 `.state/coordinator.json`이 있어야 한다.
후자는 플러그인이 기록한 socket/session을 사용한다.
`HOME/.config/herdr-projects/config.toml`이 Projects의 고정 사용자 설정 경로다(XDG_CONFIG_HOME으로 옮겨지지 않는다).

## 프로필과 권한

Projects 프로필 이름을 Router profile ID와 맞춘다.
`herdr-projects profile resolve ID`의 `name/agent/args`가 Router의 `id/kind/args`와 정확히 같아야 실행한다.
예를 들어 Projects에 `agent="codex", model="MODEL", effort="high"`를 설정하면 Router args는
`["--model", "MODEL", "-c", "model_reasoning_effort=\"high\""]`와 대응한다.
동일한 의미의 `-m`과 `--model`도 서로 다른 배열이므로 설정을 일치시킨다. 로컬 경로 인자는 절대 경로로 설정한다.

`yolo=false`, `thread_agent_args=[]`를 사용한다. 실행 인자는 이름 있는 프로필에서만 관리한다.
설정 파일 SHA-256, 프로젝트 경로와 session socket을 receipt에 고정하고 변경 시 보류한다.
이는 로컬 설정의 변경 감지이며 실제 프로세스 argv의 원격 증명은 아니다. 실행 중 설정을 편집하거나 플러그인을 업데이트하지 않는다.

`shared` / `deliberate`는 두 설정의 프로필 args에 `--add-dir /absolute/repo/.bench-router/groups`를 미리 포함해야 한다.
Router가 요청별 argv를 추가하지 않는다. 필요한 접근이 없으면 어떤 member도 제출하기 전에 거절한다.
격리가 필요한 실행에는 공유 경로 접근을 부여하지 않은 별도 프로필을 사용한다.

## 실행·회수

Router는 입력과 결과 계약을 `input.txt`로 원자 저장하고 제출 의도를 기록한 뒤
`thread start PROJECT --repo CWD --kind checkout --profile ID --task-file FILE`을 한 번 호출한다.
프로필·thread ID·cwd·kind·pane과 실제 상태를 검사하며, 초기 brief 전달이 확인되기 전에는 결과 파일이 있어도 완료 처리하지 않는다.
상태 수집은 `thread show ... --json`의 live `note`를 사용하며 오래된 `last_state`나 `Ready for review`만으로 완료를 선언하지 않는다.

- 응답 유실: 같은 task/round는 재제출하지 않는다. thread ID를 잃으면 Projects에서 `br-RUN_ID` 제목으로 효과를 점검한 뒤 명시적으로 해결한다.
- 실행 중·질문 대기: `collect --cwd CWD --run-id RUN --wait-ms N`으로 같은 실행을 관찰한다. 질문·권한 화면은 반환된 project/thread ID로 Projects `thread read` / `thread keys`에서 확인한다. 인증·권한 판단은 기존 사용자 승인 절차를 따른다.
- 후속 검토·수정: 상위 agent가 이전 결과와 검토 내용을 새 task round에 명시한다. 자동 재시작·재제출·재귀 위임은 하지 않는다.
- `completed`는 run ID·nonce·프로필 지문·결과 경로·크기·SHA-256 검사를 통과한 수신 상태다. 작업 성공은 `task_outcome`, 결과 채택은 별도 `coordination feedback`으로 기록한다.
- 실패나 전달 불확실 실행은 worker 정지와 부분 효과를 확인할 때까지 합산 4개 제한을 점유한다. `coordination release --key KEY --confirmed-stopped --note "..."`로 해제한다.
- Projects에서 직접 생성한 작업은 Router의 실행 제한에 포함되지 않는다. 조정 디렉터리는 모든 Router 호출에서 동일하게 유지한다.

`parallel`은 기존 HEAD 기반 worktree 생성 6줄을 유지한다.
Projects가 thread를 만들면 ticker가 즉시 실행할 수 있으므로, 먼저 확정된 cwd에서 receipt·입력 계약을 기록한 뒤 checkout thread로 실행한다.
worktree의 비교·병합·제거는 상위 agent가 담당한다. plugin의 `thread resolve`가 checkout worktree를 관리한다고 가정하지 않는다.
fanout, stale assessment 일괄 거부, 부분 실패 보존, 협의 라운드와 투표 계약도 유지한다.

## 검토와 후속 실행

검토도 일반 task를 만들고 `route --profile ID` 또는 `route --selection FILE`로 실행한다.
기존 receipt는 자동으로 Projects에 이관하지 않는다.

## 검증

```bash
python -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination
```

2026-10-15 Windows Python 3.15.0에서 최종 전체 70개 테스트가 통과했다. 검증 중 변경하지 않은 P1의 임시 폴더 정리에서 간헐적인 WinError 145가 한 번 발생했으며 재실행은 통과했다. 실행 모듈의 순감소는 264줄이다(테스트·문서·설정 예제 제외). 결과 계약 검사를 무력화하거나 합산 제한을 8개로 바꾼 두 회귀 실험도 테스트가 각각 실패하여 감지했다. CLI 도움말의 실행 명령을 확인했다.

2026-10-15 WSL2 Ubuntu 26.04.1 / Python 3.14.4에서도 전체 70개 중 69개 통과, Windows 전용 파일 공유 검사 1개 건너뜀을 확인했다. 운영 세션 환경 변수가 모의 CLI 테스트에 섞이지 않도록 공통 fixture에서 `BENCH_ROUTER_HERDR_SESSION=brtest`를 고정한다.

Projects CLI는 공개 소스의 JSON 형태를 따르는 fake로 대체한다. 실제 모델·PTY·플러그인 ticker의 동작과 복구는 이 검사로 증명하지 않는다.
Windows의 symlink 거절 검사는 권한이 필요한 링크 생성 대신 `Path.is_symlink` 경계를 모의 처리하고, Linux에서는 실제 링크를 만든다.

공개 근거: [CLI](https://github.com/eliasstravik/herdr-projects/blob/main/src/cli.rs),
[thread 생성·관측](https://github.com/eliasstravik/herdr-projects/blob/main/src/threads.rs),
[입력 전달](https://github.com/eliasstravik/herdr-projects/blob/main/src/brief.rs),
[프로필](https://github.com/eliasstravik/herdr-projects/blob/main/src/profiles.rs).
