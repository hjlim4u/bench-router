# CodexBar usage, credits, and cost

Live local/Shepherdr routing and `evaluate --preflight` use the official
[CodexBar 0.84.0 CLI](https://github.com/steipete/CodexBar/releases/tag/v0.84.0).
CodeBurn has been removed from the project dependency, execution, reporting, and
skill paths. Existing usage logs remain in their original provider directories.

## Install

```bash
mise run install-codexbar
codexbar --version
```

`mise run setup` and `mise run install` include this task. The installer downloads
the pinned official Linux x86_64/aarch64 release, validates its SHA-256 checksum,
and links `~/.local/bin/codexbar`. Put that directory on PATH. It needs neither
Swift nor a desktop app. Existing unrelated installations are preserved. Set
`BENCH_ROUTER_CODEXBAR=/absolute/path/to/codexbar` to select another binary.

## Preflight before paid evaluation

The existing `probe_profiles` entry point is shared by evaluation, dispatch, and
parallel dispatch. Native executable checks and `agy models` run first; only
remaining providers are queried. Disabled profiles and profiles failing the
task's static constraints are removed before any CLI/model/quota request. Parallel
dispatch checks the union of eligible members once. Provider queries run concurrently,
once per provider regardless of profile count. Recovering a single existing receipt needs
no new quota request. There is no extra inference call to test access.

* Claude and Codex start with explicit `--source oauth`, reusing their CLI login.
  Claude can fall back to an explicit Web query when its account matches the
  local CLI identity. There is no Claude/Codex interactive CLI fallback.
* Antigravity uses native `--source auto`: account-aware app/CLI/IDE probing and
  its existing OAuth fallback. Returned identities are compared with the local
  CLI display identity (Claude login metadata, Codex ID-token email, agy file-token
  email). Mismatches are excluded as `codexbar_account_mismatch`; a remote account
  that cannot be bound to the worker is `codexbar_account_unverified`.
  Native ambient CLI responses can lack identity; these keep an explicit
  `ambient_cli` binding and `ambient_account_unverified` warning rather than a
  claim of verified identity. No account or worker credentials are switched.
* A query has a 120-second outer deadline, allowing agy's native 90-second usage
  report to finish. Cancellation sends CodexBar a termination signal and gives
  it five seconds for native cleanup, then ends only the probe's own process
  group. User-launched agents are outside that group and are preserved.
* Each applicable shared session/weekly limit and model-specific limit must have
  headroom. An exhausted five-hour window excludes the model even with weekly
  allowance remaining. Claude Fable limits do not exclude Sonnet. Antigravity
  Gemini and Claude/GPT pools are separate; distinct model buckets are matched
  to the selected model, and shared allowances are never added together.
* Quota observations older than five minutes, more than one minute in the future,
  failed/missing responses, unknown percentages, and synthetic placeholder
  windows do not prove availability. The candidate is excluded with
  `codexbar_quota_unverified`. Known exhaustion uses `codexbar_quota_exhausted`.
  Fix login/source/network access and rerun; there is no silent permissive fallback.

Claude Pro Fable requires **Claude.ai Usage credits**, separate from API Console
funds. Unknown-plan Fable profiles also require verification. CodexBar receives
an additional explicit Web query only when a surviving Fable profile requires
credits. A missing/expired cookie, absent/stale balance, or account mismatch
excludes that Fable profile before paid candidate evaluation. Other eligible
models remain available. A verified nonpositive balance gives
`codexbar_credits_exhausted`; unknown balance gives `codexbar_credits_unverified`;
identity mismatch gives `codexbar_credit_account_mismatch`; an exhausted reported
positive spend cap gives `codexbar_spend_limit_exhausted`.

OAuth and same-account Web model windows are both enforced. Every fresh reported
spend cap remains binding: a Web response containing only a prepaid balance cannot
erase an OAuth spend cap. Missing balance remains unknown, not zero.

## Reserve and observations

The default reserve is **10% remaining**, matching CodexBar guard's default and
inclusive threshold. A candidate with exactly 10% remaining passes; less than
10% gives `codexbar_quota_low`. Known 100% exhaustion always excludes it.
Set `BENCH_ROUTER_MIN_REMAINING=0` to disable the reserve, or any finite percentage
from 0 through 100 to tune it. Invalid values fail explicitly. The existing usage
snapshot supplies this guard across all applicable model/shared windows without
another `codexbar guard` request.

Live evaluation formats 1, 2, and 3, dispatch output, and parallel output include
`preflight`, keyed by profile. Each entry contains provider/source, observation and
check timestamps, account-binding state, scoped windows with remaining percentages
and reset times, the reserve decision, sanitized native `pace` fields, and warnings.
Required prepaid checks include a separate credit status and verified balance.
Provider text, account emails, credentials, and reset-credit identifiers are omitted.

```json
{
  "preflight": {
    "codex-sol-high": {
      "provider": "codex",
      "source": "oauth",
      "account_binding": "matched",
      "remaining_percent": 23,
      "guard": {"min_remaining_percent": 10, "decision": "safe"},
      "pace": {"primary": {"will_last_to_reset": false, "eta_seconds": 3125}},
      "warnings": ["pace_runs_out_before_reset"]
    }
  }
}
```

This abridged example distinguishes measured remaining quota from a forecast.
Pace is advisory; it does not become a benchmark score or an invented estimate of
the task's cost. Volatile observations stay outside assessment/selection digests;
availability and the reserve are rechecked before dispatch. Shared quota is neither
summed across profiles nor reserved for parallel workers.

Linux requires a manually configured Claude.ai cookie for the Web source.
Import it privately using CodexBar's native stdin command, never a command-line
literal, committed file, agent prompt, or chat message:

```bash
codexbar config set-cookie --provider claude --stdin
codexbar usage --provider claude --source web --json
```

The Web account must match the agent CLI account. The router compares account
identity before using its balance, using the local Claude login display identity
when the OAuth response omits email. A Cloudflare challenge can prevent Web
access even with a valid cookie. OAuth quota success does not verify prepaid
credits. The router neither purchases credits, redeems reset credits, switches
accounts, nor enables paid overage automatically.

Keep `--preflight` on decision-response replays. Dispatch checks again before
execution. If every profile is excluded, stop at `no_eligible_profile` without
calling a decider. Offline evaluation and dry-run still make no quota calls;
external runners leave availability to the caller. These observations do not
reserve capacity or guarantee payment eligibility at execution time.

## Native reporting

Use CodexBar directly or the transparent `python3 -m eval.codexbar` wrapper:

```bash
codexbar usage --provider claude --source oauth --json
codexbar usage --provider codex --source oauth --json
codexbar usage --provider antigravity --source auto --json
codexbar cards --provider both
codexbar cost --provider claude --period month-to-date --json
codexbar cost --provider codex --group-by project
codexbar cost --provider codex --group-by session
python3 -m eval.codexbar cost --provider antigravity --json > antigravity-cost.json
codexbar dashboard
codexbar serve --port 8080
codexbar config validate --json
```

The wrapper forwards native options, stdout/stderr, and exit status; it does not
download packages at runtime. JSON exports retain the native CodexBar schema.
The old `overview --project`, CSV export, `doctor`, and Antigravity usage-hook
commands are removed. Use native cost grouping, JSON redirection, config
validation, and provider usage queries instead. Codex project/session grouping
is supported; no equivalent cross-provider project filter is promised.

Costs are API-price estimates, not subscription deductions or prepaid balances.
Antigravity can report tokens with unknown prices; inspect coverage/unpriced
counts even when a numeric total is zero. Incomplete history is a partial total.
Quota polling does not scan cost history. Local cost scans do not submit prompts.

Official contracts: [CLI](https://github.com/steipete/CodexBar/blob/v0.84.0/docs/cli.md),
[Claude sources and credits](https://github.com/steipete/CodexBar/blob/v0.84.0/docs/claude.md),
[Antigravity buckets](https://github.com/steipete/CodexBar/blob/v0.84.0/docs/antigravity.md).
