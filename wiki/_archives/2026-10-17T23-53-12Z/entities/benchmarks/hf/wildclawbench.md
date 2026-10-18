---
title: >-
    WildClawBench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/internlm/WildClawBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    실제 OpenClaw 개인 비서 환경에 원본 과제 60개를 끝까지 수행
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# WildClawBench

실제 OpenClaw 개인 비서 환경에 원본 과제 60개를 끝까지 수행.

HF 데이터셋 `internlm/WildClawBench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:internlm/WildClawBench"
desc = "실제 OpenClaw 개인 비서 환경에 원본 과제 60개를 끝까지 수행"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"], shape = ["long_horizon"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/internlm/WildClawBench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
