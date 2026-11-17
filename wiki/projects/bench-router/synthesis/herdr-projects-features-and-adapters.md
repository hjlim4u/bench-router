---
title: >-
  What herdr-projects uniquely does for bench-router, and why Herdr-API/other plugins don't replace it yet
category: projects
tags: [herdr, herdr-projects, adapter, bench-router, coordination]
summary: >-
  Source-verified herdr-projects 1.2.26 features used by the board runner (turn-end hooks, finish line, WORK_SETTINGS) and A/B/inline research on alternatives.
project: bench-router
base_confidence: 0.75
provenance:
  extracted: 0.8
  inferred: 0.2
lifecycle: draft
lifecycle_changed: 2026-11-07
created: 2026-11-07T00:00:00Z
updated: 2026-11-10T00:30:00Z
sources:
  - "bench-router session (2026-11-07)"
snapshots:
  - "[[_raw/_archived/2026-11-07-herdr-projects-unique-features-adapter-alternatives|2026-11-07-herdr-projects-unique-features-adapter-alternatives]]"
---

# What herdr-projects uniquely does for bench-router, and why Herdr-API/other plugins don't replace it yet

## Core Features Used by bench-router Board Runner

1. **Turn-End Detection:**
   - Plugin launches each agent with explicit hooks (Claude `--settings <file>`, Codex `-c notify=[..]`, pi `-e`) and a dedicated session ID, reading the agent's saved transcript directly.
   - Herdr `idle` alone does not signal task completion; the plugin requires a finished message, error in conversation, or `closing-note.md`.
2. **Worktree & Permission Management:**
   - Isolated git worktree per task (`herdr worktree create` under branch `work/<n>-<slug>`).
   - Default full execution permissions (`claude --dangerously-skip-permissions`, `codex --dangerously-bypass-approvals-and-sandbox`).
   - Automatically marks repo as trusted in `~/.claude.json` and `~/.codex/config.toml`.
3. **Fixed Settings in `bench_router/herdr.py`:**
   - `WORK_SETTINGS`: `workspace.from here`, `workspace.cleanup false`, `review.when never`, `review.rounds 0`, `merge.by you`, `merge.pr false`, `attempts.by 1`, `plan.approve none`, `--no-research`.

## Evaluated Alternatives

- **herdr-board (`nelsonPires5`):** Clean JSON CLI, but lacks worktree isolation (leaves isolation to agents) and has no `tell` capability.
- **tsk / htasks:** Lacks fine-grained model/effort control; attempts automatic PR merging or opening.
- **Native Thin Adapter:** Ranked highest on paper, but state machine and permission mapping risks were evaluated as high; 1.2.26 remains the stable path.

## Operational Gotchas

- Dispatch returns `conflict` when 4 admission records are active; stale records require `coordination release --key K --confirmed-stopped --note ...`.
- Concurrent routes in the same working directory trigger workspace collision guards; separate `git worktree add --detach` paths must be provided.

## Sources

- [[_raw/_archived/2026-11-07-herdr-projects-unique-features-adapter-alternatives]]
