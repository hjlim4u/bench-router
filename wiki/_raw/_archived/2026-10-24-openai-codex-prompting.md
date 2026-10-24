---
title: >-
  Prompting — Codex — excerpts (2026-10-24)
source: "url:https://developers.openai.com/codex/prompting"
captured_at: 2026-10-24T14:00:00Z
capture_kind: bounded-excerpt
immutable: true
---

# Prompting — Codex

Origin: [Prompting — Codex](https://developers.openai.com/codex/prompting).

This record preserves verbatim excerpts from the Markdown rendering of the official page on 2026-10-24 (full page sha256 `c43142cb5c847afb5a2292abe9260667e9001563dceb4e48c0550809e10306f2`, 22786 characters): the 'Prompting Codex' introduction and the 'Fix a bug' and 'Write a test' workflows; other workflows and the ChatGPT chat sections are omitted. It is not a complete copy. The remote page remains mutable.

## Verbatim excerpt — Prompting Codex

> Use Codex when you want ChatGPT to work with code, a codebase, or developer tools.
> A useful Codex prompt names the behavior you want, points to the relevant code or
> reproduction steps, preserves important constraints, and says how to verify the
> change.
>
> <a id="goal-mode"></a>
>
> For a multi-step task, enter `/plan` in the app composer when you want Codex to
> investigate and propose an approach before editing. When [Goal mode](https://learn.chatgpt.com/docs/long-running-work)
> is available, use `/goal` after the plan to set a persistent goal. See the [app slash
> commands](https://learn.chatgpt.com/docs/reference/slash-commands)
> for the current command list.

## Verbatim excerpt — Fix a bug

> Use this when you have a failing behavior you can reproduce locally.
>
> #### CLI workflow (tight loop with reproduction and verification)
>
> <WorkflowSteps>
>
> 1. Start Codex at the repo root:
>
> ```bash
>    codex
> ```
>
> 2. Give Codex a reproduction recipe, plus the file(s) you suspect:
>
> ```text
>    Bug: Clicking "Save" on the settings screen sometimes shows "Saved" but doesn't persist the change.
>
>    Repro:
>    1) Start the app: npm run dev
>    2) Go to /settings
>    3) Toggle "Enable alerts"
>    4) Click Save
>    5) Refresh the page: the toggle resets
>
>    Constraints:
>    - Do not change the API shape.
>    - Keep the fix minimal and add a regression test if feasible.
>
>    Start by reproducing the bug locally, then propose a patch and run checks.
> ```
>
> </WorkflowSteps>
>
> Context notes:
>
> - Supplied by you: the repro steps and constraints (these matter more than a high-level description).
> - Supplied by Codex: command output, discovered call sites, and any stack traces it triggers.
>
> Verification:
>
> - Codex should re-run the repro steps after the fix.
> - If you have a standard check pipeline, ask it to run it:
>
> ```text
> After the fix, run lint + the smallest relevant test suite. Report the commands and results.
> ```
>
> #### IDE extension workflow
>
> <WorkflowSteps>
>
> 1. Open the file where you think the bug lives, plus its nearest caller.
> 2. Prompt Codex:
>
> ```text
>    Find the bug causing "Saved" to show without persisting changes. After proposing the fix, tell me how to verify it in the UI.
> ```
>
> </WorkflowSteps>

## Verbatim excerpt — Write a test

> Use this when you want to define the exact scope to test.
>
> #### IDE extension workflow (selection-based)
>
> <WorkflowSteps>
>
> 1. Open the file with the function.
> 2. Select the lines that define the function. Choose "Add to Codex Thread" from command palette to add these lines to the context.
> 3. Prompt Codex:
>
> ```text
>    Write a unit test for this function. Follow conventions used in other tests.
> ```
>
> </WorkflowSteps>
>
> Context notes:
>
> - Supplied by "Add to Codex Thread" command: the selected lines (this is the "line number" scope), plus open files.
>
> #### CLI workflow (path + line range described in prompt)
>
> <WorkflowSteps>
>
> 1. Start Codex:
>
> ```bash
>    codex
> ```
>
> 2. Prompt with a function name:
>
> ```text
>    Add a test for the invert_list function in @transform.ts. Cover the happy path plus edge cases.
> ```
>
> </WorkflowSteps>
