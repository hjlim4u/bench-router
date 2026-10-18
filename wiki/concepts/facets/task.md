---
title: >-
    facet task
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/arena-category/", "url:https://arena.ai/blog/leaderboard-changelog", "url:https://arena.ai/blog/re-introducing-vision-arena-categories/", "url:https://themodelgap.com/data/benchmarks.json", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Task type. LMArena category names are the base vocabulary; agentic task types that LMArena lacks come from The Model Gap and Hugging Face official benchmarks.
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# facet task

Task type. LMArena category names are the base vocabulary; agentic task types that LMArena lacks come from The Model Gap and Hugging Face official benchmarks.

`detect`: `rule:*` is decided by the router deterministically (zero tokens); `self` is tagged by the Orchestrator in the task JSON `facets`. `evidence`: official (primary source text) | dataset (dataset card) | name_only (only the name is known).

## Index

```toml
[[facet]]
id = "general"
desc = "General conversation and questions"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "coding"
desc = "Understand, generate, and debug code across programming languages and paradigms"
detect = "rule:code_block_or_code_ext"
arena_rule = "Heuristic: code blocks, programming language names and keywords, code commands"
evidence = "official"

[[facet]]
id = "math"
desc = "Actively apply mathematical reasoning and problem-solving skills (not just explanations of math concepts)"
detect = "self"
evidence = "official"

[[facet]]
id = "creative_writing"
desc = "Craft original, imaginative, and emotionally resonant content"
detect = "self"
arena_rule = "LLM classifier with a checklist"
evidence = "official"

[[facet]]
id = "instruction_following"
desc = "Precisely follow given instructions, especially multi-step tasks and specific requirements"
detect = "self"
evidence = "official"

[[facet]]
id = "webdev_html"
desc = "Standalone HTML/CSS/JS generation within a single document scope"
detect = "rule:ext(.html,.css)"
evidence = "official"

[[facet]]
id = "webdev_react"
desc = "Multi-file application generation, including component structure, routing, state coordination, and cross-file consistency"
detect = "rule:ext(.jsx,.tsx)"
evidence = "official"

[[facet]]
id = "image_to_webdev"
desc = "Build a web page from an image (mockup or screenshot)"
detect = "self"
evidence = "official"

[[facet]]
id = "document"
desc = "Document reasoning over user-uploaded PDF files"
detect = "rule:ext(.pdf)"
evidence = "official"

[[facet]]
id = "search"
desc = "Questions that need web search"
detect = "self"
evidence = "official"

[[facet]]
id = "vision"
desc = "Questions with image input (captioning, entity recognition, humor and other subcategories)"
detect = "rule:ext(.png,.jpg,.jpeg,.webp)"
evidence = "official"

[[facet]]
id = "vision_ocr"
desc = "Images with text, with prompts asking for information from the textual components"
detect = "self"
evidence = "official"

[[facet]]
id = "vision_diagram"
desc = "Recognition and understanding of technical information in graphs, charts, or figures"
detect = "self"
evidence = "official"

[[facet]]
id = "vision_homework"
desc = "Understand and solve problems from pictures of assignments"
detect = "self"
evidence = "official"

[[facet]]
id = "repo_coding"
desc = "Resolve an issue in an existing repository with a code patch"
detect = "self"
evidence = "official"

[[facet]]
id = "terminal_ops"
desc = "Multi-step command-line work: build, install, debug, administer"
detect = "rule:kw(bash,shell,CI,docker)"
evidence = "official"

[[facet]]
id = "multi_tool"
desc = "Long tasks that juggle many real software tools"
detect = "self"
evidence = "official"

[[facet]]
id = "computer_use"
desc = "Long multi-app workflows on a desktop GUI"
detect = "self"
evidence = "official"

[[facet]]
id = "data_analysis"
desc = "Answer quantitative questions from a folder of spreadsheets and documents"
detect = "rule:ext(.csv,.xlsx,.ipynb)"
evidence = "official"

[[facet]]
id = "professional_work"
desc = "Economically valuable professional work done end to end (e.g. video editing, CAD)"
detect = "self"
evidence = "official"

[[facet]]
id = "science_reasoning"
desc = "Expert-level science and academic questions"
detect = "self"
evidence = "official"

[[facet]]
id = "abstract_reasoning"
desc = "Infer a hidden rule from a few examples and apply it exactly"
detect = "self"
evidence = "official"

[[facet]]
id = "legal"
desc = "Legal reasoning, contract review, negotiation"
detect = "self"
evidence = "dataset"

[[facet]]
id = "gui_grounding"
desc = "Locate UI elements on high-resolution professional software screens"
detect = "self"
evidence = "dataset"

[[facet]]
id = "retrieval"
desc = "Document retrieval that requires reasoning"
detect = "self"
evidence = "dataset"

[[facet]]
id = "ocr_parse"
desc = "Convert PDF, scanned, or photographed documents to structured text or JSON"
detect = "rule:ext(.pdf)"
evidence = "dataset"
```

## Other axes

- [[concepts/facets/agent_signal|agent_signal]]
- [[concepts/facets/difficulty|difficulty]]
- [[concepts/facets/domain|domain]]
- [[concepts/facets/lang|lang]]
- [[concepts/facets/shape|shape]]

## Sources

- [[references/sources/arena-category]] — <https://arena.ai/blog/arena-category/>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
- [[references/sources/arena-vision-categories]] — <https://arena.ai/blog/re-introducing-vision-arena-categories/>
- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
