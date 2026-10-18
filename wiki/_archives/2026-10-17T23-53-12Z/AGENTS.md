# Benchmark Wiki — vault 스키마

벤치마크 지식(정의, 출처, 버전 이력, 상태)을 담은 obsidian-wiki `llm-wiki` vault다. 라우터는 이 Wiki를 요청마다 탐색하지 않는다. refresh 때 `## Index` 블록만 `index.json`으로 컴파일하고, 요청 시에는 facet 역색인을 조회한다.

## 페이지 종류

| 경로 | 내용 | `## Index` 블록 |
|---|---|---|
| `concepts/facets/<axis>.md` | 축 하나의 허용 값(어휘)과 판정 방법 | `[[facet]]` 목록 |
| `entities/benchmarks/*.md`, `entities/benchmarks/{mg,hf}/*.md` | 벤치마크 하나와 그 순위표 조각(단위) | `[[unit]]` 목록 |
| `references/sources/*.md` | 정의를 인용한 공개 출처 | 없음 |

허용 axis: `task`, `lang`, `domain`, `difficulty`, `shape`, `agent_signal`.

## `## Index` 계약

본문의 `## Index` 섹션에 ```toml 블록 하나를 둔다. frontmatter가 아니라 본문에 두는 이유는 저장소가 표준 라이브러리만 쓰고(`tomllib`), frontmatter는 obsidian-wiki 규약을 그대로 따르기 때문이다.

`[[facet]]`: `id`, `desc`, `detect`(`rule:<규칙>` = 라우터가 결정적으로 판정, `self` = Orchestrator가 task JSON `facets`에 직접 태그), `evidence`(`official` | `dataset` | `name_only`), 선택 `arena_rule`(LMArena의 원 태깅 기준).

`[[unit]]`: `id`, `desc`, `metric`(`elo` | `ips` | `pass_pct` | `index`), `status`(`current` | `saturated` | `contaminated`), `adoption`, `facets`(`{axis = [값, ...]}`), 선택 `reason`(adoption 근거), `evidence`, `meaningful_gap`, `trust_grade`.

- `adoption`: `active`(역색인에 들어감) | `candidate`(수집·커버리지 확인 후 active로 올림) | `archive`(포화·대체, 조회용) | `excluded`(위임 대상이 아닌 작업, 사유만 남김). 역색인에는 `active`만 들어간다. 페이지 `lifecycle`(리뷰 상태)과는 별개다.
- `excluded` unit은 `facets = {}`일 수 있다. 나머지는 facet이 하나 이상 있어야 한다.
- unit id 형식: `arena:<config>/<category>`(HF `lmarena-ai/leaderboard-dataset`), `arena-web:<board>/<signal>`(arena.ai 웹 순위표에만 있음), `mg:<benchmark_id>/<variant>`(The Model Gap), `hf:<owner>/<dataset>`(HF 공식 벤치마크), 또는 `bench_router/data.py`의 `EVIDENCE_IDS`.
- 같은 논리 벤치마크는 페이지 하나에만 unit으로 둔다. 다른 수집처의 미러(예: HF의 `cais/hle`)는 그 페이지의 출처로만 붙인다.
- facet과 unit의 연결은 **unit 쪽에서만** 적는다. facet 페이지에 unit 목록을 적지 않는다. 역색인은 컴파일러가 만든다.
- `facets`의 값은 해당 axis 페이지에 정의된 `id`여야 한다.

## 리뷰 게이트

- frontmatter `lifecycle`이 `reviewed` 또는 `verified`인 페이지만 컴파일한다. 새 페이지는 항상 `draft`로 쓰고, 사람이 리뷰한 뒤 바꾼다.
- 벤치마크 자체의 포화·오염은 `lifecycle`이 아니라 unit `status`로 적는다.
- 공개 페이지에서 정의를 확인하지 못한 항목은 unit으로 등록하지 않거나 `evidence = "name_only"`로 표시하고, 페이지의 `## Open Questions`에 남긴다.

## 참고

- 데이터 구조 조사: `docs/benchmark-index-analysis.md`, `docs/evidence/benchmark-index-schema-2026-10-17.json`
- `index.md`·`log.md`·`.manifest.json`은 obsidian-wiki CLI가 관리한다. 컴파일러는 읽지 않는다.
