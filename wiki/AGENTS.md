# Benchmark Wiki — vault schema

An obsidian-wiki `llm-wiki` vault that holds benchmark knowledge: definitions, sources, version history, status. The router never browses this wiki per request. At refresh time it compiles only the `## Index` blocks into `index.json`; at request time it looks up the facet inverted index.

Pages are written in English, the language of the original sources, so definitions can be quoted verbatim and matched without translation drift. Keyword rules in `detect` may still list non-English keywords, because they match the task text.

## Page types

| Path | Content | `## Index` block |
|---|---|---|
| `concepts/facets/<axis>.md` | Allowed values (vocabulary) of one axis and how each is detected | `[[facet]]` array |
| `entities/benchmarks/*.md`, `entities/benchmarks/{mg,hf}/*.md` | One benchmark and its leaderboard slices (units) | `[[unit]]` array |
| `references/sources/*.md` | Public sources whose definitions are quoted | none |
| `concepts/*.md` | General model-selection concepts, separate from the facet vocabulary | none |
| `synthesis/*.md` | Comparisons and findings across sources | none |
| `projects/bench-router/**/*.md` | Project overview, implementation findings, and explicitly labeled proposals | none |

Model and effort guidance is reference knowledge, not a benchmark unit or a new facet. These pages do not have `## Index` blocks and do not change runtime routing. New pages follow the same `draft` review gate below. Their source dates and model versions must be explicit; vendor advice is not a cross-provider performance guarantee.

Source captures under `_raw/_archived/` may contain a bounded verbatim excerpt rather than a complete document. Each capture declares its scope and canonical origin; never describe an excerpt as a full original. Keep captures immutable and save a new dated capture when evidence changes.

Allowed axes: `task`, `lang`, `domain`, `difficulty`, `shape`, `agent_signal`.

## `## Index` contract

Each page body has one ```toml block in a `## Index` section. It lives in the body, not the frontmatter, because the repository uses only the standard library (`tomllib`) and the frontmatter follows the obsidian-wiki conventions unchanged.

`[[facet]]`: `id`, `desc`, `detect` (`rule:<rule>` = decided by the router deterministically, `self` = tagged by the Orchestrator in the task JSON `facets`), `evidence` (`official` | `dataset` | `name_only`), optional `arena_rule` (LMArena's original tagging rule).

`[[unit]]`: `id`, `desc`, `metric` (`elo` | `ips` | `pass_pct` | `index`), `status` (`current` | `saturated` | `contaminated`), `adoption`, `facets` (`{axis = [values, ...]}`), optional `reason` (why this adoption), `evidence`, `meaningful_gap`, `trust_grade`.

- `adoption`: `active` (enters the inverted index) | `candidate` (promote to active after collection and coverage checks) | `archive` (saturated or replaced; lookup only) | `excluded` (not a task this router delegates; reason only). Only `active` units enter the inverted index. Independent of the page `lifecycle` (review state).
- An `excluded` unit may have `facets = {}`. Every other unit needs at least one facet.
- Unit id formats: `arena:<config>/<category>` (HF `lmarena-ai/leaderboard-dataset`), `arena-web:<board>/<signal>` (only on the arena.ai web leaderboard), `mg:<benchmark_id>/<variant>` (The Model Gap), `hf:<owner>/<dataset>` (HF official benchmarks), or one of `EVIDENCE_IDS` in `bench_router/data.py`.
- A logical benchmark appears as units on one page only. Mirrors from other collectors (e.g. HF `cais/hle`) are attached to that page as sources.
  Exception: a manual exact import (`EXACT_PINS`, matched to the profile's harness and effort) keeps its own page next to the model-proxy page of the same benchmark, because it measures a different scope. The two pages link each other with `related_to`, and their `adoption` must agree unless the page states why not.
- Facet-to-unit links are written **on the unit side only**. Facet pages never list units; the compiler builds the inverted index.
- Every `facets` value must be an `id` defined on that axis page.

## Review gate

- Only pages whose frontmatter `lifecycle` is `reviewed` or `verified` are compiled. New pages are always written as `draft`; a human changes them after review.
- Saturation or contamination of the benchmark itself goes in the unit `status`, not in `lifecycle`.
- Items whose definition could not be found on public pages are either not registered or marked `evidence = "name_only"`, and listed under the page's `## Open Questions`.

## References

- Data shape survey: `docs/benchmark-index-analysis.md`, `docs/evidence/benchmark-index-schema-2026-10-17.json`
- Raw source snapshots: `_raw/web/`, `_raw/hf/`
- Archives of earlier versions: `_archives/` (the Korean draft is `_archives/2026-10-17T23-53-12Z/`)
- `index.md`, `log.md`, `.manifest.json` are managed by the obsidian-wiki CLI. The compiler does not read them.
