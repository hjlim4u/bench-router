---
title: >-
    facet domain
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/arena-expert"]
summary: >-
    직업 분야. 미국 BLS SOC 기반 23개 분야 중 LMArena 순위표가 있는 8개. Gemini 2.5 Flash가 프롬프트당 0~여러 개를 태깅한다.
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# facet domain

직업 분야. 미국 BLS SOC 기반 23개 분야 중 LMArena 순위표가 있는 8개. Gemini 2.5 Flash가 프롬프트당 0~여러 개를 태깅한다.

`detect`: `rule:*`는 라우터가 결정적으로 판정(0 토큰), `self`는 Orchestrator가 task JSON `facets`에 직접 태그. `evidence`: official(1차 출처 원문) | dataset(데이터셋 카드) | name_only(이름 외 정의 미확인).

## Index

```toml
[[facet]]
id = "software_it"
desc = "소프트웨어·IT 서비스"
detect = "self"
arena_rule = "Gemini 2.5 Flash 다중 라벨"
evidence = "official"

[[facet]]
id = "writing_language"
desc = "글쓰기·문학·언어"
detect = "self"
arena_rule = "Gemini 2.5 Flash 다중 라벨"
evidence = "official"

[[facet]]
id = "science"
desc = "생명·물리·사회 과학"
detect = "self"
arena_rule = "Gemini 2.5 Flash 다중 라벨"
evidence = "official"

[[facet]]
id = "entertainment_media"
desc = "엔터테인먼트·스포츠·미디어"
detect = "self"
arena_rule = "Gemini 2.5 Flash 다중 라벨"
evidence = "official"

[[facet]]
id = "business_finance"
desc = "비즈니스·경영·재무"
detect = "self"
arena_rule = "Gemini 2.5 Flash 다중 라벨"
evidence = "official"

[[facet]]
id = "mathematical"
desc = "수학 분야"
detect = "self"
arena_rule = "Gemini 2.5 Flash 다중 라벨"
evidence = "official"

[[facet]]
id = "legal_government"
desc = "법률·정부"
detect = "self"
arena_rule = "Gemini 2.5 Flash 다중 라벨"
evidence = "official"

[[facet]]
id = "medicine_healthcare"
desc = "의료·보건"
detect = "self"
arena_rule = "Gemini 2.5 Flash 다중 라벨"
evidence = "official"
```

## Sources

- [[references/sources/arena-expert]] — <https://arena.ai/blog/arena-expert>
