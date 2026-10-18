---
title: >-
    RedlineBench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/crosbylegal/RedlineBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    SaaS 계약 협상을 판단의 연속으로 보고 다중 턴 레드라이닝을 법적 정확성·상업 정합성 등 5개 차원으로 평가
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# RedlineBench

SaaS 계약 협상을 판단의 연속으로 보고 다중 턴 레드라이닝을 법적 정확성·상업 정합성 등 5개 차원으로 평가.

HF 데이터셋 `crosbylegal/RedlineBench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:crosbylegal/RedlineBench"
desc = "SaaS 계약 협상을 판단의 연속으로 보고 다중 턴 레드라이닝을 법적 정확성·상업 정합성 등 5개 차원으로 평가"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["legal"], domain = ["legal_government"], shape = ["multi_turn"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/crosbylegal/RedlineBench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
