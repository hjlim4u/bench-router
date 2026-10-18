---
title: >-
    LMArena WebDev (Code Arena)
category: entities
tags: [benchmark, lmarena]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/leaderboard-changelog"]
summary: >-
    웹 앱 생성 결과에 대한 쌍대 비교 투표. 2026-02-26 HTML/React로 분리, 2026-04-15 Image-to-WebDev 추가.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LMArena WebDev (Code Arena)

웹 앱 생성 결과에 대한 쌍대 비교 투표. 2026-02-26 HTML/React로 분리, 2026-04-15 Image-to-WebDev 추가.

점수 컬럼: Bradley-Terry는 `rating`·`rating_lower`·`rating_upper`, Agent는 `score`·`score_ci_lower`·`score_ci_upper`.

## Index

```toml
[[unit]]
id = "arena:webdev/overall"
desc = "웹 개발 생성 전체 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["webdev_html", "webdev_react"] }

[[unit]]
id = "arena:webdev/webdev-html"
desc = "단일 문서 HTML/CSS/JS 생성 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["webdev_html"] }

[[unit]]
id = "arena:webdev/webdev-react"
desc = "다중 파일 React 앱 생성 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["webdev_react"] }

[[unit]]
id = "arena:webdev/image_to_webdev"
desc = "이미지→웹 페이지 구현 사용자 선호"
metric = "elo"
status = "current"
adoption = "active"
facets = { task = ["image_to_webdev"] }
```

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
