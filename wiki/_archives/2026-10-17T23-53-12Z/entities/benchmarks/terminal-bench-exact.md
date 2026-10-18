---
title: >-
    Terminal-Bench 4.0 (exact import)
category: entities
tags: [benchmark, exact]
relationships:
  - target: "[[entities/benchmarks/mg/terminal-bench-4-0]]"
    type: related_to
sources: ["repo:bench_router/data.py"]
summary: >-
    프로필의 harness·effort까지 일치하는 Terminal-Bench 4.0 수동 import.
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Terminal-Bench 4.0 (exact import)

프로필의 harness·effort까지 일치하는 Terminal-Bench 4.0 수동 import. 수집 계약은 `bench_router/data.py` `EXACT_PINS`.

관련: [[entities/benchmarks/mg/terminal-bench-4-0]]

## Index

```toml
[[unit]]
id = "terminal_exact"
desc = "실제 터미널 환경의 다단계 작업 완료율"
metric = "pass_pct"
status = "current"
adoption = "active"
facets = { task = ["terminal_ops"] }
```

## Sources

- `bench_router/data.py` `EXACT_PINS`, `validate_import`
