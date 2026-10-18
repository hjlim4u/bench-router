---
title: >-
    olmOCR-bench
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/allenai/olmOCR-bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    PDF 1,403개를 마크다운으로 변환할 때 지켜야 할 성질을 단위 테스트 7,010개로 검사
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# olmOCR-bench

PDF 1,403개를 마크다운으로 변환할 때 지켜야 할 성질을 단위 테스트 7,010개로 검사.

HF 데이터셋 `allenai/olmOCR-bench`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:allenai/olmOCR-bench"
desc = "PDF 1,403개를 마크다운으로 변환할 때 지켜야 할 성질을 단위 테스트 7,010개로 검사"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/allenai/olmOCR-bench>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
