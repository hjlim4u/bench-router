---
title: >-
    LMArena Text (style control)
category: entities
tags: [benchmark, lmarena]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/arena-category/", "url:https://lmsys.org/blog/2024-05-17-category-hard", "url:https://arena.ai/blog/arena-expert", "url:https://arxiv.org/abs/2412.08687"]
summary: >-
    실제 사용자 텍스트 프롬프트에 대한 쌍대 비교 투표 Bradley-Terry 점수. 응답 길이·서식 효과를 보정한 style control 버전.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LMArena Text (style control)

실제 사용자 텍스트 프롬프트에 대한 쌍대 비교 투표 Bradley-Terry 점수. 응답 길이·서식 효과를 보정한 style control 버전.

점수 컬럼: Bradley-Terry는 `rating`·`rating_lower`·`rating_upper`, Agent는 `score`·`score_ci_lower`·`score_ci_upper`.

## Index

```toml
[[unit]]
id = "arena:text_style_control/overall"
desc = "전체 텍스트 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["general"] }

[[unit]]
id = "arena:text_style_control/coding"
desc = "코드 관련 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["coding"] }

[[unit]]
id = "arena:text_style_control/math"
desc = "수학 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["math"] }

[[unit]]
id = "arena:text_style_control/creative_writing"
desc = "창작 글쓰기 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["creative_writing"] }

[[unit]]
id = "arena:text_style_control/instruction_following"
desc = "지시 이행 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["instruction_following"] }

[[unit]]
id = "arena:text_style_control/hard_prompts"
desc = "Hard Prompts(7개 기준 중 6개 이상) 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { difficulty = ["hard_prompts"] }

[[unit]]
id = "arena:text_style_control/hard_prompts_english"
desc = "영어 Hard Prompts 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { difficulty = ["hard_prompts"], lang = ["en"] }

[[unit]]
id = "arena:text_style_control/expert"
desc = "전문가 수준 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { difficulty = ["expert"] }

[[unit]]
id = "arena:text_style_control/longer_query"
desc = "500토큰 초과 질의 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { shape = ["longer_query"] }

[[unit]]
id = "arena:text_style_control/multi_turn"
desc = "다중 턴 대화 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { shape = ["multi_turn"] }

[[unit]]
id = "arena:text_style_control/korean"
desc = "ko 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["ko"] }

[[unit]]
id = "arena:text_style_control/japanese"
desc = "ja 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["ja"] }

[[unit]]
id = "arena:text_style_control/chinese"
desc = "zh 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["zh"] }

[[unit]]
id = "arena:text_style_control/russian"
desc = "ru 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["ru"] }

[[unit]]
id = "arena:text_style_control/english"
desc = "en 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["en"] }

[[unit]]
id = "arena:text_style_control/spanish"
desc = "es 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["es"] }

[[unit]]
id = "arena:text_style_control/french"
desc = "fr 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["fr"] }

[[unit]]
id = "arena:text_style_control/german"
desc = "de 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["de"] }

[[unit]]
id = "arena:text_style_control/polish"
desc = "pl 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { lang = ["pl"] }

[[unit]]
id = "arena:text_style_control/industry_software_and_it_services"
desc = "직업 분야 software_it 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["software_it"] }

[[unit]]
id = "arena:text_style_control/industry_writing_and_literature_and_language"
desc = "직업 분야 writing_language 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["writing_language"] }

[[unit]]
id = "arena:text_style_control/industry_life_and_physical_and_social_science"
desc = "직업 분야 science 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["science"] }

[[unit]]
id = "arena:text_style_control/industry_entertainment_and_sports_and_media"
desc = "직업 분야 entertainment_media 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["entertainment_media"] }

[[unit]]
id = "arena:text_style_control/industry_business_and_management_and_financial_operations"
desc = "직업 분야 business_finance 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["business_finance"] }

[[unit]]
id = "arena:text_style_control/industry_mathematical"
desc = "직업 분야 mathematical 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["mathematical"] }

[[unit]]
id = "arena:text_style_control/industry_legal_and_government"
desc = "직업 분야 legal_government 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["legal_government"] }

[[unit]]
id = "arena:text_style_control/industry_medicine_and_healthcare"
desc = "직업 분야 medicine_healthcare 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { domain = ["medicine_healthcare"] }

[[unit]]
id = "arena:text_style_control/exclude_ties"
desc = "무승부 투표를 뺀 전체 프롬프트 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "Text Arena 정의 미공개. VisionArena 논문의 같은 이름 필터(무승부 없는 battle)로 추정"
evidence = "name_only"

[[unit]]
id = "arena:text_style_control/non_english"
desc = "영어 외 언어 프롬프트 전체 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "정의 미공개. 이름상 Polyglot 태그가 영어가 아닌 프롬프트 전체로 추정"
evidence = "name_only"
```

## Open Questions

- `exclude_ties`, `non_english`는 Text Arena 공식 정의를 찾지 못해 이름으로 추정했다 ^[inferred]. candidate로 둔다.
- 데이터셋 설명은 `text_style_control`의 `latest` split에 overall만 보인다고 하지만, 2026-10-17 통계 조회에서는 29개 category가 있었다 ^[ambiguous].

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-category]] — <https://arena.ai/blog/arena-category/>
- [[references/sources/arena-hard-prompts]] — <https://lmsys.org/blog/2024-05-17-category-hard>
- [[references/sources/arena-expert]] — <https://arena.ai/blog/arena-expert>
- [[references/sources/visionarena-paper]] — <https://arxiv.org/abs/2412.08687>
