---
title: >-
    APEX-Agents
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/mercor/apex-agents", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Long-horizon cross-application professional services tasks from banking, consulting, and law
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# APEX-Agents

Long-horizon cross-application professional services tasks from banking, consulting, and law.

From the dataset card (`mercor/apex-agents`):

> APEX–Agents APEX–Agents is a benchmark from Mercor for evaluating whether AI agents can execute long-horizon, cross-application professional services tasks. Tasks were created by investment banking analysts, management consultants, and corporate lawyers, and require agents to navigate realistic work environments with files and tools (e.g., docs, spreadsheets, PDFs, email, chat, calendar).

## Index

```toml
[[unit]]
id = "hf:mercor/apex-agents"
desc = "Long-horizon cross-application professional services tasks from banking, consulting, and law"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["professional_work"], shape = ["long_horizon"] }
reason = "Leaderboard API (2026-10-18): 13 rows, 13 models, 0 verified, 7 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/shape|shape]]: long_horizon
- [[concepts/facets/task|task]]: professional_work

## Related benchmarks

- [[entities/benchmarks/hf/apex-v1-extended]] — APEX-v1-extended
- [[entities/benchmarks/hf/chi-bench]] — χ-Bench (CHI-Bench)
- [[entities/benchmarks/mg/agents-last-exam]] — Agents' Last Exam

## Sources

- <https://huggingface.co/datasets/mercor/apex-agents>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
