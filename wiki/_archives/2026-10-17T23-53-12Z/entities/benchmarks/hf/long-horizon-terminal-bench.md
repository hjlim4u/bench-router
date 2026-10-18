---
title: >-
    Long-Horizon Terminal-Bench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/IntelligenceLab/Long-Horizon-Terminal-Bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    컨테이너 터미널에서 수백 단계 동안 유용한 작업을 지속하는지 측정 (LHTB 2.0 77과제, reward ≥ 0.95 soft solve)
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Long-Horizon Terminal-Bench

컨테이너 터미널에서 수백 단계 동안 유용한 작업을 지속하는지 측정 (LHTB 2.0 77과제, reward ≥ 0.95 soft solve).

HF 데이터셋 `IntelligenceLab/Long-Horizon-Terminal-Bench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:IntelligenceLab/Long-Horizon-Terminal-Bench"
desc = "컨테이너 터미널에서 수백 단계 동안 유용한 작업을 지속하는지 측정 (LHTB 2.0 77과제, reward ≥ 0.95 soft solve)"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["terminal_ops"], shape = ["long_horizon"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/IntelligenceLab/Long-Horizon-Terminal-Bench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
