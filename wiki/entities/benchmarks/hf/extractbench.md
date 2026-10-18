---
title: >-
    ExtractBench
category: entities
tags: [benchmark, hf-official, documents]
sources: ["url:https://huggingface.co/datasets/llamaindex/ExtractBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Schema-valid JSON extraction from a document, each value grounded with page and bounding box
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# ExtractBench

Schema-valid JSON extraction from a document, each value grounded with page and bounding box.

From the dataset card (`llamaindex/ExtractBench`):

> ExtractBench Quick links: [🌐 Website] [📜 Paper] [💻 Code] Given a document and a schema, a system returns structured data with evidence. The input is a full document, born-digital or scanned, and a schema written by the user. The output is a schema-valid JSON object, with the source page and a bounding box for each value as evidence.

## Index

```toml
[[unit]]
id = "hf:llamaindex/ExtractBench"
desc = "Schema-valid JSON extraction from a document, each value grounded with page and bounding box"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "Leaderboard API (2026-10-18): 11 rows, 11 models, 0 verified, 11 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: ocr_parse

## Related benchmarks

- [[entities/benchmarks/hf/mdpbench]] — MDPBench
- [[entities/benchmarks/hf/olmocr-bench]] — olmOCR-bench
- [[entities/benchmarks/hf/parsebench]] — ParseBench
- [[entities/benchmarks/hf/real5-omnidocbench]] — Real5-OmniDocBench

## Sources

- <https://huggingface.co/datasets/llamaindex/ExtractBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
