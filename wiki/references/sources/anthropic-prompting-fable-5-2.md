---
title: >-
  Prompting Claude Fable 5.2
category: references
tags: [source, anthropic, fable, prompt-engineering, effort, subagents]
sources:
  - "url:https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2"
source_url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2"
created: 2026-11-10T00:30:00Z
updated: 2026-11-13T03:08:44Z
as_of: 2026-11-13
summary: >-
  Fable 5.2 prompting and effort calibration: high by default, conditional xhigh, rare max, and whole-task completion.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-11-10
tier: primary
snapshots:
  - "[[_raw/_archived/2026-11-10-anthropic-prompting-fable-5-2|2026-11-10-anthropic-prompting-fable-5-2]]"
  - "[[_raw/_archived/2026-11-13-anthropic-fable-5-2-prompting|2026-11-13-anthropic-fable-5-2-prompting]]"
---

# Prompting Claude Fable 5.2

Anthropic's official prompting guide for Claude Fable 5.2 and Claude Mythos 5.2 details how the model's increased autonomous planning capacity alters prompt engineering best practices.

## Key Prompting Patterns

1. **Calibrate Effort:**
   - On Fable 5.2, start at `high` effort (the default). Use `xhigh` only where measured gains justify it; reserve `max` for ceiling measurement or rare tasks unconstrained by time and tokens.
   - For straightforward edits, reduce effort to `low` or `medium` to avoid unnecessary extended thinking.
2. **Finish the Whole Task:**
   - In agentic harnesses, Fable 5.2 can sometimes pause before completing multi-stage tasks if instructions ask for approval. Use outcome-oriented instructions: "Finish all parts the request needs before returning."
3. **Explicit Code Ownership:**
   - Fable 5.2 strongly respects stated code ownership boundaries. Prompts must explicitly grant permission to edit surrounding files (e.g., tests, fixtures, exports) or the model will only diagnose nearby bugs without fixing them.
4. **Set Expectations for Subagents:**
   - In multi-agent frameworks, Fable 5.2 tends to spawn helper subagents liberally. System prompts should explicitly define when subagents are justified (e.g., parallel file reads vs single-stream edits).
5. **Keep Caution from Piling Up:**
   - Fable 5.2 follows negative constraints strictly. Avoid stacking multiple layers of defensive safety reminders in developer prompts, which can cause excessive refusal or passive execution.

## Current guidance — checked 2026-11-13

Start at high, the Claude API default. Low suits quick interaction, well-specified tasks and high-volume workloads; medium suits interactive coding, chat and everyday knowledge work. High suits hard coding, research, agentic work and long unattended runs. Xhigh is conditional on measured gains in the hardest long-running coding and agentic work. Max is for measuring the ceiling or rare tasks where time and tokens do not matter, especially open-ended scientific discovery and mathematics. Above high, gains are uneven and task-dependent. Re-run effort sweeps for this model. At low and medium, agentic work is more likely to stop early. Effort has little effect on reply length: control length and tone through prompting. The capture also covers task completion, code ownership, subagent expectations, accumulated caution, progress reporting, harness review, final reports and safeguard refusals; these are prompting practices, not additional model-selection scores.

Related: [[concepts/model-effort-selection]], [[synthesis/vendor-guided-model-selection]].

## Sources

- [[_raw/_archived/2026-11-10-anthropic-prompting-fable-5-2]]

- [[_raw/_archived/2026-11-13-anthropic-fable-5-2-prompting]] — 2026-11-13 capture; extraction limitations are recorded in its frontmatter.
