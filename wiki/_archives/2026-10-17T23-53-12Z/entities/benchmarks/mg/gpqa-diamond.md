---
title: >-
    GPQA Diamond
category: entities
tags: [benchmark, themodelgap, reasoning]
relationships:
  - target: "[[entities/benchmarks/mg/hle]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/hmmt-feb-2026]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://arxiv.org/abs/2311.12022", "url:https://huggingface.co/datasets/Idavidrein/gpqa"]
summary: >-
    PhD-level science questions written to be 'Google-proof' — hard even for skilled non-experts with internet access.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# GPQA Diamond

PhD-level science questions written to be 'Google-proof' — hard even for skilled non-experts with internet access.

## Key Ideas

- 분류: reasoning / Expert science Q&A
- 상태: saturated, 신뢰 등급 D, 의미 있는 점수 차 7.2점, 문항 198개
- 변형: default
- 과제 형태: One item is a single graduate/PhD-level multiple-choice question in biology, physics, or chemistry, written by a subject-matter expert, with four answer options and one unambiguous correct choice. Items are deliberately constructed to survive an open-internet search: in the benchmark's own validation study, skilled non-expert annotators given the question plus 30+ minutes of unrestricted web access answered only about 34% correctly, versus about 65% for on-domain PhD-level experts. GPQA's publishers ask that the exact wording of individual questions not be reproduced in plaintext or images online (to limit training-data leakage), so no example item is quoted here — only the format is described.

관련: [[entities/benchmarks/mg/hle]], [[entities/benchmarks/mg/hmmt-feb-2026]]

## Index

```toml
[[unit]]
id = "mg:gpqa-diamond/default"
desc = "PhD-level science questions written to be 'Google-proof' — hard even for skilled non-experts with internet access."
metric = "pass_pct"
status = "saturated"
adoption = "archive"
facets = { task = ["science_reasoning"] }
reason = "Model Gap 표시 saturated"
meaningful_gap = 7.2
trust_grade = "D"
```

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://arxiv.org/abs/2311.12022>
- <https://huggingface.co/datasets/Idavidrein/gpqa> — HF 공식 미러 (점수 행 `verified=false`)
