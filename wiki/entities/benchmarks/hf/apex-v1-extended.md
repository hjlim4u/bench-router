---
title: >-
    APEX-v1-extended
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/mercor/APEX-v1-extended", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Economically valuable tasks for banking, consulting, big law, and primary care roles (n=400)
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# APEX-v1-extended

Economically valuable tasks for banking, consulting, big law, and primary care roles (n=400).

From the dataset card (`mercor/APEX-v1-extended`):

> APEX-v1-extended The AI Productivity Index (APEX) is a benchmark from Mercor for assessing whether frontier models are capable of performing economically valuable tasks across four jobs: investment banking associate, management consultant, big law associate, and primary care physician (MD). APEX-v1-extended doubles the heldout evaluation set from n=200 to n=400, with increased complexity and variety.

## Index

```toml
[[unit]]
id = "hf:mercor/APEX-v1-extended"
desc = "Economically valuable tasks for banking, consulting, big law, and primary care roles (n=400)"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["professional_work"], domain = ["business_finance", "legal_government", "medicine_healthcare"] }
reason = "Leaderboard API (2026-10-18): 2 rows, 2 models, 0 verified, 2 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/domain|domain]]: business_finance, legal_government, medicine_healthcare
- [[concepts/facets/task|task]]: professional_work

## Related benchmarks

- [[entities/benchmarks/hf/apex-agents]] — APEX-Agents
- [[entities/benchmarks/hf/chi-bench]] — χ-Bench (CHI-Bench)
- [[entities/benchmarks/mg/agents-last-exam]] — Agents' Last Exam

## Sources

- <https://huggingface.co/datasets/mercor/APEX-v1-extended>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
