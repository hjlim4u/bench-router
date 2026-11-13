---
source_url: "https://platform.claude.com/docs/en/build-with-claude/effort"
fetched_at: "2026-11-13"
extraction: "defuddle"
capture_note: "Model-specific recommendation tabs are omitted by extraction; consult the original page and Fable prompting capture."
---

Usage differs by product

Messages API

Set `output_config.effort` on the request. With no value, the model’s default level applies.

Managed Agents

Set `effort` on the agent’s model object, or in a session’s model override. With no value, Managed Agents fills in the model’s default.

The effort parameter lets you control how many tokens Claude spends when responding to requests. You can trade off between response thoroughness and token efficiency with a single model.

## Set the effort level

Set `output_config.effort` on the request. The following example runs one request at `medium` effort.

```
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Analyze the trade-offs between microservices and monolithic architectures",
        }
    ],
    output_config={"effort": "medium"},
)

for block in response.content:
    if block.type == "text":
        print(block.text)
```

## How effort works

Most Claude models default to high effort, spending as many tokens as needed for excellent results; Claude Opus 5.5 and Claude Haiku 5.5 default to medium. You can raise the effort level to `max` for the absolute highest capability, or lower it to be more conservative with token usage, optimizing for speed and cost while accepting some reduction in capability.

The effort parameter affects **all tokens** in the response, including:

- Text responses and explanations
- Tool calls and function arguments
- Thinking (when active)

Because effort applies to every output token, it works with or without thinking. Lower effort also means fewer and terser tool calls.

### Effort levels

| Level | Description | Typical use case |
| --- | --- | --- |
| `max` | Absolute maximum capability with no constraints on token spending. Available on Claude Fable 5.2, Claude Mythos 5.2, Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, Claude Mythos Preview, Claude Opus 5.5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5.5, Claude Sonnet 5, Claude Sonnet 4.6, and Claude Haiku 5.5. | Tasks requiring the deepest possible reasoning and most thorough analysis |
| `xhigh` | Extended capability for long-horizon work. Available on Claude Fable 5.2, Claude Mythos 5.2, Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, Claude Opus 5.5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Sonnet 5.5, Claude Sonnet 5, and Claude Haiku 5.5. | Long-running agentic and coding tasks (over 30 minutes) with token budgets in the millions |
| `high` | Spends as many tokens as the task needs for excellent results. The default on every model that supports effort except Claude Opus 5.5 and Claude Haiku 5.5. | Complex reasoning, difficult coding problems, agentic tasks |
| `medium` | Balanced approach with moderate token savings. The default on Claude Opus 5.5 and Claude Haiku 5.5. | Agentic tasks that require a balance of speed, cost, and performance |
| `low` | Most efficient. Significant token savings with some capability reduction. | Simpler tasks that need the best speed and lowest costs, such as subagents |

Not every model that supports `max` supports `xhigh`.

The per-model recommendations that follow override this table where they differ.

## Recommended effort levels

## Effort with tool use

When using tools, the effort parameter affects both the explanations around tool calls and the tool calls themselves. Lower effort levels tend to:

- Combine multiple operations into fewer tool calls
- Make fewer tool calls
- Proceed directly to action without preamble
- Use terse confirmation messages after completion

Higher effort levels might:

- Make more tool calls
- Explain the plan before taking action
- Provide detailed summaries of changes
- Include more comprehensive code comments

## Effort with thinking

The `thinking` parameter controls whether Claude thinks in [thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking) before answering; the `effort` parameter controls how much work Claude puts into the whole response, which in adaptive mode includes how often and how deeply it thinks. Don’t pass `adaptive` as an `effort` value: `adaptive` is a thinking mode, not an effort level.

At higher effort levels, Claude thinks more readily and at greater length. In a tool-use loop, follow-up requests that only process tool results can still skip thinking at any level. At lower levels, Claude can skip thinking entirely for simpler problems. See [Thinking and effort](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-effort) for full guidance on how the two controls work together.

On Claude Opus 4.5, the only extended-thinking-only model that supports effort, it works alongside [`budget_tokens`](https://platform.claude.com/docs/en/build-with-claude/extended-thinking): set the effort level for your task, then set the thinking token budget based on how much reasoning depth the task needs.

For per-model thinking availability, see the [per-model configuration table](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#supported-models). Effort works with or without thinking. See [How effort works](#how-effort-works).

## Change effort mid-conversation

You can run later turns of a conversation at a different effort level in two ways. A per-message effort change keeps the prompt cache. A new top-level value on the next request can invalidate all or part of the prompt cache.

### Per-message effort

[Per-message effort](https://platform.claude.com/docs/en/build-with-claude/effort-per-message) sets a new level with a `system` message in `messages`.

### Top-level effort on the next request

The top-level `output_config.effort` applies to the whole request. To run a later part of a conversation at a different level, set the new value on the next request. Because top-level effort shapes the rendered prompt, changing it between requests can invalidate cached prefixes from earlier turns. If you rely on [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) across a long session and your model doesn’t support per-message effort, pick an effort level at the start and keep it constant.

## Best practices

1. **Set effort explicitly:** The API defaults to `high` (`medium` on Claude Opus 5.5 and Claude Haiku 5.5), but the right starting point depends on your model and workload.
2. **Use low for speed-sensitive or simple tasks:** When latency matters or tasks are straightforward, low effort can significantly reduce response times and costs.
3. **Test your use case:** The impact of effort levels varies by task type. Evaluate performance on your specific use cases before deploying.
4. **Consider dynamic effort:** Adjust effort based on task complexity. Simple queries might warrant low effort, whereas agentic coding and complex reasoning benefit from high effort. See the next item before varying it within one conversation.
5. **Hold top-level effort constant within cached conversations:** Changing the top-level effort value between requests can invalidate all or part of the [prompt cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), so vary it across workloads rather than within a conversation that relies on cache hits. On models that support it, use a [per-message effort](https://platform.claude.com/docs/en/build-with-claude/effort-per-message) change instead, which preserves the cache. See [Thinking and prompt caching](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-prompt-caching).

## Next steps

[Task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets)

Give Claude an advisory token budget for the full agentic loop to help the model self-regulate on long agentic tasks.

[Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost)

Understand adaptive thinking, where Claude determines when and how much to think, and steer it with effort and prompting.

[Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)

Understand how thinking works, when Claude thinks by default, and how thinking interacts with effort.

## Availability

Effort

APIs

Models

- Claude Fable 5.2, Fable 5.1, Fable 5
- Claude Mythos 5.2, Mythos 5.1, Mythos 5, Mythos Preview
- Claude Opus 5.5, Opus 5, Opus 4.8, Opus 4.7, Opus 4.6, Opus 4.5
- Claude Sonnet 5.5, Sonnet 5, Sonnet 4.6
- Claude Haiku 5.5

### Data handling

[Data handling overview](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility)