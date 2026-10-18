---
title: >-
    EvasionBench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/FutureMa/EvasionBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    실적 발표 Q&A 16,726쌍에서 경영진 답변의 회피 수준 3단계 분류 (라벨은 Eva-4B-V2 모델이 생성)
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# EvasionBench

실적 발표 Q&A 16,726쌍에서 경영진 답변의 회피 수준 3단계 분류 (라벨은 Eva-4B-V2 모델이 생성).

HF 데이터셋 `FutureMa/EvasionBench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:FutureMa/EvasionBench"
desc = "실적 발표 Q&A 16,726쌍에서 경영진 답변의 회피 수준 3단계 분류 (라벨은 Eva-4B-V2 모델이 생성)"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["general"], domain = ["business_finance"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지. 라벨을 모델이 생성해 정답 신뢰도 확인 필요"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/FutureMa/EvasionBench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
