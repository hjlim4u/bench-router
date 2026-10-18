---
title: >-
    YC-Bench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/collinear-ai/yc-bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    CLI 도구로 결정적 시뮬레이션의 AI 스타트업 CEO를 1년간 수행 (수백 턴)
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# YC-Bench

CLI 도구로 결정적 시뮬레이션의 AI 스타트업 CEO를 1년간 수행 (수백 턴).

HF 데이터셋 `collinear-ai/yc-bench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:collinear-ai/yc-bench"
desc = "CLI 도구로 결정적 시뮬레이션의 AI 스타트업 CEO를 1년간 수행 (수백 턴)"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"], shape = ["long_horizon"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/collinear-ai/yc-bench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
