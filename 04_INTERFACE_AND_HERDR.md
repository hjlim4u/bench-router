# CLI, JSON, and Execution Contracts

Updated: 2026-10-24. Live execution follows [Projects Contract](docs/projects.md), selection follows [Vendor-guided Policy 6](docs/vendor-guided-routing.md), and metrics/digests follow [Routing Contracts](docs/routing-contracts.md).

## CLI

Global options are `--config-dir`, `--cache-dir`, and `--herdr-session`, placed before subcommands. Refer to `--help` for exact arguments.

| Command | Behavior |
|---|---|
| `route --task FILE --dry-run` / `explain --task FILE` | Offline decision packet and selection replay / Text explanation covering all candidates and constraints |
| `route --task FILE [--wait-ms N]` | Live submission and finite wait after selection; 0 returns immediately after submission |
| `evaluate --task FILE [--context FILE] [--format 1\|2\|3]` | Evaluation without selection. Default schema 2.0; format 3 yields schema 4.0 |
| `select --assessment FILE --profile ID --policy-id ID --policy-version V --reason TEXT [--accept-provisional]` | Generates selection 6.0 from completed format 3 evaluation. No execution or side-effects |
| `route --task FILE --selection FILE [--dry-run]` | Validates and replays selection 2.0, 5.0, or 6.0 |
| `route --task FILE --profile ID [--dry-run]` | Explicit unrecorded override; emits warning |
| `parallel --group FILE [--dry-run] [--wait-ms N]` | Per-task selection, worktree, and group execution with identical plan recovery |
| `refresh [--source ID] [--force] [--vault DIR]` / `--import FILE` | Collection, wiki index, and snapshot update / Approved SWE & TB manual import |
| `status` / `profiles discover [--force]` | Inspect cache & config status / Generate profiles (existing files require `--force`) |
| `wiki compile [--check]` / `wiki facets` | Compile & validate reviewed wiki / Inspect facet vocabulary |
| `evidence --task FILE [--format json\|table] [--max-units N]` | Query per-facet evidence; default 12 units, unranked |
| `collect --run-id ID --cwd DIR [--wait-ms N]` | Inspect existing receipt and retrieve results without resubmission |
| `collect --run CWD ID [--run …] --until any\|all [--wait-ms N]` | Monitor settlement or blocked state across multiple runs |
| `tell --cwd DIR [--run-id ID] --message TEXT` / `--message-file FILE` | Send explicit message to active or resumed interactive run |
| `stop --cwd DIR [--run-id ID]` / `resume --cwd DIR --run-id ID` | Explicit abort / Reopen completed conversation (no transmission) |
| `feedback --run-id ID --cwd DIR --outcome success\|partial\|fail` | Record Orchestrator verification outcome |
| `coordination status\|release\|feedback` | Shared admission & quiescence check followed by release or adoption recording |

Optional command arguments in the table are mutually exclusive in actual invocations. Stdout produces a single JSON object, except for `explain` and `evidence --format table` which output plain text. `dry-run`, `evaluate`, `explain`, and `evidence` operate without network, Herdr, or disk writes. `route`, `explain`, `parallel`, and `evaluate` accept `--host antigravity|codex|claude` and `--decision-response`. Response inputs to `evaluate` are allowed only under format 3. `--selection` and `--profile` are mutually exclusive, and neither may be combined with `--decision-response`.

| Exit Code | Meaning |
|---|---|
| 0 | selected, completed, ok, normal completion of record/control commands |
| 2 | Validation error on input, config, or arguments; unsupported schema |
| 10 | blocked; awaiting approval or answering questions |
| 11 | waiting, timed_out, delivery_uncertain; run may still be active |
| 12 | execution_failed, result_invalid |
| 13 | no_eligible_profile |
| 14 | conflict; lock/admission denied; stale_assessment |
| 15 | Storage or I/O error |
| 16 | Partial or complete refresh failure; preserves per-source last-known-good |
| 17 | decision_required, decision_unavailable; phase response or upstream selection needed |

## Input Contract

Task required fields are `schema_version="1.0"`, `task_id`, `round`, `summary`, `prompt`, and `cwd`.

- `task_id`: `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`, `round`: integer ≥1. Per-execution UUID `run_id` is generated independently.
- `summary`: Non-empty string, max 4,000 characters; `prompt`: UTF-8, max 256 KiB. Task file size limit is 1 MiB.
- `cwd`: Must exist as an absolute directory, resolved to its real canonical path. Live execution requires it to be a Git root with commits.
- `context_files`: Relative paths within `cwd`. Rejects directory traversal; does not automatically copy or upload file contents externally.
- Constraints defaults: `max_cost_tier=high`, `min_context_tokens=0`, `local_only=false`, `timeout_ms=900000`, `required_capabilities=[]`. Timeout range is 1,000–3,600,000 ms.
- `priority=quality|balanced|cost` (default `balanced`) is a compatibility field; not used for automated cost-based ranking. `exclude_profiles` provides an exclusion list.
- `execution=interactive|headless` (default `interactive`). Headless runs one-shot CLI and does not accept `tell`.
- `facets={axis: [value]}` specifies explicit task attributes. Uses vocabulary from `wiki facets` and feeds vendor-guided decisions and evidence queries. Kept separate from base `semantic_task_hash` but bundled into decision inputs.
- Unknown fields, NaN/Infinity, duplicate JSON keys, or malformed UTF-8 trigger validation errors.

Interactive submissions combine task and execution contracts under a 120 KiB limit and may expose text in process argv. Headless passes prompts via `input.txt`. `local_only` denotes locality of model inference; running cloud models is never permitted solely because Herdr itself executes locally.

`semantic_task_hash` bundles prompt, summary, constraints, priority, cwd, context_files, and exclude_profiles (plus execution for headless). `task_id` and `round` define receipt identity. File contents are not hashed, leaving artifact revision management to the upstream Orchestrator.

## Profile Configuration Contract

The TOML configuration requires `schema_version="1.0"` and `[[profile]]` entries. Required profile keys are: `id`, `enabled`, `kind`, `executable`, `args`, `model_id`, `harness_id`, `reasoning_effort`, `config_revision`, `cost_tier`, `inference_local`, `context_tokens`, and `capabilities`. Unregistered keys are rejected.

`id` matches `[a-z][a-z0-9_-]{0,47}`. `executable` must equal `kind`, and `args` is an argv array, not a shell string. Current Projects transformation accepts only model (`--model`/`-m`) and effort (`--effort`, Codex `-c model_reasoning_effort=...`). Other permission and tool flags are rejected prior to submission. Interactive permissions follow Projects `worker.access` configuration.

`model`, `harness`, and `effort` are preserved separately from evaluation matching. `context_tokens=0` represents unknown capacity and cannot satisfy positive context demands. `reasoning_effort=unknown` prevents exact matching and marks guidelines as missing. Changing `config_revision` updates the configuration fingerprint, while CLI version currently defaults to `unknown`.

[profiles.example.toml](examples/profiles.example.toml) contains disabled placeholders. `profiles discover` inspects executable CLIs to collect model and effort details into active profiles, but cannot guarantee successful live invocations. Live probes check PATH, agy models, and optional CodeBurn status; actual model runtime execution success is verified separately.

## Output and Selection Records

The route envelope uses schema 1.0 and contains: `status`, `task_id`, `round`, `run_id`, `selected`, `selection_mode`, `classification`, `candidates`, `excluded`, `snapshot_id`, `policy_version`, `config_hash`, `warnings`, `sources`, and `assessment_digest`. Vendor-guided mode also includes decision inputs, phase rationale, and candidate facts. In CLI route output, `candidates` summarizes the first 3 by ID, recording total count in `candidates_total` (this is not a top-3 ranking).

Default evaluate formats 1 and 2 provide candidate `quality`, `coverage`, `coverage_band`, `exact_evidence_weight`, and `evidence`. Fields `score`, `legacy_score`, and `cost_proxy` are omitted. Because candidate quality/coverage in basic route output does not reflect category evaluation results, read semantic decision evidence from `decision.evaluation` or `selection.decision.evaluation`. Use format 3 for constraint evaluations and public candidate suitability.

| Contract | Version |
|---|---|
| evaluate default / compatibility | 2.0 / 1.0 |
| assessment in `evaluate --format 3` | 4.0 |
| automatic single-candidate / upstream selection | 5.0 / 6.0 |
| explicit override selection | 2.0 |
| context / group | 2.0 (accepts 1.0 input) |

Legacy vendor-guided selection schemas 3.0 and 4.0 must be re-evaluated. `select` returns a 6.0 record within the `selection` object of a schema 1.0 envelope; only that object should be used as input. Schemas 5.0 and 6.0 include replayable task, stages, evaluation, uncertainty, and input digests. For field details, refer to [Upstream Integration](docs/orchestrator.md).

Live responses append: `receipt_path`, result path, `task_outcome`, `delivery_state`, `reassignment`, `coordination_key`, `thread_id`, `worktree`, `branch`, etc. On `completed`, the result path is a valid absolute path. Per-source dates are preserved rather than collapsed into a single composite date.

## Execution and Deduplication

1. Checks for an existing receipt matching the same `task_id` and `round` first. An identical semantic hash initiates `collect` without resubmission; differing contents or conflicting specified profiles yield a `conflict`. Recovering existing runs takes precedence over evaluating new policy decisions.
2. New execution checks constraints, selection replay, and current availability. Shared admission limits active runs to 4, checks path overlaps, and acquires the cwd dispatch lock.
3. Generates UUID `run_id`, 128-bit nonce, profile fingerprint, deadline, selection, and `input.txt` inside the run directory. Atomically publishes receipt and decision.
4. Interactive calls Projects 1.2.1 `add`/`delegate` once and records the board task ID. Headless launches a one-shot CLI inside a Herdr worktree pane. Execution intent is fsynced prior to external invocation.
5. Interactive verifies result contracts upon board `approval`/`done`; headless verifies upon process exit. Neither automatically resubmits, delegates to other workers, nor cancels when `blocked`, `timed_out`, or `delivery_uncertain`.
6. Pre-submission failures settle receipts and release admission slots. Uncertain submission delivery preserves state, requiring `collect` and quiescence checks.
7. `completed` releases managed panes. `resume` reopens completed sessions without re-sending inputs. `stop` and `tell` run strictly on explicit request.

Groups validate all selections upfront, assigning dedicated labels, worktrees, and receipts even for repeated profiles. Limits: max 8 tasks per group, max 16 items per group, `max_parallel` 1–4. Freezes the execution plan; identical inputs recover existing receipts. Delivers `delivery_state` and `reassignment` across group rounds.

## Subagent Result Contract

The worker completes `result.md` within `.bench-router/runs/<run_id>/` in its worktree, writing `result.json` in a single atomic operation at the end. Workers are instructed to compute the final hash using `sha256sum result.md`. The wrapper's atomic receipt/input persistence is strictly decoupled from the worker's manifest generation instructions.

```json
{"schema_version":"1.0", "run_id":"<RUN_ID>", "nonce":"<NONCE>",
 "profile_fingerprint":"<FINGERPRINT>", "status":"success",
 "result_file":"result.md", "result_sha256":"<SHA256>",
 "checks":[{"command":"verification command", "outcome":"passed", "notes":"verification notes"}]}
```

Manifest `status` is `success|partial|fail`, and `checks.outcome` is `passed|failed|not_run`. `checks` accepts an empty array and represents the worker's claims; the router does not automatically execute these commands. The Markdown file records modifications, verifications, and incomplete items. Examples: [result.synthetic.json](examples/result.synthetic.json) and [result.synthetic.md](examples/result.synthetic.md).

The router validates run ID, nonce, fingerprint, status, UTF-8 validity, regular file status, path locality, symlink escaping, size, and hash. `result.md` must be non-empty and ≤10 MiB; the manifest must be ≤64 KiB. Validated results are copied to the original cwd run directory. A `DONE` terminal line is secondary telemetry and does not substitute for the result contract. The nonce prevents confusion with stale files but does not serve as an anti-tamper security token.

## States and Follow-up Actions

| Outcome | Follow-up Action |
|---|---|
| decision_required / decision_unavailable | Complete phase responses or upstream selection; no execution performed |
| stale_assessment | Re-evaluate and re-select if no identical submission exists |
| blocked | Handle user approval or questions, then collect |
| timed_out / delivery_uncertain | Execution may be ongoing; perform `collect` first |
| execution_failed / result_invalid | Inspect transmission, partial side effects, and worker status before deciding reassignment |
| completed | Review `task_outcome`, result contents, and working branch; determine feedback and merge adoption |

`completed` certifies receipt of a well-formed result complying with the format contract. Upstream is responsible for assessing substantive correctness. Retries must not resubmit identical task/rounds blindly; verify quiescence and partial effects, then execute as an explicit new round.
