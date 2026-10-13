# 벤치마크 점수 수집·중복 제거 설계

확인일: 2026-10-13. 이 문서는 수집 및 라우팅 정책의 구현안이다. 현재 코드나 가중치를 변경하지 않는다.

## 현재 상태와 수집처

현재 `bench_router/data.py`는 Hugging Face에 호스팅된 LMArena `leaderboard-dataset`의 다섯 코호트(text, text/math, webdev, document, vision)를 자동 수집한다. SWE-bench Verified와 Terminal-Bench 4.0은 수동 import만 받는다. `categories.toml`의 9개 카테고리 중 6개는 Artificial Analysis(AA) 점수에 의존한다. AA Free 데이터로 필요한 평가 점수를 얻을 수 없으므로 새 정책의 필수 소스로 두지 않는다.

| 수집처 | 확인한 벤치마크와 범위 | 채택 방침 |
| --- | --- | --- |
| [The Model Gap 공개 데이터](https://themodelgap.com/data) | 14종, 점수 332개. Terminal-Bench 4.0/2.1, DeepSWE, Toolathlon Verified, Agents' Last Exam(ALE), HLE, ARC-AGI-2, LiveBench, AA Analyst Agent, OSWorld 2.0, SWE-bench Verified, GPQA Diamond, LiveCodeBench, HMMT Feb 2026. 각 점수에 원출처 URL·독립 평가 여부·평가기관·관측일; 일부에 effort. CC BY 4.0. | 초기 수집 우선순위 1. 원출처를 보존하고, 벤치마크별 상태·평가 조건 검사를 통과한 점수만 라우팅에 사용. |
| [HF 공식 벤치마크 API](https://huggingface.co/docs/hub/leaderboard-data-guide) | 조회 당시 공식 데이터셋 49개. 중복되는 SWE-bench Verified, Terminal-Bench 2.1, DeepSWE, ALE, HLE, Toolathlon 외에 SWE-bench Pro, MMLU-Pro, AIME 2026, MMMU-Pro, ExtractBench, ParseBench 등이 있음. | 새 벤치마크와 결측 모델을 보완. 공식 **데이터셋** 등록과 개별 **점수** 검증을 별개로 취급. 표본 조회한 관련 리더보드의 `verified`는 모두 `false`; 원출처·조건 확인 전 자동 채점에 넣지 않음. |
| [공식 Terminal-Bench](https://www.tbench.ai/)·[공식 SWE-bench](https://www.swebench.com/) 및 원 평가기관 | 버전, 제출 모델·에이전트, 실행 조건의 기준 자료. | 기존 exact import 유지. 다른 아카이브와 수치가 충돌하면 원 평가 기록으로 확인. |
| [LMArena 데이터셋](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset) | 기존 5개 코호트. | 유지. HF에 호스팅됐다는 이유로 HF 공식 벤치마크 API 점수와 같은 출처로 합치지 않음. |

The Model Gap의 Terminal-Bench **4.0도 현재 공개 데이터에 존재한다**(35점). 2.1만 있다는 이전 조사 결과는 갱신됐다. 다만 그 데이터의 `harness`는 평가기관을 가리킬 수 있으며 실제 에이전트 스캐폴드와 동일하지 않다. 따라서 4.0이라는 버전만 같다고 기존 `terminal_exact`로 승격하지 않는다. [해당 벤치마크 설명](https://themodelgap.com/benchmarks/terminal-bench-4-0)은 평가기관별 스캐폴드와 반복 횟수 차이를 명시한다.

주요 중복 구간의 대표 점수 선택 기준은 다음과 같다. 표의 HF는 [공식 벤치마크 검색 API](https://huggingface.co/api/datasets?filter=benchmark%3Aofficial)에서 확인한 데이터셋을 뜻한다. HF의 개별 점수가 `verified=false`이면 원 평가자의 점수로 간주하지 않는다.

| 논리 벤치마크 | 겹치는 수집처 | 우선 사용할 근거 |
| --- | --- | --- |
| Terminal-Bench 4.0 | 기존 공식 수동 import, The Model Gap, HF `harborframework/terminal-bench` | 프로필의 에이전트·effort까지 일치하는 공식 import. 그 외에는 버전과 평가 설정을 확인할 수 있는 The Model Gap의 독립 평가를 proxy로 사용. HF 데이터셋의 실제 버전 확인 전에는 합치지 않음. |
| SWE-bench Verified | 기존 공식 수동 import, The Model Gap, HF `SWE-bench/SWE-bench_Verified` | 정확한 실행 설정이 일치하는 기존 import. 포화 상태여서 나머지는 조회용. |
| DeepSWE·Toolathlon Verified·ALE·HLE | The Model Gap, 해당 HF 공식 데이터셋 | 같은 모델·변형·설정이면 독립 평가 여부, HLE의 도구 사용 여부, effort와 원출처가 더 구체적인 기록을 선택. 정보가 부족한 HF 행은 보류. |
| Terminal-Bench 2.1·GPQA Diamond·HMMT Feb 2026 | The Model Gap, 해당 HF 공식 데이터셋 | 이 정책에서는 조회용. 다른 버전이나 포화·오염 상태의 점수를 현재 벤치마크 점수에 더하지 않음. |
| ARC-AGI-2·LiveBench·AA Analyst Agent·OSWorld 2.0·LiveCodeBench | 확인한 범위에서 The Model Gap | 개별 변형과 상태를 따라 수집. LiveCodeBench는 포화 상태여서 조회용. |
| SWE-bench Pro·MMLU-Pro·AIME 2026·MMMU-Pro·ExtractBench·ParseBench | 확인한 범위에서 HF 공식 데이터셋 | The Model Gap에 없는 지표로 후보 등록. 원출처와 평가 조건 확인 후 활성화. |

## 무엇을 점수에 반영할지

1. **우선 반영할 후보:** Terminal-Bench 4.0, DeepSWE, Toolathlon Verified, ALE, HLE, ARC-AGI-2, LiveBench. 각 지표의 독립 평가·현재 상태·모델 커버리지를 먼저 확인한다. AA Analyst Agent는 `analysis` 작업과 측정 대상이 일치할 때만 검토한다. OSWorld 2.0은 버전·온라인/오프라인 변형을 분리하고, 이 라우터가 실제로 데스크톱 조작 작업을 배정할 때만 반영한다.
2. **HF로 보완할 후보:** SWE-bench Pro(저장소 수정), AIME 2026(수학), MMLU-Pro(일반 추론), MMMU-Pro(시각 추론), ExtractBench/ParseBench(문서 처리). 출처 및 동일 설정의 모델 간 비교 가능성을 확인한 뒤 개별 등록한다. 49개 전체를 자동 활성화하지 않는다.
3. **아카이브만 유지할 후보:** The Model Gap이 포화 또는 오염으로 표시한 SWE-bench Verified, GPQA Diamond, LiveCodeBench, HMMT Feb 2026. 기존 수동 SWE-bench Verified는 재현 가능한 exact 근거로 남기되, 신규 가중치에서 우선순위를 낮춘다. Terminal-Bench 2.1과 4.0은 별도 버전으로 보관하며 같은 `terminal_ops` 품질을 두 번 가산하지 않는다.

이는 확정 가중치가 아니다. 각 후보가 실제 `profiles.toml`의 모델을 얼마나 덮는지 측정해야 한다. 수집된 점수가 없거나 평가 조건이 다른 벤치마크에 가중치를 주면 현재 `coverage_quality()`의 결측 페널티가 선택 결과를 왜곡한다.

## 중복 제거와 비교 가능성

수집 원본은 모두 보관하되, 라우팅에는 **논리 벤치마크 한 항목당 프로필별 점수 하나**만 넣는다.

- 벤치마크 키: `suite + version + subset + metric + variant` (예: HLE `no_tools`와 `with_tools`는 별개). 표시 이름이나 수집처 이름으로 식별하지 않는다.
- 비교 코호트 키: 벤치마크 키에 평가 스캐폴드, 도구 허용, 추론 노력, 채점 방식(`pass@1`/반복·다수결 등), 데이터셋 개정판을 더한다. 값을 모르면 `unknown`으로 보존하고 아는 값과 합치지 않는다. 서로 다른 코호트의 raw 점수나 percentile을 한 순위로 정규화하지 않는다.
- 프로필 매칭: 모델 ID는 명시적 alias로만 합친다. `harness_id`와 `reasoning_effort`가 실제 프로필과 확인되면 `exact_profile`; 하나라도 불명확하면 `model_proxy`. 현재 exact import의 필수 필드를 아카이브의 평가기관 이름으로 채워 넣지 않는다.
- 동일 프로필·논리 벤치마크·비교 코호트에 여러 기록이 있으면 **설정이 완전히 명시되고 프로필에 맞는 점수 → 독립 검증/원 평가기록 → 더 상세한 조건·원출처 → 최신 관측일** 순으로 선택한다. `verified=false`는 검증 근거로 쓰지 않는다. 순위만 다르고 조건이 불명확하면 자동 선택하지 않고 충돌을 기록한다.
- 버전 또는 변형이 다른 점수는 중복이 아니라 별도 관측치다. 다만 같은 작업 역량을 측정하는 벤치마크를 여럿 활성화할 때에는 카테고리의 총 가중치 1 안에서 나누고, 동일 계열 버전은 하나만 기여시킨다.

## 최소 구현 순서

1. `data.py`의 수집처별 `FETCH`/`PARSE` 구조를 그대로 이용해 The Model Gap `benchmarks.json`·`scores.json` 수집기를 추가한다. HF는 전체 탐색 결과를 곧바로 점수화하지 말고, 승인한 `dataset_id`별 leaderboard 어댑터만 추가한다. 각 어댑터는 공통 관측 레코드(`benchmark_key`, `cohort_key`, `model_id`, `raw`, `source_url`, `source_type`, `verified`, `harness`, `scaffold`, `effort`, `observed_at`, `license`)를 반환한다. URL·날짜·수치·방향·버전이 없는 기록은 보류한다. 기존 형식의 새 벤치마크는 등록부에 ID·버전·변형·지표·방향·코호트 필드·카테고리·상태를 추가하면 수집되게 하고, 새 제공자에만 어댑터 코드를 작성한다.
2. 수집 원본과 선택 점수를 분리한다. 현재 DB의 관측 테이블에는 원출처 URL, source type, variant, 평가 스캐폴드가 없으므로 스키마 버전을 올려 추가한다. 스냅샷에는 선택된 점수와 탈락/충돌 이유, 원출처 링크, 소스 revision을 기록한다. 소스 장애 시 기존 last-good 동작을 유지한다.
3. `build_snapshot()`에서 alias 확인 → 비교 코호트 분리 → 프로필별 우선순위 선택을 한다. `normalize()`의 percentile은 **동일 조건 코호트** 안에서만 계산한다. 표본이 부족하거나 코호트에 여러 설정이 섞여 있으면 자동 라우팅에서 제외하고 조회용으로만 남긴다.
4. `categories.toml`에서 AA 필수 의존을 걷어내고, 확인된 코호트만 `coding_repo`, `terminal_ops`, `code_gen`, `math_reasoning`, `analysis`, `webdev`, `writing`, `vision_doc`, `general`에 재배분한다. 각 카테고리의 합 1과 `routing.POLICY_VERSION` 갱신을 함께 검증한다. `writing`/`webdev`는 관련성 높은 기존 LMArena 지표를 계속 쓴다. 점수 활성화는 사전 정의한 벤치마크 등록부의 상태(`candidate`, `active`, `archive`)와 모델 커버리지 검사로 제어한다.
5. 오프라인 테스트: 동일 SWE/HLE/TB 점수가 양쪽에 있을 때 한 번만 기여, 2.1/4.0·with/without tools·effort·스캐폴드 분리, `verified=false` 처리, 원출처 누락 거부, sparse 코호트 제외, source 실패 시 last-good 유지. 기존 `test_p1.py`를 중심으로 추가하고 전체 `unittest`를 실행한다.

**활성화 기준:** 벤치마크별 평가 조건이 기계적으로 확인되고, 현재 사용 가능한 프로필 중 비교 가능한 모델이 최소 둘 이상 있어야 한다. 라우팅 가중치는 실제 프로필의 커버리지와 선택 결과를 기존 정책과 비교한 뒤 한 번에 조정한다.
