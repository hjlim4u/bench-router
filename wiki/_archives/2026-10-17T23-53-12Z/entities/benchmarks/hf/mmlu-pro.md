---
title: >-
    MMLU-Pro
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    여러 학문 분야 12K 고난도 다지선다 문항의 다중 과제 이해
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# MMLU-Pro

여러 학문 분야 12K 고난도 다지선다 문항의 다중 과제 이해.

HF 데이터셋 `TIGER-Lab/MMLU-Pro`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:TIGER-Lab/MMLU-Pro"
desc = "여러 학문 분야 12K 고난도 다지선다 문항의 다중 과제 이해"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["general"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
