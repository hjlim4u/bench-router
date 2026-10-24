---
title: >-
  Anthropic per-model prompting guides — effort and agentic coding
category: references
tags: [source, reasoning, coding]
sources:
  - "url:https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1"
  - "url:https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5"
  - "url:https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5"
  - "url:https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5"
created: 2026-10-24T13:30:00Z
updated: 2026-10-24T13:30:00Z
as_of: 2026-10-24
summary: >-
  Verbatim effort and agentic-coding passages from Anthropic's per-model prompting guides for Fable 5.1, Opus 5.5, Sonnet 5.5 and Haiku 5.5.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-24
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-24-anthropic-prompting-fable-5-1|2026-10-24-anthropic-prompting-fable-5-1]]"
  - "[[_raw/_archived/2026-10-24-anthropic-prompting-opus-5-5|2026-10-24-anthropic-prompting-opus-5-5]]"
  - "[[_raw/_archived/2026-10-24-anthropic-prompting-sonnet-5-5|2026-10-24-anthropic-prompting-sonnet-5-5]]"
  - "[[_raw/_archived/2026-10-24-anthropic-prompting-haiku-5-5|2026-10-24-anthropic-prompting-haiku-5-5]]"
---

# Anthropic per-model prompting guides — effort and agentic coding

Anthropic publishes one prompting guide per model. Each has an effort section next to the model's behaviour changes. The passages below are quoted verbatim from the pages as of 2026-10-24. They add conditions the effort page does not carry, for example what happens at `low` and `medium` on long agentic tasks. The effort page's own statement still applies: "The per-model recommendations that follow override this table where they differ." ([[references/sources/anthropic-effort]]). No page in this set contradicts those recommendations.

Fable 5 and Opus 5 and older models have their own guides and are not captured here; the router registers Fable 5.1, Opus 5.5, Sonnet 5.5 and Haiku 5.5.

## Claude Fable 5.1

Source: [[_raw/_archived/2026-10-24-anthropic-prompting-fable-5-1]]

### Consider all effort levels

> Start at the default [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level, `high`, then test the other levels (`low`, `medium`, `xhigh`, and `max`) against your own evals. Effort is the primary control for trading off intelligence, latency, and cost on Claude Fable 5.1. Re-run the sweep even if you already ran one on Claude Fable 5: effort level names don't correspond to the same amount of thinking across models.

> Claude Fable 5.1's capability gains over Claude Fable 5 show up across effort levels and are largest at the higher settings. At `medium`, results roughly match Claude Fable 5 at lower cost, so step down to `medium` or `low` where your evals show quality holds. At `low`, Claude Fable 5.1 is often competitive with Claude Opus and Claude Sonnet models on cost per task while scoring higher, so include it in the comparison wherever you'd otherwise run a smaller model at a higher effort level.

## Claude Opus 5.5

Source: [[_raw/_archived/2026-10-24-anthropic-prompting-opus-5-5]]

### Calibrate effort

> [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) is the main control for how much Claude Opus 5.5 thinks, and because thinking is always on, it's the first setting to adjust when trading off intelligence, latency, and cost. Start at `medium`, the default on Claude Opus 5.5 (Claude Opus 5 defaults to `high`), set it explicitly, and test several levels against your own evals rather than carrying over the setting you used on Claude Opus 5. Effort level names don't correspond to the same amount of thinking across models: in Anthropic's testing, Claude Opus 5.5 at `medium` matches or exceeds Claude Opus 5 at `high` on coding and knowledge-work evaluations, and on several coding evaluations `low` comes close to it at much lower cost. See [Recommended effort levels for Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/effort#recommended-effort-levels-for-claude-opus-5-5).

> At a given level, Claude Opus 5.5 tends to think more per turn than Claude Opus 5, especially at `xhigh` and `max`. If you keep the `effort` value you set for Claude Opus 5, expect longer turns and more output tokens. Three adjustments help:

> * Reserve `xhigh` and `max` for work where you've measured a quality gain.

## Claude Sonnet 5.5

Source: [[_raw/_archived/2026-10-24-anthropic-prompting-sonnet-5-5]]

### Calibrate effort

> [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) is the main control for how much Claude Sonnet 5.5 thinks, and with it quality, latency, and cost. Its levels are recalibrated: a level doesn't produce the same amount of thinking as the same level on Claude Sonnet 5. Run a fresh sweep against your own evals rather than carrying over the setting you used on Claude Sonnet 5. Start at `high`, the default on the Claude API, unless your workload is agentic or latency-sensitive. For agentic coding and multistep tool use, start at `medium` for well-specified tasks and move to `high` for harder or longer ones. For chat and other latency-sensitive work, start at `medium` or `low`, because higher effort means a longer wait before the reply starts. Raise effort if quality needs it.

> Lower effort also changes how the model completes agentic work. At `low`, it keeps its thinking short and can skip verifying a change. See [Verification on coding tasks](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5#verification-on-coding-tasks). At `low` and `medium`, on long agentic tasks, it's more likely to stop and check in with the user before it completes its work. See [Steer initiative and scope](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5#steer-initiative-and-scope).

> * Reserve `xhigh` and `max` for work where you've measured a quality gain, because thinking and replies get much longer there. At those levels, `between_tools` isn't accepted, so up-front thinking can't be turned off.

### Steer initiative and scope

> **Carrying work through.** On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. It might pause to confirm a plan, ask a question it could answer itself, or stop after one part of a multipart task to ask whether to continue. Try a higher effort level first. To keep the model working without changing effort, add this to your system prompt:

> **Thoroughness at `xhigh` and `max` effort.** At these levels the model is especially thorough. After it completes a task, it can start its own rounds of review and verification, sometimes with subagents if your harness provides them. It can also make related fixes it noticed along the way. This takes more time and tokens, so run routine work at `high` or below, where it's rare. If you do want that extra thoroughness of these effort levels, but want to direct it to the task itself, add this to your system prompt:

### Verification on coding tasks

> On agentic coding tasks, Claude Sonnet 5.5 generally checks its work before it reports a change as done. At `low` effort, though, it sometimes reports a change as done without running a check that exercises it. For example, it might skip the project's tests because the project's dependencies aren't installed.

## Claude Haiku 5.5

Source: [[_raw/_archived/2026-10-24-anthropic-prompting-haiku-5-5]]

### Use effort to control thinking

> * `low` is the cheapest and fastest level. Use it for chat, short tool tasks, and simple, high-volume requests. In long agent prompts, the model is more likely to skip a search, stop early, or skip a check at this level.

> * `medium` is the default. Start here for most work, including agentic coding.

> * `high` suits knowledge work, longer agent tasks, and strict instruction following.

> * `xhigh` and `max` are for work where a quality gain on your evals justifies the cost. Thinking and replies get much longer at these levels, so also run your evals on Claude Sonnet 5.5 and compare performance, cost, and speed.

### Prevent early stopping in long agent prompts

> With a short system prompt, Claude Haiku 5.5 rarely stops before the work is done. With a long coding-agent system prompt at `low` effort, it sometimes stops early and hands the task back to the user. If you see this in your agent, add this text to your system prompt:

> Raising effort also reduces early stopping, on its own or together with this text, at a higher cost. In Anthropic's testing without the text, moving from `low` to `medium` effort roughly halved early stopping. It also more than doubled the output tokens for each attempt.

### Tell coding agents to verify their changes

> At `low` and `medium` effort, Claude Haiku 5.5 sometimes reports a code change as done without running a check. If you see the model report results without checking its work, add this paragraph, or one like it, to your system prompt:

### Keep chatbots to their system prompt

> When instruction following matters most, also use `high` effort.

### Keep reasoning out of user-facing text

> Claude Haiku 5.5 sometimes writes reasoning-like text in the reply that users see. This occurs more often with thinking off or at `low` effort. If you see this behavior, switch to adaptive thinking and `medium` effort.

## Agentic-coding prompt guidance shown for the selected model

The bench-router shows these passages for a selected Claude model (`prompt-guidance`).

### Finish the whole task

> On complex asynchronous workloads, though, nudge it not to end its turn before the work is done.

The page supplies this prompt text:

```text
You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work. For reversible actions that follow from the original request, proceed without asking. Stop only for destructive actions or genuine scope changes the user must decide. Offering follow-ups after the task is done is fine; asking permission before doing the work is not.

Exception: when the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one.

Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ('I'll…', 'let me know when…'), do that work now with tool calls. That includes retrying after errors and gathering missing information yourself. Do not stop because the context or session is long. End your turn only when the task is complete or you are blocked on input only the user can provide.

Before running a command that changes system state (such as restarts, deletes, or config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause.
```

### Keep changes and tests to what the task asks for

> It responds well to explicit instructions about what to leave out.

The page supplies this prompt text:

```text
If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files — roughly one focused test per stated behavior — and don't turn scratch checks into additional permanent test files. This is about extras only: implement every behavior the task asks for, completely.
```

### Name the early stops to avoid

> Claude Opus 5.5 is responsive to instructions that name the specific kinds of early stop you want it to avoid, such as ending the turn with a summary that announces the next step instead of taking it.

### Carrying work through

> On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done.

The page supplies this prompt text:

```text
Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.

When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.
```

### Verification on coding tasks

> If you see changes reported as complete without test or build output in the transcript, add this paragraph, or one like it, to the system prompt.

The page supplies this prompt text:

```text
When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.
```

### Prevent early stopping in long agent prompts

> With a long coding-agent system prompt at `low` effort, it sometimes stops early and hands the task back to the user.

The page supplies this prompt text:

```text
Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.
When the work the user asked for is done and checked, stop and report. Don't add new features, docs, or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.
```

### Verification on coding tasks

> At `low` and `medium` effort, Claude Haiku 5.5 sometimes reports a code change as done without running a check.

The page supplies this prompt text:

```text
When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.
```

## Reading across models

These are observations about the quoted text, not new guidance.

- Starting points agree with [[references/sources/anthropic-effort]]: Fable 5.1 `high`, Opus 5.5 `medium`, Sonnet 5.5 `high` (`medium` for well-specified agentic coding), Haiku 5.5 `medium`.
- Sonnet 5.5 and Haiku 5.5 both say lower effort raises the chance of stopping early or skipping verification; both give raising effort as a remedy.
- Opus 5.5 and Sonnet 5.5 both restrict `xhigh` and `max` to work where a quality gain has been measured. Fable 5.1's page treats `medium` and `low` as step-down choices once quality holds.

## Related

- [[references/sources/anthropic-effort]]
- [[references/sources/anthropic-model-selection]]
- [[concepts/model-effort-selection]]

## Sources

- [[_raw/_archived/2026-10-24-anthropic-prompting-fable-5-1]]
- [[_raw/_archived/2026-10-24-anthropic-prompting-opus-5-5]]
- [[_raw/_archived/2026-10-24-anthropic-prompting-sonnet-5-5]]
- [[_raw/_archived/2026-10-24-anthropic-prompting-haiku-5-5]]
