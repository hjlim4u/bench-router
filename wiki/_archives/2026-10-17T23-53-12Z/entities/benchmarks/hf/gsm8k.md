---
title: >-
    GSM8K
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/openai/gsm8k", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    2~8단계 초등 수학 문장제 8.5K
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# GSM8K

2~8단계 초등 수학 문장제 8.5K.

HF 데이터셋 `openai/gsm8k`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:openai/gsm8k"
desc = "2~8단계 초등 수학 문장제 8.5K"
metric = "pass_pct"
status = "saturated"
adoption = "archive"
facets = { task = ["math"] }
reason = "포화(초등 수학, 최상위 모델 변별력 없음)"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/openai/gsm8k>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
