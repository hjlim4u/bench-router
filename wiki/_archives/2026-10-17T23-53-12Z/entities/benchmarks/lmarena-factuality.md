---
title: >-
    LMArena Factuality (Text·Search)
category: entities
tags: [benchmark, lmarena]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/factuality-in-arena"]
summary: >-
    무작위 표본 battle의 응답에서 웹으로 검증 가능한 원자 주장을 뽑아 검색 에이전트가 보정된 참 확률을 매기고, 주장 정확도가 높은 쪽을 승자로 한 factuality battle을 사람 선호와 합친 composite Bradley-Terry. 기본 factuality 가중 25%.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LMArena Factuality (Text·Search)

무작위 표본 battle의 응답에서 웹으로 검증 가능한 원자 주장을 뽑아 검색 에이전트가 보정된 참 확률을 매기고, 주장 정확도가 높은 쪽을 승자로 한 factuality battle을 사람 선호와 합친 composite Bradley-Terry. 기본 factuality 가중 25%.

점수 컬럼: Bradley-Terry는 `rating`·`rating_lower`·`rating_upper`, Agent는 `score`·`score_ci_lower`·`score_ci_upper`.

## Index

```toml
[[unit]]
id = "arena:text_factuality/overall"
desc = "사람 선호 75% + 주장 사실성 25% 합성 점수 (Text)"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "수집 대상이 아니며, 사람 선호 순위와 중복 반영 여부 결정 필요"

[[unit]]
id = "arena:search_factuality/overall"
desc = "사람 선호 75% + 주장 사실성 25% 합성 점수 (Search)"
metric = "elo"
status = "current"
adoption = "candidate"
facets = { task = ["search"] }
reason = "수집 대상이 아니며, 사람 선호 순위와 중복 반영 여부 결정 필요"
```

## Open Questions

- factuality 순위는 사람 선호와 합성된 점수다. 사람 선호 순위와 함께 표에 넣으면 같은 투표가 두 번 반영된다 ^[inferred].

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-factuality]] — <https://arena.ai/blog/factuality-in-arena>
