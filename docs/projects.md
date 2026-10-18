# Projects 실행과 협업

현재 실행 경로는 `route` / `parallel` → herdr-projects 1.2.1 공개 CLI(board) → Herdr → Agent CLI다.
상위 agent가 작업 분해·프로필 선택·다음 라운드·결과 채택을 결정한다.
bench-router는 벤치마크 평가, 필수 제약, 실행 기록과 결과 검증을 유지한다.

## 준비

- live 실행은 Linux 또는 WSL2의 같은 사용자·Herdr 세션에서 한다.
- 확인한 계약은 Projects **1.2.1**이다(`herdr-projects version`). 다른 버전은 제출 전에 거절하고, 진행 중 실행은 기록한 버전이 바뀌면 `delivery_uncertain`으로 보류한다.
- 플러그인 설치와 사용자 설정은 운영자가 한다. Router는 설치·로그인·board 설정을 변경하지 않는다.
- task `cwd`는 커밋이 하나 이상 있는 git 저장소의 최상위여야 한다. board는 그 HEAD에서 agent 전용 worktree를 만든다(미커밋 변경은 빠지며 `dirty_base` 경고).
- Router는 `cwd`의 `info/exclude`에 `.bench-router/`를 등록해 결과 파일이 board 커밋에 섞이지 않게 한다.
- 0.2.34 시절의 receipt(`backend: "projects"`)는 자동 이관하지 않는다. 그 worker를 직접 점검하고 정리한다.

```bash
export PATH="$HOME/.local/bin:$PATH"
herdr --version                                   # herdr 0.9.3+ (https://herdr.dev)
herdr plugin install eliasstravik/herdr-projects  # Projects 플러그인 설치
herdr-projects version                            # herdr-projects 1.2.1 (...)
# 선택: export BENCH_ROUTER_PROJECTS=/absolute/path/to/herdr-projects
python3 -m bench_router.cli route --task task.json
```

## 프로필과 권한

1.2.1에는 이름 있는 프로필이 없다. Router 프로필의 `kind/args`를 task 설정으로 바꿔 넘긴다.

| Router args | board 설정 |
|---|---|
| (없음) | `--worker.agent KIND` (프로그램 기본 모델) |
| `--model M` / `-m M` | `--worker.agent KIND/M` (`herdr-projects models KIND`의 이름) |
| `--effort E`, codex `-c model_reasoning_effort="E"` | `--worker.effort E` |

그 밖의 args(`--add-dir` 등)는 표현할 수 없어 제출하지 않는다(`execution_failed`, `not_attempted`).
권한은 board의 `worker.access`(`full` | `ask`)를 그대로 따른다. 바꾸려면 `herdr-projects set worker.access ask [--repo NAME]`.
`ask`에서 claude는 편집마다, codex는 worktree 밖 쓰기마다 승인을 요청해 `blocked`가 된다.

한 receipt는 agent 한 번의 실행이다. 그래서 다음 설정을 task마다 고정한다:
`--workspace.from here --workspace.cleanup false --review.when never --review.rounds 0 --merge.by you --merge.pr false --attempts.by 1 --plan.approve none --no-research`.

## 실행·회수

Router는 입력과 결과 계약을 `input.txt`로 원자 저장하고 제출 의도를 기록한 뒤
`add br-RUN_ID --desc PROMPT --repo CWD --delegate ... --json`을 한 번 호출한다. 반환된 task ID(`repo/N`)가 출력의 `thread_id`다.
프롬프트는 argv 하나로 넘어가므로 결과 계약을 포함해 120 KiB까지다.

상태는 `list --all --json`의 `stage`/`state`로 판단하고, 제목 `br-RUN_ID`가 receipt와 다르면 보류한다.

| board | Router 상태 |
|---|---|
| stage `approval`/`done` | `details`의 worktree에서 결과 계약 검사 → `completed` / `result_invalid` |
| state `blocked` (질문·권한·한도 정지 등) | `blocked`, `diagnostic_tail`에 board의 한 줄 |
| stage `failed`/`nosummary`/`stopped`/`todo`, state `error` | `execution_failed` |
| stage `after`/`queued`/`starting` | `timed_out` (아직 시작 전) |
| 그 밖(`working`, `checking` 등) | `timed_out` (실행 중) |

- 결과 파일은 agent worktree의 `.bench-router/runs/RUN_ID/`에 쓰이고, 검사를 통과하면 `<cwd>/.bench-router/runs/RUN_ID/`로 복사된다. 출력의 `worktree`/`branch`가 agent 작업 위치다. board는 완료 시 작업을 그 브랜치에 커밋하고 `approval`에서 기다린다. 병합(`approve`)은 사람이 결정한다.
- 자원 반환: `completed`가 되면 task worktree 안의 herdr pane(agent)을 닫는다(`herdr pane list` → `pane close`, 마지막 pane이면 space도 사라진다). 그 안의 agent가 `working`/`blocked`이면 닫지 않고 다음 collect에서 다시 시도한다. 닫은 pane과 agent session은 receipt·출력의 `release`에 남는다. `completed`가 아닌 실행은 닫지 않는다.
- 이어서 작업: `resume --cwd CWD --run-id RUN`이 board의 `reopen ID`를 호출해 space를 다시 열고 같은 대화로 agent를 재시작한다(아무것도 보내지 않음). 재개한 session은 Router가 다시 닫지 않는다. 그다음 지시는 board에서 `herdr-projects tell ID "..."`로 한다.
- 응답 유실: 같은 task/round는 재제출하지 않는다. task ID를 잃으면 board에서 `br-RUN_ID` 제목으로 효과를 점검한 뒤 명시적으로 해결한다.
- 실행 중·질문 대기: `collect --cwd CWD --run-id RUN --wait-ms N`으로 같은 실행을 관찰한다. 질문·권한은 board(`herdr-projects details ID`)에서 기존 사용자 승인 절차로 처리한다.
- 후속 검토·수정: 상위 agent가 이전 결과와 검토 내용을 새 task round에 명시한다. 자동 retry·tell·재귀 위임은 하지 않는다.
- `completed`는 run ID·nonce·프로필 지문·결과 경로·크기·SHA-256 검사를 통과한 수신 상태다. 작업 성공은 `task_outcome`, 결과 채택은 별도 `coordination feedback`으로 기록한다.
- 실패나 전달 불확실 실행은 worker 정지와 부분 효과를 확인할 때까지 합산 4개 제한을 점유한다. `coordination release --key KEY --confirmed-stopped --note "..."`로 해제한다.
- board에서 직접 만든 task는 Router의 실행 제한에 포함되지 않는다.

## parallel

`parallel`은 member마다 `<cwd>/.bench-router/worktrees/GROUP/LABEL` router worktree를 만들어 receipt 공간과 board task의 `--repo`로 쓴다.
board가 그 HEAD에서 다시 agent worktree를 만들므로, member의 `worktree`/`branch`는 board가 보고한 위치로 바뀐다.
`deliberate` 2차 라운드 전에는 1차 board 브랜치를 router worktree에 `merge --ff-only`해 agent가 자기 1차 결과에서 이어가게 한다.
`shared`/`deliberate` scratchpad는 agent worktree 밖이므로 `worker.access ask`에서는 쓰기마다 승인이 필요하다.
worktree의 비교·병합·제거는 상위 agent가 담당한다. fanout, stale assessment 일괄 거부, 부분 실패 보존, 협의 라운드와 투표 계약은 유지한다.

## 검증

```bash
python -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination
```

Projects CLI는 1.2.1 소스(`src/cli/tasks.rs`의 `brief`/`details`, `crates/flow/src/state.rs`의 stage→state)를 따르는 fake로 대체하고, task마다 실제 `git worktree`를 만든다.
실제 모델·PTY·board ticker의 동작과 복구는 이 검사로 증명하지 않는다.
