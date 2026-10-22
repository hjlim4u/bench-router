---
title: >-
  Bench-router selection knowledge
category: project
tags: [agentic, coding]
sources:
  - "repo:bench-router@d1a94b1c0164f9a129f37206812a077f70053a8b"
  - "conversation:2026-10-19"
  - "conversation:2026-10-22"
created: 2026-10-19T01:52:29Z
updated: 2026-10-22T07:20:11Z
as_of: 2026-10-22
summary: >-
  Project map separating dated routing audits, current policy documentation, model/effort guidance, and multi-agent planning proposals.
provenance:
  extracted: 0.8
  inferred: 0.2
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-routing-code-evidence.json|2026-10-19-routing-code-evidence.json]]"
  - "[[_raw/_archived/2026-10-19-routing-research-context|2026-10-19-routing-research-context]]"
---

# Bench-router selection knowledge

Bench-router assesses configured agent profiles, checks mandatory constraints, and dispatches a selected profile. The 2026-10-19 audit records the earlier legacy automatic policy and external-choice path. As of the documentation inspected on 2026-10-22, `route` defaults to `vendor-guided`; the earlier weighted policy requires explicit `--policy legacy`.

## Reading map

- [[projects/bench-router/synthesis/routing-selection-audit]] owns observations about current implementation and the evidence behind its constants.
- [[projects/bench-router/synthesis/vendor-guided-routing-proposal]] owns the proposed selection procedure and its unresolved requirements.
- [[synthesis/vendor-guided-model-selection]] connects the project findings to five official source notes.
- [[concepts/model-effort-selection]] explains the model/effort distinction.
- [[projects/bench-router/synthesis/multi-agent-pattern-selection]] owns the proposed timing, information requirements, and workflow evidence for choosing collaboration patterns.
- [[projects/bench-router/synthesis/router-orchestrator-boundary]] owns the proposed split between pattern decisions in the calling layer and pattern-agnostic single-task assignment in the router.

## Knowledge and runtime boundary

The existing wiki compiler reads benchmark and facet index blocks. These new source, concept, and synthesis pages preserve research. Capturing them does not implement a new selector or make a draft recommendation active at request time.

## Related

- [[concepts/facets/task]]
- [[concepts/facets/difficulty]]
- [[entities/benchmarks/swe-bench-verified-exact]]
- [[entities/benchmarks/terminal-bench-exact]]

## Sources

- [[_raw/_archived/2026-10-19-routing-code-evidence.json]] — content hashes and inspected code/document sections at the recorded commit.
- [[_raw/_archived/2026-10-19-routing-research-context]] — user preference and proposal status.
- [Current routing policy documentation](../../../docs/vendor-guided-routing.md) — default policy inspected on 2026-10-22.
