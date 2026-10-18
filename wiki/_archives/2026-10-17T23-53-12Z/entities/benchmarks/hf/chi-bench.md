---
title: >-
    χ-Bench (CHI-Bench)
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/actava/chi-bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    미국 의료 사전 승인·이용 관리·인구 건강 관리의 장기·정책 기반 워크플로를 에이전트가 끝까지 수행
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# χ-Bench (CHI-Bench)

미국 의료 사전 승인·이용 관리·인구 건강 관리의 장기·정책 기반 워크플로를 에이전트가 끝까지 수행.

HF 데이터셋 `actava/chi-bench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:actava/chi-bench"
desc = "미국 의료 사전 승인·이용 관리·인구 건강 관리의 장기·정책 기반 워크플로를 에이전트가 끝까지 수행"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["professional_work"], domain = ["medicine_healthcare"], shape = ["long_horizon"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/actava/chi-bench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
