---
title: >-
    ResearchClawBench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/InternScience/ResearchClawBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    원시 데이터부터 출판 수준 보고서까지 자율 과학 연구를 실제 논문과 비교 평가
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# ResearchClawBench

원시 데이터부터 출판 수준 보고서까지 자율 과학 연구를 실제 논문과 비교 평가.

HF 데이터셋 `InternScience/ResearchClawBench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:InternScience/ResearchClawBench"
desc = "원시 데이터부터 출판 수준 보고서까지 자율 과학 연구를 실제 논문과 비교 평가"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["science_reasoning", "data_analysis"], shape = ["long_horizon"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/InternScience/ResearchClawBench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
