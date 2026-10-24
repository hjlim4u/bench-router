# External Evidence, Dependencies, and Verification Scope

Original research date: 2026-10-12 · Implementation alignment update: 2026-10-24. The E1 and U descriptions below record external evidence from the time of original research. This update did not re-query live external sites or account endpoints. Current implementation and subsequent validations follow the table below and [Implementation Status](docs/implementation-status.md).

| Component | Current Implementation / Verification Scope |
|---|---|
| Core CLI | Python 3.11+ standard library, executable module without extra installation |
| Arena | Revision-pinned Parquet decoded directly via `pyarrow`; collects active wiki units |
| AA / MG | AA pagination, The Model Gap public JSON adapter implemented; past live call records exist |
| SWE / TB | Approved manual imports with recorded evaluation conditions; pins Verified / TB 4.0 |
| Semantic Decision | Implements analysis, vendor-specific guidance, and benchmark phases via Jev or native bench-decider |
| Execution | Interactive via Projects 1.2.1 / headless via Herdr; current regression tests use fake CLI and actual temporary Git worktrees |
| Ancillary Tools | Optional install via uv/mise; integrated CodeBurn availability, quota, and profile discovery |

Official guidance texts and versions per model are pinned in `bench_router/guidelines.toml` and are not queried over the web at runtime. Policy 6 and record schemas are located in [Vendor-guided Routing](docs/vendor-guided-routing.md). Price, speed, and score deltas from secondary sources are never hardcoded as constants in the implementation.

## Evidence Levels

- E1: Confirmed via official web documentation.
- E2: Confirmed via live account response or installed binary. (Not present in original survey below; refer to implementation status and eval documents for subsequent live measurements across AA, Arena, MG, and direct Herdr).
- P: Policy established by this handoff. Not evidence of external performance.
- U: Requires further verification.

## Reuse Candidates

| Tool | Relevant Capabilities Confirmed via E1 | Usage Assessment |
| --- | --- | --- |
| [RouteLLM](https://github.com/lm-sys/RouteLLM) | Strong/weak pairs, preference-based router, API-compatible server, calibration/evaluation | Candidate for preference-based routing comparisons. No turnkey configuration confirmed that replaces data collection, profiles, and herdr execution |
| [Switchyard](https://github.com/NVIDIA-NeMo/Switchyard) | Model-pool routing, task/execution/composite strategies, gateway/library integration, pre-1.0 | Current README scope is broader than early drafts, including sub-agent strategies. Full replacement of CLI profiles + external scores + herdr contracts requires independent validation |
| [semantic-router](https://github.com/aurelio-labs/semantic-router) | Example utterances and vector-space route matching | Cost/benefit comparison against small local implementation if L2 necessity is demonstrated. Not added as MVP dependency |
| [Jev Official Docs](https://docs.typesafe.ai/introduction) | Choice/Score/Noul, structured responses, probability/confidence | L3 optional component. Typed output does not inherently guarantee semantic accuracy |
| [herdr Official Docs](https://herdr.dev/docs/) | Terminal and Agent automation | Required execution backend. Pinned to installed version and matching documentation |

RouteLLM is not restricted to "within a single Agent". Routing components that direct API calls can also be applied to upstream Agent selection, but would require additional integration of this project's data, profile, and delegation contracts.

## Data Source E1 Summaries and Local Action Items

### S-AA — Artificial Analysis

Official: [API docs](https://artificialanalysis.ai/data-api/docs)

E1: Free language endpoint is `/api/v2/language/models/free` using `x-api-key` authentication. Free quota is 100 requests per rolling 24-hour window, and quota scope may exceed a single key. Responses provide pagination and data payload. Provides headline Intelligence/Coding/Agentic scores, pricing, and median latency/throughput, but the Free tier omits Pro fields such as context window. No math-dedicated index was confirmed in documentation. Attribution required when sharing or displaying.

Local: Verify actual page count, null handling, index versions, applicable fields on Free tier, rate-limit headers, and redistribution terms. Pricing is a proxy for API provisioning costs and should not be equated with actual CLI subscription expenses. Never commit secrets to auth examples or logs.

### S-ARENA — Arena dataset

Official: [dataset card](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset), [files](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/tree/main)

E1: CC BY 4.0 license, latest/full split, text/vision/document style-control subsets, and webdev. Traditional subset rating and Agent Arena subset IPS score are different metrics. Do not refer to all ratings collectively as "Elo".

Local: Verify subset/category lists, actual file layout, columns, and pin revision and publish date. Even for public datasets, validate download methods and request counts. Do not generalize webdev into generic coding capability. Do not assume harnesses are identical just because Agent Arena is present.

### S-TB — Terminal-Bench

Official: [leaderboard](https://www.tbench.ai/)

E1: Current official interface is Terminal-Bench 4.0, distinguishing MODEL / AGENT / resolution rate columns. Static scraping of the page yielded no extractable data rows.

U: No stable result API or file path confirmed. Import user-approved manual snapshots with recorded source, baseline date, version, and evaluation configuration. If 2.0 results are needed, retrieve the official artifact for that version and store under an independent benchmark ID. Never fabricate missing data.

### S-SWE — SWE-bench

Official: [leaderboards](https://www.swebench.com/)

E1: Verified is a human-filtered 500-instance subset. Current default Bash Only view explicitly states the mini-SWE-agent environment. Uses % Resolved.

Local: Verify exact path, commit, agent configuration, and evaluation split in official result files/repository. Do not map mini-SWE-agent scores directly to codex-cli or claude-code. Treat SWE-bench Pro and Verified as distinct sources and versions. This handoff does not finalize a Pro collection path.

## herdr Official Evidence and Interpretation Boundaries

Official: [Agent automation](https://herdr.dev/docs/agent-automation/), [CLI reference](https://herdr.dev/docs/cli-reference/), [repository](https://github.com/herdrdev/herdr)

E1: Layout creation and Agent start are decoupled operations. Agents are controlled by name or current pane ID. `start` executes in an existing shell pane and waits for readiness. Provides `prompt/wait/read` and JSON schema extraction. Documentation recommends having lengthy outputs written directly to files.

E1: `prompt --wait` does not trace individual turns. Sending input while working may allow prior turn completion to satisfy the wait condition. `idle/done` indicates input readiness, not success certification. Timeout or stalled state alone cannot determine non-delivery.

herdr cannot be assumed to natively provide task-level exactly-once semantics or structured results. The wrapper maintains receipts and run-bound result contracts. Plugin usage, unsettled in initial research, was subsequently implemented via the public Projects 1.2.1 CLI. Remote execution via `--machine` is not implemented.

## Dependency Evidence to be Recorded by Successor Agents

1. OS, Python version, git revision, `herdr --version`, and server status.
2. `herdr api schema --json` and relevant `--help` outputs for the installed version.
3. Candidate CLI `--version`, model arguments, reasoning settings, authentication readiness.
4. Sanitized real source response fixtures, with response schema, revision, and hash.
5. URL, `retrieved_at`, `published/evaluated_at`, license/attribution, request counts.
6. Commands and outputs elevating facts from E1 to E2, explicitly displaying failures or unverified states.

URLs in this document are initial references, not immutable API guarantees. Never claim API success without valid account permissions. Never send keys to unverified third-party Jev-like domains; confirm SDKs and endpoints via official `typesafe.ai` links.
