---
title: >-
  Gemini prompting strategies — Gemini 3 and agentic workflows
category: references
tags: [source, reasoning, coding]
sources: ["url:https://ai.google.dev/gemini-api/docs/prompting-strategies"]
created: 2026-10-24T14:00:00Z
updated: 2026-10-24T14:00:00Z
as_of: 2026-10-24
summary: >-
  Verbatim Gemini 3 and agentic-workflow prompting guidance from Google's prompt design page; the router shows these passages for a selected Gemini model.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-24
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-24-google-gemini-prompting-strategies|2026-10-24-google-gemini-prompting-strategies]]"
---

# Gemini prompting strategies — Gemini 3 and agentic workflows

Google's prompt design page for the Gemini API. The passages below are quoted verbatim as of 2026-10-24 from its Gemini 3 and agentic-workflow sections.

The bench-router shows these passages for a selected Gemini model (`prompt-guidance`). They are Google's guidance only; no other vendor's prompting advice applies to Gemini.

## Gemini 3 core principles and agentic dimensions

### Be precise and direct

> **Be precise and direct:** State your goal clearly and concisely. Avoid unnecessary or overly persuasive language.

### Consistent structure

> **Use consistent structure:** Employ clear delimiters to separate different parts of your prompt. XML-style tags (e.g., `<context>`, `<task>`) or Markdown headings are effective. Choose one format and use it consistently within a single prompt.

### Critical instructions first

> **Prioritize critical instructions:** Place essential behavioral constraints, role definitions (persona), and output format requirements in the System Instruction or at the very beginning of the user prompt.

### Verbosity

> **Control output verbosity:** By default, Gemini 3 models provide direct and efficient answers. If you need a more conversational or detailed response, you must explicitly request it in your instructions.

### Reasoning and planning

> Gemini 2.5 and 3 series models automatically generate internal "thinking" text to improve reasoning performance. As such, it's generally not necessary to have the model outline, plan, or detail reasoning steps in the returned response itself. For problems that require heavy reasoning, simple requests like "Think very hard before answering" can improve performance, though at the cost of extra thinking tokens.

### Ambiguity and permission handling

> **Ambiguity and permission handling:** Defines when the model is permitted to make assumptions versus when it must pause execution to ask the user for clarification or permission.

### Persistence and recovery

> **Persistence and Recovery:** The degree to which the model attempts to self-correct errors. High persistence increases success rates but risks higher token costs or loops.

## Related

- [[references/sources/google-gemini-models]]
- [[references/sources/google-gemini-thinking]]
- [[concepts/model-effort-selection]]

## Sources

- [[_raw/_archived/2026-10-24-google-gemini-prompting-strategies]]
