---
title: >-
    Real5-OmniDocBench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/PaddlePaddle/Real5-OmniDocBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    같은 1,355페이지를 스캔·휘어짐·화면 촬영·조명·기울기 5개 조건으로 재촬영한 문서 파싱 강건성
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Real5-OmniDocBench

같은 1,355페이지를 스캔·휘어짐·화면 촬영·조명·기울기 5개 조건으로 재촬영한 문서 파싱 강건성.

HF 데이터셋 `PaddlePaddle/Real5-OmniDocBench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:PaddlePaddle/Real5-OmniDocBench"
desc = "같은 1,355페이지를 스캔·휘어짐·화면 촬영·조명·기울기 5개 조건으로 재촬영한 문서 파싱 강건성"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/PaddlePaddle/Real5-OmniDocBench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
