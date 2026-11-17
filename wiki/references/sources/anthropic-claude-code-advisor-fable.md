---
title: >-
  Claude Code: Escalate hard decisions with the advisor tool (Fable Guide)
category: references
tags: [source, claude-code, advisor, fable, configuration]
sources:
  - "url:https://code.claude.com/docs/en/advisor"
source_url: "https://code.claude.com/docs/en/advisor"
created: 2026-11-10T00:25:00Z
updated: 2026-11-10T00:25:00Z
as_of: 2026-11-10
summary: >-
  Official Claude Code documentation on configuring and invoking Claude Fable 5.2 via the advisor tool (/advisor, --advisor, advisorModel), model pairings, version requirements, and billing to usage credits.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-11-10
tier: primary
snapshots:
  - "[[_raw/_archived/2026-11-10-anthropic-advisor-tool|2026-11-10-anthropic-advisor-tool]]"
---

# Claude Code: Escalate hard decisions with the advisor tool (Fable Guide)

The official Claude Code documentation outlines how to pair daily-driver models (Sonnet, Opus) with a higher-capability advisor model (such as Claude Fable 5.2).

## Configuration Options

- **Interactive Command:** `/advisor fable` (or `/advisor` menu)
- **CLI Flag:** `claude --advisor fable`
- **Settings Configuration (`~/.claude.json`):**
  ```json
  {
    "advisorModel": "fable"
  }
  ```
- **Direct Model Selection:** `claude --model claude-fable-5-2` or `/model fable`
- **Minimum CLI Version:** Claude Code **v2.1.321 or later** is required for Fable 5.2 (Fable 5.1 required v2.1.257).

## Common Model Pairings

| Main Model | Advisor Model | Purpose |
|---|---|---|
| **Sonnet 5.5** | **Fable 5.2** | High speed and efficiency for general execution, invoking Fable only at difficult architectural/decision moments. |
| **Opus 5.5** | **Fable 5.2** | Heavy autonomous engineering with top-tier reasoning escalations. |
| **Fable 5.2** | **Fable 5.2** | Highest capability configuration. (Claude Code rejects pairing a weaker advisor like Opus or Sonnet to a Fable main model). |

## Billing & Usage Credits

- On Claude Pro / Team plans, Fable usage bills to **usage credits** rather than the flat subscription allowance.
- Claude Code requires a one-time user consent to bill Fable usage to credits before Fable can be activated as the advisor or primary model.
