---
source_url: https://aistudio.google.com/docs/models/gemini-4-neon.md
captured_at: 2026-11-19T08:02:38Z
scope: Complete verbatim Markdown of the Google AI Studio Gemini 4 Neon model specification page (.md endpoint).
immutable: true
---

> ## AI Agent Context
> - Full documentation index: https://aistudio.google.com/llms.txt
> - Gemini Docs MCP server (consistent live info): https://gemini-api-docs-mcp.dev
> - Coding agent skills & setup guide: https://aistudio.google.com/docs/coding-agents.md

# Gemini 4 Neon

Gemini 4 Neon (`gemini-4-neon`) brings frontier-level intelligence with fast end-to-end task completion across complex software engineering, knowledge work, and science workflows, featuring a unified 1M-token context window and long decode up to 1M tokens.

{% button href="https://aistudio.google.com/prompts/new_chat?model=gemini-4-neon" variant="ais" %}Try in Google AI Studio{% /button %}

## Documentation  {% id="documentation" %}

Visit the [What's new in Gemini 4 Neon](/docs/whats-new-gemini-4-neon) page
for full coverage of features, pricing, and migration guidance, or read [Choosing a model](/docs/choosing-a-model) to compare Neon against Carbon, Hydrogen, and Flash-Lite.

## gemini-4-neon  {% id="gemini-4-neon" %}

{% table variant="model" %}
  * Property
  * Description

  ---

  *     {% section class="model-property" %}
  {% icon name="id_card" /%}Model code

    {% /section %}

  * `gemini-4-neon`

  ---

  *     {% section class="model-property" %}
  {% icon name="save" /%}Supported data types

    {% /section %}

  *     **Inputs** Text, Image, Video, Audio, and PDF

    **Output** Text


  ---

  *     {% section class="model-property" %}
  {% icon name="token_auto" /%}Token limits{% sup %}[[*]](/docs/tokens){% /sup %}

    {% /section %}

  *     **Context window (unified input and output token limit)** 1,048,576

    **Max output** 65,536 (default synchronous) / up to 1,048,576 (with [long decode](/docs/long-decode))


  ---

  *     {% section class="model-property" %}
  {% icon name="handyman" /%}Capabilities

    {% /section %}

  *     {% section class="three-column-grid" %}
  {% section %}
  [**Agentic video understanding**](/docs/video-understanding#agentic-video-understanding)

  {% badge label=Supported (defaults to static) type="supported" /%}

  {% /section %}

  {% section %}
  [**Audio generation**](/docs/speech-generation)

  {% badge type="not-supported" /%}

  {% /section %}

  {% section %}
  [**Code execution**](/docs/code-execution)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Computer use**](/docs/computer-use)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Context caching**](/docs/caching)

  {% badge label=Supported (Implicit only) type="supported" /%}

  Note: Explicit caching is not supported.

  {% /section %}

  {% section %}
  [**File search**](/docs/file-search)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Function calling**](/docs/function-calling)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Grounding with Google Maps**](/docs/maps-grounding)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Grounding with Google Search**](/docs/google-search)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Image generation**](/docs/image-generation)

  {% badge type="not-supported" /%}

  {% /section %}

  {% section %}
  [**Live API**](/docs/live-api)

  {% badge type="not-supported" /%}

  {% /section %}

  {% section %}
  [**Structured outputs**](/docs/structured-output)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Thinking**](/docs/thinking)

  {% badge label=Supported (low, medium, high, xhigh) type="supported" /%}

  {% /section %}

  {% section %}
  [**URL context**](/docs/url-context)

  {% badge type="supported" /%}

  {% /section %}

    {% /section %}


  ---

  *     {% section class="model-property" %}
  {% icon name="speed" /%}Consumption options

    {% /section %}

  *     {% section class="three-column-grid" %}
  {% section %}
  [**Batch API**](/docs/batch-api)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Flex inference**](/docs/flex-inference)

  {% badge type="supported" /%}

  {% /section %}

  {% section %}
  [**Priority inference**](/docs/priority-inference)

  {% badge type="supported" /%}

  {% /section %}

    {% /section %}


  ---

  *     {% section class="model-property" %}
  {% icon name="123" /%}Versions

    {% /section %}

  *     Read the [model version patterns](/docs/models#model-versions) for more details.

    *   Stable: `gemini-4-neon`


  ---

  *     {% section class="model-property" %}
  {% icon name="calendar_month" /%}Latest update

    {% /section %}

  * November 2026

  ---

  *     {% section class="model-property" %}
  {% icon name="id_card" /%}Model card

    {% /section %}

  * [Model card](https://deepmind.google/models/model-cards/gemini-4-neon/)

  ---

  *     {% section class="model-property" %}
  {% icon name="paid" /%}Pricing

    {% /section %}

  * [Pricing](/docs/pricing#gemini-4-neon)
{% /table %}
