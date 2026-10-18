---
title: >-
    olmOCR-bench
category: entities
tags: [benchmark, hf-official, documents]
sources: ["url:https://huggingface.co/datasets/allenai/olmOCR-bench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    1,403 PDFs with 7,010 unit tests on PDF-to-markdown conversion
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# olmOCR-bench

1,403 PDFs with 7,010 unit tests on PDF-to-markdown conversion.

From the dataset card (`allenai/olmOCR-bench`):

> olmOCR-bench olmOCR-bench is a dataset of 1,403 PDF files, plus 7,010 unit test cases that capture properties of the output that a good OCR system should have. This benchmark evaluates the ability of OCR systems to accurately convert PDF documents to markdown format while preserving critical textual and structural information. Quick links: 📃 Paper 🛠️ Code 🎮 Demo Table 1.

## Index

```toml
[[unit]]
id = "hf:allenai/olmOCR-bench"
desc = "1,403 PDFs with 7,010 unit tests on PDF-to-markdown conversion"
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "Leaderboard API (2026-10-18): 21 rows, 21 models, 0 verified, 17 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active. Rows are mostly dedicated OCR/parsing models (LightOnOCR, chandra, surya), not general coding agents"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: ocr_parse

## Related benchmarks

- [[entities/benchmarks/hf/extractbench]] — ExtractBench
- [[entities/benchmarks/hf/mdpbench]] — MDPBench
- [[entities/benchmarks/hf/parsebench]] — ParseBench
- [[entities/benchmarks/hf/real5-omnidocbench]] — Real5-OmniDocBench

## Sources

- <https://huggingface.co/datasets/allenai/olmOCR-bench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
