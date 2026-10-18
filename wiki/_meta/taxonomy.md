# Tag Taxonomy

Canonical tags for this vault. Rules: at most 5 tags per page (`visibility/` tags excluded), lowercase and hyphenated, prefer broad over narrow.
A benchmark page carries 1 type tag, 1 collector tag, and up to 3 topic tags derived from its units' facets (most frequent first).

## Type

- `benchmark` — a benchmark page under `entities/`
- `facet` — a facet axis page
- `index` — part of the compiled index vocabulary
- `source` — a public source page

## Collector

- `lmarena` — LMArena leaderboard dataset or arena.ai web leaderboard
- `themodelgap` — The Model Gap
- `hf-official` — Hugging Face official benchmark datasets
- `exact` — manual exact import (`EXACT_PINS`)
- `aa` — Artificial Analysis

## Topic

Derived from unit facets: `task` values map as below, `agent_signal` maps to `agentic`, excluded units map to `out-of-scope`.

- `agentic` — task: computer_use, gui_grounding, multi_tool, professional_work, terminal_ops ; agent_signal: *
- `coding` — task: coding, repo_coding
- `data-analysis` — task: data_analysis
- `documents` — task: document, ocr_parse
- `general` — task: general, instruction_following
- `legal` — task: legal
- `math` — task: math
- `out-of-scope` — units with adoption = excluded
- `reasoning` — task: abstract_reasoning, science_reasoning
- `search` — task: retrieval, search
- `vision` — task: vision, vision_diagram, vision_homework, vision_ocr
- `web-frontend` — task: image_to_webdev, webdev_html, webdev_react
- `writing` — task: creative_writing

## Aliases

| Alias | Canonical |
|---|---|
| `agent` | `agentic` |
| `composite` | `general` |
| `frontend` | `web-frontend` |
| `hf` | `hf-official` |
| `lm-arena` | `lmarena` |
| `mg` | `themodelgap` |
| `ocr` | `documents` |
| `retrieval` | `search` |
| `webdev` | `web-frontend` |

## Usage (2026-10-18)

| Tag | Pages |
|---|---|
| `benchmark` | 79 |
| `hf-official` | 40 |
| `agentic` | 19 |
| `themodelgap` | 14 |
| `source` | 13 |
| `coding` | 10 |
| `out-of-scope` | 10 |
| `general` | 9 |
| `lmarena` | 9 |
| `documents` | 6 |
| `facet` | 6 |
| `index` | 6 |
| `reasoning` | 6 |
| `math` | 4 |
| `legal` | 3 |
| `vision` | 3 |
| `data-analysis` | 2 |
| `exact` | 2 |
| `search` | 2 |
| `aa` | 1 |
| `web-frontend` | 1 |
| `writing` | 1 |
