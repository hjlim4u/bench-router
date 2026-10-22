# CLI·JSON·herdr 실행 계약 v1

현재 구현의 실행 연결은 [Projects 계약](docs/projects.md)을 따른다. 아래의 직접 Herdr 명령 절차는 원래 설계 기록이며, 결과 파일·입력·선택 계약은 유지한다.

## CLI

| 명령 | 동작 | MVP |
| --- | --- | --- |
| route --task FILE --dry-run | validate → classify → filter → select; 실행 side effect 없음 | 필수 |
| route --task FILE | 선택 후 fresh Agent에 전달하고 유한 timeout으로 기다림 | 필수 |
| refresh [--source ID] [--force] | 소스 갱신 및 snapshot 게시 | 필수 |
| refresh --source ID --import FILE | 승인된 수동 source observation import | TB/SWE 필요 시 |
| status | 소스별 age·failures·unmatched·설정 상태 | 필수 |
| explain --task FILE [--context FILE] | dry-run의 전체 점수/제외 근거 + 제약 결과·지표를 사람이 읽는 형태로 출력 | 필수 |
| evaluate --task FILE [--context FILE] [--format 1\|2] | 전 프로필의 facts·제약 결과·benchmark 평가와 assessment_digest. 선택 없음 (2.0, docs/routing-contracts.md §1.3) | 다중 기준 |
| route --task FILE --selection FILE [--dry-run] | Orchestrator 선택 기록(profile, assessment_digest, policy, reason)으로 실행. digest 불일치면 stale_assessment | 다중 기준 |
| route --task FILE --profile ID [--dry-run] | 선택 기록 없이 지정 프로필 실행(selection_unrecorded 경고) | 호환 |
| wiki compile [--check] | 검토된 benchmark wiki 페이지를 index.json으로 컴파일·게시(--check는 검증만) | 선택 |
| wiki facets | Orchestrator가 task.facets에 고를 수 있는 전체 어휘(active unit이 있는 값만). facets에 설명, detection에 판정 규칙; 자동 판정 값도 직접 지정 가능 | 선택 |
| evidence --task FILE [--format json\|table] | 작업 facet에 맞는 benchmark 결과를 프로필별로 출력; 작업 유형 일치 우선, 합산·모델 순위 없음, 네트워크·쓰기 없음 | 선택 |
| parallel --group FILE [--dry-run] | task × fanout을 각자 worktree에서 병렬 위임. group 2.0은 task별 context·selections | 선택 |
| collect --run-id ID --cwd ABS_PATH | 기존 receipt의 Agent/결과를 읽고 대기·회수; prompt 재전송 없음 | 필수 |
| feedback --run-id ID --cwd ABS_PATH --outcome success\|partial\|fail | Orchestrator 평가 기록 | 필수 |
| coordination status\|release\|feedback | 합산 활성 작업·소유권 기록 조회, 정지 확인 후 슬롯 해제, 별도 결과 채택 기록 | 선택 |
| route --no-wait, --machine, plugin 액션 | 비동기/원격/플러그인 | 보류 |

route/collect/status/refresh는 stdout에 JSON 한 객체만 내보낸다. 로그·진행 정보는 stderr로 보내며 secret은 제거한다. explain의 사람용 출력만 예외다. --dry-run은 네트워크, herdr 호출, 파일/DB mutation 없이 동작하고 온라인 가용성 미확인을 명시한다.

`coordination`도 stdout JSON 한 객체를 출력한다. `route`/`collect`에는 coordination_key, project, thread_id가 포함된다. 완료와 채택은 구분한다. admission 거절은 conflict(14)이며 제출하지 않는다. Projects의 보고서는 실행별 결과 계약을 대체하지 않는다.

종료 코드는 **라우터의 코드**이며 herdr의 exit code를 그대로 노출하지 않는다.

| 코드 | 의미 |
| --- | --- |
| 0 | selected(dry-run) 또는 계약 검사를 통과한 completed |
| 2 | JSON/설정/인자 validation 오류, 미지원 기능 |
| 10 | blocked, 추가 승인/질문 필요 |
| 11 | timed_out 또는 delivery_uncertain; 실행 중일 수 있음 |
| 12 | execution_failed 또는 result_invalid |
| 13 | no_eligible_profile; 위임 없음 |
| 14 | task/round hash 충돌, receipt lock 사용 중, 또는 stale_assessment(평가 후 정적 입력 변경) |
| 15 | 내부 저장소/출력 I/O 오류 |
| 16 | refresh 대상 소스 일부/전체 실패; last-good 유지 여부를 JSON에 명시 |

refresh/status가 정상 종료하면 0이다. completed는 산출물 수신의 성공을 뜻한다. 작업 내용의 성공/부분 성공/실패는 task_outcome과 후속 feedback으로 구분한다.

## 입력 계약

필수: schema_version="1.0", task_id, round, summary, prompt, cwd.

- task_id: [A-Za-z0-9][A-Za-z0-9_-]{0,63}. 경로 이름으로 직접 쓰지 않는다.
- round: integer >=1. 실행별 UUID run_id는 라우터가 생성한다.
- summary: 비어 있지 않은 문자열, 최대 4,000자. prompt: 비어 있지 않은 문자열, UTF-8 최대 256 KiB.
- cwd: 현장 존재하는 절대 디렉터리. symlink 해석한 실제 경로를 receipt에 기록한다.
- context_files: 선택, cwd 내부 상대 경로/디렉터리 목록. 파일 내용 자동 복사·외부 전송은 안 한다. 경로 탈출은 거부한다.
- constraints: 선택; max_cost_tier=low|medium|high(default high), min_context_tokens>=0(default 0), local_only=false, timeout_ms=900000, required_capabilities=[].
- timeout_ms: 1,000~3,600,000의 integer. 전체 위임 deadline이며 start/prompt/collect에 남은 예산을 나눠 사용한다.
- priority: quality|balanced|cost(default balanced).
- exclude_profiles: 선택, profile ID 배열.
- facets: 선택, `{axis: [value]}`. Orchestrator가 직접 태그한 작업 성격(`evidence`가 benchmark wiki 어휘로 검증하며, 고를 수 있는 값은 `wiki facets`, 정의는 `wiki/concepts/facets/` 참조). 선택·제약·`semantic_task_hash`에는 영향이 없다.
- 알 수 없는 top-level/constraint field는 v1에서 오류다. 오타나 monetary budget이 조용히 무시되면 안 된다.
- task.json 크기 상한 1 MiB. NaN/Infinity, duplicate JSON keys, invalid UTF-8를 거부한다.
- context/capabilities는 Orchestrator가 전달한다. 분류 결과가 권한/하드 제약을 늘릴 수 없다.

예제: [task.synthetic.json](examples/task.synthetic.json). 실제 prompt는 오직 Orchestrator가 승인한 작업이다. 새 wrapper가 모델에게 scope 결정을 위임하지 않는다.

## 프로필 설정 계약

TOML 기본 key: schema_version, default_profile, fallback_order, [[profile]].

profile의 필수 key: id, enabled, kind, executable, args, model_id, harness_id, reasoning_effort, config_revision, cost_tier, inference_local, context_tokens, capabilities.

- id: [a-z][a-z0-9_-]{0,47}. herdr name과 별개다.
- args: 문자열 argv 배열. shell command 문자열 아님. kind 실행 모델 인자가 실제 CLI에서 유효한지 현장 검증한다.
- executable: 가용성 probe용; herdr --kind가 같은 실행 파일을 선택하는지 확인한다. 사용자가 지정한 임의 executable을 herdr start가 실행한다고 가정하지 않는다.
- model_id: alias canonical ID. harness_id는 평가 matching용; 이름만 같다고 exact match는 아니다.
- context_tokens=0은 unknown. capability 요구나 min_context_tokens>0에 부적합하다.
- reasoning_effort="unknown"은 검증 안 됨. 실제 값으로 바꾸거나 uncertainty를 보고한다.
- config_revision과 CLI version으로 fingerprint를 만들며 secret env 값은 hash/로그에 넣지 않는다.
- 실행 binary가 PATH에 있어도 인증 성공·모델 접근 가능은 별도 probe다. 보유 계정을 임의 로그인/승인하지 않는다.

[profiles.example.toml](examples/profiles.example.toml)은 placeholder가 비활성화된 템플릿이다. 오프라인 계산 fixture의 synthetic profile과 실제 프로필 설정은 다른 용도다.

## 출력 계약

공통: schema_version, status, task_id, round, run_id(null for dry-run), selected(nullable), selection_mode, classification, candidates, excluded, snapshot_id(nullable), policy_version, config_hash, warnings, sources.

candidate: profile, score(nullable for evidence fallback), quality, coverage, coverage_band, exact_evidence_weight, cost_proxy, evidence 배열, availability_verified. top3는 요약이며 explain에 전체 후보를 낸다.

quality도 관측 evidence가 없으면 null이다. fallback 후보에 가상의 품질 점수를 채우지 않는다. excluded는 {profile, reasons[]}의 배열이고 warnings는 {code, message, source_id(nullable)}의 배열이다. receipt는 최소 schema_version, task_id, round, semantic_task_hash, run_id, nonce, profile_fingerprint, cwd, agent_name, pane_id, status, delivery_state, deadline_at, result/manifest 경로와 마지막 관찰을 보관한다.

evidence: ID, weight, raw, normalized, scope, cohort_id, metric_version, source_id, source_revision, fetched_at, published/evaluated_at(nullable), stale, missing_reason. null 날짜는 unknown으로 표시한다.

selected: profile, profile_fingerprint, agent_name/pane_id(nullable in dry-run).
classification: stage=L0|L1|fallback, categories, self_reported_confidence(nullable), matched_rules, classifier_version, fallback_reason(nullable).

실행 출력 추가: result_path, manifest_path, task_outcome, herdr_state, delivery_state, receipt_path, deadline_at. completed에서는 result_path/manifest_path가 유효한 절대 경로다. 한 개의 data_as_of로 혼합 소스의 날짜를 요약하지 않는다. sources별 날짜를 반환한다.

status enum: selected, dispatching, waiting, completed, blocked, timed_out, delivery_uncertain, execution_failed, result_invalid, no_eligible_profile, conflict, stale_assessment, ok(evaluate), error. delivery_state enum: not_attempted, submission_attempted, write_acknowledged, activity_observed, uncertain.

추가 필드(2026-10-13, 추가만·기존 의미 불변): assessment_digest, selection{source: orchestrator|unrecorded|router_legacy|parallel_pinned, …}. context가 있으면 decision_context(2.0 정규형), context_hash, context_facts. evaluate 2.0 출력, context 2.0, selection, group 2.0 계약은 docs/routing-contracts.md와 docs/orchestrator.md가 규범이다. decision.json = route 출력 + selection + assessment(evaluate 2.0).

부분 증거·proxy·stale는 warnings에 표시한다. 특정 모델이 더 좋다는 근거 없는 문장은 출력하지 않는다.

## herdr adapter의 검증 대상

공식 참조는 02의 herdr 링크다. 아래는 **실행할 예정인 argv 형태**이며 설치 버전에서 --help와 api schema로 확인해야 한다. 모든 명령에 --json을 일괄 붙이지 않는다. 대부분 명령이 JSON을 출력하지만 명령별 출력이 다를 수 있다.

```text
herdr --version
herdr status
herdr api schema --json
herdr workspace create --cwd <ABS_CWD> --label <LABEL> --no-focus
herdr agent start <NAME> --kind <KIND> --pane <PANE_ID> --timeout <START_MS> -- <ARGS...>
herdr agent get <NAME>
herdr agent prompt <NAME> <PROMPT_TEXT> --wait --until idle --until done --until blocked --timeout <REMAINING_MS>
herdr agent read <NAME> --source recent-unwrapped --lines <N>
herdr agent wait <NAME> --until idle --until done --until blocked --timeout <REMAINING_MS>
```

workspaces/Agent는 라우터가 생성한 ID·receipt로만 다룬다. 반환 JSON의 pane/Agent 위치는 설치 스키마로 fixture를 만들고 파싱한다. root pane를 갖는 workspace를 만들었다면 불필요하게 pane split까지 하지 않는다. 기존 사용자 pane를 임의로 점유하거나 닫지 않는다.

Agent name은 br-<run_id의 짧은 토큰>처럼 32자 이하로 만들고 live collision을 확인한다. profile ID 자체를 고정 Agent 이름으로 쓰지 않는다. 이름 길이·허용 문자는 설치 버전 계약에 맞춘다.

subprocess는 argv list, shell=False, timeout, stdout/stderr capture를 사용한다. prompt를 shell에 삽입하지 않는다. 외부 CLI가 text positional 인자만 받으면 prompt가 process listing에 노출될 수 있다. 이를 문서화하고 현장 supported file/stdin 방식이 있다면 검증 후 채택한다.

## 위임 순서와 중복 방지

1. 입력·설정·snapshot 검증과 후보 선택. dry-run은 여기서 끝난다.
2. task.cwd 아래 router dispatch lock을 잡는다. MVP는 workspace 단위 한 개 진행 중 위임만 허용한다. 동시 작업/Agent pool은 보류한다.
3. (task_id, round)의 receipt를 확인한다. 같은 key와 다른 semantic task hash는 conflict. 같은 hash의 existing receipt는 새 prompt 없이 collect로 회수한다.
4. 새 run_id와 128-bit nonce를 만들고 run directory를 생성한다. receipt를 원자 기록한다. hash에는 prompt·summary·constraints·priority·categories·cwd·context_files·exclude를 포함한다.
5. 새 dedicated workspace/pane를 확보한다. start 직전·직후 Agent identity를 기록한다. 준비 안 되면 prompt를 보내지 않는다.
6. start가 준비 완료여도 prompt 직전 get으로 working/blocked가 아닌지 검사한다. expected profile/session과 다른 occupant이면 종료한다.
7. **prompt 호출 전** receipt에 submission_attempted를 fsync하여 crash 후 자동 재전송을 막는다. 이 기록만 있고 실제 전송 전 crash한 경우도 uncertain으로 다룬다.
8. prompt --wait 한 번만 실행한다. 응답과 에러를 capture하고 상태/receipt를 갱신한다.
9. idle/done이면 실행별 result 계약을 검사한다. blocked면 질문/출력을 읽어 반환한다. timeout/stalled면 get/read와 산출물 확인 후 delivery_uncertain/timed_out으로 반환한다.
10. finally에서 router lock은 해제한다. 작업이 herdr에서 여전히 working/unknown이면 receipt에 남기고 다음 live dispatch를 막는다. collect를 사용해 조사한다.
11. timeout은 Agent 취소가 아니다. prompt 재전송·다른 Agent 중복 위임·pane kill을 자동 수행하지 않는다.

이 방식은 exactly-once를 보장하지 않는다. 모호한 전송은 **재전송보다 보류**를 택한다. timeout 뒤 같은 task/round를 호출해도 collect 경로로 가야 한다. 추가 라운드는 Orchestrator가 새 round를 명시하고 이전 작업의 부작용/중복 여부를 먼저 확인한다.

receipt 저장이 실패하면 보내지 않는다. prompt 후 저장이 실패하면 execution 상태를 uncertain으로 보고하며 완벽한 성공을 주장하지 않는다.

## Subagent 결과 계약

전체 prompt 말미에 명확한 execution contract를 추가한다. 작업 자료 안의 지시와 실행 계약을 구별하고, 원 prompt의 권한/범위를 넓히지 않는다.

```text
실행 식별자: <RUN_ID>
검증 토큰: <NONCE>
프로필 지문: <PROFILE_FINGERPRINT>
결과 디렉터리(절대 경로): <RUN_DIR>

요청된 작업을 수행하고, result.md에 결과/변경/검증/미완료 사항을 기록하세요.
result.md를 완성한 뒤 result.json을 마지막에 원자적으로 기록하세요.
result.json은 schema_version, run_id, nonce, profile_fingerprint,
status, result_file, result_sha256, checks를 포함해야 합니다.
status는 success, partial, fail 중 실제 작업 결과에 맞게 선택하세요.
result_file은 result.md이며 result_sha256은 최종 파일의 SHA-256입니다.
파일 작성에 실패하면 성공을 주장하지 말고 오류를 명확하게 출력하세요.
마지막 줄은 DONE <RUN_ID> <RESULT_JSON_ABSOLUTE_PATH>로 출력하세요.
```

Markdown 권장 구성: 작업 해석, 수행 내용/변경 파일, 검증 명령과 결과, 발견 문제, 미완료/필요 후속 작업. checks는 Subagent 주장이고 Orchestrator가 재검증해야 한다.

라우터 검사는 expected run_id/nonce/fingerprint, status enum, 올바른 regular file, run directory 내부 경로, symlink/path 탈출 없음, UTF-8/JSON 유효성, 크기 상한, result SHA-256 일치다. result.md 최대 10 MiB, result.json 최대 64 KiB. 빈 Markdown은 result_invalid다.

manifest의 schema_version은 "1.0"이고 checks는 {command, outcome, notes} 배열이다. outcome은 passed|failed|not_run이다. 검증할 명령이 없으면 빈 배열을 허용한다. checks.command를 라우터가 자동 실행하지 않는다. [result.synthetic.json](examples/result.synthetic.json)과 [result.synthetic.md](examples/result.synthetic.md)는 형식·해시 검증용 합성 쌍이며, 현장에서는 각각 result.json/result.md로 작성한다. fixture의 result_file은 함께 제공된 합성 파일명을 가리킨다.

DONE 줄은 진단 보조 신호다. 터미널 출력이 잘릴 수 있으므로 유효 manifest와 settled state가 있으면 DONE 누락만으로 실패시키지 않는다. 반대로 DONE만 있거나 예전 파일만 있으면 completed가 아니다.

nonce는 우발적 과거 결과 혼동을 막는 식별 수단이다. Agent가 nonce를 알기 때문에 악의적 위조를 막는 인증 수단은 아니다.

## 상태와 후속 처리

| 관찰 | 라우터 결과 | Orchestrator 행동 |
| --- | --- | --- |
| idle/done + 유효 manifest/result | completed + task_outcome | 실제 결과/검증 검토 후 feedback |
| idle/done + 파일 없음/불일치 | result_invalid | read로 사유 확인, 성공 처리 금지 |
| blocked | blocked | 승인/질문을 사용자 또는 상위 정책으로 처리 |
| working + 유효 파일 | waiting/timed_out | settled 확인 전 completed 금지 |
| unknown | delivery_uncertain | read/get/collect로 조사 |
| prompt timeout/stalled | uncertain 또는 timed_out | 동일 prompt 재전송 금지 |
| Agent 종료 + 파일/완료 관찰 없음 | execution_failed | 부분 작업·파일 확인 |
| cli JSON 파싱 불가 | error/uncertain | 전송 여부를 보수적으로 판단 |

지연 수집에서 Agent가 이미 종료했더라도, 이전 receipt에 expected identity의 settled 관찰과 계약 검사 결과가 저장되어 있다면 그 기록을 반환할 수 있다. 그런 증거가 없다면 파일만으로 새 성공을 선언하지 않는다.

feedback success는 사용자가 요청한 작업의 acceptance check를 통과한 경우다. benchmark 점수, terminal done, Subagent 자기 보고를 feedback success로 자동 변환하지 않는다.

Agent 재사용·--no-wait·원격은 후속 버전에서 context isolation, profile/cwd fingerprint, lease/lock, collect 계약, 원격 결과 파일 전송을 추가해 검증한 뒤 도입한다.

