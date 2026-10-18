---
title: >-
    ParseBench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/llamaindex/ParseBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    실제 기업 문서 파싱을 표·차트·내용 충실도·서식·시각 grounding 5개 차원으로 평가
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# ParseBench

실제 기업 문서 파싱을 표·차트·내용 충실도·서식·시각 grounding 5개 차원으로 평가.

HF 데이터셋 `llamaindex/ParseBench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:llamaindex/ParseBench"
desc = "실제 기업 문서 파싱을 표·차트·내용 충실도·서식·시각 grounding 5개 차원으로 평가"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/llamaindex/ParseBench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
