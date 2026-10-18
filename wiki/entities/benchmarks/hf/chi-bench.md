---
title: >-
    χ-Bench (CHI-Bench)
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/actava/chi-bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    End-to-end U.S. healthcare workflows: prior authorization, utilization management, population care management
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# χ-Bench (CHI-Bench)

End-to-end U.S. healthcare workflows: prior authorization, utilization management, population care management.

From the dataset card (`actava/chi-bench`):

> Clinical Healthcare In-Situ Environment Task fixtures for a long-horizon, policy-rich healthcare-workflow agent benchmark 🎉 χ-Bench has been accepted to NeurIPS 2026, Evaluations & Datasets Track! Read the paper. What is in this dataset CHI-Bench evaluates AI agents on end-to-end U.S.

## Index

```toml
[[unit]]
id = "hf:actava/chi-bench"
desc = "End-to-end U.S. healthcare workflows: prior authorization, utilization management, population care management"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["professional_work"], domain = ["medicine_healthcare"], shape = ["long_horizon"] }
reason = "Leaderboard API (2026-10-18): 3 rows, 3 models, 0 verified, 3 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/domain|domain]]: medicine_healthcare
- [[concepts/facets/shape|shape]]: long_horizon
- [[concepts/facets/task|task]]: professional_work

## Related benchmarks

- [[entities/benchmarks/hf/apex-agents]] — APEX-Agents
- [[entities/benchmarks/hf/apex-v1-extended]] — APEX-v1-extended
- [[entities/benchmarks/mg/agents-last-exam]] — Agents' Last Exam

## Sources

- <https://huggingface.co/datasets/actava/chi-bench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
