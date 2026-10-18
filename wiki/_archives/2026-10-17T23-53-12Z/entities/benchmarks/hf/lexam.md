---
title: >-
    LEXam
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/LEXam-Benchmark/LEXam", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    스위스·EU·국제법 340개 법학 시험의 다지선다·서술형 법률 추론 (영어·독일어)
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LEXam

스위스·EU·국제법 340개 법학 시험의 다지선다·서술형 법률 추론 (영어·독일어).

HF 데이터셋 `LEXam-Benchmark/LEXam`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:LEXam-Benchmark/LEXam"
desc = "스위스·EU·국제법 340개 법학 시험의 다지선다·서술형 법률 추론 (영어·독일어)"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["legal"], domain = ["legal_government"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/LEXam-Benchmark/LEXam>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
