---
title: >-
    LEXam-hard
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/joelniklaus/LEXam-hard", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    LEXam 서술형 중 강한 오픈 모델이 가장 못 푸는 518문항, 법률 조사 에이전트 평가용
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LEXam-hard

LEXam 서술형 중 강한 오픈 모델이 가장 못 푸는 518문항, 법률 조사 에이전트 평가용.

HF 데이터셋 `joelniklaus/LEXam-hard`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:joelniklaus/LEXam-hard"
desc = "LEXam 서술형 중 강한 오픈 모델이 가장 못 푸는 518문항, 법률 조사 에이전트 평가용"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["legal"], domain = ["legal_government"], difficulty = ["hard_prompts"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/joelniklaus/LEXam-hard>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
