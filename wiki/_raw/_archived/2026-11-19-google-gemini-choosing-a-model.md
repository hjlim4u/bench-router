---
source_url: https://aistudio.google.com/docs/choosing-a-model.md
captured_at: 2026-11-19T08:02:38Z
scope: Complete verbatim Markdown of the Google AI Studio Choosing a model guide (.md endpoint).
immutable: true
---

> ## AI Agent Context
> - Full documentation index: https://aistudio.google.com/llms.txt
> - Gemini Docs MCP server (consistent live info): https://gemini-api-docs-mcp.dev
> - Coding agent skills & setup guide: https://aistudio.google.com/docs/coding-agents.md

# Choosing a model

Pick a Gemini model by matching its reasoning depth, response speed, and token price to your task. Every general-purpose Gemini model accepts text, images, audio, video, and PDFs.

* **Default to [`gemini-4-hydrogen`](/docs/models/gemini-4-hydrogen):** Fast and cost-efficient for everyday coding, interactive apps, tool-using agents, and multimodal documents.
* **Use [`gemini-4-neon`](/docs/models/gemini-4-neon) for complex, high-frequency tasks:** Sits between Hydrogen and Carbon, with deeper reasoning than Hydrogen and faster task completion than Carbon. Built for multi-file coding, knowledge work, and science workflows. Paid tier only.
* **Use [`gemini-4-carbon`](/docs/models/gemini-4-carbon) for your hardest problems:** Spends more thinking tokens to verify edge cases across system architecture, debugging, science, and security.
* **Use [`gemini-3.5-flash-lite`](/docs/models/gemini-3.5-flash-lite) for high-volume text generation:** Lowest-cost general model for extraction, translation, summarization, and sub-second latency targets.
* **Check specialized models for dedicated tasks and modalities:** We also have purpose-built models such as [`gemini-decision-1`](/docs/decisions-api) for classification, routing, and scoring decisions your code branches on, [Nano Banana](/docs/image-generation) for images, [Gemini Omni](/docs/omni) for video, and [Gemini 3.8 Live](/docs/live-api) for real-time voice.

Send a request with the [Interactions API](/docs/interactions-overview), and swap `model` to test any tier on your prompts:

{% tabs %}
  {% tab label="Python" %}
  ```python
  from google import genai
  
  client = genai.Client()
  
  interaction = client.interactions.create(
      model="gemini-4-hydrogen",  # Or "gemini-4-neon", "gemini-4-carbon", "gemini-3.5-flash-lite"
      input="Design a Postgres schema for multi-tenant webhook delivery with exponential retry.",
  )
  
  print(interaction.output_text)
  ```

  {% /tab %}

  {% tab label="JavaScript" %}
  ```javascript
  import { GoogleGenAI } from "@google/genai";
  
  const client = new GoogleGenAI({});
  
  const interaction = await client.interactions.create({
    model: "gemini-4-hydrogen", // Or "gemini-4-neon", "gemini-4-carbon", "gemini-3.5-flash-lite"
    input: "Design a Postgres schema for multi-tenant webhook delivery with exponential retry.",
  });
  
  console.log(interaction.output_text);
  ```

  {% /tab %}

  {% tab label="REST" %}
  ```bash
  curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "gemini-4-hydrogen",
      "input": "Design a Postgres schema for multi-tenant webhook delivery with exponential retry."
    }'
  ```

  {% /tab %}

{% /tabs %}

## General-purpose and reasoning models  {% id="reasoning-models" %}

Gemini 4 Carbon, Neon, and Hydrogen share a 1M unified context window, [long decode](/docs/long-decode) up to 1M tokens, and built-in tools ([Google Search](/docs/google-search), [code execution](/docs/code-execution), [function calling](/docs/function-calling), [computer use](/docs/computer-use), and [structured outputs](/docs/structured-output)). They differ in how many thinking tokens they spend per turn, how fast they respond, and what they cost.

| Model | Speed | Thinking levels | Price per 1M tokens (input / output) |
| :--- | :--- | :--- | :--- |
| [`gemini-4-carbon`](/docs/models/gemini-4-carbon) | Deliberate | `low`, `medium` (default), `high` | $2.00 / $10.00 (intro thru Nov 30) |
| [`gemini-4-neon`](/docs/models/gemini-4-neon) | Moderate | `low`, `medium`, `high` (default), `xhigh` | $3.00 / $15.00 |
| [`gemini-4-hydrogen`](/docs/models/gemini-4-hydrogen) | Fast | `low`, `medium`, `high` (default), `xhigh` | $1.50 / $7.50 |
| [`gemini-3.5-flash-lite`](/docs/models/gemini-3.5-flash-lite) | Fastest | `minimal` (default), `low`, `medium`, `high` | $0.30 / $2.50 |

A few details the table leaves out:

* **Introductory pricing:** Carbon's price is introductory through November 30, 2026. From December 1, 2026, it's $4.00 input and $20.00 output per 1M tokens. Neon has no introductory price.
* **Free tier:** Hydrogen and Flash-Lite are available on the free tier. Carbon and Neon aren't.
* **Context and output:** Flash-Lite has a 1M-token input window and a separate 64K output limit, rather than the unified 1M window.

For full tier details and rate limits, see [Pricing](/docs/pricing) and [Rate limits](/docs/rate-limits).

### When to choose each model  {% id="when-to-choose" %}

* **Gemini 4 Hydrogen (`gemini-4-hydrogen`):** Start here for most new projects. Hydrogen cuts fabricated claims by more than 5x compared to [Gemini 3.8 Flash](/docs/whats-new-gemini-3.8) by flagging missing context instead of guessing, and batches read and search tool calls in parallel. Choose it for everyday coding, interactive web apps, multimodal document pipelines, and parallel worker agents.
* **Gemini 4 Neon (`gemini-4-neon`):** Sits between Hydrogen and Carbon. Finishes faster with fewer output tokens than Carbon while handling harder reasoning than Hydrogen. Choose it for complex software engineering, dense knowledge work, and science workflows where Hydrogen isn't enough and you don't need Carbon's extra verification.
* **Gemini 4 Carbon (`gemini-4-carbon`):** Our strongest reasoning model. Carbon spends more thinking tokens per turn to test hypotheses, isolate root causes across repositories, and check fixes against tests. Choose it for system architecture, multi-file debugging, dense multimodal analysis, formal proofs, and security audits, or when a faster model gets stuck.
* **Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`):** Our fastest, lowest-cost general model. Choose it when you need generated text at high volume, such as translation, summarization, and structured JSON extraction, or when you have sub-second latency targets. If your code only needs a label, a yes/no, or a score to branch on (classification, routing, or moderation), consider [`gemini-decision-1`](/docs/decisions-api), which returns calibrated answers with zero output tokens.

## Pair models in multi-step workflows  {% id="pair-models" %}

You don't have to pick one model for your whole app. Because Carbon, Neon, and Hydrogen share the same request schema, context window, and tools, you can route each step to the model that fits it.

A common pattern pairs `gemini-4-carbon` with `gemini-4-hydrogen`. Have Carbon design system interfaces or isolate a hard bug on the first turn. Then pass `previous_interaction_id` to Hydrogen to write the code edits, run parallel subagent tasks, and iterate on tests at lower latency and cost.

{% tabs %}
  {% tab label="Python" %}
  ```python
  from google import genai
  
  client = genai.Client()
  
  # Turn 1: Use Carbon to diagnose a concurrency bug and design the fix.
  plan = client.interactions.create(
      model="gemini-4-carbon",
      input=(
          "Identify the race conditions in a Redis-backed distributed lock "
          "that renews TTL on a background thread, and outline a safe fix."
      ),
  )
  
  # Turn 2: Hand the conversation to Hydrogen to implement code and unit tests.
  implementation = client.interactions.create(
      model="gemini-4-hydrogen",
      previous_interaction_id=plan.id,
      input="Write the Python implementation and pytest suite for your proposed fix.",
  )
  
  print(implementation.output_text)
  ```

  {% /tab %}

  {% tab label="JavaScript" %}
  ```javascript
  import { GoogleGenAI } from "@google/genai";
  
  const client = new GoogleGenAI({});
  
  // Turn 1: Use Carbon to diagnose a concurrency bug and design the fix.
  const plan = await client.interactions.create({
    model: "gemini-4-carbon",
    input:
      "Identify the race conditions in a Redis-backed distributed lock " +
      "that renews TTL on a background thread, and outline a safe fix.",
  });
  
  // Turn 2: Hand the conversation to Hydrogen to implement code and unit tests.
  const implementation = await client.interactions.create({
    model: "gemini-4-hydrogen",
    previous_interaction_id: plan.id,
    input: "Write the TypeScript implementation and Vitest suite for your proposed fix.",
  });
  
  console.log(implementation.output_text);
  ```

  {% /tab %}

  {% tab label="REST" %}
  ```bash
  PLAN_ID=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "gemini-4-carbon",
      "input": "Identify the race conditions in a Redis-backed distributed lock that renews TTL on a background thread, and outline a safe fix."
    }' | jq -r '.id')
  
  curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"gemini-4-hydrogen\",
      \"previous_interaction_id\": \"$PLAN_ID\",
      \"input\": \"Write the Python implementation and pytest suite for your proposed fix.\"
    }"
  ```

  {% /tab %}

{% /tabs %}

In [Gemini Managed Agents](/docs/agents), the [Antigravity agent](/docs/antigravity-agent) runs on `gemini-4-hydrogen` by default and lets you override `model` in [`agent_config`](/docs/antigravity-agent#model-selection) for tasks that need `gemini-4-carbon` or `gemini-4-neon`. If you manage conversation history on the client with the [`generateContent` API](/docs/text-generation?generate-content=true), return prior model turns and [thought signatures](/docs/thought-signatures?generate-content=true) unchanged when switching models across turns.

## Tune speed, cost, and reasoning depth  {% id="tune-reasoning-and-cost" %}

Before switching to a larger or smaller model, tune [`thinking_level`](/docs/thinking#thinking-levels). Thinking level sets how much internal reasoning a model performs before answering, which controls latency and token spend.

| Thinking level | Supported models | Token use | When to use |
| :--- | :--- | :--- | :--- |
| `minimal` | `gemini-3.5-flash-lite` (default) | Near-zero thinking, lowest latency | High-throughput extraction, translation, and summarization. Not supported on Gemini 4 models. |
| `low` | All Gemini 4 models, `gemini-3.5-flash-lite` | Fewest tokens, fast first token | Cost- and latency-sensitive chat, summarization, and straightforward tool calls. |
| `medium` | `gemini-4-carbon` (default), `gemini-4-neon`, `gemini-4-hydrogen`, `gemini-3.5-flash-lite` | Balanced | Default for Carbon. Good fit on Neon and Hydrogen for interactive coding and live UI prototyping. |
| `high` | `gemini-4-neon` (default), `gemini-4-hydrogen` (default), `gemini-4-carbon`, `gemini-3.5-flash-lite` | Deeper multi-step reasoning | Default on Neon and Hydrogen for coding, agents, and multimodal work. Maximum depth on Carbon. |
| `xhigh` | `gemini-4-neon`, `gemini-4-hydrogen` | Most tokens, deepest reasoning | Hard multi-step coding and agent problems where `high` isn't enough. |

Run your evaluations across all supported levels with `max_output_tokens` set to at least 65,536 so the limit doesn't cut answers short. Then pick the lowest `thinking_level` that passes your quality bar. Keep `xhigh` (on `gemini-4-neon` and `gemini-4-hydrogen`) for hard multi-step problems where `high` isn't enough, since `xhigh` increases latency and token use.

### Lower cost and latency with inference options  {% id="inference-options" %}

Once you pick a model and thinking level, use these API options to match your production budget and latency targets:

* **[Implicit context caching](/docs/caching):** Runs by default on Gemini 4 prompts of at least 4,096 tokens and discounts cached input tokens by 95%. Place shared system instructions, tool definitions, and reference documents at the start of your prompt to maximize cache hits.
* **[Flex inference](/docs/flex-inference) and [Batch API](/docs/batch-api):** Cut token costs by 50% for offline evaluations, dataset processing, and non-urgent multi-step agent runs.
* **[Priority inference](/docs/priority-inference):** Route user-facing production traffic to non-sheddable compute queues for consistent low latency under peak load.

See [Optimization and inference](/docs/optimization) for a side-by-side comparison of service tiers.

## Specialized and media models  {% id="specialized-models" %}

For scoring, media generation, real-time audio, embeddings, or robotics, use a purpose-built model. Each guide covers its model options.

| Workload | Start with |
| :--- | :--- |
| Classification, routing, and scoring | [`gemini-decision-1`](/docs/decisions-api) |
| Image generation and editing | [`gemini-nano-banana-2.1`](/docs/image-generation) |
| Video generation and editing | [`gemini-omni-1.2-flash`](/docs/omni) |
| Real-time voice and video agents | [`gemini-3.8-live`](/docs/live-api) |
| Text-to-speech | [`gemini-3.8-flash-tts`](/docs/speech-generation) |
| Speech-to-text | [`gemini-3.5-transcribe`](/docs/transcribe) |
| Multimodal embeddings | [`gemini-embedding-2`](/docs/embeddings) |
| Music generation | [`lyria-3.5`](/docs/music-generation) |
| Robotics | [`gemini-robotics-er-2-preview`](/docs/robotics-overview) |
| Managed agents | [Antigravity](/docs/antigravity-agent), [Deep Research](/docs/deep-research) |

See [All models](/docs/models) for the full list.

## Upgrade from earlier Gemini models  {% id="upgrade-paths" %}

Use these targets when upgrading from earlier Gemini 3 or Gemini 2.5 models. Check [Deprecations](/docs/deprecations) for shutdown and automatic routing dates.

| Current model | Recommended upgrade | Migration guide |
| :--- | :--- | :--- |
| `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3-flash-preview` | `gemini-4-hydrogen` | [Migrate from Gemini 3.8 Flash and earlier](/docs/whats-new-gemini-4-hydrogen#migrate-from-gemini-3-8-flash) |
| `gemini-3.1-pro-preview` | `gemini-4-neon` (or `gemini-4-carbon` for your hardest problems) | [Gemini 4 Neon migration checklist](/docs/whats-new-gemini-4-neon#migration-checklist) |
| `gemini-3.1-flash-lite` | `gemini-3.5-flash-lite` | [Migrate to Gemini 3.5 Flash-Lite](/docs/whats-new-gemini-3.6#migrate-to-gemini-3-5-flash-lite) |
| `gemini-2.5-pro` | `gemini-4-hydrogen` (or `gemini-4-carbon` for your hardest problems) | [Migrate from Gemini 3.8 Flash and earlier](/docs/whats-new-gemini-4-hydrogen#migrate-from-gemini-3-8-flash) |
| `gemini-2.5-flash`, `gemini-2.5-flash-lite` | `gemini-4-hydrogen` or `gemini-3.5-flash-lite` | [Migrate from Gemini 3.8 Flash and earlier](/docs/whats-new-gemini-4-hydrogen#migrate-from-gemini-3-8-flash) |

## What's next  {% id="whats-next" %}

* Compare model specs and launch AI Studio playgrounds on [Latest Gemini models](/docs/latest-model).
* Browse the full endpoint catalog on [All models](/docs/models).
* Configure `thinking_level` and thought summaries in the [Thinking guide](/docs/thinking).
* Review [Optimization and inference](/docs/optimization), [Pricing](/docs/pricing), and [Rate limits](/docs/rate-limits).
