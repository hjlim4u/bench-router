---
title: >-
    MDPBench
category: entities
tags: [benchmark, hf-official, documents]
sources: ["url:https://huggingface.co/datasets/Delores-Lin/MDPBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Multilingual parsing of digital and photographed documents across diverse scripts
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# MDPBench

Multilingual parsing of digital and photographed documents across diverse scripts.

From the dataset card (`Delores-Lin/MDPBench`):

> MDPBench: A Benchmark for Multilingual Document Parsing in Real-World Scenarios We introduce Multilingual Document Parsing Benchmark, the first benchmark for multilingual digital and photographed document parsing. Document parsing has made remarkable strides, yet almost exclusively on clean, digital, well-formatted pages in a handful of dominant languages.

## Index

```toml
[[unit]]
id = "hf:Delores-Lin/MDPBench"
desc = "Multilingual parsing of digital and photographed documents across diverse scripts"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "Leaderboard API (2026-10-18): 15 rows, 15 models, 0 verified, 15 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: ocr_parse

## Related benchmarks

- [[entities/benchmarks/hf/extractbench]] — ExtractBench
- [[entities/benchmarks/hf/olmocr-bench]] — olmOCR-bench
- [[entities/benchmarks/hf/parsebench]] — ParseBench
- [[entities/benchmarks/hf/real5-omnidocbench]] — Real5-OmniDocBench

## Sources

- <https://huggingface.co/datasets/Delores-Lin/MDPBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
