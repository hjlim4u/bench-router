---
title: >-
  Prompting Claude Fable 5.1 — effort and agentic-coding excerpts (2026-10-24)
source: "url:https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1"
captured_at: 2026-10-24T13:30:00Z
capture_kind: bounded-excerpt
immutable: true
---

# Prompting Claude Fable 5.1

Origin: [Prompting Claude Fable 5.1 — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1).

This record preserves verbatim excerpts of the sections that concern effort levels and agentic coding behaviour, taken from the Markdown rendering of the official page on 2026-10-24 (full page sha256 `2683e696addd5707c125d89242637eae2ee0cf7d35562aa26639602057331426`, 54907 characters). It is not a complete copy; sections on other topics are omitted. The remote page remains mutable.

## Verbatim excerpt — Consider all effort levels

> Start at the default [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level, `high`, then test the other levels (`low`, `medium`, `xhigh`, and `max`) against your own evals. Effort is the primary control for trading off intelligence, latency, and cost on Claude Fable 5.1. Re-run the sweep even if you already ran one on Claude Fable 5: effort level names don't correspond to the same amount of thinking across models.
>
> Claude Fable 5.1's capability gains over Claude Fable 5 show up across effort levels and are largest at the higher settings. At `medium`, results roughly match Claude Fable 5 at lower cost, so step down to `medium` or `low` where your evals show quality holds. At `low`, Claude Fable 5.1 is often competitive with Claude Opus and Claude Sonnet models on cost per task while scoring higher, so include it in the comparison wherever you'd otherwise run a smaller model at a higher effort level.
>
> Two effort-specific behaviors have their own sections: at `low`, Claude Fable 5.1 calls search and retrieval tools less often (see [Search triggering at low effort](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#search-triggering-at-low-effort)), and at `xhigh` and `max` it can think for longer before writing a long deliverable (see [Leave room for long outputs at xhigh and max effort](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#leave-room-for-long-outputs-at-xhigh-and-max-effort)).

## Verbatim excerpt — Search triggering at low effort

> At `low` effort, Claude Fable 5.1 is less likely than Claude Fable 5 to call a search or retrieval tool, and more likely to answer from memory. In some cases the simplest fix is to raise effort for the affected turns rather than the whole conversation. See [Change effort mid-conversation](https://platform.claude.com/docs/en/build-with-claude/effort#changing-effort-mid-conversation).
>
> In other cases, a prompt nudge toward verification helps. In the system prompt, say that recognizing a name isn't the same as knowing its current state, and that such names should be searched as the user wrote them:
>
> ```text wrap
> When a query centers on a name you do not confidently recognize, or recognize from a fast-moving area like AI models and developer tools where the landscape shifts within months, the name itself is the thing to verify: search before answering, and include the name as the user wrote it in at least one query alongside any reformulations. This holds even when you have some background on it — partial background is exactly what makes an out-of-date answer sound authoritative, so familiarity is not a reason to skip the search.
> ```

## Verbatim excerpt — Leave room for long outputs at xhigh and max effort

> At `xhigh` and especially `max` effort, Claude Fable 5.1 can think for longer before it starts writing its reply. When a single request asks for a long deliverable, such as a full rewrite of a long document, it might draft much of that deliverable in its thinking and then write it again as the reply, which means a longer wait and more output tokens. The simplest approach is to run requests like these at `high`, the recommended starting point, and move to `xhigh` or `max` only where you've measured a quality gain (see [Consider all effort levels](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#consider-all-effort-levels)). If you do run them at `xhigh` or `max`:
>
> * Set `max_tokens` to leave room for the thinking and the reply, not just the reply length you expect.
> * Append the following note to the end of the user message. It makes the thinking much shorter on prose and code requests. Replace `[max_tokens]` with the request's actual `max_tokens` value, for example 64,000.
>
> ```text wrap
> Everything produced in one reply, including any reasoning or drafting done before the reply, counts toward a single limit of about [max_tokens] tokens. If that limit is reached before the reply is finished, the person receives a cut-off response and has to start over. Composing an entire output or deliverable in full as reasoning and then again as a reply would double the length of the turn without improving the result, so don't do that.
>
> Instead, when the person has asked for a long or effort-intensive deliverable such as a multi-section document, a large table or dataset, or a complete code file, spend extra effort on understanding the request, checking the inputs the answer depends on, settling the structure and other difficult decisions, and otherwise using the reasoning space to reason and the output space to write an output. Usually it is not needed to draft an output multiple times.
> ```

## Verbatim excerpt — Finish the whole task

> Claude Fable 5.1 can run very long tasks without much guidance on methodology, especially when the goal is clear. On complex asynchronous workloads, though, nudge it not to end its turn before the work is done. Without the nudge, the model sometimes describes what it would do next instead of doing it ("Next, I'll …") or stops to ask permission for a step the original request already covered ("Shall I apply this?"). Users have to reply "continue" or "go ahead," which suits pair programming and other human-in-the-loop work but doesn't use the model's full long-horizon capability.
>
> Two system prompt additions together mitigate this. Apply both. If you need to limit prompt length, use only the first, which keeps most of the effect. The first tells the model not to ask about work already requested and to carry out the next steps it has stated:
>
> ```text wrap
> You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work. For reversible actions that follow from the original request, proceed without asking. Stop only for destructive actions or genuine scope changes the user must decide. Offering follow-ups after the task is done is fine; asking permission before doing the work is not.
>
> Exception: when the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one.
>
> Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ('I'll…', 'let me know when…'), do that work now with tool calls. That includes retrying after errors and gathering missing information yourself. Do not stop because the context or session is long. End your turn only when the task is complete or you are blocked on input only the user can provide.
>
> Before running a command that changes system state (such as restarts, deletes, or config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause.
> ```
>
> The opening sentence, which tells the model the user isn't watching, carries much of the effect. Keep it as written. If your product needs the model to stop for specific confirmations, add a sentence after it listing them. This block can also make the model less likely to ask about ambiguous requests, so check that trade-off on your own tasks.
>
> The second defines the user's request as the scope of the deliverable:
>
> ```text wrap
> # Delivering work
> The user's request — or the plan they approved — sets the scope, and the scope is the deliverable: don't quietly narrow, widen, or swap it. Read ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different readings would lead to materially different work. If you see a real problem with the task as specified, say so in a sentence or two and keep building under stated assumptions; if the user hears the concern and reaffirms, that is their decision, so deliver the full request.
>
> If a question comes up partway, first do everything that doesn't depend on the answer; then state the assumption you made, or — when going ahead on a wrong guess would be unsafe or would make the work useless — put the question at the end of a turn that also delivers that progress. If one part turns out to be blocked, complete every other part in full and say exactly what you left out and why — the whole task is the deliverable, and scaling it down is the user's call, not yours. A step you have decided on is something to run, not to announce: describing the next step and ending the turn leaves it undone until the user replies.
>
> Keep changes to what the request needs. Something else you notice worth doing — cleanup or documentation the task didn't call for, a change to a file the task didn't require — is a suggestion to make at the end, not a change to make; actions clearly beyond what the ask implies, and risky or destructive ones, still need the user's go-ahead.
> ```

## Verbatim excerpt — Keep changes and tests to what the task asks for

> When asked to implement an open-ended feature, Claude Fable 5.1 delivers what's asked for and sometimes more: it might fix nearby code, extend behavior the task didn't mention, or commit more test files than the change warrants. It responds well to explicit instructions about what to leave out. With the following instruction, unrequested additions and committed test code drop substantially with no measurable change in task success:
>
> ```text wrap
> If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files — roughly one focused test per stated behavior — and don't turn scratch checks into additional permanent test files. This is about extras only: implement every behavior the task asks for, completely.
> ```
