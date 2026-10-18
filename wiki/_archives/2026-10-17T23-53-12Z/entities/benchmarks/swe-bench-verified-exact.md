---
title: >-
    SWE-bench Verified (exact import)
category: entities
tags: [benchmark, exact]
relationships:
  - target: "[[entities/benchmarks/mg/swe-bench-verified]]"
    type: related_to
sources: ["repo:bench_router/data.py"]
summary: >-
    프로필의 harness·effort까지 일치하는 SWE-bench Verified 수동 import. 포화 상태라 판별력이 낮다.
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# SWE-bench Verified (exact import)

프로필의 harness·effort까지 일치하는 SWE-bench Verified 수동 import. 포화 상태라 판별력이 낮다. 수집 계약은 `bench_router/data.py` `EXACT_PINS`.

관련: [[entities/benchmarks/mg/swe-bench-verified]]

## Index

```toml
[[unit]]
id = "swe_verified_exact"
desc = "실제 GitHub 이슈 패치가 숨은 테스트를 통과하는 비율"
metric = "pass_pct"
status = "saturated"
adoption = "active"
facets = { task = ["repo_coding"] }
```

## Sources

- `bench_router/data.py` `EXACT_PINS`, `validate_import`
