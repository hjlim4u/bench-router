---
title: >-
    SWE-bench Multimodal
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/SWE-bench/SWE-bench_Multimodal", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    JS/TS 시각 소프트웨어 저장소 이슈 612건, 각 과제에 스크린샷·녹화·다이어그램 등 이미지 포함
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# SWE-bench Multimodal

JS/TS 시각 소프트웨어 저장소 이슈 612건, 각 과제에 스크린샷·녹화·다이어그램 등 이미지 포함.

HF 데이터셋 `SWE-bench/SWE-bench_Multimodal`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:SWE-bench/SWE-bench_Multimodal"
desc = "JS/TS 시각 소프트웨어 저장소 이슈 612건, 각 과제에 스크린샷·녹화·다이어그램 등 이미지 포함"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["repo_coding", "vision"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/SWE-bench/SWE-bench_Multimodal>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
