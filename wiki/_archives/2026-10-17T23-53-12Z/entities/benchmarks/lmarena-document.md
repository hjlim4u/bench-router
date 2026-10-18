---
title: >-
    LMArena Document (style control)
category: entities
tags: [benchmark, lmarena]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/leaderboard-changelog"]
summary: >-
    사용자가 올린 PDF에 대한 문서 추론 쌍대 비교 (2026-03-03 공개).
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LMArena Document (style control)

사용자가 올린 PDF에 대한 문서 추론 쌍대 비교 (2026-03-03 공개).

점수 컬럼: Bradley-Terry는 `rating`·`rating_lower`·`rating_upper`, Agent는 `score`·`score_ci_lower`·`score_ci_upper`.

## Index

```toml
[[unit]]
id = "arena:document_style_control/overall"
desc = "PDF 문서 추론 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["document"] }
```

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
