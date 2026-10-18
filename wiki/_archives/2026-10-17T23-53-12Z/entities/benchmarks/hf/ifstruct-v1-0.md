---
title: >-
    IFStruct v1.0
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/LiquidAI/ifstruct-v1.0", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    다양하게 표현된 요구를 따라 스키마에 맞는 JSON/YAML을 제약 디코딩 없이 생성하는지 (구조만 채점)
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# IFStruct v1.0

다양하게 표현된 요구를 따라 스키마에 맞는 JSON/YAML을 제약 디코딩 없이 생성하는지 (구조만 채점).

HF 데이터셋 `LiquidAI/ifstruct-v1.0`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:LiquidAI/ifstruct-v1.0"
desc = "다양하게 표현된 요구를 따라 스키마에 맞는 JSON/YAML을 제약 디코딩 없이 생성하는지 (구조만 채점)"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["instruction_following"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/LiquidAI/ifstruct-v1.0>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
