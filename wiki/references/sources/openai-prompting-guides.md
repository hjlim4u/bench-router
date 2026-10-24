---
title: >-
  OpenAI prompting guides — GPT-6, prompt engineering, Codex
category: references
tags: [source, reasoning, coding]
sources:
  - "url:https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra"
  - "url:https://developers.openai.com/api/docs/guides/prompt-engineering"
  - "url:https://developers.openai.com/codex/prompting"
created: 2026-10-24T14:00:00Z
updated: 2026-10-24T14:00:00Z
as_of: 2026-10-24
summary: >-
  Verbatim prompting guidance from OpenAI's GPT-6 best practices, prompt engineering and Codex pages; the router shows these passages for a selected OpenAI model.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-24
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-24-openai-gpt-6-prompting-best-practices|2026-10-24-openai-gpt-6-prompting-best-practices]]"
  - "[[_raw/_archived/2026-10-24-openai-prompt-engineering|2026-10-24-openai-prompt-engineering]]"
  - "[[_raw/_archived/2026-10-24-openai-codex-prompting|2026-10-24-openai-codex-prompting]]"
---

# OpenAI prompting guides — GPT-6, prompt engineering, Codex

Quoted verbatim as of 2026-10-24. The GPT-6 page says its prompts are "a starting point across the GPT-6 model family. They address behavior observed with GPT-6 Astra; evaluate them with your chosen model and workload." The bench-router shows these passages for a selected OpenAI model (`prompt-guidance`). They are OpenAI's guidance only.

The prompt engineering page frames the difference between model types: "GPT models like `gpt-6-astra` benefit from precise instructions that explicitly provide the logic and data required to complete the task in the prompt." and "Generally speaking, reasoning models will provide better results on tasks with only high-level guidance. This differs from GPT models, which benefit from very precise instructions." Both are captured in [[_raw/_archived/2026-10-24-openai-prompt-engineering]].

## GPT-6 best practices

### Initiative and follow-through

> To encourage more autonomous work, start with this prompt:

The page supplies this prompt text:

```text
You should infer the user's intent and task scope from the instructions and prior conversation context. Your job is to bias towards action and carry the user's intended task to completion.

When the user expresses intent to perform new work or fix an existing issue, persist until the user's intended goal is complete. Progress autonomously towards the user's goal (e.g. creating isolated worktrees / checkouts if needed, resolving merge conflicts, read-only actions, creating draft PRs etc.) unless they are clearly destructive or irreversible.
```

### Follow through on requests that imply authorization

> Prompt the model to follow through if the user’s prompt implies authorization:

The page supplies this prompt text:

```text
When the user's prompt indicates a request for action, such as "can you...", "I want to...", "help me..." and similar expressions, treat these as instructions to do the work and take action. Do not stop at acknowledging capability (e.g. "Yes…"), proposing a plan, or offering to continue. Do not settle for a partial or "helpful enough" solution that does not fully satisfy the user's task to save time, effort or tokens. If a task requires sustained work, complete all the necessary work until the intended outcome is fulfilled.
```

### Instruction priority

> Make the priority of user instructions and skills explicit.

The page supplies this prompt text:

```text
The user's instructions take precedence over guidelines provided in a skill. If explicit user instructions conflict with a skill's instructions, prioritize the user's instructions.
```

### Testing and verification

> For coding tasks, calibrate how much testing and verification a change requires. This can help avoid unnecessary tests or repeated checks for small changes.

The page supplies this prompt text:

```text
Do not write tests for reversible, low-impact changes that mirror the implementation. If you do choose to verify your work with tests, make sure that the tests are meaningful and necessary to verify implementation.

Run tests appropriate to the change and complete required checks. Once those pass, broaden or repeat testing only when new changes, failures, or unresolved concerns justify it; otherwise, continue toward completing the task.
```

## Codex

### Codex prompt contents

> A useful Codex prompt names the behavior you want, points to the relevant code or reproduction steps, preserves important constraints, and says how to verify the change.

The Codex capture also holds the page's "Fix a bug" and "Write a test" workflows: [[_raw/_archived/2026-10-24-openai-codex-prompting]].

## Related

- [[references/sources/openai-model-selection]]
- [[concepts/model-effort-selection]]

## Sources

- [[_raw/_archived/2026-10-24-openai-gpt-6-prompting-best-practices]]
- [[_raw/_archived/2026-10-24-openai-prompt-engineering]]
- [[_raw/_archived/2026-10-24-openai-codex-prompting]]
