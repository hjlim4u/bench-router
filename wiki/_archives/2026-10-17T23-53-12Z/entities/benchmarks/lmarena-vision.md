---
title: >-
    LMArena Vision (style control)
category: entities
tags: [benchmark, lmarena]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/re-introducing-vision-arena-categories/", "url:https://arxiv.org/abs/2412.08687"]
summary: >-
    이미지 입력 질의에 대한 쌍대 비교 투표. 하위 카테고리 정의는 2025-10 'Re-introducing Vision Arena Categories' 기준이며, 메시지당 0~여러 개 태그.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LMArena Vision (style control)

이미지 입력 질의에 대한 쌍대 비교 투표. 하위 카테고리 정의는 2025-10 'Re-introducing Vision Arena Categories' 기준이며, 메시지당 0~여러 개 태그.

점수 컬럼: Bradley-Terry는 `rating`·`rating_lower`·`rating_upper`, Agent는 `score`·`score_ci_lower`·`score_ci_upper`.

## Index

```toml
[[unit]]
id = "arena:vision_style_control/overall"
desc = "이미지 입력 질의 전체 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["vision"] }

[[unit]]
id = "arena:vision_style_control/ocr"
desc = "이미지 속 텍스트 정보 질의 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision_ocr"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/diagram"
desc = "그래프·차트·도표 이해 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision_diagram"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/homework"
desc = "과제 사진 문제 풀이 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision_homework"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/captioning"
desc = "이미지 일반 설명 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/entity_recognition"
desc = "이미지 속 개체·사물·인물 식별·설명 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/humor"
desc = "이미지 속 유머 식별·설명 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/creative_writing_vision"
desc = "이미지 기반 창작 글쓰기 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision", "creative_writing"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/creative_writing"
desc = "이미지 기반 창작 글쓰기 사용자 선호 (creative_writing_vision과 관계 미확인)"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision", "creative_writing"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/chinese"
desc = "중국어 이미지 질의 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"], lang = ["zh"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"

[[unit]]
id = "arena:vision_style_control/english"
desc = "영어 이미지 질의 사용자 선호"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["vision"], lang = ["en"] }
reason = "정의는 확인됨. 현재 수집 대상이 아니며 커버리지 미확인"
```

## Open Questions

- 블로그는 7개 카테고리만 정의한다. 데이터셋의 `chinese`, `english`, `creative_writing`/`creative_writing_vision` 구분은 정의를 찾지 못했다 ^[ambiguous].
- 태깅이 수동인지 자동인지 블로그는 밝히지 않는다. 원 논문은 Gemini 1.5 Flash 분류였다.

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-vision-categories]] — <https://arena.ai/blog/re-introducing-vision-arena-categories/>
- [[references/sources/visionarena-paper]] — <https://arxiv.org/abs/2412.08687>
