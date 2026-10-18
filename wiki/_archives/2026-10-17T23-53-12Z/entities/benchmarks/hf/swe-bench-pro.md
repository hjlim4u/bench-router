---
title: >-
    SWE-bench Pro
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    11개 오픈소스 저장소(Go·Python·JS·TS) 실제 PR 기반 장기 SWE 과제, 숨은 fail-to-pass·pass-to-pass 테스트로 채점 (V2 642과제)
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# SWE-bench Pro

11개 오픈소스 저장소(Go·Python·JS·TS) 실제 PR 기반 장기 SWE 과제, 숨은 fail-to-pass·pass-to-pass 테스트로 채점 (V2 642과제).

HF 데이터셋 `ScaleAI/SWE-bench_Pro`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:ScaleAI/SWE-bench_Pro"
desc = "11개 오픈소스 저장소(Go·Python·JS·TS) 실제 PR 기반 장기 SWE 과제, 숨은 fail-to-pass·pass-to-pass 테스트로 채점 (V2 642과제)"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["repo_coding"], shape = ["long_horizon"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
