---
title: >-
    Typed Decisions
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/LocalLLaMA/typed-decisions", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    비정형 상태 하나를 보고 다섯 개의 타입 질문에 확률 분포로 답하기
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Typed Decisions

비정형 상태 하나를 보고 다섯 개의 타입 질문에 확률 분포로 답하기.

HF 데이터셋 `LocalLLaMA/typed-decisions`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:LocalLLaMA/typed-decisions"
desc = "비정형 상태 하나를 보고 다섯 개의 타입 질문에 확률 분포로 답하기"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/LocalLLaMA/typed-decisions>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
