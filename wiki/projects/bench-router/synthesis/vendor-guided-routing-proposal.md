---
title: >-
  Proposed routing based on official model and effort guidance
category: synthesis
tags: [agentic, reasoning, coding]
sources:
  - "conversation:2026-10-19"
  - "repo:bench-router@d1a94b1c0164f9a129f37206812a077f70053a8b"
  - "url:https://developers.openai.com/api/docs/guides/model-selection"
  - "url:https://platform.claude.com/docs/en/about-claude/models/choosing-a-model"
  - "url:https://platform.claude.com/docs/en/build-with-claude/effort"
  - "url:https://ai.google.dev/gemini-api/docs/models"
  - "url:https://ai.google.dev/gemini-api/docs/thinking"
created: 2026-10-19T01:52:29Z
updated: 2026-10-19T01:52:29Z
as_of: 2026-10-19
summary: >-
  Unimplemented proposal: use official workload/configuration advice to narrow eligible profiles, then compare quality evidence and explicit cost constraints.
provenance:
  extracted: 0.2
  inferred: 0.8
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-openai-model-selection|2026-10-19-openai-model-selection]]"
  - "[[_raw/_archived/2026-10-19-anthropic-model-selection|2026-10-19-anthropic-model-selection]]"
  - "[[_raw/_archived/2026-10-19-anthropic-effort|2026-10-19-anthropic-effort]]"
  - "[[_raw/_archived/2026-10-19-google-gemini-models|2026-10-19-google-gemini-models]]"
  - "[[_raw/_archived/2026-10-19-google-gemini-thinking|2026-10-19-google-gemini-thinking]]"
  - "[[_raw/_archived/2026-10-19-routing-code-evidence.json|2026-10-19-routing-code-evidence.json]]"
  - "[[_raw/_archived/2026-10-19-routing-research-context|2026-10-19-routing-research-context]]"
---

# Proposed routing based on official model and effort guidance

**Status: research proposal; not implemented or experimentally validated.** The user's expressed preference is to ground model/effort decisions in official vendor guidance. The detailed procedure below is an assistant-authored design, not a shared vendor standard or a fully approved implementation plan. ^[inferred]

## Proposed procedure

1. Apply mandatory constraints to configured profiles: tools, context, locality, availability, supported model/effort, and any explicit spending ceiling.
2. Describe the request using clarity, ambiguity, reasoning demands, expected tool-use duration, output requirements, deadline, and quality/cost preference. Preserve the reasons for these judgments.
3. Match each provider's candidates against its dated, model-specific recommendations. Retain the documented model/version and source of each match.
4. Check relevant benchmark results and available workflow evaluations, including the measured harness and effort. A benchmark score alone does not demonstrate that the current task's quality bar is met.
5. Where quality is established and cost is prioritized, compare actual estimates among qualifying candidates. When evidence does not resolve the choice, record the uncertainty rather than claiming an optimum.
6. Record the selected profile, reasons, guideline versions, evidence, estimates, and current assessment digest. Recheck constraints before dispatch.

All six steps are project-level synthesis. ^[inferred]

## Why this changes the selection basis

The [[projects/bench-router/synthesis/routing-selection-audit|current legacy policy]] trades benchmark percentiles against cost tiers using fixed coefficients. This proposal uses official recommendations as conditional starting rules and treats quality, cost, and feasibility as separately inspectable facts. It does not claim to eliminate all policy judgment. ^[inferred]

## Reusable and unresolved parts

| Existing capability | Proposed use |
|---|---|
| `evaluate` eligibility and facts | Retain mandatory checks and expose decision inputs |
| Evidence table with measured effort | Inspect relevant evaluations and mismatched conditions |
| `route --selection` | Execute a recorded eligible choice |
| Selection policy/version and reason | Identify the policy actually used |

Reusing these boundaries could avoid a second dispatch system. That is an architectural inference, not a completed change. ^[inferred]

Before implementation, resolve guideline storage and update ownership, supported CLI settings, the quality acceptance procedure, treatment of missing evaluations, and how to choose between unresolved providers. Existing code does not enforce these proposed rules. The current digest also omits wiki/facet evidence; the workflow already requires separate provenance rechecks.

## Related

- [[projects/bench-router/bench-router]]
- [[synthesis/vendor-guided-model-selection]]
- [[concepts/model-effort-selection]]
- [[references/sources/openai-model-selection]]
- [[references/sources/anthropic-effort]]
- [[references/sources/google-gemini-thinking]]

## Sources

- [[_raw/_archived/2026-10-19-routing-research-context]] — user preference and unimplemented status.
- [[_raw/_archived/2026-10-19-routing-code-evidence.json]] — existing boundaries and provenance limitations.
- [[_raw/_archived/2026-10-19-openai-model-selection]]
- [[_raw/_archived/2026-10-19-anthropic-model-selection]]
- [[_raw/_archived/2026-10-19-anthropic-effort]]
- [[_raw/_archived/2026-10-19-google-gemini-models]]
- [[_raw/_archived/2026-10-19-google-gemini-thinking]]
