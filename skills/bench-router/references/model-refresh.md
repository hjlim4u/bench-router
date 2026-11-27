# Model & Guideline Refresh Workflow

Run this workflow only when the user explicitly asks to check newly released vendor models or refresh bench-router's model catalog or official model/effort guidance. For a routine benchmark snapshot update alone, use `bench-router refresh` directly. Do not run this workflow during ordinary task delegation.

## 1. Mode detection (dual-mode)

Resolve the workspace's Git top-level root first (`git rev-parse --show-toplevel`, falling back to CWD if not in a git repository), then check for `wiki/AGENTS.md` and `bench_router/guidelines.toml` at that root:

- **Repo Maintainer mode**: Both markers exist at the root → run **Stages 1–4** below.
- **End-User mode**: Either marker is absent (installed `bench-router` CLI outside the source repo) → run **End-User mode** only.

## 2. Capability slots (host-agnostic extensibility)

Different hosts (Antigravity, Claude Code, Codex, bare CLI agents) expose different skills, MCP servers, and tools. Resolve each needed slot using the first usable provider from:
1. Repo override: `<git-root>/.bench-router/refresh-capabilities.md` (if present)
2. User override: `${XDG_CONFIG_HOME:-~/.config}/bench-router/refresh-capabilities.md` (if present)
3. Default table below

Overrides name providers only. Bind any wiki or index writer explicitly to the detected checkout's `wiki/`. If a provider fails or cannot access the intended target, fall through to the next provider in order. Report the resolved slot map (active vs fallback/skipped) in the final summary.

| Slot | Purpose | Preferred skills / plugins (in order) | Bare fallback |
|---|---|---|---|
| `web_research` | Survey vendor releases, official docs, and independent benchmarks | `wiki-research` skill → web-search MCP (e.g. Perplexity, Tavily) | Host native web search; if no search tool exists, fetch known/supplied canonical URLs directly and report limited survey coverage |
| `doc_fetch` | Retrieve clean verbatim Markdown from official vendor docs | Direct `.md` endpoints (`aistudio.google.com/docs/*.md`, `platform.claude.com/docs/*.md`, `developers.openai.com/api/docs/*.md`) → `defuddle` → `ctx7` | `curl` / Python `urllib` + plain-text extraction |
| `wiki_sync` | Atomically update `wiki/index.md`, `log.md`, `hot.md`, `.manifest.json` | `obsidian-wiki memory sync WIKI_RESEARCH` (bound to checkout `wiki/`) | Leave all managed files untouched and report `wiki sync pending` |
| `search_index` | Refresh local search index after wiki edits | `qmd update` (and `qmd embed` if stale vectors reported) when `QMD_WIKI_COLLECTION` is set | Skip and report `skipped` |
| `code_verify` | Keep diffs minimal and verify repo invariants | `ponytail` principles + `python3 -m unittest` + `python3 -m bench_router.cli wiki compile --check` | `python3 -m unittest` + `python3 -m bench_router.cli wiki compile --check` |

## 3. Repo Maintainer mode (Stages 1–4)

### Stage 1 — Survey & verbatim capture
1. Use `web_research` and `doc_fetch` to inspect official model catalogs, model-selection/effort guides, and independent leaderboards (Artificial Analysis, Vals AI, LMArena, Terminal-Bench, plus local `${XDG_CACHE_HOME:-~/.cache}/bench-router/bench-router.db` when present).
2. Save immutable dated verbatim captures under `wiki/_raw/_archived/YYYY-MM-DD-<source>.md` with YAML frontmatter (`source_url`, `captured_at`, `scope`, `immutable: true`). Reuse identical captures and keep the same `<source>` suffix when recapturing a guide. For a second capture on the same UTC date, use `YYYY-MM-DDTHHMMSSZ-<source>.md`. Start `scope` with `Complete verbatim Markdown` for complete captures and describe the actual bounds of excerpts.
   - `test_p0.py:test_v118` flags a newer complete capture of an active source until the corresponding reference in `guidelines.toml` is updated. `test_v109` verifies that each prompting quote matches its own capture.
3. Record inaccessible, incomplete (e.g., omitted tabs), or HTTP-404 sources as `unverified`. Never treat missing extraction or a guessed 404 URL as evidence to drop valid guidance; preserve the last supported rule until a canonical passage confirms a change.

### Stage 2 — Wiki update
1. Update affected `wiki/references/sources/*.md` and `wiki/synthesis/*.md` pages (folded `>-` scalars for `title`/`summary`, explicit `as_of` dates, `snapshots:` wikilinks, and a closing `## Sources` section).
   - When a source page is re-captured, re-read the whole page, not only the new model's section: update every existing model's status and description (e.g. "previous-generation", "legacy", deprecation), the "for new projects use…" banner, and upgrade/migration tables.
   - Mark wiki summaries as such. Text inside quotes or tables labeled "verbatim" must match the capture; labels like "Default to" that the page does not literally say are `^[inferred]`, not `^[extracted]`.
2. Keep all newly created pages at `lifecycle: draft` and omit `## Index` TOML blocks on model/effort guidance pages (per `wiki/AGENTS.md`, guidance is reference knowledge, not a benchmark unit or facet).
3. Verify the pages' `lifecycle`, `sources`, and capture links. Continue through runtime sync and offline verification before running `wiki_sync` or `search_index`.

### Stage 3 — Runtime & config sync
1. For every changed guide, record which routing fields changed, which were reviewed and confirmed, or which remain pending for lack of complete evidence. Update `bench_router/guidelines.toml` accordingly:
   - Preserve each vendor's schema shape: OpenAI and Claude use combo `start` rows, conditional `escalation` rows, and optional role-only `model` rows; Gemini uses factored `model` rows (`supported`, `default`, optional `advanced`) + `effort_class` (never add a `start` key to Gemini, which switches `decision.py`'s loader branch).
   - Keep every `strategy`, `role`, `when`, and `text` verbatim from its own vendor capture. Retain legacy `[sources.*]` entries under their own IDs when older rows still quote them. Bump `version`, `as_of`, and `[vendor.<id>].revision` only for substantive changes; leave unchanged evidence and revisions alone.
   - Compare the current guide with the previous capture and review all affected models, including existing ones. Check starting points, roles, strategies, and effort defaults, ranges, and escalation conditions. Update the active source reference after reviewing a complete capture, even when no routing text changed.
   - Prefer the vendor's task-selection text for model roles, such as Google's "When to choose each model" bullets. Apply recommendations within their published scope, including guidance specific to migration or new projects.
   - Keep model-scoped `prompt_guidance` isolated to the models its source covers (e.g., `claude-sonnet-5-5` is tested to pull only from its own prompting guide).
2. Sync `bench_router/defaults/{profiles,aliases}.toml` and `examples/{profiles.default,aliases.example}.toml` **byte-for-byte** (and `bench_router/defaults/env` ↔ `.env.example` if touched; *why*: `test_p1.py:test_v63` enforces exact byte equality).
3. Update dated assertions in `test_p0.py` only when official vendor guidance genuinely changed.

### Stage 4 — Verify & refresh
1. Run `python3 -m bench_router.cli wiki compile --check` and `python3 -m unittest discover` from the checkout. For changed model-selection guidance, verify the affected role, strategy, or effort in the offline `evaluate` guidance request. Follow `test_p0.py:test_v119` for an example that checks the request against Google's captures.
2. Run `wiki_sync` and `search_index` after the offline checks pass. If `wiki_sync` is unavailable, leave managed files untouched and report `wiki sync pending`.
3. If bundled defaults changed, verify the affected default models and aliases against a temporary cache without touching user config:
   `python3 -m bench_router.cli --config-dir bench_router/defaults --cache-dir <tmp> refresh`
4. Run shared `refresh` and `status` as **separate** commands (partial fetch failure returns exit 16), and report per-source results, fresh skips, and unmatched names.
5. If the shared installation is in scope, verify it from outside the checkout after updating it from the verified revision. Compare the installed `bench-router` output from `prompt-guidance` for an affected model with the checkout, including `guidelines_version` and vendor `revision`. Verify the affected `evaluate` guidance field when routing text changed. Check that the installed skill's copy of this reference matches the checkout. Report installation as pending if only the checkout was verified.

## 4. End-User mode

When running outside the `bench-router` source repository:
1. Run `bench-router status` and `bench-router refresh` separately; inspect per-source results, fresh skips, and unmatched names.
2. Distinguish unresolved aliases (`aliases.toml`) from missing profiles (`profiles.toml`) — an unmatched benchmark slug alone proves neither a release nor an alias.
3. Ask explicit user confirmation before running `bench-router profiles discover --merge` or editing `aliases.toml`, then re-run `bench-router refresh` after approved changes.

## 5. Safety gates & reporting

- **Manual trigger & human gates**: Never auto-commit, auto-push, promote wiki pages past `draft`, or silently edit `${XDG_CONFIG_HOME:-~/.config}/bench-router/profiles.toml`.
- **Report**: Summarize (a) detected mode and resolved root, (b) resolved capability slots (active vs fallback/skipped), (c) modified/created files, (d) test, compiler, defaults-verification, and shared refresh/status results, and (e) any unverified, 404, or rumored models left out of runtime config.
