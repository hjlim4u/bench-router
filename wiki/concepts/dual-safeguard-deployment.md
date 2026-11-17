---
title: >-
  Dual-safeguard deployment model
category: concepts
tags: [concept, safety, alignment, anthropic, deployment, dual-use]
sources:
  - "[[references/sources/anthropic-claude-fable-and-mythos-5-2]]"
created: 2026-11-10T00:25:00Z
updated: 2026-11-10T00:25:00Z
summary: >-
  Deployment pattern where identical underlying model weights are released in two safeguard tiers: standard commercial production safeguards (Fable) vs verified permissive access (Mythos).
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.9
lifecycle: draft
lifecycle_changed: 2026-11-10
---

# Dual-safeguard deployment model

The **Dual-Safeguard Deployment Model** is Anthropic's strategy for balancing frontier capability release with catastrophic risk prevention in dual-use domains (cybersecurity and biological/chemical threats).

## Architectural Principle

Rather than training separate capability models or retraining restricted checkpoints:
1. **Identical Weights:** Both models share the exact same foundation model weights, core reasoning, token limits, and pricing.
2. **Safeguard Tier A (General Access — e.g. Claude Fable 5.2):** Built-in classifiers and post-training guardrails block out-of-scope cyberattacks, malware development, and CBRN (chemical, biological, radiological, nuclear) synthesis pathways. Available publicly via API and developer platforms.
3. **Safeguard Tier B (Vetted Access — e.g. Claude Mythos 5.2):** Relaxed dual-use guardrails enabling legitimate defense-in-depth security audits, vulnerability discovery, de novo protein/capsid modeling, and biomedical research. Gated behind verification programs (Anthropic Cyber Verification Program, Life Sciences Verification Program).
