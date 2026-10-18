---
title: >-
    ExtractBench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/llamaindex/ExtractBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    문서와 사용자 스키마를 받아 근거(페이지·bbox)가 붙은 스키마 준수 JSON을 추출
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# ExtractBench

문서와 사용자 스키마를 받아 근거(페이지·bbox)가 붙은 스키마 준수 JSON을 추출.

HF 데이터셋 `llamaindex/ExtractBench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:llamaindex/ExtractBench"
desc = "문서와 사용자 스키마를 받아 근거(페이지·bbox)가 붙은 스키마 준수 JSON을 추출"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/llamaindex/ExtractBench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
