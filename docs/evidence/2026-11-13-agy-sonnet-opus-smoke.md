# agy Sonnet / Opus selection and invocation smoke check

Verified 2026-11-13 on `fix/stable-selection-availability`, including the uncommitted availability fix.

## Candidate and selection checks

The installed `agy models` lists `claude-{sonnet,opus}-5-5-{low,medium,high}`.
All six corresponding `agy-claude-*` profiles already exist and are enabled in
`~/.config/bench-router/profiles.toml`. No user configuration was changed.

All six passed:

- Default task constraints against the complete installed profile configuration (`eligible=True`).
- Real `herdr.probe_profiles()` CLI, native model-list and usage checks (exclusion reason `None`).
- Format 3 assessment, `decision.bind()` and selection replay (`ok` → `selected`).

Selection replay used the six real agy profiles and an explicit model/effort task filter.
This verifies candidate selection and record validation, not an automatic preference over other models.
The canonical model remains `claude-sonnet-5-5` or `claude-opus-5-5` for vendor guidance;
the execution argument retains its effort suffix, e.g. `--model claude-sonnet-5-5-low`.

## Actual local execution

Both calls used `herdr.dispatch(..., selection=..., backend="local")`, real live preflight,
and temporary git repositories. The task requested `AGY_SMOKE_OK` and only the router result files.

| Profile | Run ID | Router result | Manifest status | Result file SHA-256 |
| --- | --- | --- | --- | --- |
| `agy-claude-opus-5-5-low` | `3b312436-8f97-45b7-8007-df47d9455260` | `completed` | `success` | `4da17071a3c0ffb2e739a488ea2eaccc6d4e0fd76e5461b93c392fc4bb7fc00d` |
| `agy-claude-sonnet-5-5-low` | `67081796-d58c-4aed-ac15-b64582fb2f1b` | `completed` | `success` | `93f13fa47180ef1b2325065a839294ce40067691b01faf9a6b50c37cb0c64449` |

The router validated the result contracts; an additional read confirmed the marker,
successful manifest and matching hashes. Medium/high were assessed and replayed but not invoked.

The initial Sonnet dispatch into the still-busy Opus fixture returned `conflict` without
starting a second process, as required by admission control. Sonnet completed in a separate fixture.

Raw local artifacts: `/tmp/bench-router-agy-smoke-852dqpwj/` (`preflight.json`,
per-profile selections, dispatch outputs, `opus-collection.json`, and both repositories' receipts/logs).
These temporary artifacts are not committed and may be removed by system cleanup.

## Conclusion

Both model families are valid agy candidates and can execute through a recorded router selection.
The incomplete generic `agy-worker` profile is a separate configuration issue; these explicit profiles
provide valid native model IDs. No additional engine or profile changes were needed for this check.
