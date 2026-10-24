# CLI·JSON·실행 계약

갱신: 2026-10-24. 실제 실행은 [Projects 계약](docs/projects.md), 선택은 [vendor-guided 정책 6](docs/vendor-guided-routing.md), 지표와 digest는 [라우팅 계약](docs/routing-contracts.md)을 따른다.

## CLI

전역 옵션은 `--config-dir`, `--cache-dir`, `--herdr-session`이며 하위 명령 앞에 둔다. 명령의 정확한 인자는 `--help`를 따른다.

| 명령 | 동작 |
|---|---|
| `route --task FILE --dry-run` / `explain --task FILE` | 오프라인 판단 패킷·선택 재현 / 전체 후보·제약을 포함한 텍스트 설명 |
| `route --task FILE [--wait-ms N]` | 선택 후 live 제출·유한 대기; 0은 제출 직후 반환 |
| `evaluate --task FILE [--context FILE] [--format 1\|2\|3]` | 선택 없는 평가. 기본 schema 2.0, format 3은 schema 4.0 |
| `select --assessment FILE --profile ID --policy-id ID --policy-version V --reason TEXT [--accept-provisional]` | 완료된 format 3 평가에서 selection 6.0 생성. 실행·쓰기 없음 |
| `route --task FILE --selection FILE [--dry-run]` | 선택 2.0·5.0·6.0 검증·재생 |
| `route --task FILE --profile ID [--dry-run]` | 기록 없는 명시적 override, 경고 |
| `parallel --group FILE [--dry-run] [--wait-ms N]` | task별 선택·worktree·group 실행과 동일 plan 회수 |
| `refresh [--source ID] [--force] [--vault DIR]` / `--import FILE` | 수집·wiki index·snapshot 갱신 / 승인 SWE·TB import |
| `status` / `profiles discover [--force]` | 캐시·설정 상태 / 프로필 생성(기존 파일은 force 필요) |
| `wiki compile [--check]` / `wiki facets` | 검토된 wiki 컴파일·검증 / facet 어휘 |
| `evidence --task FILE [--format json\|table] [--max-units N]` | facet별 근거 조회, 기본 12 unit, 순위 없음 |
| `collect --run-id ID --cwd DIR [--wait-ms N]` | 기존 receipt 관찰·결과 회수, 재전송 없음 |
| `collect --run CWD ID [--run …] --until any\|all [--wait-ms N]` | 여러 run의 settle 또는 blocked 관찰 |
| `tell --cwd DIR [--run-id ID] --message TEXT` / `--message-file FILE` | 실행 중 또는 resume한 대화형 run에 명시적 메시지 |
| `stop --cwd DIR [--run-id ID]` / `resume --cwd DIR --run-id ID` | 명시적 중단 / 완료된 대화 재개(전송 없음) |
| `feedback --run-id ID --cwd DIR --outcome success\|partial\|fail` | Orchestrator 검증 결과 기록 |
| `coordination status\|release\|feedback` | 공유 admission·정지 확인 후 해제·결과 채택 기록 |

표의 선택 인자는 실제 명령에서 하나를 고른다. stdout은 JSON 한 객체이며 `explain`과 `evidence --format table`은 텍스트다. dry-run·evaluate·explain·evidence는 네트워크·Herdr·파일 쓰기 없이 동작한다. route·explain·parallel·evaluate는 `--host antigravity|codex|claude`, `--decision-response`를 받는다. evaluate의 응답 입력은 format 3에서만 허용한다. `--selection`·`--profile`은 배타적이고 `--decision-response`와도 함께 쓸 수 없다.

| 코드 | 의미 |
|---|---|
| 0 | selected·completed·ok·기록/제어 명령 정상 |
| 2 | 입력·설정·인자 validation 오류, 미지원 schema |
| 10 | blocked, 승인·질문 대기 |
| 11 | waiting·timed_out·delivery_uncertain; 실행 중일 수 있음 |
| 12 | execution_failed·result_invalid |
| 13 | no_eligible_profile |
| 14 | conflict·잠금/admission 거절·stale_assessment |
| 15 | 저장소·I/O 오류 |
| 16 | refresh 일부/전체 실패; 소스별 last-good 유지 |
| 17 | decision_required·decision_unavailable; 판단 응답 또는 상위 선택 필요 |

## 입력 계약

task 필수 필드는 `schema_version="1.0"`, `task_id`, `round`, `summary`, `prompt`, `cwd`다.

- task_id: `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`, round: integer ≥1. 실행별 UUID run_id는 별도 생성한다.
- summary는 비어 있지 않은 최대 4,000자, prompt는 UTF-8 최대 256 KiB다. task 파일은 최대 1 MiB다.
- cwd는 존재하는 절대 디렉터리이며 실제 경로로 정규화한다. live는 커밋이 있는 Git 최상위여야 한다.
- context_files는 cwd 내부 상대 경로 목록이다. 파일 본문 자동 복사·외부 전송을 하지 않고 경로 탈출을 거부한다.
- constraints 기본: max_cost_tier=high, min_context_tokens=0, local_only=false, timeout_ms=900000, required_capabilities=[]. timeout은 1,000–3,600,000ms다.
- priority=quality|balanced|cost(기본 balanced)는 호환 입력이며 자동 비용 순위로 쓰지 않는다. exclude_profiles는 제외 목록이다.
- execution=interactive|headless(기본 interactive). headless는 one-shot CLI이며 tell을 받지 않는다.
- facets=`{axis: [value]}`는 명시적 작업 특성이다. `wiki facets` 어휘를 사용하고 vendor-guided 판단·근거 검색에 반영한다. 기본 semantic_task_hash에는 없지만 decision 입력에 별도로 묶인다.
- 알 수 없는 필드·NaN/Infinity·duplicate JSON key·잘못된 UTF-8은 validation 오류다.

interactive 제출은 실행 계약을 합쳐 120 KiB 제한이며 argv 노출 가능성이 있다. headless prompt는 input.txt로 전달한다. `local_only`는 모델 inference의 로컬성을 뜻하며 Herdr가 로컬이라는 이유로 cloud 모델을 허용하지 않는다.

semantic_task_hash는 prompt·summary·constraints·priority·cwd·context_files·exclude_profiles를 묶고, headless이면 execution도 포함한다. task_id/round는 receipt identity다. 파일 본문 전체를 hash하지 않으므로 상위가 artifact revision을 관리한다.

## 프로필 설정 계약

TOML은 `schema_version="1.0"`, `[[profile]]`을 갖는다. profile 필수 키는 id·enabled·kind·executable·args·model_id·harness_id·reasoning_effort·config_revision·cost_tier·inference_local·context_tokens·capabilities다. 미등록 키를 허용하지 않는다.

id는 `[a-z][a-z0-9_-]{0,47}`다. executable은 kind와 같아야 하고 args는 shell 문자열이 아닌 argv다. 현재 Projects 변환은 모델(`--model`/`-m`)·effort(`--effort`, Codex `-c model_reasoning_effort=...`)만 받는다. 다른 권한·도구 인자는 제출 전에 거부한다. interactive 권한은 Projects worker.access 설정을 따른다.

model/harness/effort는 평가 매칭과 구분해서 보존한다. context_tokens=0은 불명이며 양수 context 요구를 만족하지 않는다. reasoning_effort=unknown은 exact 매칭 불가·가이드 결측이다. config_revision 변경은 지문에 반영하며 CLI 버전은 현재 unknown이다.

[profiles.example.toml](examples/profiles.example.toml)은 모두 비활성 placeholder다. `profiles discover`는 실행 가능한 CLI의 모델·effort 정보를 수집해 활성 프로필을 만들지만 계정 호출 성공을 보장하지 않는다. live probe는 PATH·agy models·선택적 CodeBurn 상태를 확인하며 모델의 실제 실행 성공은 별도다.

## 출력과 선택 기록

route envelope는 schema 1.0이며 status·task_id·round·run_id·selected·selection_mode·classification·candidates·excluded·snapshot_id·policy_version·config_hash·warnings·sources·assessment_digest를 포함한다. vendor-guided에는 decision 입력·단계별 근거·후보 facts도 제공한다. CLI route candidates는 ID순 첫 3개 요약이며 candidates_total에 전체 수를 남긴다. 상위 3위가 아니다.

기본 evaluate 1·2의 후보는 quality·coverage·coverage_band·exact_evidence_weight·evidence를 제공한다. score·legacy_score·cost_proxy는 없다. 기본 route의 후보 quality/coverage는 category 평가 결과가 아니므로 의미 판단 근거는 `decision.evaluation` 또는 `selection.decision.evaluation`에서 읽는다. 제약 결과·공개 후보별 적합성은 format 3을 사용한다.

| 계약 | 버전 |
|---|---|
| evaluate 기본 / 호환 | 2.0 / 1.0 |
| evaluate `--format 3`의 assessment | 4.0 |
| 자동 단일 후보 / 상위 선택 selection | 5.0 / 6.0 |
| 명시적 override selection | 2.0 |
| context / group | 2.0, 입력 1.0도 수용 |

과거 vendor-guided selection 3.0·4.0은 재평가한다. `select`는 schema 1.0 응답의 `selection` 객체에 6.0 기록을 반환하며 그 객체만 입력 파일로 사용한다. 5.0·6.0에는 재생용 task·stages·evaluation·uncertainty·입력 digest가 있다. 상세 필드는 [상위 연동](docs/orchestrator.md)을 따른다.

live 응답에는 receipt_path·결과 경로·task_outcome·delivery_state·reassignment·coordination_key·thread_id·worktree·branch 등이 추가된다. completed의 결과 경로는 유효한 절대 경로다. source별 날짜를 유지하고 혼합 소스를 한 기준일로 요약하지 않는다.

## 실행과 중복 방지

1. 같은 task/round의 receipt를 먼저 확인한다. 같은 semantic hash는 재전송 없이 collect, 다른 내용·지정 profile 충돌은 conflict다. 기존 실행 회수는 새 정책 판단보다 우선한다.
2. 새 실행은 제약·선택 재생·현재 가용성을 확인한다. 공유 admission은 활성 4개와 경로 중첩을 검사하고 cwd dispatch lock을 사용한다.
3. UUID run_id·128-bit nonce·프로필 지문·deadline·선택·input.txt를 run 디렉터리에 기록한다. receipt와 decision을 원자 게시한다.
4. interactive는 Projects 1.2.1의 add/delegate를 한 번 호출하고 board task ID를 기록한다. headless는 Herdr worktree pane에서 one-shot CLI를 실행한다. 제출 의도는 외부 호출 전에 fsync한다.
5. interactive는 board approval/done에서, headless는 종료 후 결과 계약을 검사한다. blocked·timed_out·delivery_uncertain은 자동 재전송·다른 worker 위임·취소를 하지 않는다.
6. 제출 전 확정 실패는 receipt settle과 admission 반환을 수행한다. 제출 여부 불확실은 상태를 보존하고 collect/정지 확인을 요구한다.
7. completed는 관리 대상 pane을 반환한다. resume은 완료 대화를 같은 세션으로 다시 열며 전송하지 않는다. stop/tell은 명시적 요청에만 수행한다.

group은 모든 선택을 먼저 검증하며, 반복 profile도 별도 label·worktree·receipt를 사용한다. task당 8·group당 16·max_parallel 1–4다. 실행 plan을 동결하고 동일 입력은 기존 receipts를 회수한다. group rounds에도 delivery_state와 reassignment를 전달한다.

## Subagent 결과 계약

worker는 자기 worktree의 `.bench-router/runs/<run_id>/`에 result.md를 완성하고 result.json을 마지막에 한 번에 작성한다. `sha256sum result.md`로 최종 hash를 계산하도록 안내한다. wrapper 자신의 receipt·input 원자 기록과 worker manifest 작성 지시를 구분한다.

```json
{"schema_version":"1.0", "run_id":"<RUN_ID>", "nonce":"<NONCE>",
 "profile_fingerprint":"<FINGERPRINT>", "status":"success",
 "result_file":"result.md", "result_sha256":"<SHA256>",
 "checks":[{"command":"검증 명령", "outcome":"passed", "notes":"검증 결과"}]}
```

manifest status는 success|partial|fail, checks.outcome은 passed|failed|not_run이다. checks는 빈 배열도 허용하며 worker의 주장이다. 라우터가 명령을 자동 실행하지 않는다. Markdown에는 변경·검증·미완료 사항을 기록한다. 형식 예는 [result.synthetic.json](examples/result.synthetic.json)과 [result.synthetic.md](examples/result.synthetic.md)에 있다.

라우터는 run ID·nonce·fingerprint·상태·UTF-8·regular file·경로 내부성·symlink 탈출·크기·hash를 검사한다. result.md는 비어 있지 않은 최대 10 MiB, manifest는 최대 64 KiB다. 유효 결과는 원래 cwd run 디렉터리로 복사한다. `DONE` 터미널 줄은 보조 진단이며 결과 계약을 대체하지 않는다. nonce는 과거 파일 혼동을 막는 식별자이며 악의적 위조를 막는 인증 수단은 아니다.

## 상태와 후속 처리

| 결과 | 후속 행동 |
|---|---|
| decision_required / decision_unavailable | 단계 응답 또는 상위 선택을 완료; 실행 없음 |
| stale_assessment | 같은 제출이 없다면 재평가·재선택 |
| blocked | 사용자 승인·질문 처리 후 collect |
| timed_out / delivery_uncertain | 실행 중일 수 있으므로 collect_first |
| execution_failed / result_invalid | 전송·부분 효과·worker 상태를 검토하고 재배정 여부 결정 |
| completed | task_outcome·결과 내용·작업 브랜치를 검토하고 feedback·채택/병합 결정 |

`completed`는 형식에 맞는 결과를 받았다는 뜻이다. 내용의 정확성은 상위가 판단한다. 재시도는 같은 task/round 재전송이 아니라 부분 효과·정지 여부를 확인한 후 명시적 새 round로 수행한다.
