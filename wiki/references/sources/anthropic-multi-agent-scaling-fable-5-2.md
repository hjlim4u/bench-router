---
title: >-
  Safely scaling multi-agent teams with Claude Fable 5.2
category: references
tags: [source, claude-dev, multi-agent, fable, safety, fermat-theorem]
sources:
  - "url:https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/"
source_url: "https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/"
created: 2026-11-10T00:30:00Z
updated: 2026-11-10T00:30:00Z
as_of: 2026-11-10
summary: >-
  Research report on formalizing Fermat's Last Theorem in Lean 4 with a 1,000-agent Claude Fable 5.2 team across 28.7 hours using SQLite shared state, sandbox isolation, and command classifier monitoring.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-11-10
tier: primary
snapshots:
  - "[[_raw/_archived/2026-11-10-claudedev-multi-agent-teams-fable-5-2|2026-11-10-claudedev-multi-agent-teams-fable-5-2]]"
---

# Safely scaling multi-agent teams with Claude Fable 5.2

Published on `claude.dev` on November 9, 2026 by Barry Zhang, Tianyi Peng, Elle Najt, Keller Scholl, and Lance Martin.

## Key Experiment Architecture

- **Goal:** Formalize the proof of Fermat's Last Theorem in Lean 4.
- **Agent Team:** 1,000 instances of Claude Fable 5.2 running concurrently in isolated execution sandboxes without internet access.
- **Coordination Mechanism:** A central SQLite database maintaining the proof tree, dependency dag, and task assignments.
- **Role Partitioning:** Lead agents broke down statements and verified dependency integrity; helper agents tackled individual lemmas.
- **Safety Controls:** Offline monitor and runtime classifier checked every bash command and file edit before execution.
- **Outcome:** The team completed the proof in **28.7 hours**, using **one-third as many output tokens** and generating a proof **one-seventh the length** of prior research benchmarks (which required human steering and external scaffolding).

## Sources

- [[_raw/_archived/2026-11-10-anthropic-claude-dev-scaling-multi-agent-teams-fable-5-2]]
- [[_raw/_archived/2026-11-10-claudedev-multi-agent-teams-fable-5-2]]
