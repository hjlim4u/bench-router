---
title: >-
    LMArena Vision (style control)
category: entities
tags: [benchmark, lmarena, vision, writing]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/re-introducing-vision-arena-categories/", "url:https://arxiv.org/abs/2412.08687"]
summary: >-
    Pairwise votes on image-input questions. Subcategory definitions follow 'Re-introducing Vision Arena Categories' (2025-10); each message can carry zero or more tags.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LMArena Vision (style control)

Pairwise votes on image-input questions. Subcategory definitions follow 'Re-introducing Vision Arena Categories' (2025-10); each message can carry zero or more tags.

Score columns: `rating`, `rating_lower`, `rating_upper` (Bradley-Terry).

## Index

```toml
[[unit]]
id = "arena:vision_style_control/overall"
desc = "User preference on all image-input questions"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["vision"] }

[[unit]]
id = "arena:vision_style_control/ocr"
desc = "Images with text; prompts ask for information from the text"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["vision_ocr"] }
reason = "Verified 2026-10-18 (121 models, 2026-10-09): scores for claude-opus-5-5 (claude-opus-5.5-high) and gpt-6.1-sol (gpt-6.1-sol-max)"

[[unit]]
id = "arena:vision_style_control/diagram"
desc = "Technical information in graphs, charts, or figures"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["vision_diagram"] }
reason = "Verified 2026-10-18 (121 models, 2026-10-09): scores for claude-opus-5-5 (claude-opus-5.5-high) and gpt-6.1-sol (gpt-6.1-sol-max)"

[[unit]]
id = "arena:vision_style_control/homework"
desc = "Problems from pictures of assignments"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["vision_homework"] }
reason = "Verified 2026-10-18 (116 models, 2026-10-09): scores for claude-opus-5-5 (claude-opus-5.5-high) and gpt-6.1-sol (gpt-6.1-sol-max)"

[[unit]]
id = "arena:vision_style_control/captioning"
desc = "Requests for general descriptions of images"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"] }
reason = "Verified 2026-10-18 (34 models): 0 current profile models (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon absent)"

[[unit]]
id = "arena:vision_style_control/entity_recognition"
desc = "Recognize, identify, and explain specific objects, items, or people in images"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"] }
reason = "Verified 2026-10-18 (51 models): 0 current profile models (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon absent)"

[[unit]]
id = "arena:vision_style_control/humor"
desc = "Identify funny elements or explain a joke in an image"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"] }
reason = "Verified 2026-10-18 (91 models): 0 current profile models (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon absent)"

[[unit]]
id = "arena:vision_style_control/creative_writing_vision"
desc = "Creative writing based on an image"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision", "creative_writing"] }
reason = "Verified 2026-10-18 (101 models): only one profile model has a score (claude-opus-5-5 via claude-opus-5.5-high); needs a second profile model before making active"

[[unit]]
id = "arena:vision_style_control/creative_writing"
desc = "Creative writing based on an image (legacy 34-model slice superseded by creative_writing_vision)"
metric = "elo"
status = "current"
adoption = "archive"
facets = { task = ["vision", "creative_writing"] }
reason = "Legacy tag (34 models, newest claude-opus-4-20250514); superseded by creative_writing_vision (101 models)"

[[unit]]
id = "arena:vision_style_control/chinese"
desc = "Image questions in Chinese"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"], lang = ["zh"] }
reason = "Verified 2026-10-18 (125 models): 0 current profile models (claude-opus-5-5, gpt-6.1-sol, gemini-4-argon absent)"

[[unit]]
id = "arena:vision_style_control/english"
desc = "Image questions in English"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["vision"], lang = ["en"] }
reason = "Verified 2026-10-18 (165 models, 2026-10-09): scores for claude-opus-5-5 (claude-opus-5.5-high) and gpt-6.1-sol (gpt-6.1-sol-max)"
```

## Open Questions

- The blog defines 7 categories. In `vision_style_control` (`split=latest`, checked 2026-10-18), `creative_writing` has only 34 older models (newest `claude-opus-4-20250514`), whereas `creative_writing_vision` has 101 models up to `claude-opus-5.5-high`. No separate blog definition was found for `chinese` (125 models) or `english` (165 models) ^[ambiguous].
- The blog does not say whether tagging is manual or automated. The original paper used Gemini 1.5 Flash.

## Facets

- [[concepts/facets/lang|lang]]: en, zh
- [[concepts/facets/task|task]]: creative_writing, vision, vision_diagram, vision_homework, vision_ocr

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/hf/mmmu-pro]] — MMMU-Pro
- [[entities/benchmarks/hf/swe-bench-multimodal]] — SWE-bench Multimodal
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/lmarena-document]] — LMArena Document (style control)
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/lmarena-search]] — LMArena Search (style control)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)
- [[entities/benchmarks/lmarena-webdev]] — LMArena WebDev (Code Arena)

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-vision-categories]] — <https://arena.ai/blog/re-introducing-vision-arena-categories/>
- [[references/sources/visionarena-paper]] — <https://arxiv.org/abs/2412.08687>
- [[references/sources/visionarena-battle]] — <https://huggingface.co/datasets/lmarena-ai/VisionArena-Battle>
