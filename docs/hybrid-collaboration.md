# Herdr CLI와 A2A의 선택적 협업

상위 agent가 작업 분해·실행 방식 선택·결과 채택을 담당한다. 정확한 cwd와 argv, worktree 격리, 결과 파일 계약이 필요한 실행에는 기존 `route`/`parallel`을 사용한다. 전달한 자료만으로 수행 가능한 역할별 검토와 질의응답에는 `review`/`a2a` Adapter를 사용한다. Adapter는 원본 herdr-a2a의 공개 CLI를 호출하며 공통 조정 기록으로 기존 경로와의 중복·작업 소유권·합산 실행 수를 검사한다. 단계 순서를 자동 진행하는 워크플로 실행기는 추가하지 않는다.

검증 기준은 수정하지 않은 herdr-a2a `b94d60f1c255d63e5c69d8fd3f8f288b81922057`이다. [검증 근거](evidence/herdr-a2a-collaboration.md)와 [패턴·기록 예제](../examples/hybrid-collaboration.json)를 함께 읽는다. 예제 JSON은 설명과 검증용 fixture이며 `--task` 또는 `--group`에 넣는 입력이 아니다.

## 실행 방식 선택

| 조건 / 패턴 | 실행 방식 | 상위 agent의 책임 |
| --- | --- | --- |
| 코드 수정, 도구 실행, 정확한 cwd/argv, 새 worker 필요 | 기존 `route` | 실행 환경 선택, 결과 계약 확인 후 실제 변경·테스트 검증 |
| 여러 독립 구현안 비교 | 기존 `parallel` | worktree 격리, 변경 비교·병합. worktree는 HEAD에서 시작하므로 미커밋 변경 포함 여부 확인 |
| 구현 → 검토 → 수정 | `route` → A2A 검토 → 새 `route` round | 실제 diff·테스트·판정 기준 전달, 채택한 지적만 수정 요청에 반영 |
| 여러 전문가 검토 | A2A 독립 요청 → 상위 agent 종합 | 동일 버전 입력을 역할별 전달, 부분 실패 보존, 투표 대신 근거로 판단 |
| 실행 중 추가 질문 | A2A 같은 task에 `continue` | input-required 질문에 답변. 인증·권한 요구는 사용자에게 연결 |
| 완료 후 후속 검토·토론 | A2A 새 `delegate` | 이전 결과·채택 결론·미해결 질문을 본문에 다시 포함 |

A2A의 contextId는 같은 물리 worker나 이전 대화 기억을 보장하지 않는다. referenceTaskIds도 이전 결과를 자동으로 입력에 넣지 않는다. worker 재사용 여부는 정확성의 전제로 삼지 않는다. public A2A에는 요청별 정확한 cwd·임의 argv·fresh worker 지정이 없으므로, 클라이언트를 특정 worktree에서 실행했다는 이유만으로 그 worktree를 검사했다고 판단하지 않는다.

공통 조정 계층은 동시 활성 작업을 최대 4개로 제한한다. input-required/auth-required와 전달 불확실 작업도 슬롯을 점유한다. A2A failed/canceled/rejected는 작업 효과와 실제 worker 정지를 확인할 때까지 슬롯을 유지한다. 같은 경로 또는 부모·자식 경로에 native 작업과 다른 작업이 겹치면 차단하며, A2A 검토끼리는 같은 스냅샷 내용을 병렬로 검토할 수 있다. 경합·용량 부족은 conflict로 반환하므로 새 작업 ID를 생성하지 말고 기존 작업을 회수한 뒤 같은 요청을 다시 호출한다. `parallel.max_parallel`은 4 이하로 두고 다른 활성 작업도 고려한다. 한도는 실행 중인 작업 수이며, 유휴 worker의 메모리까지 제한하는 기능은 아니다. 검토 후 수정 최대 2회는 상위 agent가 관리한다.

모든 상위 agent는 같은 OS 사용자와 같은 조정 디렉터리를 사용한다. 기본값은 `$XDG_STATE_HOME/bench-router/coordination`(없으면 `~/.local/state/bench-router/coordination`), 필요하면 절대 경로의 `BENCH_ROUTER_COORDINATION_DIR`로 통일한다. 운영 중 디렉터리를 바꾸거나 삭제하면 중복 판별과 합산 한도를 우회하게 된다. Windows와 WSL이 같은 물리 디렉터리를 동시에 사용하지 않는다. 직접 `herdr`/`herdr-a2a`를 호출하거나 다른 프로세스가 자체적으로 실행한 작업은 이 제한에 포함되지 않는다. 도입 전에 기존 실행을 회수·정리한다. `collect`는 기존 native receipt를 조정 기록에 등록하고, `review`도 같은 cwd의 미해결 native receipt를 등록한다. 다른 디렉터리의 기존 실행을 자동 검색하지는 않는다.

하위 agent에게 재위임을 요청하지 않는다. 검토 프롬프트의 도구 사용·파일 쓰기 금지는 권한 통제가 아니므로, 실제 제한이 필요하면 운영자가 reviewer의 도구 권한을 제한해야 한다. 이 조건을 확보하지 못한 작업은 native 격리 경로로 보낸다.

## Adapter 설정과 명령

1. 기존 `profiles.toml`에 검토 프로필을 설정하고 `evaluate --task REVIEW_TASK`의 후보에서 `profile_fingerprint`를 확인한다. prompt에는 검토할 실제 내용과 완료 기준을 포함한다. `context_files`와 `required_capabilities`를 요구하는 작업은 Adapter가 거절한다. task의 cwd는 조정용 작업 범위이며 A2A worker의 실제 cwd 지정이 아니다.
2. [설정 예제](../examples/a2a-bindings.example.json)를 사용자 설정 디렉터리의 `a2a-bindings.json`으로 복사하고 값을 채운다. `agent`는 `<profile ID>-<fingerprint 앞 12자리>`, binding의 model은 해당 profile의 model_id와 같아야 한다. Codex stock runtime은 요청별 `--model`을 지원하지 않으므로, 선택 모델은 플러그인 역할의 `args`에 `-m MODEL`로 고정하고 `model` 필드는 비워 둔다. 플러그인에 이 이름의 headless 검토 역할을 구성한다. 공개 discover의 이름·runtime·available과 task 응답의 target·runtime·instance를 검사한다.
3. 운영자가 gateway가 실제로 읽는 설정과 runtime 인자·권한을 확인하고 그 파일의 절대 경로·SHA-256을 binding에 기록한다. 예를 들어 PowerShell `Get-FileHash -Algorithm SHA256 CONFIG_FILE`로 구한 해시를 소문자로 기록한다. 설정 파일의 내용이 바뀌면 제출을 거절한다. 프로필 변경은 새 fingerprint와 역할 이름을 사용하고 이전 worker를 회수·정리한다. 전체 설정 파일의 다른 항목만 바뀌어도 확인 후 해시를 갱신한다.
4. 이 파일 해시는 **운영자가 확인한 로컬 설정의 변경 감지**다. 공개 API가 실제 실행 argv·reasoning 설정을 증명하지 않으므로 gateway가 해당 파일을 로드했다는 원격 증명은 아니다. plugin 내부 재시도·worker 재사용은 Adapter가 변경하지 않는다. gateway URL은 자격 증명 없는 명시적 loopback HTTP origin만 허용한다.

```text
python -m bench_router.cli review --task REVIEW_TASK --profile REVIEW_PROFILE
python -m bench_router.cli a2a get --key COORDINATION_KEY
python -m bench_router.cli a2a continue --key COORDINATION_KEY --answer-file ANSWER_UTF8_FILE
python -m bench_router.cli a2a cancel --key COORDINATION_KEY
python -m bench_router.cli a2a close --key COORDINATION_KEY
python -m bench_router.cli coordination status
python -m bench_router.cli coordination feedback --key COORDINATION_KEY --input-hash INPUT_HASH --decision accepted --note "independent verification evidence"
python -m bench_router.cli coordination release --key COORDINATION_KEY --confirmed-stopped --note "worker stopped and partial effects inspected"
```

global 옵션 `--config-dir`, `--cache-dir`, `--herdr-session`은 subcommand 앞에 둔다. A2A는 binding의 gateway로 고정되며 `--herdr-session`으로 바꾸지 않는다. binding의 선택 필드 `command`는 CLI 실행용 shell-free argv 접두부다. 기본은 `herdr-a2a`; Windows에서 npm의 POSIX shim이 맞지 않으면 `node.exe`와 빌드된 `dist/bridge/cli.js` 절대 경로를 넣는다. 이 경로는 설치된 플러그인 root를 유지해야 한다. 환경 변수 `BENCH_ROUTER_A2A`는 command가 없을 때만 사용한다. 응답의 coordination_key와 input_hash를 보존한다. backend_status는 원본 상태 이름, status는 기존 종료 코드에 맞춘 waiting/blocked/completed/execution_failed/delivery_uncertain 등이다. 큰 원본 응답은 response_path에 저장해 중복 문맥 전달을 줄인다. 실제 slot 상태는 active로 확인한다.

작업 키는 canonical cwd + task_id + round다. 같은 키는 backend·요청 내용·설정에 고정된다. 같은 내용이라도 다른 작업 ID나 다른 cwd는 별도 작업이므로 상위 agent가 단계 ID를 안정적으로 유지해야 한다. `review` 재호출은 원래 작업을 조회하며 초기 ID가 유실된 경우 재제출하지 않는다. 설정이 변경됐어도 기존 작업은 `a2a get --key`로 회수한다. native `collect`는 기록된 Herdr 세션을 사용하고 다른 세션을 명시하면 거절한다.

`feedback`은 기록된 요청의 input_hash가 일치하고 completed인 경우에만 accepted를 허용한다. 현재 저장소가 검토 대상 이후 바뀌었는지는 상위 agent가 별도로 확인해야 한다. `release`는 실제 worker 정지와 효과 확인 뒤의 수동 해제다. 같은 키의 backend 고정은 해제하지 않으며, 기존 native receipt의 미해결 상태도 우회하지 않는다. 이어가기 응답이 유실되면 중복 답변을 차단하고 답변 파일과 불확실 상태를 보존한다.

Adapter의 개별 CLI 호출 제한은 30초이며, A2A 작업 자체의 실행 시간은 plugin 설정을 따른다. task.timeout_ms를 plugin의 요청별 실행 제한으로 전달할 수 없다. 별도 실행 시간·부작용 보장이 필요한 작업은 native 경로를 사용한다. auth-required는 자동으로 답하지 않는다.

## 준비와 전달

1. 기존 `evaluate`로 후보의 사실·제약을 확인하고, 상위 agent가 역할에 맞는 프로필을 선택한다. A2A의 논리 agent 이름을 bench-router 프로필 ID와 동일하다고 가정하지 않는다. 운영자가 설정한 A2A agent의 runtime·모델·실행 설정을 확인하고 근거를 기록한다. 확인할 수 없으면 설정을 unknown으로 기록하고 동등한 성능 비교에서 제외한다. 모델 지정만으로 나머지 argv·reasoning 설정까지 같아지지는 않는다.
2. 기존 CLI는 README의 task/selection 계약을 그대로 사용한다. A2A는 준비된 gateway에 `discover --json`으로 역할을 확인한다. gateway URL과 Herdr 세션을 기록하고 사용자 환경의 올바른 세션인지 확인한다. 선택한 gateway URL은 모든 후속 명령에 동일하게 지정한다. 비밀 값이 포함된 URL은 기록하지 않는다.
3. 검토 입력에는 목적, 완료 기준, 변경 대상의 정확한 내용(diff와 필요한 주변 코드), 테스트 명령·결과, 이전 단계의 채택 결론을 포함한다. 대상 내용의 정확한 UTF-8 바이트에 SHA-256을 계산한다. 커밋 ID만으로 미커밋 변경을 식별하지 않는다. 로컬 파일 경로만 전달해서 읽었다고 가정하지 않는다.
4. 명령 길이/모델 context 한도를 넘는 자료는 상위 agent가 검토 단위로 나눈다. 각 단위의 범위·해시·공통 제약을 보존하고 검토에서 빠진 범위를 명시한다. 자료가 부족하면 A2A 검토자가 근거 없는 승인을 내리지 말고 질문하도록 요청한다. 저장소 탐색이 필요하면 해당 작업을 환경이 확정된 기존 CLI 단계로 계획한다.
5. 최초 A2A 제출에는 `--wait`를 붙이지 않아 task ID를 먼저 받고 즉시 저장한다. 명령 문자열을 조립하지 말고 argv 배열로 호출한다. JSON 직렬화된 본문을 한 인자로 넘기며 stdout 원본과 stderr를 별도로 보존한다. stdin/파일 입력 플래그를 임의로 가정하지 않는다.

Adapter가 내부에서 사용하는 원본 공개 명령은 다음과 같다. 이 명령을 직접 실행하면 공통 조정을 거치지 않으므로, 일반 협업에서는 위의 Adapter 명령을 사용한다. MESSAGE는 위 자료를 포함한 단일 문자열이고, AGENT/MODEL/URL/ID는 확인한 실제 값이다.

```text
herdr-a2a discover --base-url URL --json
herdr-a2a delegate AGENT MESSAGE --base-url URL --json
herdr-a2a get ID --base-url URL --json
herdr-a2a continue ID ANSWER --base-url URL --json
herdr-a2a cancel ID --base-url URL --json
herdr-a2a close ID --base-url URL --json
```

`continue --wait --json`은 이미 ID를 보존한 task의 답변 후 대기에 사용할 수 있다. 원본 CLI의 `--wait`는 SSE를 내부에서 소비해 마지막 결과를 출력하며, 호출자에게 이벤트마다 task ID를 출력하는 명령이 아니다. 최초 비동기 제출 후에는 작업 시간이 지난 뒤 `get`으로 관측한다. 짧은 고정 간격의 무한 조회 루프를 추가하지 않고, 상위 agent의 작업 대기/재개 시점에 조회한다. 대기가 끝나도 task가 진행 중이면 기록을 보존하고 pending 상태를 보고한다.

## 패턴별 진행

**구현 → 검토 → 수정:** 기존 CLI 실행 결과를 수집하고 상위 agent가 변경과 테스트를 확인한다. 실제 변경 대상과 근거를 A2A에 전달한다. 검토 완료 후 지적의 재현 가능성·관련성·심각도를 판정한다. 채택한 지적과 현재 버전의 산출물을 포함해 기존 CLI의 새 round로 수정을 위임한다. 이전 실행의 효과를 확인한 후에만 round를 올린다. 매 수정 후 다시 테스트한다. 최대 2회 수정 뒤에도 미해결이면 현재 결과와 미해결 사항을 보고한다.

**병렬 전문가 검토:** 동일한 입력 해시를 고정하고 정확성·보안 등 다른 질문을 독립 요청한다. 성공 결과는 다른 검토가 실패해도 보존한다. 누락된 검토 범위와 실패를 기록하며 전원 승인으로 표현하지 않는다. 상위 agent가 상충하는 의견을 소스와 재현 테스트로 해결한다. 요구사항·제품 판단이 필요한 쟁점은 사용자에게 묻는다.

**질의응답·후속 토론:** input-required는 질문 원문과 필요한 자료를 확인해 같은 task에 답한다. auth-required나 권한 요청은 상위 agent가 임의 승인하지 않는다. 완료된 task는 이어갈 수 없으므로 필요한 이전 결과를 본문에 넣어 새 task를 만든다. worker가 사라진 경우의 재작업도 효과와 입력을 확인한 뒤 새 단계로 명시한다. contextId 유지나 같은 worker 재선택을 성공 조건으로 삼지 않는다.

## 기록·채택·복구

Adapter는 공통 조정 디렉터리에 작업 소유권·입력 해시·실행 위치·상태·채택 판단을 기록한다. A2A 입력·평가 근거·응답·답변은 작업 키의 하위 디렉터리에 저장한다. native는 기존 receipt를 참조한다. 최초 제출 전 의도를 fsync하고, 조정 기록은 짧은 프로세스 간 잠금과 원자 교체로 갱신한다. 조정 잠금을 잡은 채 모델 실행을 기다리지 않는다. 실행 도중 중단되어도 자동 만료·재전송하지 않는다. 상위 agent는 선택적으로 `<cwd>/.bench-router/collaborations/<협업ID>/`에 이 키들과 단계 의존 관계를 연결한다. 예제 JSON의 record는 이러한 상위 기록의 설명용 예시다. 자격 증명·토큰은 기록하지 않는다.

필수 기록은 협업 ID·단계·의존 단계, 입력 해시, 실행 방식·프로필·모델과 설정 확인 근거, 실행 ID와 위치, 제출 시각, 마지막 관측 상태, 원본 응답 위치, 상위 agent의 채택/보류/기각 및 근거다. 제출과 실행 상태는 backend 원본 값을 보존하고, 결과 채택은 별도 판단으로 남긴다.

| 상황 | 처리 |
| --- | --- |
| 기존 CLI timed_out / delivery_uncertain | 같은 run_id/cwd로 `collect`. 새 ID로 재전송하지 않음 |
| A2A ID를 확보한 뒤 응답·연결 유실 | 같은 gateway/task ID로 `get`. 계속 진행 중일 수 있음 |
| 제출 응답 유실로 ID를 모름 | delivery_uncertain으로 기록, gateway·worker 상태와 효과를 조사. 자동 재제출·backend 전환 금지 |
| RESULT_UNAVAILABLE / 결과 추출 실패 | 이미 실행됐을 수 있음. 파일·효과를 조사하고 자동 재실행 금지 |
| completed / manifest 유효 | 전달·결과 형식의 근거일 뿐. 상위 agent의 실제 검증 전까지 채택 보류 |
| 검토 대상 해시 변경 | 기존 검토를 새 버전의 승인으로 사용하지 않음. 변경 범위를 재검토 |
| 취소 | 이미 발생한 변경은 남을 수 있음. 상태와 효과를 확인하고 필요 시 별도 복구 |
| close | 종료된 task만 정리. 같은 worker가 다른 작업을 수행 중이면 거부될 수 있음 |

다른 backend로의 선택은 제출 전에 한다. 제출 이후 전환은 기존 작업의 상태와 효과를 확인하고 별도 단계로 결정한다. 도구가 제공하는 재시도 정책을 exactly-once 보장으로 표현하지 않는다.

## 검증과 도입 판정

```text
node eval/herdr_a2a_collaboration.mjs .bench-router/herdr-a2a-patch-check
python -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination
```

프로브는 원본 gateway·SDK·HTTP/SSE·선택 정책을 사용하되 worker와 relay 완료를 모의 처리한다. 명시적 입력 전달, worker 교체, 병렬 부분 실패, input-required 이어가기, 완료 task 이어가기 거부를 검사한다. fixture의 오래된 검토 보류·중복 제출 금지·완료와 채택 구분은 **상위 agent 규약 예제의 일관성 검사**이며 자동 복구 실행기를 검증한 것이 아니다. 실제 CLI 구현·모델 품질·PTY·SQLite 복구·실제 전송 유실은 별도 검증이 필요하다.

`test_coordination`은 새 Python Adapter와 native dispatch를 fake CLI로 실행한다. backend 간 중복, 동시 admission 4개 한도, 쓰기 범위 충돌, 설정 변경·응답 identity 검사, 초기/이어가기 응답 유실, session 고정, 입력 해시와 채택 판단을 검증한다. 이 테스트는 plugin 내부 재시도 중복이나 실제 모델 품질·비용을 검증하지 않는다.

실제 비교는 같은 과제·모델·입력·판정 기준에서 CLI 조합/A2A 조합/혼합 조합을 반복 실행한다. 신규 worker와 재사용 worker를 나누고 전체 시간, 모델 사용량(없으면 unknown), 정확성, 중복 실행, 실패 후 회수를 기록한다. 실행 환경을 맞출 수 없는 실험은 동등 비교에서 제외한다. 품질·격리·복구가 유지되면서 시간·비용 또는 협업 편의의 개선이 관측된 패턴만 기본 사용으로 승격한다. 현재는 opt-in이며 실제 성능 이점은 입증되지 않았다.
