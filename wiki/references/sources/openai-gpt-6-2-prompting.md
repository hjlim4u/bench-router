---
title: >-
  OpenAI prompting and migration guide — Using GPT-6.2
category: references
tags: [source, openai, prompting, responses-api, migration]
sources:
  - "url:https://developers.openai.com/api/docs/guides/latest-model.md"
source_url: "https://developers.openai.com/api/docs/guides/latest-model"
created: 2026-11-18T08:00:21Z
updated: 2026-11-18T08:16:00Z
as_of: 2026-11-18
summary: >-
  Verbatim prompting best practices and migration quickstart from OpenAI's "Using GPT-6.2" guide (gpt-6.2-astra and gpt-6.2-sol).
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.57
lifecycle: draft
lifecycle_changed: 2026-11-18
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-11-18-openai-latest-model-gpt-6-2|2026-11-18-openai-latest-model-gpt-6-2]]"
---

# OpenAI prompting and migration guide — Using GPT-6.2

Quoted verbatim from `https://developers.openai.com/api/docs/guides/latest-model.md` as of 2026-11-18. ^[extracted]

> Use GPT-6.2 Astra for the most demanding tasks or GPT-6.2 Sol for complex work at lower cost.

## What's new

- **Prefix edits**: "Starting with GPT-6.2, the Responses API drops reasoning items after mid-conversation edits to the conversation history (prefix edits), certain model changes (including downgrades), or changes to the end user or organization. When the model loses access to reasoning items, answer quality can decline and the model may use more tokens to repeat earlier work. Review your integration to identify edits such as changes to earlier developer messages or tool calls. To preserve reasoning and keep earlier input eligible for prompt caching, keep the prefix unchanged when you change settings between responses."
- **Changes to the `instructions` field in the Responses API**: "Models starting with GPT-6.2 append top-level `instructions` after `input` in the Responses API. To make reusable instructions eligible for prompt caching, put them in a `developer` message as the first item in `input`. Use top-level `instructions` for developer guidance that applies only to the current request."

## Prompting best practices

> Use the following prompts as a starting point across the GPT-6.2 model family. The examples address behaviors we’ve seen when working with GPT-6.2 Astra and Sol. If you recognize one in your own application, try the prompt in that section.

### Writing style

> Use the following prompt if you want to use the model as a collaborator and thought partner for day to day work.

```text
Write using terminology the user and sources use. Keep technical details and use domain-specific language when they make the explanation more precise. Use the active voice and keep closely related details together. Cover the key points up front, and avoid references that the reader can only make sense of later in the response. Give the user enough context to follow your reasoning.
```

> Prompt the model to adapt to the audience it is drafting material for, such as writing in documents, emails, messages and external posts.

```text
When drafting a message or any other material on behalf of the user to be sent to an external audience, consider who will read it and tailor the content to that intended audience. The intended audience likely does not have the same context as the user, so ensure that you provide the background information or reasoning required for the audience to understand the content. When reviewing or editing existing content, preserve the author’s content and wording, and follow the user's instruction carefully for what edits they want.
```

> During longer tasks, the model can carry shorthand from its reasoning or from other agents into its final answer. Remind it to write a self-contained response that’s clear to someone who hasn’t followed the progress updates.

```text
Treat your final answer as the user's first look at your work, and not as a continuation of intermediate commentary. The final answer must always be fully self-contained: users should never need to read earlier commentary updates for context, since they are collapsed when the final answer is shown to the user.

Write the final answer and all other human-facing material anew for the intended reader. Do not copy or closely paraphrase your reasoning or adopt its writing style. Do not carry over working shorthand, jargon, or abbreviations from your reasoning, tool calls, or instructions to subagents and automations.
```

### Task completion

> For work that can proceed without supervision, specify the outcome the model should complete and which decisions need the user’s input.

```text
Avoid stopping to end the turn while the task is incomplete or if there is an authorized next step you can take, and instead take the next steps within task scope to progress the user's request. If your final response before ending the turn is a suggested next step, a plan, a request to the user for a routine decision, instructions for a task to execute, or similar handoff to the user, take these steps yourself to make progress towards what the user asked for. Make sure that you have authorization to do so, and flag any assumptions or decisions you maketo the user.

Only stop to clarify with the user if there is significant change in task scope, you are concretely blocked, have a decision that the user needs to resolve, or before irreversible or destructive actions.
```

> Ask the model to verify that it has completed the requested work. Higher reasoning effort can help it persist through the final checks on complex or long-running tasks. In the Responses API, set the level with `reasoning.effort`.

```text
Bias towards action, and persist until you've completed the task the user asked for. Avoid stopping to end the turn while the task is incomplete or if there is an authorized next step you can take, and instead take the next steps within task scope to progress the user's request. Make sure that you have accounted for every part of the user's request, and persist until you've delivered a result that fully satisfies the user's goal. If a task requires sustained work, do all the necessary work until the intended outcome is completely fulfilled.

Progress autonomously towards the user's goal (e.g. creating isolated worktrees / checkouts if needed, resolving merge conflicts, creating draft PRs etc) unless they are clearly destructive or irreversible. Before ending a turn or calling your work complete, check that your work fully satisfies what the user asked for. If any steps remain or any part of the result still needs verification, follow through on this work before finishing.
```

> When a detail is unclear, give the model room to state what it’s assuming and continue with the task.

```text
Make reasonable, reversible assumptions to carry work forward and state them if it progresses the task within scope. Do not second guess yourself, stop after describing what you could do, offer to do the work, or provide a partial answer unless there is no way you can proceed.
```

### Coding style

> Describe the codebase’s conventions and any behavior that existing callers rely on. For example, specify when to reuse existing logic, how narrowly to scope a change, and when to add a test for behavior the existing suite doesn’t cover.

```text
Above all, be thorough in producing high-quality, correct code that completely fulfills the user's task. Keep the code easy to read and verify that the user-requested outcome works as they intend. Follow these instructions when coding:

(a) Reuse existing logic in the user's repo when you can. You should reuse existing classes, methods, representations, and APIs in the codebase as long as they preserve correctness. Before consolidating or removing code, preserve the behavior its callers rely on unless the task requires changing it.
(b) Skip new tests unless requested, required by the repo, or needed to catch a specific regression existing tests would miss.
(c) Make sure that code is human readable. Do not use fewer lines, shorter variable names, minified formatting, or dense one-liners as substitutes for simplicity. Ensure that comments and variable names are readable and understandable to a human. Code-golfed expressions count as overly complex when they encode many branches, conditions, or hidden assumptions.
(d) Avoid unnecessary indirection and abstraction. Helper functions, utility functions, and class abstractions can add cognitive complexity even when they do not add branches.
```

### Frontend design

> If the application depends on a specific visual style, describe it in the prompt. Specify the kinds of images it should use and the typography it should follow, including a particular typeface when that matters. Keep interface copy focused on what people need to know or do.

```text
When generating webpages or apps with a frontend user interface, follow these instructions:

- When choosing visuals, generally prefer realistic images from ImageGen or image search that suit the project's style and purpose. Use SVGs when the user specifically asks for them.
- Include a text element only when it provides information the user needs, helps them navigate or act, or fulfills an explicit content request. Remove decorative numbering, filler badges, redundant headings, and explanatory copy that merely restates what the surrounding interface already makes clear, while preserving necessary labels, instructions, and status feedback.
```

## Migration quickstart (API & model parameters)

- **Reasoning effort**: Start with `medium` for a new integration. If you currently use `none` or `minimal`, use `low` instead.
- **Tool calling**: Use the Responses API (Chat Completions is supported, but tool calling requires Responses).
- **Unsupported parameters**: Omit `temperature`, `top_p`, `logprobs`, and `top_logprobs` in Chat Completions; omit `temperature`, `top_p`, and `top_logprobs` and remove `message.output_text.logprobs` from `include` in Responses.
- **Prompt caching**: Move stable instructions from top-level `instructions` into a `developer` message at the beginning of `input`; replace `prompt_cache_retention` with `prompt_cache_options.ttl = "30m"`.
- **Zero Data Retention**: With ZDR enabled (`store: false`), pass prior output items back in order, including encrypted reasoning items.
- **Service tiers and regions**: Both models support US and EU data residency with Standard, Fast, and Batch processing; Ultrafast supports US data residency only.

## Related

- [[concepts/responses-api-prefix-continuity]]
- [[references/openai-gpt-6-2]]
- [[references/sources/openai-model-selection]]
- [[references/sources/openai-prompting-guides]]
- [[synthesis/Research: OpenAI GPT-6.2 Astra and GPT-6.2 Sol]]
- [[_raw/_archived/2026-11-18-openai-latest-model-gpt-6-2]]
