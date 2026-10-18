---
title: >-
    SWE-bench Multilingual
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    9개 언어 41개 저장소의 실제 GitHub 이슈 300건 해결, 단위 테스트로 검증
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# SWE-bench Multilingual

9개 언어 41개 저장소의 실제 GitHub 이슈 300건 해결, 단위 테스트로 검증.

HF 데이터셋 `SWE-bench/SWE-bench_Multilingual`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:SWE-bench/SWE-bench_Multilingual"
desc = "9개 언어 41개 저장소의 실제 GitHub 이슈 300건 해결, 단위 테스트로 검증"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["repo_coding"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
