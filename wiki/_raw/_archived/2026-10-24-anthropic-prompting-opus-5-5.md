---
title: >-
  Prompting Claude Opus 5.5 — effort and agentic-coding excerpts (2026-10-24)
source: "url:https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5"
captured_at: 2026-10-24T13:30:00Z
capture_kind: bounded-excerpt
immutable: true
---

# Prompting Claude Opus 5.5

Origin: [Prompting Claude Opus 5.5 — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5).

This record preserves verbatim excerpts of the sections that concern effort levels and agentic coding behaviour, taken from the Markdown rendering of the official page on 2026-10-24 (full page sha256 `b826453f6e710fd9b2d4a3fc0e2bcc192cf69dc9d3ae59e79c92bb111677d9bf`, 28875 characters). It is not a complete copy; sections on other topics are omitted. The remote page remains mutable.

## Verbatim excerpt — Calibrate effort

> [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) is the main control for how much Claude Opus 5.5 thinks, and because thinking is always on, it's the first setting to adjust when trading off intelligence, latency, and cost. Start at `medium`, the default on Claude Opus 5.5 (Claude Opus 5 defaults to `high`), set it explicitly, and test several levels against your own evals rather than carrying over the setting you used on Claude Opus 5. Effort level names don't correspond to the same amount of thinking across models: in Anthropic's testing, Claude Opus 5.5 at `medium` matches or exceeds Claude Opus 5 at `high` on coding and knowledge-work evaluations, and on several coding evaluations `low` comes close to it at much lower cost. See [Recommended effort levels for Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/effort#recommended-effort-levels-for-claude-opus-5-5).
>
> At a given level, Claude Opus 5.5 tends to think more per turn than Claude Opus 5, especially at `xhigh` and `max`. If you keep the `effort` value you set for Claude Opus 5, expect longer turns and more output tokens. Three adjustments help:
>
> * Set `max_tokens` high enough to leave room for the model's thinking tokens and the reply. Thinking counts toward `max_tokens` even when thinking content isn't returned to you, so a limit sized for Claude Opus 5 with thinking off can cut replies off. For the long turns that agentic coding can produce, a `max_tokens` of 128,000, the model's maximum, has worked well in Anthropic's testing.
> * Reserve `xhigh` and `max` for work where you've measured a quality gain.
> * To get less thinking, lower the effort level first. Lowering effort reduces thinking, and with it cost and latency, more reliably than prompt instructions do.
>
> Changing the top-level `effort` value between requests invalidates the prompt cache. To change the level partway through a conversation, use a [per-message effort change](https://platform.claude.com/docs/en/build-with-claude/effort#change-effort-mid-conversation-beta) (beta) instead, which keeps the cache. A change holds for every later turn until another one replaces it.

## Verbatim excerpt — Unattended agentic runs

> On long tasks with several parts, Claude Opus 5.5 keeps the user updated as it works, and some of those updates end the turn with text rather than a tool call ([`stop_reason: "end_turn"`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#end-turn)). An unattended agent loop that treats such a turn as the end of the task stops running there. A few harness and prompt changes help it keep running.
>
> Treat a text-only end of turn as a report rather than as proof the task is done. Keep the task's parts in a checklist the model updates, such as a to-do tool or a file. If a turn ends with items still open and no blocker stated, send a short user message naming them, such as the following one. You can also state the completion condition up front and have a separate, smaller model check the conversation against it at each end of turn, returning its reason as the next user message when the condition isn't met. Either way, stop after two or three automatic continuations on the same task rather than repeating them indefinitely, so that a run that is genuinely stuck ends and can be reviewed.
>
> ```text wrap
> Your task list still has open items: migrate the remaining two endpoints and update their tests. Continue with them. If one is blocked, say what is blocking it.
> ```
>
> If something the model started is still running, such as a background command or a subagent, don't treat the task as done yet: wait for it to finish and return its output to the model as the next user message.
>
> A system prompt addition can also make these early stops less frequent. Claude Opus 5.5 is responsive to instructions that name the specific kinds of early stop you want it to avoid, such as ending the turn with a summary that announces the next step instead of taking it. It also helps to name the stops you do want, for example when no work can advance without the user's input.
>
> The following paragraph is one example of such an addition, written for agents that run fully unattended, where you want the model to keep working rather than stop to report. Treat it as a starting point: you might need to adapt it for your own application. Add it at the end of your system prompt from the first request of the session: adding it partway through changes the `system` prompt and invalidates the conversation's earlier thinking blocks (see [Add instructions with a mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#new-instructions)). Because it tells the model to put status notes in the same message as its next tool call, those notes arrive between tool calls as progress updates. The text of these updates comes back empty at the default `thinking.display`. Set `display: "updates"` to receive a summary of each (see [User-facing progress updates](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5#user-facing-progress-updates)). With this addition the model carries on where it would otherwise have stopped to check in, so keep your own confirmation step for risky or irreversible actions, and leave the addition out of human-in-the-loop applications, where someone is there to answer. Expect somewhat more tool calls and output tokens per task.
>
> ```text wrap
> A standing instruction from the user, the person you are working for. It is about how your turns end. A message with no tool call in it ends your turn, and the work stops there until you are asked to continue. The user has seen you end turns in four ways while work they asked for was still owed, and does not want any of them. One: a long summary of what was done that closes by announcing the next step and has no tool call, so the next thing never starts. Two: an offer to carry on with something unless the user would prefer otherwise, which stops to wait for an answer the user was not going to give. Three: a list of decisions for the user when, by your own account, none of them blocks the rest of the work. Four: deciding that this is a good place to report, because the turn has been long or a milestone is done. Status notes are welcome, and so are your recommendations on open decisions, but put them in the same message as your next tool call and carry on with whatever does not depend on the user's answer. If you notice yourself inviting the user to redirect you or offering to wait, delete it and do the next thing. The stops the user does want are the ones where nothing can move without them, or where the thing blocking you is deliberately protected from you. This does not override the need for confirmation on risky or destructive actions.
> ```
