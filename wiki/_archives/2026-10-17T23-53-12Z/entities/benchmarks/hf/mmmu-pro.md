---
title: >-
    MMMU-Pro
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/MMMU/MMMU_Pro", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    다분야 멀티모달 이해 (이미지+문항, 옵션 증강·비전 전용 설정)
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# MMMU-Pro

다분야 멀티모달 이해 (이미지+문항, 옵션 증강·비전 전용 설정).

HF 데이터셋 `MMMU/MMMU_Pro`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:MMMU/MMMU_Pro"
desc = "다분야 멀티모달 이해 (이미지+문항, 옵션 증강·비전 전용 설정)"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["vision", "science_reasoning"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/MMMU/MMMU_Pro>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
