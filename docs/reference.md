# bench-router Detailed Reference

Updated: 2026-10-24. The default selection policy is [Vendor-guided Policy 6](vendor-guided-routing.md), shared across `route`, `parallel`, and installed Skills. Quality and coverage metrics described below serve as diagnostic evidence in `evaluate` formats 1 and 2 and are not used for automated selection. Weighted-sum automated selection and `--policy legacy` have been removed.

This document covers configuration formats, CLI commands, exit codes, evaluation pathways, data refresh mechanisms, live delegation contracts, parallel dispatch, and historical validation records. For a project overview, consult [README](../README.md) first.

---

## Requirements

- Offline evaluation and data refresh run on Linux, WSL2, and Windows. Live Projects execution runs on Linux or WSL2.
- Python 3.11+.
- Evaluation, selection and `route --dry-run` need no Herdr or Agent CLI.
- Live delegation picks a runner with `--runner` (see [Runners](#runners)). `external` needs neither Herdr nor an agent CLI, `local` needs the authenticated Agent CLI, and `herdr` (the `auto` choice when `herdr-projects` is on PATH) requires Herdr, herdr-projects **1.2.1** (board), and authenticated Agent CLIs. The task `cwd` must be the root of a Git repository containing at least one commit. See [docs/projects.md](projects.md).
- Refreshing Artificial Analysis data requires an API key (Free tier suffices).

From a clone, `mise run install` installs the CLI as an editable uv tool (it follows the clone, so `wiki compile` finds `wiki/`) together with the global Agent Skill; rerun it after `git pull` to refresh the Skill copy. Alternatively, install the CLI with `uv tool install /absolute/path/to/bench-router`, then run `bench-router init` to create shared profiles and aliases without overwriting existing files. The installed `bench-router` command works from any directory; `init` is offline and data collection is separate (`bench-router refresh --source mg`). Arena refresh requires the optional extra: `uv tool install '/absolute/path/to/bench-router[arena]'`. Run `uv tool update-shell` and restart the shell if the command is not on PATH.

The core CLI also runs directly as a Python module from the repository root without installation. Set up the development environment using `mise install && mise run setup` or `uv sync --extra arena`. `mise run test` executes the complete offline test suite, and `mise run refresh` performs a `--force` refresh across all sources. Installed packages include the compiled index but not the original wiki; recompilation needs `bench-router wiki compile --vault /absolute/path/to/bench-router/wiki`.

```bash
cd /path/to/bench-router
python3 -m bench_router.cli --help
```

<a id="여러-agent에서-skill-사용-글로벌-또는-프로젝트별-설치"></a>
<a id="using-as-a-skill-across-multiple-agents"></a>
### Using as a Skill Across Multiple Agents (Global or Project-Local Installation)

The `skills/bench-router/` directory bundles the complete `bench_router` engine (with built-in `index.json` and `guidelines.toml`) via symlinks. When [`npx skills`](https://skills.sh/) copies (`dereferences`) the skill directory during installation, it operates **fully autonomously without requiring the original repository or `wiki/` directory**.

```bash
# 1. Global installation (-g): connect across all detected agents (Claude Code, Codex, Cursor, Gemini CLI, etc.)
npx skills add hjlim4u/bench-router -g
# (To install from a local clone: npx skills add /abs/path/to/bench-router -g)

# 2. Local installation into a specific project directory
cd /abs/path/to/my-project && npx skills add hjlim4u/bench-router

# 3. Manual symlink installation without Node.js
ln -s "$REPO/skills/bench-router" "$AGENT_SKILLS/bench-router"
```

The Skill's `scripts/cli.py` and `scripts/decide.py` directly invoke the bundled `bench_router` package. Agents running within the same OS environment share user configuration (`~/.config/bench-router`) and cache (`~/.cache/bench-router`). Because native Windows and WSL implement distinct file-locking primitives, do not share the same physical cache between Windows and WSL concurrently. Running within a single unified environment allows safe sharing without duplication. `route` never modifies the cache; schedule periodic `refresh` runs in only one place per user. Manual `refresh` shares the same locks and cache. On Windows, register the `refresh` command once in Windows Task Scheduler.

---

## Configuration

The default configuration directory is `$XDG_CONFIG_HOME/bench-router` (`~/.config/bench-router`), configurable via `--config-dir`. The default cache directory is `$XDG_CACHE_HOME/bench-router` (`~/.cache/bench-router`), configurable via `--cache-dir`.

| File / Environment Variable | Required | Description |
|---|---|---|
| `profiles.toml` | **Yes** | Inventory of candidate Agent profiles |
| `aliases.toml` | No (Recommended) | Source model string → profile `model_id` mapping (refer to `unmatched_sample` in `status`) |
| `categories.toml` | No | Uses internal `bench_router/categories.toml` if absent |
| `env` | No | API key storage (recommended permissions: `chmod 600`). Load via `set -a; . ~/.config/bench-router/env; set +a` |
| `ARTIFICIAL_ANALYSIS_API_KEY` | No (for `aa` refresh) | Free API key for Artificial Analysis. Public `arena`, `mg` and `tb_auto` data and `wiki compile` work without it |
| `TYPESAFE_API_KEY` (or `JEV_API_KEY`) | No (for Skill decisions) | Optional external API key for Jev in live route/parallel or `decide.py`. If absent or failed, falls back to native decision packets handled by the host agent's `bench-decider` |

<a id="profilestoml"></a>
### profiles.toml

Routing operates at the **profile** granularity (Agent CLI + model + execution configuration). In schema 1.0 all keys are required; unrecognized keys trigger configuration errors. Schema 2.0 adds caller-owned profiles (below).

```toml
schema_version = "1.0"

[[profile]]
id = "claude-opus-high"                              # [a-z][a-z0-9_-]{0,47}
enabled = true
kind = "claude"                                      # herdr --kind value; must match executable
executable = "claude"
args = ["--model", "claude-opus-5-5", "--effort", "high"]  # model and effort settings only
model_id = "claude-opus-5-5"                         # canonical ID mapped in aliases.toml
harness_id = "claude-code"                           # for exact benchmark matching
reasoning_effort = "high"                            # "unknown" prevents exact matching
config_revision = "2026-10-12c"                      # change config → update revision → shifts fingerprint
cost_tier = "high"                                   # low | medium | high (policy relative tier, not billing cost)
inference_local = false
context_tokens = 0                                   # 0 = unknown → fails min_context_tokens constraints
capabilities = ["filesystem_write"]

[[profile]]
id = "codex-sol-high"
enabled = true
kind = "codex"
executable = "codex"
args = ["-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=\"high\""]
model_id = "gpt-6.1-sol"
harness_id = "codex-cli"
reasoning_effort = "high"
config_revision = "2026-10-12"
cost_tier = "medium"
inference_local = false
context_tokens = 0
capabilities = ["filesystem_write"]
```

The model names and effort levels above are illustrative. Confirm supported models using `herdr-projects models KIND`. `args` can only translate `--model`/`-m`, `--effort`, and Codex `-c model_reasoning_effort="E"` into Projects settings. Passing other flags (such as `--permission-mode`, `-s`, `-a`) terminates with `execution_failed` prior to submission.

Permissions follow Projects `worker.access` (`full` | `ask`). Modify using `herdr-projects set worker.access ask [--repo NAME]`. Under `ask`, Claude requires approval on every file edit and Codex on writes outside the worktree, pausing in `blocked`. For details, see [Projects Profiles and Permissions](projects.md#profiles-and-permissions).

Live `route` and `parallel` check PATH availability, and Antigravity checks the active model list via `agy models`. When `codeburn quota --format json` is available, provider status and quota window exhaustion are checked for Claude and Codex. CodeBurn installations under `.bench-router/codeburn` are detected automatically, overridable via PATH or `BENCH_ROUTER_CODEBURN`. When CodeBurn is unavailable, checks fall back to PATH while retaining agy model verification.

#### Caller-owned profiles (schema 2.0)

`schema_version = "2.0"` accepts the same keys, but `kind`, `executable` and `args` go all together or not at all. A profile with all three is a CLI profile, validated and fingerprinted exactly as in 1.0. A profile without them is caller-owned: the caller's executor (API, host Agent tool, external CLI) runs it by profile ID. Its fingerprint hashes only `model_id`, `harness_id`, `reasoning_effort` and `config_revision` (fingerprint version 2), so bump `config_revision` whenever the caller's execution setup changes. Do not put URLs, API keys or commands in profiles. The `herdr` and `local` runners exclude caller-owned profiles with `unsupported_execution_profile` and never convert them to a CLI; the `external` runner hands them to the caller. 1.0 files keep working unchanged.

```toml
schema_version = "2.0"

[[profile]]
id = "caller-agent-example"
enabled = false
model_id = "REPLACE_WITH_CANONICAL_MODEL_ID"
harness_id = "caller-tool-harness"
reasoning_effort = "unknown"
config_revision = "replace-after-verification"
cost_tier = "high"
inference_local = false
context_tokens = 0
capabilities = []
```

`profiles discover [--force]` generates candidate configurations in `profiles.toml` from installed CLIs. Codex inspects `models_cache.json` and per-model effort; Claude inspects guidelines models and CLI help effort flags; agy inspects account model listings, merged with CodeBurn observed models. Generated profiles default to `enabled=true`, `cost_tier=high`, and `context_tokens=0`. Review permissions, capabilities, context limits, and live account invocation status before use. Overwriting existing files requires `--force`.

<a id="aliasestoml"></a>
### aliases.toml

Because external sources name models differently, specify **verbatim source string → canonical ID** mappings here. This table serves as an explicit override mechanism.

Even without aliases, `refresh` normalizes source names to profile `model_id`: ignoring case, dots, spaces, and hyphens, and stripping trailing effort annotations (`(High)`, `-high`). For example, `Claude Opus 5.5 (High)`, `claude-opus-5.5-high`, and `claude-opus-5-5` all resolve to `claude-opus-5-5`. Adding a new profile automatically links matching names on the next refresh. Explicit aliases take precedence over automated normalization.

What automated normalization does not match: divergent suffixes such as `-preview`, `(xHigh, Codex Harness)`, or unconfigured models. Map them manually as follows. Rows with explicit effort match profile effort first, falling back to rows without effort:

```toml
[arena]
"claude-opus-5.5-high" = "claude-opus-5-5"

[aa]
"claude-opus-5-5-high" = "claude-opus-5-5"
"gpt-6-1-sol-high" = "gpt-6.1-sol"
```

Unmatched names can be inspected via `unmatched_count` and `unmatched_sample` in `status`.

---

## Commands

All commands emit a **single JSON object** to stdout (except `explain` and `evidence --format table`, which output text). Diagnostic logs go to stderr. Global options include: `--config-dir`, `--cache-dir`, `--herdr-session NAME` (or environment variable `BENCH_ROUTER_HERDR_SESSION`). The Projects executable path defaults to `herdr-projects`, overridable via `BENCH_ROUTER_PROJECTS`. `--herdr-session` must match the session containing the target project.

| Command | Action |
|---|---|
| `refresh [--source aa\|arena\|mg\|tb_auto] [--force] [--vault DIR]` | Fetches automated sources and compiles reviewed wiki pages (`index.json`) → publishes snapshot. Skips if within TTL |
| `refresh --source swe\|tb --import FILE` | Imports approved manual benchmark results |
| `wiki compile [--vault DIR] [--check]` | Compiles reviewed benchmark wiki pages into `index.json` (`--check` validates only) |
| `wiki facets` | Emits vocabulary, descriptions, and rule mappings available for tagging in `task.facets` |
| `evidence --task FILE [--format json\|table] [--max-units N]` | Emits per-profile benchmark evidence matching task facets (no sums or rankings; read-only) |
| `status` | Reports source ages, failure counts, last errors, unmatched models, and snapshot/config consistency |
| `profiles discover [--force]` | Discovers installed CLIs and generates candidate profiles (requires `--force` to overwrite) |
| `route --task FILE --dry-run` | Generates offline decision packets; validates saved responses or selection records (no network, herdr, or disk writes) |
| `explain --task FILE [--context FILE]` | Outputs human-readable candidate rationale, evidence, disqualifications, constraint results, and metrics |
| `evaluate --task FILE [--context FILE] [--format 1\|2\|3]` | Evaluates facts (schema 2.0 default) / format 3 evaluates phased suitability and evidence (schema 4.0; no selection) |
| `select --assessment FILE --profile ID --policy-id ID --policy-version V --reason TEXT [--accept-provisional]` | Produces selection 6.0 from a completed format 3 assessment; save only the inner `selection` object |
| `route --task FILE --selection FILE` | Dispatches the profile chosen by the Orchestrator with selection evidence; returns `stale_assessment` if inputs changed |
| `route --task FILE [--wait-ms N]` | Selects profile, delegates via Herdr, and waits/collects within timeout budget; `--wait-ms 0` returns immediately after dispatch |
| `parallel --group FILE [--dry-run]` | Dispatches multiple agents into isolated worktrees in parallel ([Parallel Dispatch](#parallel-dispatch-and-collaboration-levels)) |
| `collect --run-id ID --cwd DIR [--wait-ms N]` | Observes and collects an active run; **never re-sends prompts** |
| `collect --run CWD ID [--run …] --until any\|all [--wait-ms N]` | Observes multiple runs until one (`any`) or all (`all`) settle |
| `stop --cwd DIR [--run-id ID]` | Stops an active run (board `stop`, or closes workspace for headless tasks); next collect records `execution_failed` |
| `resume --run-id ID --cwd DIR` | Reopens a closed board task and agent conversation in the same session (no prompt sent) |
| `tell --cwd DIR [--run-id ID] --message TEXT \| --message-file F` | Delivers a message to an active or resumed agent; logged in `runs/ID/messages.jsonl`; never sent autonomously |
| `feedback --run-id ID --cwd DIR --outcome success\|partial\|fail [--evaluator X] [--note Y]` | Records Orchestrator verification verdict |
| `coordination status\|release\|feedback` | Inspects shared active executions (limit 4), releases slots after confirming worker stoppage (`release`), and records adoption |

### Example Usage

```bash
export PATH="$HOME/.local/bin:$PATH"                 # herdr, claude, codex
set -a; . ~/.config/bench-router/env; set +a          # AA API key

bench-router refresh                       # aa, arena, mg, tb_auto + wiki index
bench-router status
bench-router route --task task.json --dry-run
bench-router explain --task task.json
bench-router evidence --task task.json --format table
bench-router --herdr-session work route --task task.json      # live delegation
bench-router collect --run-id <RUN_ID> --cwd /abs/project --wait-ms 60000
bench-router feedback --run-id <RUN_ID> --cwd /abs/project --outcome success --evaluator orchestrator
```

### Exit Codes

| Code | Meaning |
|---|---|
| 0 | `selected` (dry-run), `completed`, normal termination for refresh/status/feedback |
| 2 | Invalid input, configuration, or argument error |
| 10 | `blocked` — Agent is paused waiting on user approval or prompt response |
| 11 | `timed_out` / `delivery_uncertain` — Execution may still be active; check via `collect`. `handed_off` — external runner: run the returned `invocation`, then `collect` |
| 12 | `execution_failed` / `result_invalid` |
| 13 | `no_eligible_profile` — Task not dispatched |
| 14 | `conflict` — Incompatible task/round content, unresolved runs, or lock contention; `stale_assessment` — Task, config, snapshot, or context changed after evaluation |
| 15 | Internal storage or I/O error |
| 16 | Partial or complete failure during refresh (last-good data preserved) |
| 17 | `decision_required` — Pending native decision packet resolution / `decision_unavailable` — Decision impossible or abstained; not dispatched |

---

## Input: task.json

```json
{
  "schema_version": "1.0",
  "task_id": "fix-pager-001",
  "round": 1,
  "summary": "Fix an off-by-one bug in pager.paginate.",
  "prompt": "paginate(...) in pager.py skips the first page. Please resolve.",
  "cwd": "/home/me/project",
  "context_files": ["pager.py"],
  "constraints": {"max_cost_tier": "high", "min_context_tokens": 0, "local_only": false,
                  "timeout_ms": 900000, "required_capabilities": ["filesystem_write"]},
  "priority": "balanced",
  "exclude_profiles": []
}
```

- Required: `schema_version`, `task_id` (`[A-Za-z0-9][A-Za-z0-9_-]{0,63}`), `round` (≥1), `summary` (≤4000 chars), `prompt` (≤256 KiB), `cwd` (existing absolute path).
- Optional: `facets` (`{axis: [value]}`). Used when the Orchestrator explicitly tags task characteristics defined in `wiki facets`, reflected in `evidence` table queries.
- Unrecognized keys, NaN/Infinity, duplicate JSON keys, invalid UTF-8, and `context_files` pointing outside `cwd` return exit code 2.
- During live dispatch, the prompt combined with execution contract text must not exceed 120 KiB, because Herdr passes prompts strictly as single argv arguments.
- **`cwd` must be trusted by target Agent CLIs in advance.** Unrecognized directories trigger trust confirmation dialogs in Claude Code or Codex, resulting in `blocked`. The router never automates security confirmations.

---

## Selection Methodology

Default `route` evaluates task analysis, vendor guidance, and benchmark relevance under Policy 6. Multiple viable candidates request upstream selection. `evaluate --format 3` (schema 4.0) → `select` → `route --selection` produces selection schema 6.0; automated single-candidate selection produces schema 5.0. Historical vendor-guided schemas 3.0 and 4.0 require re-evaluation. Detailed decision flows, responses, and digests follow [Vendor-guided Routing Policy](vendor-guided-routing.md); legacy 2.0 overrides follow [Routing Contracts](routing-contracts.md).

The classification and quality/coverage formulas below apply to default fact evaluations in `evaluate --format 1|2`. They are distinct from semantic suitability under vendor guidance and do not rank candidates.

1. **Classification**
   - Applies summary keyword and `context_files` extension rules. A category is adopted only when two or more distinct rules match within that single category.
   - Unmatched tasks fall back to `general`, recording `fallback_reason`.
2. **Hard Constraints**: Applies `enabled`, `exclude_profiles`, `max_cost_tier`, `min_context_tokens`, `required_capabilities`, and `local_only`. If context is provided, `tokens.required_context` and `max_estimated_cost_usd` are applied (`routing.CONSTRAINTS`). Live mode checks executable/kind consistency, PATH availability, `agy models`, and optional CodeBurn quota. Unsupported arguments are rejected prior to submission.
3. **Evidence and Scoring**
   - Category weights `w` and evidence mappings `v` compute evidence weights `a_b = Σ w_c·v_cb`.
   - Normalizes percentiles across the cohort population (`(mean rank − 1)/(N − 1)`, or 0.5 if N=1).
   - Coverage `C` represents the sum of observed evidence weights.
   - Quality `Q = C·Q_obs + (1−C)·0.5 − 0.1·(1−C)`. Missing data receives a prior of 0.5 and a penalty of 0.1; an empirical score of 0 is not treated as missing.
4. **Selection**: `Q` and `C` are informational evidence; candidates are ordered by profile ID. Using `select` requires completing format 3 decisions. Manual selections based on format 1 or 2 constitute schema 2.0 overrides. If no executable candidate exists, returns `no_eligible_profile` (exit 13).

Default category evidence mappings (`categories.toml`):

| Category | Evidence (Weights) |
|---|---|
| coding_repo | swe_verified_exact 0.6, aa_coding 0.4 |
| terminal_ops | terminal_exact 0.7, aa_coding 0.3 |
| code_gen | aa_coding 1.0 |
| webdev | arena_webdev 0.6, aa_coding 0.4 |
| math_reasoning | arena_text_math 1.0 |
| analysis | aa_intelligence 0.6, arena_text 0.4 |
| writing | arena_text 1.0 |
| vision_doc | arena_document 0.5, arena_vision 0.5 |
| general | aa_intelligence 1.0 |

Default evaluations provide `quality`, `coverage`, `coverage_band`, `exact_evidence_weight`, raw values, normalized values, scopes, cohorts, conditions, revisions, timestamps, and `missing_reason` per candidate. Format 2 nests these under `candidates[].evaluations.benchmark`; format 1 flattens them into `candidates[]`. Composite scores, legacy scores, and cost proxies are omitted. Real semantic decision evidence resides in `decision.evaluation` or `selection.decision.evaluation`; full candidate suitability is inspected in format 3. The initial 3 candidates summarized in CLI route output follow profile ID order, not a quality ranking.

---

## Data Collection (refresh)

| Source | Method | Evidence | TTL / Max Allowed Age |
|---|---|---|---|
| `aa` | Artificial Analysis Free API, full pagination | `aa_intelligence`, `aa_coding`, and active wiki units (`aa:*`) | 24h / 7d |
| `arena` | LMArena `leaderboard-dataset` (CC BY 4.0), config-specific `latest` Parquet pinned to revision SHA (decoded via `pyarrow`, category filtered locally) | `arena_text`, `arena_text_math`, `arena_webdev`, `arena_document`, `arena_vision`, and active wiki units (`arena:*`) | 24h / 7d |
| `mg` | The Model Gap (`themodelgap.com/data`, CC BY 4.0) JSON | Active wiki units (`mg:*`) | 24h / 7d |
| `swe` | Manual `--import` results, pinned to SWE-bench Verified | `swe_verified_exact` | 168h / 30d |
| `tb` | Manual `--import` results, pinned to Terminal-Bench 4.0 | `terminal_exact` | 168h / 30d |
| `tb_auto` | Official Terminal-Bench 4.0 page hydration, published model/effort/agent retained as model proxies | `terminal_proxy` | 168h / 30d |

- **Response Handling**: 20 MiB response cap; request limits: aa 50, arena 300, mg 4, tb_auto 3. Status 401, 403, and 429 are never retried; 5xx and network errors retry up to 2 times.
- **Timeouts**: Global timeout of **180s** per source (**600s** for arena). Per-request timeouts and backoffs dynamically scale down within remaining budgets.
- **Failure Recovery**: If any page fails or schemas diverge, new data for that source is not published, retaining last-good snapshots. Identical payloads mark `unchanged` and update check timestamps.
- **Storage**: SQLite (`bench-router.db`: sources / snapshots / observations) retains the 3 most recent raw payloads per source. Concurrent refreshes are blocked via OS file locks.
- **Publishing**: `snapshot.json` is written to a temporary file, fsynced, and swapped via `os.replace`. The prior valid snapshot moves to `snapshot.last-good.json`; reproducible copies remain in `snapshots/` for 30 days.
- **Router Consumption**: If the snapshot is missing or corrupted, last-good is used. If unavailable, default policies flag missing evaluations and request provisional decisions. `route` never triggers refresh runs.
- **Arena Name Collisions**: Multiple entries with identical names can occur in source data. They are included in cohorts but disambiguated as `name#rank=N` to prevent accidental name-only matches.

Manual import format (`--import FILE`):

```json
{"schema_version": "1.0", "evidence_id": "terminal_exact",
 "source_url": "https://www.tbench.ai/", "attribution": "Terminal-Bench",
 "published_at": "2026-10-01",
 "benchmark": {"suite": "terminal-bench", "version": "4.0", "subset": "core",
               "metric": "resolved_rate", "direction": "higher", "variant": "default",
               "dataset_revision": "v4.0.0", "evaluation_harness": "terminal-bench-official",
               "aggregation": "pass@1_mean_5"},
 "rows": [{"model_id": "claude-opus-5-5", "harness_id": "claude-code",
           "reasoning_effort": "high", "raw": 0.61}]}
```

`harness_id` identifies the agent scaffold (e.g. Claude Code); `evaluation_harness` identifies the evaluation and scoring harness. `model_id` records the exact evaluated model version. Scores are grouped into normalized cohorts only when benchmark versions, dataset revisions, variants, evaluation harnesses, scaffolds, reasoning efforts, and aggregation methods match. Exact evidence requires matching profile `model_id`, `harness_id`, and `reasoning_effort`. Existing exact scores in cache lacking new conditions are excluded as `missing_conditions` until re-imported. Automated metrics lacking explicit conditions record `null` and serve strictly as model-level proxy evidence.

<a id="정기-실행-예시-설치하지-않음"></a>
<a id="periodic-execution-example-not-installed"></a>
### Periodic Execution (Example, Not Installed)

`refresh` executes once and exits. The following systemd example applies to Linux or WSL2; users must configure and activate services and timers independently. On Windows, use Windows Task Scheduler.

```ini
# ~/.config/systemd/user/bench-router-refresh.service
[Service]
Type=oneshot
WorkingDirectory=/path/to/bench-router-handoff
EnvironmentFile=%h/.config/bench-router/env
ExecStart=/usr/bin/python3 -m bench_router.cli refresh

# ~/.config/systemd/user/bench-router-refresh.timer
[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true
[Install]
WantedBy=timers.target
```

---

## Live Dispatch and Result Contracts

<a id="runners"></a>
### Runners

The global `--runner auto|herdr|local|external` option (env `BENCH_ROUTER_RUNNER`, default `auto`) selects the executor of a new live `route`/`parallel` run. `auto` resolves to `herdr` when `herdr-projects` (`BENCH_ROUTER_PROJECTS`) is on PATH and to `local` otherwise. The choice is recorded as the receipt `backend` (`projects-1.2`, `local-1`, `external-1`). `collect`, `stop` and re-dispatch of the same task/round follow the recorded backend, not the current flag. Every runner shares the receipt, coordination (four-active limit, overlap guard), nonce and result contract below.

| Runner | Executes | Tasks | Worktree | `stop` | `tell`/`resume` |
|---|---|---|---|---|---|
| `herdr` | Projects board agent or Herdr pane | interactive, headless | Projects/Herdr | board stop / workspace close | yes (board runs) |
| `local` | profile one-shot CLI as a detached `sh -c` subprocess (own session, output in `runs/RUN/output.log`) | headless only | `git worktree add` under `.bench-router/worktrees/runs/RUN` | SIGTERM to the process group | no |
| `external` | nothing; the caller runs the agent | any | same as local | records the caller's statement that its agent stopped | no |

`external` returns `handed_off` (exit 11) plus `invocation`: `cwd` (worktree), `prompt_path` (prompt with result contract), `result_dir`, `argv` (suggested one-shot CLI for CLI profiles, else null), `model_id` and `deadline_at`. It does not probe local CLIs (availability stays unverified), so schema 2.0 caller-owned profiles are eligible; `local` and `herdr` exclude them as `unsupported_execution_profile`. `collect` on an external run completes once `result_dir` holds a valid `result.json`/`result.md` pair; a re-dispatch of the same round reports without waiting.

Live `route` (without `--dry-run`) proceeds as follows:

1. Checks PATH availability and constraints to select a profile, pinning Projects version and session to the receipt. Live credentials and model access are verified by the target agent.
2. Acquires `<cwd>/.bench-router/dispatch.lock`. Dispatches run serially per cwd.
3. Existing receipts matching `(task_id, round)` branch based on content hash: identical hashes recover existing runs via **collect without retransmission**; divergent hashes trigger `conflict`. Unresolved prior runs block new delegations (`unresolved_run`).
4. Generates a UUID `run_id` and 128-bit nonce, atomically writing the receipt. Selection rationale is recorded in `decision.json`.
5. Translates profile `kind/args` into board configuration (`--worker.agent kind/model`, `--worker.effort`). Non-translatable arguments terminate with `execution_failed`. Atomically writes `input.txt`.
6. Fsyncs `submission_attempted` to the receipt **prior** to submission. Invokes `add br-<run_id> --desc PROMPT --repo CWD --delegate` **exactly once** and records the returned board task ID (`thread_id`, e.g. `repo/12`). Disables automated review, attempts, plans, and merges (`--review.when never`, `--merge.by you`), adopting board `worker.access`.
7. When board stage reaches `approval`/`done`, validates result contracts in the task worktree. Blocked states return single-line board diagnostics (`diagnostic_tail`). Timeouts and stalled runs record `timed_out`/`delivery_uncertain` without retransmitting.

Reaching `completed` closes the agent pane to release system resources (`release`). Active or prompt-waiting agents are left open. Resuming conversation context uses `python3 -m bench_router.cli resume --cwd CWD --run-id RUN` to reopen the board task and restart the agent in the same session.

The execution contract appends to the prompt. Agents must write two files to `.bench-router/runs/<run_id>/` inside their assigned worktree. Upon passing validation, the router copies them to `<cwd>/.bench-router/runs/<run_id>/`. The `.bench-router/` directory is registered in `info/exclude` to prevent pollution of board commits:

- `result.md`: Report of findings, changes, verification, and open items (max 10 MiB, non-empty).
- `result.json`: Manifest written once at completion (max 64 KiB).

```json
{"schema_version": "1.0", "run_id": "...", "nonce": "...", "profile_fingerprint": "...",
 "status": "success|partial|fail", "result_file": "result.md",
 "result_sha256": "<sha256 of result.md>",
 "checks": [{"command": "...", "outcome": "passed|failed|not_run", "notes": "..."}]}
```

The router marks `completed` only when:
- run_id, nonce, and profile fingerprint match
- Target files are regular files (not symlinks or references outside the run directory)
- File size, UTF-8 validity, and JSON syntax checks pass
- SHA-256 hash matches `result.md`

`completed` certifies receipt compliance, not task correctness. Substantive results are reflected in `task_outcome` (agent self-report). Orchestrators must review substantive success and record verdicts via `feedback`. Evaluated agents have previously reported `success` despite incorrect code changes.

The run directory preserves `receipt.json`, `decision.json`, `input.txt`, `result.md`, `result.json`, and `feedback.jsonl`. Verify status in Projects using `project` and `thread_id`. Terminating active threads terminates the agent; inspect effects before cleanup.

<a id="병렬-위임과-협업-수준"></a>
<a id="parallel-dispatch-and-collaboration-levels"></a>
## Parallel Dispatch and Collaboration Levels

`parallel --group FILE` binds multiple tasks and execution instances. Group 2.0 accepts task contexts and explicit selections, permitting repeated profiles. Bounded by 8 tasks per group, 16 items total, and `max_parallel` 1–4. Schema 1.0 fanout uses the same vendor-guided policy without automated score rankings.

For each member, a router worktree is created at `<cwd>/.bench-router/worktrees/<group_id>/<label>` (branch `br/<group_id>/<label>`, based on HEAD), providing receipt and lock isolation. Agents operate in additional worktrees created by Projects. Re-running the same group file recovers saved plans and receipts without retransmission. Worktrees, group files, and workers are never provisioned before all selections complete.

Schema 1.0 input structure (illustrative; multiple candidates request upstream selection rather than auto-selecting two):

```json
{"schema_version": "1.0", "group_id": "fix-pager", "cwd": "/home/me/project",
 "isolation": "shared", "fanout": 2, "max_parallel": 4,
 "tasks": [{"schema_version": "1.0", "task_id": "pager", "round": 1,
            "summary": "Fix paginate off-by-one", "prompt": "..."}]}
```

- `cwd` must be the root of a Git repository; tasks do not specify `cwd`. `tasks × fanout ≤ 16`, `fanout` 1–8, `max_parallel` 1–4 (matching shared admission limits).
- Group 1.0 repeats Policy 6 while excluding previously chosen profiles from subsequent comparisons. Depleted candidates return `fanout_reduced`; multiple viable candidates return `decision_unavailable`. Group 2.0 dispatches the explicit selection list with labels `<task_id>-<k>`.
- **The root repository must be trusted by each Agent CLI beforehand.** Untrusted repositories trigger trust prompts during worker launch, pausing in `blocked`. Trusting the root repository covers child worktrees for both Claude and Codex.
- Uncommitted changes do not carry into worktrees (`dirty_base` warning). Router worktrees provide receipt isolation, while real agent edits commit to board worktrees (`work/br-<run_id>`). Comparing, merging, and cleaning up worktrees is managed by the Orchestrator.

| `isolation` | Behavior |
|---|---|
| `isolated` (default) | Worktree isolation only. Agents remain unaware of each other |
| `shared` | Shared scratchpad at `<cwd>/.bench-router/groups/<group_id>/shared/`. Agents write only to their own `<label>.md` and `<label>/` subdirectories and read peer notes to share dead ends, observations, and intermediate results. Because the scratchpad resides outside the worktree, board `worker.access ask` requires approval on each write (`blocked`) |

Execution outputs contain member profiles, worktrees, branches, and rounds with status, run_id, receipt_path, result_path, task_outcome, delivery_state, and reassignment. Results persist in `groups/GROUP/group.json`. All completed returns 0; partial completions or failures return `partial_failure` (16); conflicts return 14. Pre-dispatch incomplete decisions return 17, stale inputs return 14, and empty candidate sets return 13. Uncertain members follow `collect_first`.

<a id="agent-간-통신"></a>
<a id="inter-agent-communication"></a>
### Inter-Agent Communication

The router does not implement multi-agent patterns directly; it provides primitive communication building blocks composed by the Orchestrator.

| Block | Direction | Command |
|---|---|---|
| Task Handoff | Orchestrator → Agent, start | `route` / `parallel`. `--wait-ms 0` returns `timed_out` (in progress) and run_id immediately after dispatch |
| Result Collection | Agent → Orchestrator, end | `collect --cwd --run-id [--wait-ms]`, validates result contracts. Parallel re-runs group file |
| Mid-Run Steering | Orchestrator → Agent, mid-run | `tell` (interactive execution only) |
| Shared State | Agent ↔ Agent, mid-run | `isolation: shared` shared scratchpad |
| Progress & Queries | Agent → Orchestrator, mid-run | `collect` `blocked` state, board diagnostics, shared notes |

Two common orchestration utilities are provided:

| Utility | Command | Behavior |
|---|---|---|
| Multi-run Waiting | `collect --run CWD RUN_ID [--run …] --until any\|all [--wait-ms N]` | Polls runs via `collect`. `any` returns `ok` and `ready` (run_id list) when any run settles or blocks; `all` waits for all. Times out with `timed_out` |
| Cancellation | `stop --cwd CWD [--run-id RUN]` | Invokes board `stop` (or closes workspace in headless mode), logging to `messages.jsonl`. Next `collect` marks `execution_failed` and releases concurrency admission |

Example: In best-of-N, dispatch N attempts with `--wait-ms 0`, observe completion via `collect --run … --until any`, review the winning result, and `stop` remaining runs. Multi-round voting proceeds via new `route` rounds containing previous deliverables.

Member router worktrees reside at `<cwd>/.bench-router/worktrees/<group_id>/<label>`, displayed in `--dry-run` output. Because they hold only one incomplete run at a time, `tell` can be invoked without `--run-id`.

<a id="비대화형-실행"></a>
<a id="headless-execution"></a>
### Headless Execution

Setting `"execution": "headless"` in the task runs one-shot CLIs instead of interactive board agents. Default is `interactive`.

1. `herdr worktree create` builds `<cwd>/.bench-router/worktrees/runs/<run_id>` (branch `br/<run_id>`) and pane.
2. Adds an agentless task (`br-<run_id>`) to the board, using `report` to show working → done/error status. Board tasks are display-only; board failures do not interrupt CLI execution.
3. Runs `claude -p`, `codex exec`, or `agy -p` inside the pane with profile model and effort settings. Prompts pass via `runs/<run_id>/input.txt` rather than argv. Exit codes persist in `runs/<run_id>/exit_code`.
4. `collect` validates `exit_code` and result contracts rather than board stages. Running processes return `timed_out`; closed panes return `execution_failed`. Panes close upon completion.

- Supported kinds: claude, codex, agy. Profile args are restricted to model and effort (identical to interactive mode).
- **Executes with permission prompts bypassed** because no interactive user is present (`--dangerously-skip-permissions`, or `--dangerously-bypass-approvals-and-sandbox` in Codex). Restrict to trusted repositories.
- Mid-run messages are rejected (`tell` unsupported). Communication is limited to initial inputs, result contracts, and shared scratchpads.

---

## Testing

```bash
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn
```

| File | Scope |
|---|---|
| `test_p0.py` | Inputs, metrics, constraints, default evaluation, wiki/facet/evidence, Policy 6 stages, guidelines, public evaluation, upstream selection |
| `test_p1.py` | Ingestion and caching (V11–V18): pagination, last-good fallback, payload hashing, HTTP errors/timeouts, locking, atomic publish, aliases, and cohorting |
| `test_p3.py` | Parallel dispatch (V30–V34): worktree isolation, fanout, shared scratchpads, re-run idempotency (requires git) |
| `test_p2.py` | Delegation (V19–V29): argv handoff, task ID capture, launch failures, pre-submission states, result contracts, path traversal prevention, timeout idempotency, crash recovery, conflict locks |
| `test_coordination.py` | Shared admission limits, path collision prevention, ownership, adoption records, stoppage verification |
| `test_codeburn.py` | Availability, quota, usage metrics, profile discovery fixtures |

Live execution tests use test doubles conforming to Projects 1.2.1 CLI (`src/cli/tasks.rs`), constructing real temporary `git worktree` instances per task. Historical direct Herdr smoke tests reflect earlier execution pathways and do not certify Projects live operations. Empirical evidence resides in `docs/evidence/` (herdr help, API schema, skills, claude/codex `--help`).

---

## Verification Status (2026-10-12)

The historical records below reflect direct Herdr execution under legacy policies. As of 2026-10-24, the offline test suite passes 163 of 165 tests (2 skipped); environmental limitations are detailed in [Implementation Status](implementation-status.md). Do not confuse historical 35/35 counts with the current test suite. These records do not validate quality or cost under Policy 6 and Projects live dispatch.

| Item | Result |
|---|---|
| Offline Tests | 35/35 passed |
| AA Live Call | Success (Free tier, index v4.3, 4 pages, 697 models) |
| Arena Live Call | Success (revision `e16f9023…`). During HF outages, failed at 180s timeout, retaining last-good snapshots |
| herdr + Claude Code / Codex Live Delegation | Success. Blocked unresolved runs, zero duplicate transmissions, verified result hashes, clean collect |
| Live Score Comparison between Two Candidates | Selected codex on general/balanced task; reached completed |
| `parallel` Live (2026-10-13; deliberate mode, now removed; fanout 2: claude + codex) | Ran concurrently in two worktrees; both rounds completed; shared notes and voting confirmed (`winner=null`); clean main worktree (~2 min) |
| Benchmark Suite v1 (20 tasks × 2 profiles) | [eval/results/v1.md](../eval/results/v1.md), Cost: [v1-cost.md](../eval/results/v1-cost.md) |

Summary of benchmark suite v1 (single attempt per task; not a statistical proof):

| Policy | Success Rate | API-Equivalent Cost per Success |
|---|---|---|
| Fixed default (claude) | 20/20 | $0.234 |
| Low-cost-first (codex) | 19/20 | $0.070 |
| bench-router | 20/20 | $0.217 |

Simpler tasks caused success rate ceiling effects; bench-router matched default selections in 18 of 20 tasks (12 due to sparse evidence). Costs reflect token counts converted to API list prices, not actual subscription expenditures (`eval/cost.py`).

### Evaluation Tools

```bash
python3 eval/workset.py            # Self-check: initial state fails, reference answers pass
python3 eval/run.py --tag T        # Dispatches live per (task, profile) + hidden checks (session 'breval')
python3 eval/cost.py --tag T       # Aggregates tokens and API-equivalent costs per run
```

---

## Known Limitations

- **Evidence data may have gaps.** Missing AA coding metrics, uncollected manual exact benchmarks, and harness/effort differences are recorded as diagnostics. Missing data is never converted to default selections or treated as a score of zero.
- `cost_tier` values are policy categories, not empirical billing amounts.
- Profile fingerprints do not encode CLI versions (`unknown`).
- Decisions and feedback are preserved as files in run directories rather than SQLite. Execution token consumption is not aggregated within the router (measured only in evaluation tools).
- Remote dispatch (`--machine`), automated agent pools, and embedding classifiers are not implemented. Wait reductions use `--wait-ms` and `collect`; session resumption uses `resume`. Bounded LLM judgments operate via Jev/native decision stages.
- File locks use `fcntl` on Linux/WSL2 and `msvcrt` on Windows. Do not share caches concurrently across native Windows and WSL. Projects live execution requires Linux or WSL2.
- Prompts pass as Herdr argv parameters, visible in local process listings.

## Decisions Changed from Initial Design

| Initial Design | Current Implementation | Rationale |
|---|---|---|
| Result contracts: write `result.json` atomically | "Write once at completion; compute `sha256sum`" | Demanding atomic writes prompted agents to execute helper scripts and `mv`, stalling in approval pauses. The router validates only after agent exit and verifies hashes, making atomic writing unnecessary |
| Store decisions and feedback in SQLite | Files in run directories: `decision.json`, `feedback.jsonl` | Directory files suffice until aggregation queries are required |
| Dependency-free Arena Parquet parsing | Direct Parquet decoding via `pyarrow` | Hugging Face datasets-server `/filter` endpoints suffered 20–60s latencies and frequent 5xx errors, dropping wiki units (2026-10-21). Environments without `pyarrow` fail only Arena refresh, falling back to last-good snapshots |
| Conditional GET (304) | Mark `unchanged` when payload hashes match | AA and HF documentation lack ETag specifications |
| Unbounded refresh retries | 180s global timeout per source (600s for Arena) | Prevents runaway accumulation of requests, retries, and backoff delays |

## Licenses and Attribution

- Arena data: LMArena `leaderboard-dataset`, CC BY 4.0. Recorded in `sources.*.attribution` within snapshots.
- The Model Gap data: `themodelgap.com`, CC BY 4.0.
- AA data: Artificial Analysis. Attribution required when sharing or displaying.
- API credentials must be stored strictly in configuration files (`env`, permissions `chmod 600`), never committed to repositories or exposed in logs.
