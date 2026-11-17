---
title: >-
  Advisor-orchestrator pattern for frontier models
category: concepts
tags: [concept, agentic, orchestration, advisor, claude-code, cost-optimization]
sources:
  - "[[references/sources/anthropic-claude-code-advisor-fable]]"
  - "[[references/sources/anthropic-claude-fable-and-mythos-5-2]]"
created: 2026-11-10T00:25:00Z
updated: 2026-11-10T00:25:00Z
summary: >-
  Architecture pattern that pairs a fast, cost-effective daily driver (Sonnet/Opus) with a high-capability frontier model (Fable) consulted selectively at critical decision points.
provenance:
  extracted: 0.85
  inferred: 0.15
  ambiguous: 0.0
base_confidence: 0.9
lifecycle: draft
lifecycle_changed: 2026-11-10
---

# Advisor-orchestrator pattern for frontier models

As frontier models reach extreme capabilities and higher token unit costs ($8/$40 per M tokens), running them end-to-end for routine file reads, shell commands, and syntax edits introduces unnecessary cost and latency.

The **Advisor-Orchestrator Pattern** decouples routine execution from architectural decision-making:

```mermaid
flowchart TD
    User(["Task / Prompt"]) --> Worker["Main Worker Model: Sonnet 5.5 / Opus 5.5"]
    Worker --> Tools["File Edits / Bash / Tests"]
    Worker -- "Hard Architectural Decision / Blocked" --> Advisor["Advisor Model: Fable 5.2"]
    Advisor -- "Guidance & Strategy" --> Worker
    Worker --> Done(["Completed Task"])
```

## Benefits

1. **Token Cost Savings:** 80-90% of session tokens run at daily-driver pricing, while Fable is invoked only on a fraction of prompts.
2. **Latency Reduction:** Sub-second to low-latency generation for routine commands; extended adaptive thinking is spent only when needed.
3. **Guardrail Compliance:** Avoids credit-depletion risks on subscription accounts while preserving frontier reasoning when an impasse occurs.
