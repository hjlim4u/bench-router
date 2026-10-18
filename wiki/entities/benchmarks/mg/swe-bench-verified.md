---
title: >-
    SWE-bench Verified
category: entities
tags: [benchmark, themodelgap, coding]
relationships:
  - target: "[[entities/benchmarks/swe-bench-verified-exact]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/deepswe]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/livecodebench]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://www.swebench.com/verified.html", "url:https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified"]
summary: >-
    Gives an agent a real closed GitHub issue and checks whether its patch fixes it and passes the project's real test suite.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# SWE-bench Verified

Gives an agent a real closed GitHub issue and checks whether its patch fixes it and passes the project's real test suite.

## Key Ideas

- Category: coding / Bug fixing
- Lifecycle: saturated, trust grade D, meaningful gap 4.5 points, 500 items
- Variants: default
- Task shape: One task = a real, previously-closed GitHub issue (bug report or feature request) from one of a fixed set of popular open-source Python repositories, paired with a snapshot of that repo's code at the commit right before the human fix was merged. The AI agent gets the issue description and access to the codebase, has to figure out which files to change and how, and outputs a patch. It never sees the human's actual fix or any later commit history. Grading is automatic: the project's own test suite is run against the patched code, and the task counts as solved only if specific tests that used to fail now pass and nothing that used to pass now breaks.

Related: [[entities/benchmarks/mg/deepswe]], [[entities/benchmarks/mg/livecodebench]]

## Index

```toml
[[unit]]
id = "mg:swe-bench-verified/default"
desc = "Gives an agent a real closed GitHub issue and checks whether its patch fixes it and passes the project's real test suite."
metric = "pass_pct"
status = "saturated"
adoption = "archive"
facets = { task = ["repo_coding"] }
reason = "The Model Gap marks it saturated"
meaningful_gap = 4.5
trust_grade = "D"
```

## Facets

- [[concepts/facets/task|task]]: repo_coding

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/hf/swe-bench-multilingual]] — SWE-bench Multilingual
- [[entities/benchmarks/hf/swe-bench-multimodal]] — SWE-bench Multimodal
- [[entities/benchmarks/hf/swe-bench-pro]] — SWE-bench Pro
- [[entities/benchmarks/mg/deepswe]] — DeepSWE
- [[entities/benchmarks/swe-bench-verified-exact]] — SWE-bench Verified (exact import)

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://www.swebench.com/verified.html>
- <https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified> — HF official mirror (score rows `verified=false`)
