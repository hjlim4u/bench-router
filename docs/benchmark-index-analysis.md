# Benchmark Data Structures and Relevance Index Design Analysis

Research date: 2026-10-17. The schemas, external figures, and retrieval procedures below reflect **the design analysis and proposal records as of that date**. External data sources were not re-queried during this update.

Implementation cross-check (2026-10-24): Compiling reviewed wiki pages in `wiki.py`, facet retrieval, observation/missing data condition tables in `evidence.py`, and active wiki unit-based collection across AA, Arena, and The Model Gap are now implemented. The system has expanded beyond the initial 9 evidence items; the active schema follows [wiki/AGENTS.md](../wiki/AGENTS.md). Model selection retrieval under Policy 6 does not apply the 12-unit table display limit, supplying comparable observations and relevance to upstream selection. Not all relational models and candidate collection proposals below are implemented. Current behavior resides in [Data Specification](../03_ROUTING_AND_DATA_SPEC.md) and [Vendor-guided Routing Policy](vendor-guided-routing.md).

## 1. Scope and Conclusions

Investigated data structures across the 9 evidence items supported by the initial codebase (AA 2, Arena 5, manual SWE/TB import 2), 14 The Model Gap catalog entries from earlier collection designs, and 6 candidate HF benchmarks. Although 49 official HF benchmarks were identified, not all 49 were analyzed in depth. Task data was examined via representative records, configuration files, and schemas; not all task instances were semantically reviewed.

Observed fields, types, representative response hashes, and HF revisions are recorded in the [Structure Investigation Log](evidence/benchmark-index-schema-2026-10-17.json). Authenticated AA live endpoints were not invoked; public OpenAPI specifications were referenced. Restricted task bodies for DeepSWE, HLE, and GPQA were not downloaded. Dataset Viewer rows/statistics and HF repository revisions were queried separately and do not constitute an atomic snapshot.

**The recommended model is a multi-attribute index preserving native source taxonomies. Retrieval results connect directly to evaluation units where scores can be independently identified.** Task descriptions connect as relevance evidence, while model scores are retrieved from separate observation tables. Decision trees can serve as navigational guides compiled from this index.

The rationale is as follows:

- Arena already publishes category-specific scores, and Terminal, ALE, and ExtractBench provide structured task metadata. There is no need to invent taxonomies from scratch.
- Languages, actions, domains, and input formats intersect within the same dataset. Forcing single hierarchical structures causes duplication or omissions.
- Granular task classifications differ from published score granularities. Fine-grained task retrieval does not automatically yield fine-grained capability scores.
- HF leaderboard APIs, evaluation definitions, and submission result files provide divergent information. Ingesting only representative API scores risks missing published sub-scores.

## 2. Actual Structures of Ingested Data

### 2.1 Artificial Analysis: Per-Model Aggregate Index JSON

The current adapter reads `aa_intelligence` and `aa_coding`. The public OpenAPI Free tier response structure is:

```text
tier, intelligence_index_version, pagination, data[]
data[]: id, name, slug, release_date, model_creator,
        evaluations, pricing, performance, ...
evaluations: artificial_analysis_intelligence_index,
             artificial_analysis_coding_index,
             artificial_analysis_agentic_index,
             several domain-specific capability indices
```

The Free schema contains no individual task records. The Pro `Evaluations` schema includes individual fields such as `terminalbench_v4_0`, `scicode`, and `hle`, but concrete values were not verified in active accounts. `null` signifies unmeasured or not applicable, not a score of zero. The API's `intelligence_index_version` does not specify patch versions, necessitating independent tracking of methodology revisions. [API Documentation](https://artificialanalysis.ai/data-api/docs), [OpenAPI](https://artificialanalysis.ai/api/v2/openapi)

**Application:** AA composite indices are registered as `aggregate` evaluation units. Constituent evaluations can be recorded via `contains` relationships, but individual scores must never be back-calculated or duplicated from aggregate indices. When individual metrics are secured, they connect as distinct evaluation units.

### 2.2 Arena: Scores Parquet by Category, Model, and Date

`lmarena-ai/leaderboard-dataset` consists of `latest`/`full` Parquet files across multiple configs. Rows in the active configs contain:

```text
model_name, organization, license,
rating, rating_lower, rating_upper, variance, vote_count,
rank, category, leaderboard_publish_date
```

`full` contains historical leaderboard snapshots rather than raw task texts. Row counts do not equal task counts. Separate Agent configs feature `score`, `score_ci_lower`, `score_ci_upper`, `observation_count`, and `session_count` instead of `rating`. Not all configs from the same provider can share a single score schema. [Dataset Card](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset)

Classifications in the active configs verified via Dataset Viewer `category` statistics:

| config | Category Count | Category Examples | Target Unit in Index |
| --- | ---: | --- | --- |
| `text_style_control` | 29 | `coding`, `math`, `creative_writing`, `instruction_following`, `korean`, industry categories | Scores per config + category |
| `webdev` | 5 | `overall`, `webdev`, `webdev-react`, `webdev-html`, `image_to_webdev` | Scores by web task type |
| `vision_style_control` | 11 | `ocr`, `diagram`, `captioning`, `homework`, `entity_recognition`, `overall`, etc. | Scores by visual task category |
| `document_style_control` | 1 | `overall` | Document composite score |

Category counts reflect the investigation response. Raw text and row counts per model are recorded in `arena_categories` within the [Structure Investigation Log](evidence/benchmark-index-schema-2026-10-17.json). [Text Stats](https://datasets-server.huggingface.co/statistics?dataset=lmarena-ai%2Fleaderboard-dataset&config=text_style_control&split=latest), [Web Stats](https://datasets-server.huggingface.co/statistics?dataset=lmarena-ai%2Fleaderboard-dataset&config=webdev&split=latest), [Vision Stats](https://datasets-server.huggingface.co/statistics?dataset=lmarena-ai%2Fleaderboard-dataset&config=vision_style_control&split=latest), [Document Stats](https://datasets-server.huggingface.co/statistics?dataset=lmarena-ai%2Fleaderboard-dataset&config=document_style_control&split=latest)

**Application:** Connect published categories directly before classifying raw tasks. For example, Korean responses link to `korean`, creative writing to `creative_writing`, and React interfaces to `webdev-react` as relevant evidence. Each link serves as an applicability hypothesis; name alignment alone does not guarantee sufficient suitability. Document `overall` cannot be subdivided into OCR or table-extraction scores.

The initial codebase collected four `overall` variants and text `math` from these categories, omitting confidence intervals and vote counts in parsed observations. Expanding categories in the new index requires extending ingestion ranges and observation schemas. [Current Code](../bench_router/data.py)

### 2.3 SWE/TB Ingestion: Evaluation Conditions + Profile Scores JSON

Existing ingestion records suite, version, subset, metric, variant, revision, evaluation harness, and aggregation in `benchmark`, with `model_id`, `harness_id`, `reasoning_effort`, and `raw` in `rows[]`. Individual task descriptions or results are absent. SWE is pinned to Verified, TB to 4.0. [Validation & Parsing Code](../bench_router/data.py)

**Application:** Used for mapping profiles to scores and comparison conditions. Task content for building the relevance index must combine with the raw datasets below.

## 3. Ingestion Candidates and Raw Task Data

### 3.1 The Model Gap: Decoupled Catalog and Score Tables

Direct JSON downloads contained 14 rows in `benchmarks.json` and 351 rows in `scores.json`. Recorded based on actual HTTP responses rather than website counts or historical design docs:

```text
benchmarks[]:
  id, name, category, skill, measures, task_shape,
  variants, source_url, sources, related_benchmarks,
  n_items, lifecycle, trust_grade, meaningful_gap, notes, ...

scores[]:
  model_id, benchmark_id, variant, value,
  source_url, source_type, harness, date_observed, notes,
  effort?  // populated in 202 of 351 rows in this response
```

All 14 benchmarks supplied `measures`, `task_shape`, `category`, and `skill`, providing a strong starting point for catalog search. However, provider summaries, trust grades, and lifecycle states must be separated from official benchmark classifications. While `harness` was present for all scores in this response, evaluation organizations such as `artificial-analysis` and `vals-ai` were also used as values, so it must not be treated strictly as an Agent scaffold. `date_observed` must also be distinguished from evaluation execution dates. [Metadata](https://themodelgap.com/data/benchmarks.json), [Scores](https://themodelgap.com/data/scores.json)

Investigation results across 14 items and 6 candidate HF benchmarks ('Verified' denotes structure confirmation, not complete validation of all tasks or scores):

| Benchmark | Raw Format & Verified Fields | Advantages for Index / Limitations |
| --- | --- | --- |
| [SWE-bench Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) | Parquet, test 500 rows. `instance_id`, `repo`, `problem_statement`, `difficulty`, commits, patch/test fields | Retrieve relevance via repo and issue descriptions. No need to index patches or solutions. Current ingestion covers holistic evaluation scores |
| [SWE-bench Pro](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro) | Parquet: default 642 rows, separate hard/v1 configs. Adds `repo_language`, `issue_categories`, `requirements`, `interface` | Leverage native categories, languages, and requirements. Some fields are serialized JSON strings requiring type-checked parsing |
| [Terminal-Bench 4.0](https://huggingface.co/datasets/harborframework/terminal-bench/blob/main/registry.json) | `registry.json` contains 4.0.0, 66 task paths. Each task contains `task.toml`, `instruction.md`, environment and validation files | Leverage TOML category/subcategory/tags and instructions. Descriptions are empty in some samples |
| [Terminal-Bench 2.1](https://huggingface.co/datasets/harborframework/terminal-bench-2.1) | 89 tasks across Harbor directories. Sample TOML contains category/tags/difficulty and keywords | Separate from 4.0. Versions differ in vocabulary and time estimation units; preserve raw values and versions |
| [DeepSWE](https://huggingface.co/datasets/datacurve/deep-swe) | Parquet, per-task TOML, instructions, and manifests present in HF file list, but gated | File structure confirmed. Bodies unverified; register only at the public description level |
| [Toolathlon Verified](https://github.com/hkust-nlp/Toolathlon/blob/main/tasks/finalpool/academic-pdf-report/task_config.json) | Public GitHub repo with per-task `task_config.json`, `docs/task.md`. Sample config includes `needed_mcp_servers`, `needed_local_tools` | Explicit tool and service combinations. `meta` is empty in sample, so do not assume domain taxonomies reside there |
| [Agents' Last Exam](https://huggingface.co/datasets/agents-last-exam/agents-last-exam) | `task_cards.parquet`, `default/v1_1` 150 rows. title/summary/category/subdomain/task_split/task_prompt/agent_must_do/software/input_files/taxonomy | High level of structured metadata across tasks, domains, apps, and formats. Input files, reference outputs, and environments distributed separately |
| [HLE](https://huggingface.co/datasets/cais/hle) | HF card schema includes question/image/answer_type/raw_subject/category. Body gated | Subject/category can be leveraged, but raw body analysis unexecuted. Isolate tool-enabled variants |
| [GPQA Diamond](https://huggingface.co/datasets/Idavidrein/gpqa) | HF raw data gated. Task bodies and exact columns unverified in this pass | Register at TMG description level only. Do not imply access to native classifications |
| [LiveCodeBench](https://huggingface.co/datasets/livecodebench/code_generation_lite) | JSONL sample includes question_content/platform/contest_id/contest_date/difficulty/starter_code/test_cases/metadata | Suitable for algorithmic and contest problem retrieval with date filters. Distinct from repo edits. Metadata is string-typed in sample |
| [ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2/blob/main/data/evaluation/0934a4d8.json) | Per-task JSON `train[]` and `test[]` contain integer input/output grids | No natural language descriptions or domain categories. Register at the grid-transformation level; semantic analysis requires separate work |
| [LiveBench](https://huggingface.co/datasets/livebench/math) | Domain HF repositories. Math sample includes category/task/subtask/turns/release·removal date/ground_truth | Leverage native tasks/subtasks and releases. Category sub-scores cannot be synthesized from TMG Overall scores |
| [HMMT Feb 2026](https://huggingface.co/datasets/MathArena/hmmt_feb_2026) | Parquet schema: problem_idx/problem_type/problem/answer | Native `problem_type` can be utilized. Question taxonomy does not equal model score in that domain |
| [AA Analyst Agent](https://themodelgap.com/benchmarks/aa-analyst-agent) | Verified TMG descriptions and aggregate scores. Raw individual tasks unverified | Register under public description of spreadsheet and document analysis. Do not assume per-task retrieval |
| [OSWorld 2.0 Family](https://github.com/xlang-ai/OSWorld-V2/blob/main/evaluation_examples/examples/chrome/030eeff7-b492-4218-b312-701ec99ee0cc.json) | Official V2 repo per-app JSON samples include instruction/snapshot/related_apps/config/evaluator | Leverage apps, environments, and instructions. Jointly identify release manifests, full/offline variants, and revisions |
| [MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro) | Parquet schema: category/question/options/answer/src | Leverage for academic domain retrieval. Domain questions exist, but sample eval.yaml declares only an aggregate task |
| [AIME 2026](https://huggingface.co/datasets/MathArena/aime_2026) | Parquet schema: problem_idx/problem/answer | Native taxonomy is sparse. Register as math contest evaluation, adding detailed taxonomies when necessary |
| [MMMU-Pro](https://huggingface.co/datasets/MMMU/MMMU_Pro) | standard 4/10 options and vision config. subject/question/images/img_type/topic_difficulty | Leverage native subjects and input modalities. Separate scores across configs |
| [ExtractBench](https://huggingface.co/datasets/llamaindex/ExtractBench) | short/medium/long JSONL. id/category/pdf/data_schema/field_rules/repeated_structure/tags/expected_output | Tags already provide challenge/delivery/length/domain axes. Distinguish schema-based document extraction from page layout interpretation |
| [ParseBench](https://huggingface.co/datasets/llamaindex/ParseBench) | table/chart/text_content/text_formatting/layout JSONL. pdf/category/id/type/rule/page/tags, etc. | Rows represent inspection rules rather than entire documents. Preserve document-page-rule relationships and map to evaluation dimensions |

### 3.2 HF: Connecting Evaluation Definitions, Leaderboards, and Submissions

HF features data serving distinct roles:

| Data | Concrete Structure | Purpose |
| --- | --- | --- |
| `/api/datasets?filter=benchmark:official` | Array of dataset ID, tags, revisions, etc. | Dataset discovery. Not tasks or scores |
| Dataset `eval.yaml` | name/description/evaluation_framework/tasks[]. Tasks include id/config/split | Identifying independent evaluation items |
| `/api/datasets/{id}/leaderboard` | rank/modelId/value/verified/source/filename/notes/pullRequest | Discovering model results and linking raw outputs |
| `.eval_results/*.yaml` in models | Multiple results. Sample includes dataset.id/dataset.task_id/value/date/source/notes | Recovering sub-scores and conditions omitted from summary metrics |

The table above reflects raw HTTP response fields, distinct from Python SDK casing (`model_id`, etc.). None of the 5 leaderboard responses queried contained an explicit `task_id` column. Evaluation definitions and submission results must be read together. [Official Documentation](https://huggingface.co/docs/hub/leaderboard-data-guide)

In ParseBench submission YAMLs, 6 values were verified: `mean`, `table`, `layout`, `text_content`, `text_formatting`, and `chart`. Because these reflect specific pipeline runs, they do not imply performance for arbitrary CLI agents or base LLMs. While `table` can be referenced for table extraction tasks, whether that pipeline matches the delegated agent must be verified independently. [Submission Source](https://huggingface.co/KDLAI/KDL-Frontier-Parser-nano/blob/main/.eval_results/parsebench.yaml)

Declaring sub-items in `eval.yaml` does not imply that all candidate models have recorded scores. `verified=false` results must never be converted to verified status.

## 4. Index Model Aligned with Data

### 4.1 Minimal Relational Schema

Proposal for the retrieval contract, representable in SQLite or small JSON catalogs without introducing graph databases:

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

- `evaluation_id` identifies what a score represents. `case_id` identifies individual questions, problems, or documents. Never treat both as the same `task_id`.
- `supports_relevance` links relevance rationale, distinct from score aggregation. When task composition within a published score is ambiguous, record it as unverified.
- Evaluation items can be registered even before scores are acquired, decoupling relevance retrieval from data availability.
- Scores are stored per evaluation condition. If environment, tool access, scaffolding, effort, scoring methods, repetition counts, or revisions are ambiguous, do not assume equivalence to known conditions.
- Base models, CLI agents, and document analysis pipelines are distinguished in `evaluated_system`, documenting the exact matching scope with profiles.

### 4.2 Multi-Attribute Taxonomies and Native Classification Preservation

Initial shared axes should span a minimal scope directly verified in source data:

| Axis | Source Grounding Examples |
| --- | --- |
| Task & Deliverables | SWE issue/requirements, ALE agent_must_do, Parse/Extract evaluation definitions |
| Input Modalities | ALE input_files.format, MMMU config, Extract pdf/schema |
| Environment & Tools | Toolathlon needed_mcp_servers, ALE software, OSWorld related_apps |
| Domain & Language | MMLU/HLE domains, Pro repo_language, Arena language categories |
| Document Attributes | Extract length/challenge/delivery/domain tags |

Native classifications are preserved as `source_namespace + source_revision + field + value`, attaching rationale and mapping versions when mapped to common attributes. For example, Extract's `domain:D1` is not converted to a specific industry name without an official mapping table. Missing attributes are marked unknown, indicating neither lack of support nor ineligibility.

Normalized task vocabularies involve design decisions. Rather than attaching synthetic confidence scores, record sources, mapping rules, usage examples, and counterexamples. Matching a single language or domain attribute should not elevate a benchmark to a primary evaluation without confirming target actions and outcomes.

### 4.3 Retrieval and Response

1. The Orchestrator delivers a compact representation of the task, input, and environment. Invoking new classification models is never mandatory.
2. Candidate evaluations are queried across attributes. Compound tasks query required actions independently and aggregate matching evaluations.
3. Reference documentation and inspection rules verify applicability. When native categories are sparse, lexical search across short descriptions serves as an auxiliary fallback.
4. Matching observations are mapped to target profiles. If sub-scores are unavailable, the holistic aggregate nature of the score is stated explicitly.
5. Returns `evaluation_id`, matched attributes, relevance evidence, score distributions, candidate observations, missing/unknown flags, and reference links.

Initial retrieval can operate via set operations over compact catalogs or standard SQLite indices. If searching tens of thousands of raw task texts becomes necessary, evaluate SQLite FTS5. Mappings between Korean prompts and English classifications are supplemented via multilingual aliases or structured Orchestrator inputs. The need for embeddings or LLM re-classification should be evaluated only after measuring retrieval omissions.

If decision trees are used, they must support multi-branch exploration. For example, PDF processing, structured extraction, and repository code modification must be searchable independently. Leaf nodes reference attribute retrieval rather than static benchmark lists, reducing the overhead of managing duplicate taxonomies.

## 5. Examples and Resource Consumption

### Request: Convert PDF Tables to JSON

- Relevant candidates: ExtractBench schema extraction, ParseBench table, and Arena document overall if needed.
- Scope: Extracting structured data across full documents and interpreting table structures on a single page evaluate different capabilities. ParseBench table scores must not be generalized to long-document JSON extraction.
- Granularity: Use table/long sub-scores if present in submission outputs. If only mean exists, present mean; if defined without recorded scores, mark as missing.
- Entity match: Scores from document processing pipelines must not be attributed to different agents using the same base model.

### Request: Modify Existing Python Code with Korean Instructions

- Primary retrieval targets the action of modifying existing repositories, checking SWE suite content and conditions.
- Do not make Arena `korean` the primary evaluation based solely on prompt language. If Korean output fluency is explicitly required, it serves as an auxiliary observation.
- The mere use of a terminal does not warrant attaching Terminal holistic scores to all code editing requests.

### Refresh and Caching

Task analysis and alias/mapping creation occur during registration and data refresh. High-frequency request flows handle compact structured queries and local observation mapping. While workflows can be designed with zero runtime LLM calls for classification, token consumption remains for generating structured inputs and parsing outputs.

Cache keys for relevant evaluation lists bind normalized task characteristics and catalog/mapping versions. Result caches including observations also bind score snapshots and profile fingerprints, re-verifying freshness and conditions. When catalogs are small and retrieval overhead is negligible, caching can be deferred. Concrete latency and token savings have not yet been empirically measured.

## 6. Implementation Priorities

1. **Leverage Existing Score Structures:** Register Arena category-specific evaluations, preserving confidence intervals and vote counts. Ingest sub-items from HF eval.yaml and submission results.
2. **Connect Richly Categorized Tasks:** Map Terminal TOML, ALE task cards, Toolathlon tool configurations, and Extract/Parse tags. Avoid beginning with LLM re-classification of entire benchmark corpora.
3. **Annotate Metadata-Only Entries:** Use TMG descriptions for retrieval, returning appropriate statuses for unverified, gated, or aggregate-only entries.
4. **Measure Retrieval Quality on Real Requests:** Log missing relevant evaluations, superfluous inclusions, unsubstantiated sub-score interpretations, observation availability, response token volume, and p50/p95 retrieval latencies. Compare efficacy against the legacy 9-category mapping and full-text prompt delivery.

This sequence allows the index to materialize around published classifications and concrete score granularities.
