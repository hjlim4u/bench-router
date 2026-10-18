---
title: >-
    LMArena 생성 미디어
category: entities
tags: [benchmark, lmarena]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"]
summary: >-
    이미지·영상 생성과 편집 쌍대 비교. 이 라우터는 CLI 에이전트에 텍스트·코드 작업을 위임하므로 배정 대상이 아니다.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LMArena 생성 미디어

이미지·영상 생성과 편집 쌍대 비교. 이 라우터는 CLI 에이전트에 텍스트·코드 작업을 위임하므로 배정 대상이 아니다.

점수 컬럼: Bradley-Terry는 `rating`·`rating_lower`·`rating_upper`, Agent는 `score`·`score_ci_lower`·`score_ci_upper`.

## Index

```toml
[[unit]]
id = "arena:text_to_image/overall"
desc = "텍스트→이미지 생성"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "CLI 에이전트 위임 대상이 아님"

[[unit]]
id = "arena:image_edit/overall"
desc = "이미지 편집"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "CLI 에이전트 위임 대상이 아님"

[[unit]]
id = "arena:text_to_video/overall"
desc = "텍스트→영상 생성"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "CLI 에이전트 위임 대상이 아님"

[[unit]]
id = "arena:image_to_video/overall"
desc = "이미지→영상 생성"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "CLI 에이전트 위임 대상이 아님"

[[unit]]
id = "arena:video_edit/overall"
desc = "영상 편집"
metric = "elo"
status = "current"
adoption = "excluded"
facets = {  }
reason = "CLI 에이전트 위임 대상이 아님"
```

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
