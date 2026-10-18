---
title: >-
    LEXam-hard
category: entities
tags: [benchmark, hf-official, legal]
sources: ["url:https://huggingface.co/datasets/joelniklaus/LEXam-hard", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    The 518 open LEXam questions that strong open models score lowest on, for legal-research agents
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LEXam-hard

The 518 open LEXam questions that strong open models score lowest on, for legal-research agents.

From the dataset card (`joelniklaus/LEXam-hard`):

> LEXam-hard The 518 open questions of LEXam that the strongest open models score lowest on. LEXam is a benchmark of law exam questions from the University of Zurich (Fan et al., ICLR 2026; website, code). This is a filtered copy of its open_question test split for evaluating agents that can do legal research.

## Index

```toml
[[unit]]
id = "hf:joelniklaus/LEXam-hard"
desc = "The 518 open LEXam questions that strong open models score lowest on, for legal-research agents"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["legal"], domain = ["legal_government"], difficulty = ["hard_prompts"] }
reason = "Leaderboard API (2026-10-18): 12 rows, 12 models, 0 verified, 11 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/difficulty|difficulty]]: hard_prompts
- [[concepts/facets/domain|domain]]: legal_government
- [[concepts/facets/task|task]]: legal

## Related benchmarks

- [[entities/benchmarks/hf/lexam]] — LEXam
- [[entities/benchmarks/hf/redlinebench]] — RedlineBench

## Sources

- <https://huggingface.co/datasets/joelniklaus/LEXam-hard>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
