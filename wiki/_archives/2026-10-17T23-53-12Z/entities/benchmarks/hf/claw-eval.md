---
title: >-
    Claw-Eval
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/claw-eval/Claw-Eval", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    통신·재무·운영 등 24개 범주 실제 에이전트 과제 + 멀티모달·다중 턴 분할
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Claw-Eval

통신·재무·운영 등 24개 범주 실제 에이전트 과제 + 멀티모달·다중 턴 분할.

HF 데이터셋 `claw-eval/Claw-Eval`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:claw-eval/Claw-Eval"
desc = "통신·재무·운영 등 24개 범주 실제 에이전트 과제 + 멀티모달·다중 턴 분할"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/claw-eval/Claw-Eval>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
