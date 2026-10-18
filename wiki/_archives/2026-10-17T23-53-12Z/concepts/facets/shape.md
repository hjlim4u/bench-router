---
title: >-
    facet shape
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/arena-category/", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    요청 형태.
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# facet shape

요청 형태.

`detect`: `rule:*`는 라우터가 결정적으로 판정(0 토큰), `self`는 Orchestrator가 task JSON `facets`에 직접 태그. `evidence`: official(1차 출처 원문) | dataset(데이터셋 카드) | name_only(이름 외 정의 미확인).

## Index

```toml
[[facet]]
id = "longer_query"
desc = "500토큰 초과 질의 (약 10%)"
detect = "rule:prompt_tokens>500"
evidence = "official"

[[facet]]
id = "multi_turn"
desc = "여러 턴으로 이어진 대화"
detect = "rule:round>1"
evidence = "official"

[[facet]]
id = "long_horizon"
desc = "수백 단계·수 시간에 걸친 긴 에이전트 작업"
detect = "self"
evidence = "dataset"
```

## Sources

- [[references/sources/arena-category]] — <https://arena.ai/blog/arena-category/>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
