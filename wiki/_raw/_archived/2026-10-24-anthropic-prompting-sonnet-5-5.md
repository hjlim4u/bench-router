---
title: >-
  Prompting Claude Sonnet 5.5 — effort and agentic-coding excerpts (2026-10-24)
source: "url:https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5"
captured_at: 2026-10-24T13:30:00Z
capture_kind: bounded-excerpt
immutable: true
---

# Prompting Claude Sonnet 5.5

Origin: [Prompting Claude Sonnet 5.5 — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5).

This record preserves verbatim excerpts of the sections that concern effort levels and agentic coding behaviour, taken from the Markdown rendering of the official page on 2026-10-24 (full page sha256 `69e646b9ce97c2c5af96522017ce16a309a6d18653f940014c27e4f91ec49b39`, 28044 characters). It is not a complete copy; sections on other topics are omitted. The remote page remains mutable.

## Verbatim excerpt — Calibrate effort

> [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) is the main control for how much Claude Sonnet 5.5 thinks, and with it quality, latency, and cost. Its levels are recalibrated: a level doesn't produce the same amount of thinking as the same level on Claude Sonnet 5. Run a fresh sweep against your own evals rather than carrying over the setting you used on Claude Sonnet 5. Start at `high`, the default on the Claude API, unless your workload is agentic or latency-sensitive. For agentic coding and multistep tool use, start at `medium` for well-specified tasks and move to `high` for harder or longer ones. For chat and other latency-sensitive work, start at `medium` or `low`, because higher effort means a longer wait before the reply starts. Raise effort if quality needs it.
>
> Lower effort also changes how the model completes agentic work. At `low`, it keeps its thinking short and can skip verifying a change. See [Verification on coding tasks](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5#verification-on-coding-tasks). At `low` and `medium`, on long agentic tasks, it's more likely to stop and check in with the user before it completes its work. See [Steer initiative and scope](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5#steer-initiative-and-scope).
>
> Three adjustments help:
>
> * Set `max_tokens` with room for thinking and the reply you expect. Thinking counts toward `max_tokens` even when thinking content isn't returned to you. A limit sized for a request without thinking can cut the reply off. For agentic coding, set `max_tokens` to 128,000, the model's maximum, and [stream](https://platform.claude.com/docs/en/build-with-claude/streaming) the response.
> * Reserve `xhigh` and `max` for work where you've measured a quality gain, because thinking and replies get much longer there. At those levels, `between_tools` isn't accepted, so up-front thinking can't be turned off.
> * To get less thinking, lower the effort level. From `medium` up, the model thinks briefly before almost every reply, even a greeting, which adds to the time before the first visible token. Asking it in the system prompt to think less doesn't reliably reduce its thinking. At `low`, it skips thinking on most simple requests.
>
> Changing the top-level `effort` value between requests invalidates the prompt cache. To change the level partway through a conversation, use a [per-message effort change](https://platform.claude.com/docs/en/build-with-claude/effort#change-effort-mid-conversation-beta) (beta) instead, which keeps the cache. A change holds for every later turn until another one replaces it. For example, in an interactive session at `low`, add a change to `high` before the user's hard problem, and a change back to `low` after Claude answers it. Per-message effort changes need adaptive thinking. With `between_tools`, they return a 400 error, as [Running without up-front thinking](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5#running-without-up-front-thinking) explains.

## Verbatim excerpt — Steer initiative and scope

> How far Claude Sonnet 5.5 goes on its own depends on the effort level and the request. At lower effort, it sometimes checks in before a coding task is done. At higher effort, or on an open-ended request, it can do more than you asked. Steer it with the effort level and with instructions in your system prompt.
>
> **Carrying work through.** On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. It might pause to confirm a plan, ask a question it could answer itself, or stop after one part of a multipart task to ask whether to continue. Try a higher effort level first. To keep the model working without changing effort, add this to your system prompt:
>
> ```text wrap
> Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.
>
> When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.
> ```
>
> With this prompt, the model carries more of the work through at `low` and `medium` effort, so sessions at those levels run longer and cost more. The prompt doesn't replace your own rules about risky or irreversible actions. Keep those rules in your system prompt.
>
> **Unrequested additions when coding.** The model tends to add tests, documentation, and small supporting files that fit your repository's conventions, even when you don't ask for them. It does this at every effort level, and more at higher effort. The requested change itself stays close to what was asked. Most teams will welcome this. If you prefer changes limited to what was explicitly requested, add only the second paragraph of that prompt, which starts "When the work the user asked for is done." At `xhigh` and `max` effort, that paragraph reduces these additions and makes changes smaller overall.
>
> **Thoroughness at `xhigh` and `max` effort.** At these levels the model is especially thorough. After it completes a task, it can start its own rounds of review and verification, sometimes with subagents if your harness provides them. It can also make related fixes it noticed along the way. This takes more time and tokens, so run routine work at `high` or below, where it's rare. If you do want that extra thoroughness of these effort levels, but want to direct it to the task itself, add this to your system prompt:
>
> ```text wrap
> When the work the user asked for is done and its checks pass, stop and report. Don't start extra rounds of review or hardening on your own, and don't launch reviewer sub-agents unless the user asked for a review. If you think a deeper review is worth doing, say so at the end.
> ```
>
> In testing on coding tasks at `max` effort, this stopped the model from launching reviewer subagents and cut session cost by about a third, with no change in quality. It makes self-started review rounds by the main agent less frequent but doesn't remove them entirely.
>
> **Open-ended requests.** When a request is open-ended, for example "show me what you can do with this," the model can start building a presentation, report, or video when you only wanted ideas. If you want ideas or a plan first, say so in the request, or add this to your system prompt:
>
> ```text wrap
> When the user asks for ideas, options or a plan, give them that and stop. Don't start building or changing anything until they say to go ahead.
> ```

## Verbatim excerpt — Verification on coding tasks

> On agentic coding tasks, Claude Sonnet 5.5 generally checks its work before it reports a change as done. At `low` effort, though, it sometimes reports a change as done without running a check that exercises it. For example, it might skip the project's tests because the project's dependencies aren't installed.
>
> If you see changes reported as complete without test or build output in the transcript, add this paragraph, or one like it, to the system prompt. At `low` effort, it makes skipped or superficial checks rare, with no measurable change in task quality and only a slightly higher cost per task:
>
> ```text wrap
> When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.
> ```
