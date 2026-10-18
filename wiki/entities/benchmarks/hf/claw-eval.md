---
title: >-
    Claw-Eval
category: entities
tags: [benchmark, hf-official, agentic]
sources: ["url:https://huggingface.co/datasets/claw-eval/Claw-Eval", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    End-to-end agent tasks across 24 categories plus multimodal and multi-turn splits
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Claw-Eval

End-to-end agent tasks across 24 categories plus multimodal and multi-turn splits.

From the dataset card (`claw-eval/Claw-Eval`):

> Claw-Eval End-to-end transparent benchmark for AI agents acting in the real world. Paper | Leaderboard | Code Dataset Structure Splits Split Examples Description general 161 Core agent tasks across 24 categories (communication, finance, ops, productivity, etc.) multimodal 101 Multimodal agentic tasks requiring perception and creation (webpage generation, video QA, document extraction, etc.) multi_turn 38 Multi-turn …

## Index

```toml
[[unit]]
id = "hf:claw-eval/Claw-Eval"
desc = "End-to-end agent tasks across 24 categories plus multimodal and multi-turn splits"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["multi_tool"] }
reason = "Leaderboard API (2026-10-18): 23 rows, 22 models, 0 verified, 15 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: multi_tool

## Related benchmarks

- [[entities/benchmarks/hf/skillsbench]] — SkillsBench
- [[entities/benchmarks/hf/wildclawbench]] — WildClawBench
- [[entities/benchmarks/hf/yc-bench]] — YC-Bench
- [[entities/benchmarks/mg/toolathlon-verified]] — Toolathlon-Verified

## Sources

- <https://huggingface.co/datasets/claw-eval/Claw-Eval>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
