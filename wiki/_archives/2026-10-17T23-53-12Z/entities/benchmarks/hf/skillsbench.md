---
title: >-
    SkillsBench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/benchflow/skillsbench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    에이전트 스킬 활용 과제. 감사된 v1.1 결과는 별도 skillsbench-leaderboard 데이터셋
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# SkillsBench

에이전트 스킬 활용 과제. 감사된 v1.1 결과는 별도 skillsbench-leaderboard 데이터셋.

HF 데이터셋 `benchflow/skillsbench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:benchflow/skillsbench"
desc = "에이전트 스킬 활용 과제. 감사된 v1.1 결과는 별도 skillsbench-leaderboard 데이터셋"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/benchflow/skillsbench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
