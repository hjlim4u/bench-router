---
title: >-
    Terminal-Bench (연속 릴리스)
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/harborframework/terminal-bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    버전 태그로 주기 릴리스되는 연속 벤치마크. main은 최신 버전을 추적하므로 점수에 버전을 고정해야 한다
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Terminal-Bench (연속 릴리스)

버전 태그로 주기 릴리스되는 연속 벤치마크. main은 최신 버전을 추적하므로 점수에 버전을 고정해야 한다.

HF 데이터셋 `harborframework/terminal-bench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:harborframework/terminal-bench"
desc = "버전 태그로 주기 릴리스되는 연속 벤치마크. main은 최신 버전을 추적하므로 점수에 버전을 고정해야 한다"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/harborframework/terminal-bench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
