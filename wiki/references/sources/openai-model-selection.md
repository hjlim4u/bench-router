---
title: >-
  OpenAI model and reasoning-effort selection
category: references
tags: [source, agentic, reasoning]
sources: ["url:https://developers.openai.com/api/docs/guides/model-selection"]
created: 2026-10-19T01:52:29Z
updated: 2026-11-26T00:49:17Z
as_of: 2026-11-26
summary: >-
  Official OpenAI starting combinations (updated 2026-11-18 for GPT-6.2 Astra and Sol), Terra workload guidance, and task-based comparisons.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-10-19
tier: supporting
snapshots:
  - "[[_raw/_archived/2026-10-19-openai-model-selection|2026-10-19-openai-model-selection]]"
  - "[[_raw/_archived/2026-10-24-openai-model-selection|2026-10-24-openai-model-selection]]"
  - "[[_raw/_archived/2026-10-27-openai-model-selection|2026-10-27-openai-model-selection]]"
  - "[[_raw/_archived/2026-11-13-openai-model-selection|2026-11-13-openai-model-selection]]"
  - "[[_raw/_archived/2026-11-18-openai-model-selection|2026-11-18-openai-model-selection]]"
  - "[[_raw/_archived/2026-11-26-openai-model-selection|2026-11-26-openai-model-selection]]"
  - "[[_raw/_archived/2026-11-26-openai-codex-models|2026-11-26-openai-codex-models]]"
---

# OpenAI model and reasoning-effort selection

OpenAI's Model selection guide, checked on 2026-10-24, pairs workloads with a model and a reasoning effort. Quotations below are verbatim.

> If cost and latency aren’t a concern, you can default to Astra. To reduce costs or latency, use the guidance below to choose a model and reasoning effort for your needs.

## When to consider GPT-6.1 Terra

> Try GPT-6.1 Terra for concise writing based on supplied material, computer-use tasks with a defined outcome, and scoped code fixes. Provide clear inputs, requirements, and a way to verify the result, such as checking saved records or running regression tests.

> Compare it with GPT-6.1 Sol on the same inputs and reasoning effort. For writing, judge audience fit, voice, and useful detail as well as accuracy and length. For computer use, check the saved result and the accuracy of the completion report.

## Documented starting points

| Model | Effort shown in the guide | Workload, verbatim |
|---|---|---|
| Luna | Low | Fine-grained edits, well-scoped problem-solving, and simple data extraction. |
| Luna | Extra high | Finding current context across multiple apps, prioritizing work, and solving problems with clear constraints. |
| GPT-6.1 Sol | Medium | Complex technical work and coordinated deliverables you expect to revise. |
| GPT-6.1 Sol | Extra high | Polished deliverables, connected visual systems, and decisions built from conflicting evidence. |
| Astra | Low | Concise writing and content adaptation that preserve facts and nuance. |
| Astra | Medium | Ambitious projects that need broad context, reliable interactions, and complete results. |
| Astra | Extra high | Demanding analysis and complex deliverables with exacting requirements. |

The page presents Extra high as a starting point for these workloads; it does not advise against it.

## Evaluation principle

> If you can, experiment using the same inputs to compare results and keep the lightest setting that meets your quality bar.

> A task you’re waiting on may need a faster setting than one that runs overnight.

## Limits

These are dated starting points. The page distinguishes product/version availability and does not establish a common score for competing vendors. Display labels above are not verified CLI flags or configured bench-router profile IDs. The page names no default reasoning effort.

## Related

- [[concepts/model-effort-selection]]
- [[synthesis/vendor-guided-model-selection]]
- [[concepts/facets/task]]

## Current guidance — checked 2026-11-13

The seven documented Luna/Sol/Astra starting combinations remain unchanged. Terra is recommended for concise writing from supplied material, defined-outcome computer use and scoped code fixes; the captured page does not prescribe a fixed Terra effort. Compare Terra and Sol with the same inputs and effort. Define acceptance criteria first; check writing quality, saved computer-use results and regression tests. Evaluate completion time including review and repair, then vary effort with the model and inputs held fixed. Interactive recommendations were not fully captured. Earlier interactive examples below remain dated historical evidence, not a fresh verification.

Related: [[concepts/model-effort-selection]], [[synthesis/vendor-guided-model-selection]].

## Current guidance — checked 2026-11-26

Two official guidance details from `developers.openai.com/api/docs/guides/model-selection.md` and `developers.openai.com/codex/models.md` supplement the 2026-11-18 capture: ^[extracted]

- **Explicit API workflow default**: *"For most API workflows, start with **GPT-6.2 Sol** at medium reasoning effort."* Use **GPT-6.2 Astra** for demanding engineering or analysis, **GPT-6.1 Terra** to interpret visual information (charts, screenshots), and **GPT-6 Luna** for small, repeatable tasks.
- **Codex & ChatGPT Work guidance**:
  - **Max vs Ultra**: **Max** allocates more single-task reasoning time when depth outweighs speed/usage; **Ultra** uses parallel subagents when complex work can be divided into meaningful parts (most tasks need neither). **GPT-6 Luna** supports reasoning efforts up to **Max**, but **not Ultra**.
  - **Codex starting effort & context**: For `GPT-6.2 Astra` or `GPT-6.2 Sol`, start with the client-selected default effort and adjust per task (both support up to 1M context via `model_context_window` in `config.toml`; `GPT-6.1 Sol` uses 500K by default in Codex/Work). Start `Luna` at **High**, and `GPT-6 Astra` at **Light** (`low`).
  - **Multi-agent & retirements**: `GPT-6.2 Astra` and `GPT-6.2 Sol` support subagent delegation via the Responses API Multi-agent beta. `GPT-5.3-Codex-Spark` retired on 2026-09-14, and `GPT-5.5` retired from ChatGPT-authenticated Codex on 2026-10-14 (replaced by `gpt-6.1-sol` on paid plans and `gpt-6-luna` on Free/Go).

See also [[references/sources/openai-specialized-models]] for `gpt-6-cyber`, `astra-for-law-6-2`, and Healthcare configurations.

## Current guidance — checked 2026-11-18

The Model Selection guide updated on 2026-11-17/18 to introduce **GPT-6.2 Astra** and **GPT-6.2 Sol** alongside **GPT-6.1 Terra** and **GPT-6 Luna**. ^[extracted]

- **GPT-6.2 Astra** (*Complex professional work*): "Create slides and spreadsheets that follow your templates, analyze scientific data, and design complex 3D parts."
  - **Low**: "Turning a clear brief into polished work that's ready to use."
  - **Medium**: "Planning and carrying out complex projects, adjusting the approach as new information comes in."
  - **Extra high**: "Solving open-ended problems that require weighing trade-offs and testing assumptions."
- **GPT-6.2 Sol** (*Efficient everyday work*): "Write and test code, draft clear documents, and complete multistep workflows across apps."
  - **Medium**: "Fixing bugs and adding features in an existing codebase, or drafting documents for review."
  - **Extra high**: "Working through multistep tasks that need testing and revision along the way."
- **GPT-6.1 Terra** (*Visual reasoning and computer use*): **Medium** — "Navigating desktop apps, updating records, and making focused fixes you can verify."
- **GPT-6 Luna** (*Frequent, bounded tasks*): **Low** / **Extra high** unchanged.

Across all six listed work types (3D and design, Software engineering, Data analysis, Creating deliverables, Computer use, Research decisions), the guide orders models from strongest fit to weakest fit as: `GPT-6.2 Astra, GPT-6.2 Sol, GPT-6.1 Terra, GPT-6 Luna`. ^[extracted]

Related: [[concepts/model-effort-selection]], [[synthesis/vendor-guided-model-selection]], [[references/sources/openai-gpt-6-2-prompting]].

## Sources

- [[_raw/_archived/2026-11-26-openai-model-selection]] — 2026-11-26 full Markdown capture confirming GPT-6.2 Sol medium API default.
- [[_raw/_archived/2026-11-26-openai-codex-models]] — 2026-11-26 full Markdown capture of Codex Max/Ultra rules, context defaults, and retirements.
- [[_raw/_archived/2026-11-18-openai-model-selection]] — 2026-11-18 bounded text excerpt of the updated guide with GPT-6.2 Astra and Sol.
- [[_raw/_archived/2026-10-27-openai-model-selection]] — defuddle markdown capture of updated guide including GPT-6.1 Terra.
- [[_raw/_archived/2026-10-24-openai-model-selection]] — verbatim excerpts of every quoted row and sentence.
- [[_raw/_archived/2026-10-19-openai-model-selection]] — earlier bounded excerpt; canonical link and capture scope are recorded there.

- [[_raw/_archived/2026-11-13-openai-model-selection]] — 2026-11-13 capture; extraction limitations are recorded in its frontmatter.
