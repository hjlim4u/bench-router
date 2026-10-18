---
title: >-
    Artificial Analysis 지수
category: entities
tags: [benchmark, aa]
sources: ["url:https://artificialanalysis.ai/api/v2/language/models/free"]
summary: >-
    Artificial Analysis Free API의 모델별 집계 지수. API 키가 있을 때만 수집된다.
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Artificial Analysis 지수

Artificial Analysis Free API(`/api/v2/language/models/free`)의 모델별 집계 지수. 현재 어댑터는 `artificial_analysis_intelligence_index`와 `artificial_analysis_coding_index`만 읽는다(`bench_router/data.py` `AA_FIELDS`).

## Index

```toml
[[unit]]
id = "aa_intelligence"
desc = "AA 종합 지능 지수 (여러 평가의 집계)"
metric = "index"
status = "current"
adoption = "active"
facets = { task = ["general"] }
reason = "ARTIFICIAL_ANALYSIS_API_KEY가 있을 때만 수집"

[[unit]]
id = "aa_coding"
desc = "AA 코딩 지수 (코딩 평가의 집계)"
metric = "index"
status = "current"
adoption = "active"
facets = { task = ["coding"] }
reason = "ARTIFICIAL_ANALYSIS_API_KEY가 있을 때만 수집"
```

## Open Questions

- API 키가 없어 Free 응답의 다른 평가 필드를 확인하지 못했다. 키를 받으면 ingest 때 추가 여부를 정한다.

## Sources

- <https://artificialanalysis.ai/api/v2/language/models/free>
- `bench_router/data.py` `AA_FIELDS`
