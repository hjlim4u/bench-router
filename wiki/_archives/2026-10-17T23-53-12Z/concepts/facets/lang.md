---
title: >-
    facet lang
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/arena-category/"]
summary: >-
    프롬프트 언어. LMArena는 Polyglot으로 언어를 태깅한다.
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# facet lang

프롬프트 언어. LMArena는 Polyglot으로 언어를 태깅한다.

`detect`: `rule:*`는 라우터가 결정적으로 판정(0 토큰), `self`는 Orchestrator가 task JSON `facets`에 직접 태그. `evidence`: official(1차 출처 원문) | dataset(데이터셋 카드) | name_only(이름 외 정의 미확인).

## Index

```toml
[[facet]]
id = "ko"
desc = "한국어 프롬프트"
detect = "rule:script(hangul)"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"

[[facet]]
id = "ja"
desc = "일본어 프롬프트"
detect = "rule:script(kana)"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"

[[facet]]
id = "zh"
desc = "중국어 프롬프트"
detect = "rule:script(han_only)"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"

[[facet]]
id = "ru"
desc = "러시아어 프롬프트"
detect = "rule:script(cyrillic)"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"

[[facet]]
id = "en"
desc = "영어 프롬프트"
detect = "self"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"

[[facet]]
id = "es"
desc = "스페인어 프롬프트"
detect = "self"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"

[[facet]]
id = "fr"
desc = "프랑스어 프롬프트"
detect = "self"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"

[[facet]]
id = "de"
desc = "독일어 프롬프트"
detect = "self"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"

[[facet]]
id = "pl"
desc = "폴란드어 프롬프트"
detect = "self"
arena_rule = "Polyglot 언어 태깅"
evidence = "official"
```

## Sources

- [[references/sources/arena-category]] — <https://arena.ai/blog/arena-category/>
