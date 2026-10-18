---
title: >-
    LMArena Text (style control)
category: entities
tags: [benchmark, lmarena, general, coding, math]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/arena-category/", "url:https://lmsys.org/blog/2024-05-17-category-hard", "url:https://arena.ai/blog/arena-expert", "url:https://arxiv.org/abs/2412.08687"]
summary: >-
    Bradley-Terry scores from pairwise votes on real user text prompts. The style-control version adjusts for response length and formatting.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LMArena Text (style control)

Bradley-Terry scores from pairwise votes on real user text prompts. The style-control version adjusts for response length and formatting.

Score columns: `rating`, `rating_lower`, `rating_upper` (Bradley-Terry).

## Index

```toml
[[unit]]
id = "arena:text_style_control/overall"
desc = "User preference on all text prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["general"] }

[[unit]]
id = "arena:text_style_control/coding"
desc = "User preference on coding prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["coding"] }

[[unit]]
id = "arena:text_style_control/math"
desc = "User preference on math prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["math"] }

[[unit]]
id = "arena:text_style_control/creative_writing"
desc = "User preference on creative writing prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["creative_writing"] }

[[unit]]
id = "arena:text_style_control/instruction_following"
desc = "User preference on instruction-following prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["instruction_following"] }

[[unit]]
id = "arena:text_style_control/hard_prompts"
desc = "User preference on Hard Prompts (6+ of 7 criteria)"
metric = "elo"
status = "current"
adoption = "active"
facets = { difficulty = ["hard_prompts"] }

[[unit]]
id = "arena:text_style_control/hard_prompts_english"
desc = "User preference on English Hard Prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { difficulty = ["hard_prompts"], lang = ["en"] }

[[unit]]
id = "arena:text_style_control/expert"
desc = "User preference on expert-level prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { difficulty = ["expert"] }

[[unit]]
id = "arena:text_style_control/longer_query"
desc = "User preference on queries longer than 500 tokens"
metric = "elo"
status = "current"
adoption = "active"
facets = { shape = ["longer_query"] }

[[unit]]
id = "arena:text_style_control/multi_turn"
desc = "User preference on multi-turn conversations"
metric = "elo"
status = "current"
adoption = "active"
facets = { shape = ["multi_turn"] }

[[unit]]
id = "arena:text_style_control/korean"
desc = "User preference on Korean prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["ko"] }

[[unit]]
id = "arena:text_style_control/japanese"
desc = "User preference on Japanese prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["ja"] }

[[unit]]
id = "arena:text_style_control/chinese"
desc = "User preference on Chinese prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["zh"] }

[[unit]]
id = "arena:text_style_control/russian"
desc = "User preference on Russian prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["ru"] }

[[unit]]
id = "arena:text_style_control/english"
desc = "User preference on English prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["en"] }

[[unit]]
id = "arena:text_style_control/spanish"
desc = "User preference on Spanish prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["es"] }

[[unit]]
id = "arena:text_style_control/french"
desc = "User preference on French prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["fr"] }

[[unit]]
id = "arena:text_style_control/german"
desc = "User preference on German prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["de"] }

[[unit]]
id = "arena:text_style_control/polish"
desc = "User preference on Polish prompts"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["pl"] }

[[unit]]
id = "arena:text_style_control/industry_software_and_it_services"
desc = "User preference on prompts in the occupational field Software and IT Services"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["software_it"] }

[[unit]]
id = "arena:text_style_control/industry_writing_and_literature_and_language"
desc = "User preference on prompts in the occupational field Writing, Literature, and Language"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["writing_language"] }

[[unit]]
id = "arena:text_style_control/industry_life_and_physical_and_social_science"
desc = "User preference on prompts in the occupational field Life, Physical, and Social Science"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["science"] }

[[unit]]
id = "arena:text_style_control/industry_entertainment_and_sports_and_media"
desc = "User preference on prompts in the occupational field Entertainment, Sports, and Media"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["entertainment_media"] }

[[unit]]
id = "arena:text_style_control/industry_business_and_management_and_financial_operations"
desc = "User preference on prompts in the occupational field Business, Management, and Financial Operations"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["business_finance"] }

[[unit]]
id = "arena:text_style_control/industry_mathematical"
desc = "User preference on prompts in the occupational field Mathematical"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["mathematical"] }

[[unit]]
id = "arena:text_style_control/industry_legal_and_government"
desc = "User preference on prompts in the occupational field Legal and Government"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["legal_government"] }

[[unit]]
id = "arena:text_style_control/industry_medicine_and_healthcare"
desc = "User preference on prompts in the occupational field Medicine and Healthcare"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["medicine_healthcare"] }

[[unit]]
id = "arena:text_style_control/exclude_ties"
desc = "User preference on all prompts, excluding tied votes"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "Page exists (arena.ai/leaderboard/text/exclude-ties, plots labeled 'Ties Excluded') but no page states how tied votes are handled. Inferred from the VisionArena filter of the same name"
evidence = "name_only"

[[unit]]
id = "arena:text_style_control/non_english"
desc = "User preference on all non-English prompts"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "No definition published; inferred from the name (prompts whose Polyglot tag is not English)"
evidence = "name_only"
```

## Open Questions

- Searched again 2026-10-18: arena.ai has Exclude Ties leaderboards (`/leaderboard/text/exclude-ties`, `/exclude-ties-no-style-control`), but no public text defines the tie handling (dropped from the fit vs. counted as half-wins). `non_english` was not found on any page. Leaderboard pages answer 403 to scripts, so only the HF dataset is a sanctioned source.
- Model names in this dataset carry the effort inside the name (e.g. `Claude Opus 4.6 (High)` and `Claude Opus 4.6` both exist; `gpt-5.4-high`; WebDev has `GPT-5.4 (High, Codex Harness)`). `aliases.toml [arena]` must map an exact string per profile, because `build_snapshot` marks multiple matches as ambiguous.

- No official Text Arena definition was found for `exclude_ties` and `non_english`; both are inferred from their names ^[inferred]. Kept as candidate.
- The dataset card says the `text_style_control` `latest` split shows only `overall`, but the 2026-10-17 statistics query returned 29 categories ^[ambiguous].

## Facets

- [[concepts/facets/difficulty|difficulty]]: expert, hard_prompts
- [[concepts/facets/domain|domain]]: business_finance, entertainment_media, legal_government, mathematical, medicine_healthcare, science, software_it, writing_language
- [[concepts/facets/lang|lang]]: de, en, es, fr, ja, ko, pl, ru, zh
- [[concepts/facets/shape|shape]]: longer_query, multi_turn
- [[concepts/facets/task|task]]: coding, creative_writing, general, instruction_following, math

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/artificial-analysis]] — Artificial Analysis indexes
- [[entities/benchmarks/hf/ace]] — ACE
- [[entities/benchmarks/hf/aime-2026]] — AIME 2026 (MathArena)
- [[entities/benchmarks/hf/evasionbench]] — EvasionBench
- [[entities/benchmarks/hf/gsm8k]] — GSM8K
- [[entities/benchmarks/hf/ifstruct-v1-0]] — IFStruct v1.0
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/lmarena-document]] — LMArena Document (style control)
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/lmarena-search]] — LMArena Search (style control)
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)
- [[entities/benchmarks/lmarena-webdev]] — LMArena WebDev (Code Arena)

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-category]] — <https://arena.ai/blog/arena-category/>
- [[references/sources/arena-hard-prompts]] — <https://lmsys.org/blog/2024-05-17-category-hard>
- [[references/sources/arena-expert]] — <https://arena.ai/blog/arena-expert>
- [[references/sources/visionarena-paper]] — <https://arxiv.org/abs/2412.08687>
