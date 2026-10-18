---
title: >-
    ScreenSpot-Pro
category: entities
tags: [benchmark, hf-official]
sources: ["url:https://huggingface.co/datasets/likaixin/ScreenSpot-Pro", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    VS Code·PyCharm 등 전문 고해상도 앱 화면에서 지시한 UI 요소 위치 찾기
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# ScreenSpot-Pro

VS Code·PyCharm 등 전문 고해상도 앱 화면에서 지시한 UI 요소 위치 찾기.

HF 데이터셋 `likaixin/ScreenSpot-Pro`. 설명은 데이터셋 카드에서 가져왔다(`_raw/hf/official.json`).

## Index

```toml
[[unit]]
id = "hf:likaixin/ScreenSpot-Pro"
desc = "VS Code·PyCharm 등 전문 고해상도 앱 화면에서 지시한 UI 요소 위치 찾기"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["gui_grounding"] }
reason = "HF 점수 행은 verified=false. 원출처·평가 조건 확인 전에는 active 금지"
evidence = "dataset"
```

## Sources

- <https://huggingface.co/datasets/likaixin/ScreenSpot-Pro>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
