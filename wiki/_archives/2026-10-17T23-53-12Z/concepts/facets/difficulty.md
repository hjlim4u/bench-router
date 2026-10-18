---
title: >-
    facet difficulty
category: concepts
tags: [facet, index]
sources: ["url:https://lmsys.org/blog/2024-05-17-category-hard", "url:https://arena.ai/blog/arena-expert"]
summary: >-
    프롬프트 난이도.
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# facet difficulty

프롬프트 난이도.

`detect`: `rule:*`는 라우터가 결정적으로 판정(0 토큰), `self`는 Orchestrator가 task JSON `facets`에 직접 태그. `evidence`: official(1차 출처 원문) | dataset(데이터셋 카드) | name_only(이름 외 정의 미확인).

## Index

```toml
[[facet]]
id = "hard_prompts"
desc = "구체성·도메인 지식·복잡성·문제 해결·창의성·기술적 정확성·실제 적용 7개 기준 중 6개 이상"
detect = "self"
arena_rule = "LLM이 7개 기준 판정, 6점 이상"
evidence = "official"

[[facet]]
id = "expert"
desc = "해당 분야 최상위 전문가가 낼 법한 프롬프트 (약 5.5%)"
detect = "self"
arena_rule = "DeepSeek-v3 zero-shot, 프롬프트만 사용"
evidence = "official"
```

## Sources

- [[references/sources/arena-hard-prompts]] — <https://lmsys.org/blog/2024-05-17-category-hard>
- [[references/sources/arena-expert]] — <https://arena.ai/blog/arena-expert>
