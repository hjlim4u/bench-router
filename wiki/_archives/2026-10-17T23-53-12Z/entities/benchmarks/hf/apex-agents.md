---
title: >-
    APEX-Agents
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/mercor/apex-agents", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    투자은행·컨설팅·기업법무 실무자가 만든 480개 장기·교차 앱 전문 업무를 파일·도구 환경에서 수행
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# APEX-Agents

투자은행·컨설팅·기업법무 실무자가 만든 480개 장기·교차 앱 전문 업무를 파일·도구 환경에서 수행.

HF 데이터셋 `mercor/apex-agents`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:mercor/apex-agents"
desc = "투자은행·컨설팅·기업법무 실무자가 만든 480개 장기·교차 앱 전문 업무를 파일·도구 환경에서 수행"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["professional_work"], shape = ["long_horizon"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/mercor/apex-agents>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
