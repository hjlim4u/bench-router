---
title: >-
    ParseBench
category: entities
tags: [benchmark, hf-official, documents]
sources: ["url:https://huggingface.co/datasets/llamaindex/ParseBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Enterprise document parsing on tables, charts, content faithfulness, semantic formatting, visual grounding
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# ParseBench

Enterprise document parsing on tables, charts, content faithfulness, semantic formatting, visual grounding.

From the dataset card (`llamaindex/ParseBench`):

> ParseBench Quick links: [🌐 Website] [📜 Paper] [💻 Code] ParseBench is a benchmark for evaluating document parsing systems on real-world enterprise documents, with the following characteristics: Multi-dimensional evaluation.

## Index

```toml
[[unit]]
id = "hf:llamaindex/ParseBench"
desc = "Enterprise document parsing on tables, charts, content faithfulness, semantic formatting, visual grounding"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "Leaderboard API (2026-10-18): 33 rows, 33 models, 0 verified, 33 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active. Rows are mostly dedicated OCR/parsing models (LightOnOCR, chandra, surya), not general coding agents"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: ocr_parse

## Related benchmarks

- [[entities/benchmarks/hf/extractbench]] — ExtractBench
- [[entities/benchmarks/hf/mdpbench]] — MDPBench
- [[entities/benchmarks/hf/olmocr-bench]] — olmOCR-bench
- [[entities/benchmarks/hf/real5-omnidocbench]] — Real5-OmniDocBench

## Sources

- <https://huggingface.co/datasets/llamaindex/ParseBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
