# Repository Guidelines

## Project Structure & Module Organization

`bench_router/` contains the CLI (`cli.py`), routing policy (`routing.py`), benchmark collection and snapshots (`data.py`), dispatch receipts and the herdr runner (`herdr.py`), Herdr-free local/external runners (`runners.py`), parallel worktree dispatch (`parallel.py`), benchmark wiki compilation (`wiki.py`), request-time benchmark evidence tables (`evidence.py`), and bundled category weights (`categories.toml`). `wiki/` is the benchmark wiki (Obsidian vault); its schema is `wiki/AGENTS.md`. `eval/` holds comparison and cost scripts. `examples/` contains sample profiles, tasks, and synthetic results. Root-level `test_p0.py`, `test_p1.py`, `test_p2.py`, and `test_p3.py` cover routing, data refresh, dispatch, and parallel dispatch respectively; `test_coordination.py` covers admission and `test_codeburn.py` the CodeBurn helpers. Numbered root documents describe the design; `docs/evidence/` records external API evidence.

## Build, Test, and Development Commands

Use Python 3.11+ on Linux or WSL2. Run commands from the repository root; there is no installation or build step.

Core commands need only the standard library. For Arena refresh (`pyarrow`) and the CodeBurn CLI, `mise install && mise run setup` installs them (uv, `.venv/`); `mise run test` and `mise run refresh` wrap the commands below.

```bash
python3 -m bench_router.cli --help
python3 -m bench_router.cli status
python3 -m bench_router.cli route --task task.json --dry-run
python3 -m bench_router.cli wiki compile --check
python3 -m bench_router.cli evidence --task task.json --format table
python3 -m unittest test_p0 test_p1 test_p2 test_p3 test_coordination test_codeburn test_evidence_policy
```

`--help` lists CLI options. `status` inspects cached sources and snapshots. The default dry run produces an offline vendor-guided decision packet, or validates a supplied response/selection, without network access, herdr calls, or file writes; it needs a valid task and `profiles.toml`. Pending/unavailable decisions return exit 17. The final command runs the offline test suite. Refresh and live dispatch require Linux or WSL2 because locking uses `fcntl`.

## Coding Style & Naming Conventions

Match the existing Python style: four-space indentation, `snake_case` modules/functions, `PascalCase` classes, and `UPPER_SNAKE_CASE` constants. Keep JSON output contracts and input validation explicit. Use standard-library facilities where practical; no formatter or linter is configured in this repository. Test methods follow `test_vNN_description`, matching the numbered validation cases.

## Testing Guidelines

Use `unittest`; add a focused case to the matching `test_p*.py` file when changing behavior. Tests should use synthetic data or fake herdr responses, not live services. Run the full suite before a pull request. No coverage threshold is configured. For changes to live dispatch, also report any manual herdr smoke test performed.

## Commit & Pull Request Guidelines

Recent commits use concise, scoped subjects such as `docs: ...`, `eval: ...`, `herdr: ...`, and `bench-router: ...`; follow that pattern. In pull requests, explain the behavior change, relevant contract or configuration changes, and test results. Link an issue when one exists. Include sample CLI output for interface changes; screenshots are only useful if a visual artifact changes.

## Configuration & Secrets

Start with `examples/profiles.example.toml`. Keep `profiles.toml` and API credentials in the user config directory, not in commits. Supply `ARTIFICIAL_ANALYSIS_API_KEY` through the environment for AA refreshes.
