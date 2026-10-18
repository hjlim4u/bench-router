---
title: >-
    Real5-OmniDocBench
category: entities
tags: [benchmark, hf-official, documents]
sources: ["url:https://huggingface.co/datasets/PaddlePaddle/Real5-OmniDocBench", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    Document parsing robustness under scanning, warping, screen photography, illumination, and skew
base_confidence: 0.55
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Real5-OmniDocBench

Document parsing robustness under scanning, warping, screen photography, illumination, and skew.

From the dataset card (`PaddlePaddle/Real5-OmniDocBench`):

> Real5-OmniDocBench A Full-Scale Physical Reconstruction Benchmark for Robust Document Parsing in the Wild Leaderboard | Overview | Dataset | Evaluation | Submit Results | Citation Real5-OmniDocBench measures the robustness of document parsing systems under five physical acquisition conditions: Scanning, Warping, Screen-Photography, Illumination, and Skew.

## Index

```toml
[[unit]]
id = "hf:PaddlePaddle/Real5-OmniDocBench"
desc = "Document parsing robustness under scanning, warping, screen photography, illumination, and skew"
metric = "index"
status = "current"
adoption = "candidate"
facets = { task = ["ocr_parse"] }
reason = "Leaderboard API (2026-10-18): 17 rows, 17 models, 0 verified, 17 external-source rows; 0 rows for proprietary models. None of the configured profile models appear. Check the original source and evaluation conditions before making active"
evidence = "dataset"
```

## Facets

- [[concepts/facets/task|task]]: ocr_parse

## Related benchmarks

- [[entities/benchmarks/hf/extractbench]] — ExtractBench
- [[entities/benchmarks/hf/mdpbench]] — MDPBench
- [[entities/benchmarks/hf/olmocr-bench]] — olmOCR-bench
- [[entities/benchmarks/hf/parsebench]] — ParseBench

## Sources

- <https://huggingface.co/datasets/PaddlePaddle/Real5-OmniDocBench>
- [[_raw/hf/official.json]] — card description from the list API, fetched 2026-10-17
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
