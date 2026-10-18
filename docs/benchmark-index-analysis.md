# 벤치마크 데이터 구조와 관련성 인덱스 설계 분석

조사일: 2026-10-17. 상태: 공개 데이터 응답·파일을 확인한 설계 분석. 아래 스키마와 검색 절차는 제안이며 현재 라우터의 동작을 뜻하지 않는다.

## 1. 조사 범위와 결론

현재 코드가 지원하는 evidence 9개(AA 2, Arena 5, SWE/TB 수동 import 2), 기존 수집 설계의 The Model Gap 14개 항목, 추가 HF 후보 6개를 대상으로 데이터 형태를 조사했다. HF 공식 벤치마크 목록 49개를 발견했지만 49개 전체의 내용을 분석한 것은 아니다. 과제 데이터는 대표 레코드·설정 파일·스키마를 확인했으며, 모든 과제를 의미적으로 검토한 것은 아니다.

관측한 필드·타입·일부 응답 해시·HF revision은 [구조 조사 기록](evidence/benchmark-index-schema-2026-10-17.json)에 보관했다. 인증이 필요한 AA 실응답은 호출하지 않았으며 공개 OpenAPI를 사용했다. DeepSWE/HLE/GPQA의 제한된 과제 본문은 내려받지 않았다. Dataset Viewer의 행·통계와 HF 저장소 revision은 각각 조회한 값이며 하나의 원자적 스냅샷은 아니다.

**권장 형태는 소스의 분류를 보존한 다중 속성 인덱스다. 검색 결과는 점수를 독립적으로 식별할 수 있는 평가 단위에 연결한다.** 과제 설명은 관련성의 근거로 연결하고, 모델별 점수는 별도 관측 테이블에서 조회한다. Decision Tree는 이 인덱스에서 생성하는 탐색 안내로 사용할 수 있다.

근거는 다음과 같다.

- Arena에는 이미 범주별 점수가 있고, Terminal/ALE/ExtractBench 등에는 구조화된 과제 메타데이터가 있다. 모든 범주를 새로 만들 필요가 없다.
- 같은 데이터 안에서도 언어·행동·도메인·입력 형식이 교차한다. 단일 상하 관계로 표현하면 중복이나 누락이 생긴다.
- 과제의 세부 분류와 공개된 점수의 세부 단위는 다르다. 세밀하게 검색됐다고 그 능력만의 점수가 생기지는 않는다.
- HF의 리더보드 API, 평가 정의, 제출 결과 파일은 서로 다른 정보를 제공한다. API의 대표 점수만 수집하면 실제로 공개된 하위 점수를 놓칠 수 있다.

## 2. 현재 수집 데이터의 실제 구조

### 2.1 Artificial Analysis: 모델별 집계 지수 JSON

현재 어댑터는 `aa_intelligence`, `aa_coding`만 읽는다. 공개 OpenAPI의 Free 응답 구조는 다음과 같다.

```text
tier, intelligence_index_version, pagination, data[]
data[]: id, name, slug, release_date, model_creator,
        evaluations, pricing, performance, ...
evaluations: artificial_analysis_intelligence_index,
             artificial_analysis_coding_index,
             artificial_analysis_agentic_index,
             여러 분야별 capability index
```

Free 스키마에는 개별 과제 레코드가 없다. Pro용 `Evaluations` 스키마에는 `terminalbench_v4_0`, `scicode`, `hle` 등의 개별 평가 필드가 있지만, 실제 계정의 가용 값은 확인하지 않았다. `null`은 미측정 또는 비적용이며 0점이 아니다. API의 `intelligence_index_version`은 patch 버전까지 표현하지 않으므로 방법론 revision도 별도로 기록할 필요가 있다. [API 문서](https://artificialanalysis.ai/data-api/docs), [OpenAPI](https://artificialanalysis.ai/api/v2/openapi)

**활용:** AA 종합 지수는 `aggregate` 평가 단위로 등록한다. 구성 평가 목록은 `contains` 관계로 기록할 수 있지만, 종합 지수에서 개별 평가 점수를 역산하거나 같은 점수를 복제하지 않는다. 개별 값이 확보되면 별도 평가 단위로 연결한다.

### 2.2 Arena: 범주·모델·발행일별 점수 Parquet

`lmarena-ai/leaderboard-dataset`은 여러 config의 `latest`/`full` Parquet로 구성된다. 현재 사용하는 config의 행은 다음 필드를 가진다.

```text
model_name, organization, license,
rating, rating_lower, rating_upper, variance, vote_count,
rank, category, leaderboard_publish_date
```

`full`은 과제 원문 전체가 아니라 과거 리더보드 스냅샷이다. 이 데이터의 행 수는 과제 수가 아니다. 별도의 Agent config에는 `rating` 대신 `score`, `score_ci_lower`, `score_ci_upper`, `observation_count`, `session_count` 등이 있다. 같은 제공자의 모든 config를 같은 점수 스키마로 처리할 수는 없다. [데이터 카드](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset)

Dataset Viewer의 `category` 통계에서 확인한 현재 사용 config의 분류는 다음과 같다.

| config | 범주 수 | 실제 범주 예 | 인덱스에 사용할 단위 |
| --- | ---: | --- | --- |
| `text_style_control` | 29 | `coding`, `math`, `creative_writing`, `instruction_following`, `korean`, 산업별 범주 | config + category별 점수 |
| `webdev` | 5 | `overall`, `webdev`, `webdev-react`, `webdev-html`, `image_to_webdev` | 웹 작업 종류별 점수 |
| `vision_style_control` | 11 | `ocr`, `diagram`, `captioning`, `homework`, `entity_recognition`, `overall` 등 | 시각 과제 범주별 점수 |
| `document_style_control` | 1 | `overall` | 문서 종합 점수 |

범주 수는 조사 응답 기준이다. 원문과 범주별 모델 행 수는 [구조 조사 기록의 arena_categories](evidence/benchmark-index-schema-2026-10-17.json)에 있다. [텍스트 통계](https://datasets-server.huggingface.co/statistics?dataset=lmarena-ai%2Fleaderboard-dataset&config=text_style_control&split=latest), [웹 통계](https://datasets-server.huggingface.co/statistics?dataset=lmarena-ai%2Fleaderboard-dataset&config=webdev&split=latest), [비전 통계](https://datasets-server.huggingface.co/statistics?dataset=lmarena-ai%2Fleaderboard-dataset&config=vision_style_control&split=latest), [문서 통계](https://datasets-server.huggingface.co/statistics?dataset=lmarena-ai%2Fleaderboard-dataset&config=document_style_control&split=latest)

**활용:** 새로 과제 원문을 분류하기 전에 공개 범주를 직접 연결한다. 예를 들어 한국어 응답에는 `korean`, 창작에는 `creative_writing`, React 화면에는 `webdev-react`를 관련 근거로 탐색할 수 있다. 각 연결은 적용 가설이며 이름 일치만으로 충분한 적합성을 보장하지 않는다. 문서의 `overall`을 OCR·표 추출 전용 점수로 분해할 수는 없다.

현재 코드는 이 범주 중 `overall` 네 종류와 텍스트 `math`만 수집한다. 또한 원본의 신뢰구간·투표 수를 파싱된 observation에 보존하지 않는다. 새 인덱스에서 범주를 늘리려면 수집 범위와 observation 필드도 확장해야 한다. [현재 코드](../bench_router/data.py)

### 2.3 현재 SWE/TB import: 평가 조건 + 프로필별 점수 JSON

현재 import는 `benchmark`에 suite/version/subset/metric/variant/revision/평가 하네스/aggregation을 담고, `rows[]`에 `model_id`, `harness_id`, `reasoning_effort`, `raw`를 담는다. 개별 과제 설명이나 결과는 없다. SWE는 Verified, TB는 4.0으로 고정돼 있다. [검증·파싱 코드](../bench_router/data.py)

**활용:** 프로필과 점수의 연결 및 비교 조건에 사용한다. 관련성 인덱스를 만들 과제 내용은 아래의 원 데이터셋과 결합해야 한다.

## 3. 수집 후보와 원 과제 데이터

### 3.1 The Model Gap: 설명 카탈로그와 점수 표가 이미 분리됨

직접 받은 JSON은 `benchmarks.json` 14행, `scores.json` 351행이었다. 웹 안내 페이지의 건수나 기존 설계 문서의 건수와 다르므로 실제 응답을 기준으로 기록했다.

```text
benchmarks[]:
  id, name, category, skill, measures, task_shape,
  variants, source_url, sources, related_benchmarks,
  n_items, lifecycle, trust_grade, meaningful_gap, notes, ...

scores[]:
  model_id, benchmark_id, variant, value,
  source_url, source_type, harness, date_observed, notes,
  effort?  // 이번 응답 351행 중 202행에 값 있음
```

14개 항목 모두 `measures`, `task_shape`, `category`, `skill`을 제공했다. 이 값은 카탈로그 검색의 좋은 출발점이다. 다만 이 제공자의 요약·신뢰등급·상태 판정을 원 벤치마크의 공식 분류와 구분해야 한다. `harness`는 이번 응답의 모든 점수에 있었지만 `artificial-analysis`, `vals-ai` 같은 평가기관도 값으로 쓰이므로 Agent 스캐폴드로 간주하면 안 된다. `date_observed`도 평가 실행일과 구분한다. [실제 메타데이터](https://themodelgap.com/data/benchmarks.json), [실제 점수](https://themodelgap.com/data/scores.json)

아래는 14개 항목과 추가 HF 후보 6개의 조사 결과다. '확인'은 해당 구조를 확인했다는 뜻이며 전체 과제·점수의 완전 검증을 뜻하지 않는다.

| 항목 | 원 데이터의 형태·확인 필드 | 인덱스에 유리한 정보 / 한계 |
| --- | --- | --- |
| [SWE-bench Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) | Parquet, test 500행. `instance_id`, `repo`, `problem_statement`, `difficulty`, commit, patch/test 관련 필드 | 저장소·이슈 설명으로 관련성 검색. patch/정답을 검색 요약에 넣을 필요 없음. 현재 import는 전체 평가 점수 |
| [SWE-bench Pro](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro) | Parquet. 조사 시 default 642행, 별도 hard/v1 config. `repo_language`, `issue_categories`, `requirements`, `interface` 추가 | 원 분류·언어·요구사항 활용. 일부 필드는 JSON처럼 보이는 문자열이므로 타입을 확인해 파싱 |
| [Terminal-Bench 4.0](https://huggingface.co/datasets/harborframework/terminal-bench/blob/main/registry.json) | `registry.json`에 4.0.0·66개 과제 경로. 각 과제의 `task.toml`, `instruction.md`, 환경·검증 파일 | TOML의 category/subcategory/tags, 과제 지시문 활용. 표본에서 description이 빈 값인 경우도 있음 |
| [Terminal-Bench 2.1](https://huggingface.co/datasets/harborframework/terminal-bench-2.1) | 89개 과제의 Harbor 디렉터리. 표본 TOML에 category/tags/difficulty와 task keywords | 4.0과 분리. 버전 간 분류 어휘·시간 추정 단위가 달라 원값과 버전을 보존 |
| [DeepSWE](https://huggingface.co/datasets/datacurve/deep-swe) | HF 파일 목록에 Parquet와 과제별 TOML·지시문·manifest가 있으나 gated | 파일 구조는 확인. 본문 필드는 미확인이라 공개 설명 수준으로만 검색 등록 |
| [Toolathlon Verified](https://github.com/hkust-nlp/Toolathlon/blob/main/tasks/finalpool/academic-pdf-report/task_config.json) | 공개 GitHub의 과제별 `task_config.json`, `docs/task.md`. 표본 config에 `needed_mcp_servers`, `needed_local_tools` | 도구·서비스 조합이 명시적. `meta`는 표본에서 비어 있어 여기에 도메인 분류가 있다고 가정하면 안 됨 |
| [Agents' Last Exam](https://huggingface.co/datasets/agents-last-exam/agents-last-exam) | `task_cards.parquet`, `default/v1_1` 150행. title/summary/category/subdomain/task_split/task_prompt/agent_must_do/software/input_files/taxonomy | 작업·도메인·앱·파일 형식의 구조화 수준이 높음. 입력 파일·참조 출력·환경은 별도 배포 |
| [HLE](https://huggingface.co/datasets/cais/hle) | HF 카드에 question/image/answer_type/raw_subject/category 등의 스키마. 본문 gated | subject/category를 활용할 수 있으나 실제 본문 분석은 미실시. 도구 허용 변형을 분리 |
| [GPQA Diamond](https://huggingface.co/datasets/Idavidrein/gpqa) | HF 원 데이터 gated. 이번 조사에서는 과제 본문·정확한 열 미확인 | TMG 설명 수준으로만 등록. 원 데이터 분류를 확보한 것처럼 표현하지 않음 |
| [LiveCodeBench](https://huggingface.co/datasets/livecodebench/code_generation_lite) | JSONL 표본에 question_content/platform/contest_id/contest_date/difficulty/starter_code/test_cases/metadata | 알고리즘·대회 문제와 날짜 조건 검색에 적합. 저장소 수정 작업과 구분. metadata는 표본에서 문자열 |
| [ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2/blob/main/data/evaluation/0934a4d8.json) | 과제별 JSON의 `train[]`, `test[]` 안에 input/output 정수 격자 | 자연어 설명·도메인 분류가 원래 없음. 격자 변환 능력 수준으로 등록하고 세부 의미는 별도 분석 필요 |
| [LiveBench](https://huggingface.co/datasets/livebench/math) | 분야별 HF 저장소. math 표본에 category/task/subtask/turns/release·removal date/ground_truth | 원 task/subtask와 평가 배포판을 활용. TMG의 Overall 점수에서 분야별 점수를 만들어낼 수 없음 |
| [HMMT Feb 2026](https://huggingface.co/datasets/MathArena/hmmt_feb_2026) | Parquet 스키마에 problem_idx/problem_type/problem/answer | 원 problem_type 활용 가능. 문항 분류가 곧 모델별 해당 영역 점수는 아님 |
| [AA Analyst Agent](https://themodelgap.com/benchmarks/aa-analyst-agent) | TMG의 작업 설명·집계 점수 확인. 이번 조사에서 개별 과제 원본은 미확인 | 스프레드시트·문서 기반 분석이라는 공개 설명으로 등록. 과제별 검색 가능하다고 가정하지 않음 |
| [OSWorld 2.0 계열](https://github.com/xlang-ai/OSWorld-V2/blob/main/evaluation_examples/examples/chrome/030eeff7-b492-4218-b312-701ec99ee0cc.json) | 공식 V2 저장소의 앱별 JSON 표본에 instruction/snapshot/related_apps/config/evaluator | 앱·환경·작업 지시를 활용. release manifest와 full/offline·개정 변형을 함께 식별 |
| [MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro) | Parquet 스키마에 category/question/options/answer/src | 학문 분야 검색에 활용. 분야별 문항은 존재하지만 표본 eval.yaml은 종합 task만 선언 |
| [AIME 2026](https://huggingface.co/datasets/MathArena/aime_2026) | Parquet 스키마에 problem_idx/problem/answer | 기본 분류가 빈약. 수학 대회 평가로 등록하고 세부 주제 분류는 필요할 때 추가 |
| [MMMU-Pro](https://huggingface.co/datasets/MMMU/MMMU_Pro) | standard 4/10 options와 vision config. subject/question/images/img_type/topic_difficulty | 원 subject·입력 형태 활용. config별 평가 점수를 구분 |
| [ExtractBench](https://huggingface.co/datasets/llamaindex/ExtractBench) | short/medium/long JSONL. id/category/pdf/data_schema/field_rules/repeated_structure/tags/expected_output | 태그에 challenge/delivery/length/domain 축이 이미 있음. 문서+스키마 기반 추출과 페이지 해석을 구분 |
| [ParseBench](https://huggingface.co/datasets/llamaindex/ParseBench) | table/chart/text_content/text_formatting/layout JSONL. pdf/category/id/type/rule/page/tags 등 | 한 행은 문서 전체가 아니라 검사 규칙. 문서·페이지·규칙 관계를 유지하고 평가 차원별 점수에 연결 |


### 3.2 HF: 평가 정의·리더보드·제출 결과를 연결해야 함

HF에는 역할이 다른 데이터가 있다.

| 데이터 | 실제 구조 | 용도 |
| --- | --- | --- |
| `/api/datasets?filter=benchmark:official` | dataset ID·tags·revision 등의 배열 | 데이터셋 발견. 과제나 점수 자체가 아님 |
| 데이터셋의 `eval.yaml` | name/description/evaluation_framework/tasks[]. tasks에는 id/config/split | 독립된 평가 항목 식별 |
| `/api/datasets/{id}/leaderboard` | rank/modelId/value/verified/source/filename/notes/pullRequest 등 | 모델별 결과 발견 및 원 결과 참조 |
| 모델 등의 `.eval_results/*.yaml` | 복수 결과. 표본에서는 dataset.id/dataset.task_id/value/date/source/notes | 대표값에서 빠진 하위 점수와 조건 복원 |

위 표는 실제 HTTP 응답 필드명이며 Python SDK의 `model_id` 등과 표기가 다르다. 이번에 조회한 5개 leaderboard 응답의 행에는 `task_id`를 직접 나타내는 필드가 없었다. 평가 정의와 제출 결과를 함께 읽어야 한다. [공식 접근 방법](https://huggingface.co/docs/hub/leaderboard-data-guide)

ParseBench의 실제 제출 YAML에서는 `mean`, `table`, `layout`, `text_content`, `text_formatting`, `chart`의 6개 값을 확인했다. 특정 파이프라인의 평가 결과이므로 임의의 CLI Agent나 기반 LLM의 결과를 뜻하지 않는다. 표 추출 요청에 `table`을 참조할 수 있지만 그 파이프라인이 위임 대상과 일치하는지는 따로 확인해야 한다. [제출 원본](https://huggingface.co/KDLAI/KDL-Frontier-Parser-nano/blob/main/.eval_results/parsebench.yaml)

`eval.yaml`에 하위 항목이 선언돼 있는 것과 모든 후보 모델에 해당 점수가 있는 것도 다르다. `verified=false` 결과는 검증된 결과로 바꾸지 않는다.

## 4. 데이터에 맞춘 인덱스 모델

### 4.1 최소 관계 구조

아래는 새 검색 계약의 제안이다. 기존 SQLite나 작은 JSON 카탈로그로 표현할 수 있으며 그래프 DB를 도입할 필요는 없다.

```text
benchmark_release
  suite, version, dataset_revision, source_refs
    ├─ evaluation
    │    evaluation_id, source_task_id, config, split,
    │    category, metric, unit, direction, aggregation
    │      └─ observation
    │           evaluated_system, cohort, value,
    │           uncertainty, provenance, freshness
    └─ case
         case_id, source_labels, description_ref, environment
           └─ supports_relevance → evaluation

facet → evaluation / case
```

- `evaluation_id`는 점수가 무엇을 의미하는지 식별하는 항목이다. `case_id`는 개별 문제·업무·문서를 식별한다. 둘을 같은 `task_id`로 취급하지 않는다.
- `supports_relevance`는 관련성을 설명하는 관계이며 점수 집계 관계와 구분한다. 공개 점수에 어떤 과제가 포함되는지 불명확하면 미확인으로 남긴다.
- 점수를 아직 확보하지 못해도 평가 항목을 등록할 수 있다. 내용의 관련성과 데이터 가용성을 따로 반환한다.
- 점수는 평가 조건별로 보관한다. 환경·도구 허용·scaffold·effort·채점법·반복 수·revision 등이 불명확하면 알려진 조건과 같다고 가정하지 않는다.
- 기반 모델, CLI Agent, 문서 분석 파이프라인을 `evaluated_system`에서 구분하고 프로필과 일치하는 범위를 명시한다.

### 4.2 다중 속성과 원 분류 보존

처음 공통화할 축은 원 데이터에 실제로 존재하는 작은 범위로 잡는다.

| 축 | 소스의 근거 예 |
| --- | --- |
| 작업·산출물 | SWE의 issue/requirements, ALE의 agent_must_do, Parse/Extract의 평가 정의 |
| 입력 형식 | ALE의 input_files.format, MMMU config, Extract의 pdf/schema |
| 환경·도구 | Toolathlon의 needed_mcp_servers, ALE의 software, OSWorld의 related_apps |
| 분야·언어 | MMLU/HLE의 분야, Pro의 repo_language, Arena의 언어별 category |
| 문서 특성 | Extract의 length/challenge/delivery/domain 태그 |

원 분류는 `source_namespace + source_revision + field + value`로 보존하고, 공통 속성과의 대응에 근거와 mapping 버전을 붙인다. 예를 들어 Extract의 `domain:D1`은 공식 대응표를 확인하기 전 구체적인 업종명으로 바꾸지 않는다. 없는 속성은 unknown이며 비지원이나 부적합을 뜻하지 않는다.

정규화한 작업 용어에는 설계 판단이 들어간다. 임의의 수치 신뢰도를 붙이기보다 출처·대응 규칙·적용 예·반례를 남긴다. 언어나 분야 하나만 일치한다고 주요 평가로 제시하지 않고, 어떤 행동과 성과를 평가하는지 확인한다.

### 4.3 검색과 반환

1. Orchestrator가 이미 이해한 작업·입력·환경을 작은 구조로 전달한다. 새 분류 모델 호출은 필수로 두지 않는다.
2. 속성에서 평가 후보를 검색한다. 복합 작업은 필요한 행동별로 검색해 해당 평가를 합친다.
3. 원문·검사 규칙의 참조로 적용 범위를 확인한다. 원 분류가 부족하면 짧은 설명의 어휘 검색을 보조로 쓴다.
4. 대상 프로필에 대응하는 관측을 연결한다. 하위 점수가 없으면 전체 점수임을 명시한다.
5. `evaluation_id`, 매칭 속성, 관련성 근거, 점수 범위, 프로필별 관측, missing/unknown과 상세 참조를 반환한다.

첫 검색은 작은 카탈로그의 집합 연산이나 SQLite 일반 인덱스로 구성할 수 있다. 수만 과제의 본문 검색이 필요해지면 SQLite FTS5 등을 검토한다. 한국어 요청과 영어 원 분류의 대응은 다국어 alias 또는 Orchestrator의 구조화 입력으로 보완한다. 임베딩·LLM 재판정의 필요성은 검색 누락을 측정한 뒤 판단한다.

Decision Tree를 사용한다면 복수 분기를 탐색할 수 있게 한다. 예를 들어 PDF 처리, 구조화 값 추출, 기존 코드 수정은 각각 탐색할 수 있어야 한다. 말단은 고정 벤치마크 목록 대신 속성 검색을 참조한다. 이 방식으로 별도의 분류 계층과 원 인덱스를 중복 관리하는 비용을 줄일 수 있다.

## 5. 예시와 자원 사용

### PDF의 표를 JSON으로 변환하는 요청

- 관련 후보: ExtractBench의 스키마 추출, ParseBench의 table, 필요하면 Arena 문서 overall.
- 적용 범위: 문서 전체의 구조화 추출과 페이지의 표 구조 해석은 평가 대상이 다르다. ParseBench table 점수를 긴 문서 전체의 JSON 추출 능력으로 확대하지 않는다.
- 조회 단위: 제출 결과에 table/long 등이 있으면 그 값을 사용한다. mean만 있으면 mean으로 제시하고, 정의만 있고 점수가 없으면 missing이다.
- 대상 일치: 문서 처리 파이프라인의 점수를 같은 기반 모델을 사용하는 다른 Agent의 실적으로 옮기지 않는다.

### 한국어로 기존 Python 코드 수정을 요청

- 주요 검색 근거는 기존 저장소를 수정하는 행동이다. SWE 계열의 내용과 조건을 확인한다.
- 요청 언어 하나로 Arena `korean`을 주요 코드 수정 평가로 삼지 않는다. 한국어 문장 품질 자체가 요구되면 별도 보조 관측으로 볼 수 있다.
- 터미널을 도구로 쓴다는 사실만으로 모든 수정 요청에 Terminal 전체 점수를 필수로 붙이지 않는다.

### 갱신과 캐시

원 과제 분석과 alias/mapping 작성은 등록·갱신 때 수행한다. 빈번한 요청에서는 짧은 구조화 입력의 검색과 로컬 관측 연결을 처리한다. 분류를 위한 추가 LLM 호출을 0회로 설계할 수 있지만 구조화 입력 생성과 반환 결과를 읽는 토큰은 남는다.

관련 평가 목록의 캐시 키는 정규화한 작업 특성 + catalog/mapping 버전으로 둔다. 관측을 포함한 결과 캐시는 score snapshot·프로필 지문도 포함하고, 최신성과 적용 조건을 재확인한다. 카탈로그가 작아 검색 비용이 충분히 낮으면 캐시는 나중에 추가해도 된다. 구체적인 밀리초·토큰 절감률은 아직 측정하지 않았다.

## 6. 구현에 들어갈 경우 우선순위

1. **기존 점수 구조 활용:** Arena category별 평가를 등록하고 신뢰구간·투표 수를 보존한다. HF eval.yaml과 제출 결과에서 하위 항목을 가져온다.
2. **분류가 풍부한 과제 연결:** Terminal TOML, ALE task cards, Toolathlon 도구 설정, Extract/Parse 태그를 연결한다. 전체 문제를 LLM으로 재분류하는 일부터 시작할 필요는 없다.
3. **메타데이터만 있는 항목 표시:** TMG 설명을 검색에 활용하고, 미확인·gated·집계 점수만 있는 항목은 그 상태를 반환한다.
4. **실제 요청으로 검색 품질 측정:** 관련 평가 누락, 불필요한 포함, 근거 없는 하위 점수 해석, 관측 가용률, 반환 토큰 수, 검색 p50/p95를 기록한다. 현행 9개 분류나 설명 전체를 전달하는 방법과 비교해 효과를 확인한다.

이 순서라면 실제로 공개된 분류와 점수 단위에 맞춰 인덱스를 구체화할 수 있다.
