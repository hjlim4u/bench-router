---
title: >-
  Google Gemini model roles
category: references
tags: [source, agentic, coding]
sources: ["url:https://ai.google.dev/gemini-api/docs/models"]
created: 2026-10-19T01:52:29Z
updated: 2026-11-13T03:08:44Z
as_of: 2026-11-13
summary: >-
  Gemini 4 Carbon, Argon and Hydrogen roles, alongside dated descriptions of earlier models.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-google-gemini-models|2026-10-19-google-gemini-models]]"
  - "[[_raw/_archived/2026-10-24-google-gemini-models|2026-10-24-google-gemini-models]]"
  - "[[_raw/_archived/2026-11-13-google-gemini-models|2026-11-13-google-gemini-models]]"
---

# Google Gemini model roles

The official catalog describes model capabilities and intended uses. The following is a dated subset, not an exhaustive list or a price comparison.

> For any new projects, use our latest models: 3.5 Flash-Lite or 3.8 Flash.

> Most production apps should use a specific stable model.

| Model listed on 2026-10-24 | Published description, verbatim |
|---|---|
| Gemini 3.5 Flash-Lite | Our fastest, most cost-effective 3.5 model for high-throughput execution. |
| Gemini 3.8 Flash | Our most intelligent Flash model, engineered for long-horizon software engineering, autonomous agents, and complex enterprise workflows. |
| Gemini 4 Argon | Our flagship reasoning model with a unified 1M context window and long decodes up to 1M tokens. |
| Gemini 3.1 Pro preview | Listed as `gemini-3.1-pro-preview` without a description; its preview status must remain explicit. |

## Limits

A family label does not establish task success, actual spend, or availability in Antigravity or another agent harness. Thinking defaults and accepted levels belong to the specific model's configuration documentation. Model releases can change these roles.

## Related

- [[references/sources/google-gemini-thinking]]
- [[synthesis/vendor-guided-model-selection]]
- [[concepts/facets/task]]

## Current guidance — checked 2026-11-13

The catalog now lists Gemini 4 Carbon, Argon and Hydrogen. Carbon is described as the strongest reasoning model for complex software engineering, multimodal knowledge work, scientific reasoning and cybersecurity defense. Argon is the efficient frontier reasoning model, with faster responses and lower token spend per turn than Carbon across complex coding, agentic, math and science tasks. Hydrogen targets speed and efficiency for everyday coding and agentic workflows. Each lists 1M context and 65K / 1M output, with runtime conditions documented separately. Older model roles below remain dated historical evidence; a catalog role does not establish installed CLI availability or a cross-vendor ranking.

Related: [[concepts/model-effort-selection]], [[synthesis/vendor-guided-model-selection]].

## Sources

- [[_raw/_archived/2026-10-24-google-gemini-models]] — verbatim model descriptions and selection advice.
- [[_raw/_archived/2026-10-19-google-gemini-models]] — earlier bounded excerpt and canonical origin.

- [[_raw/_archived/2026-11-13-google-gemini-models]] — 2026-11-13 capture; extraction limitations are recorded in its frontmatter.
