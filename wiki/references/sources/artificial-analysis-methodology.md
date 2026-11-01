---
title: >-
  Artificial Analysis methodology
category: references
tags: [source, benchmark, aa, coding]
sources:
  - "url:https://artificialanalysis.ai/methodology"
  - "url:https://artificialanalysis.ai/methodology/intelligence-benchmarking"
  - "url:https://artificialanalysis.ai/methodology/performance-benchmarking"
created: 2026-10-31T00:00:00Z
updated: 2026-10-31T00:00:00Z
as_of: 2026-10-31
summary: >-
  How Artificial Analysis builds Intelligence Index v5.0 (9 evaluations, 4 categories at 25%) and measures API speed, price and cache hit rate; includes retired constituents.
provenance:
  extracted: 0.9
  inferred: 0.07
  ambiguous: 0.03
base_confidence: 0.58
lifecycle: draft
lifecycle_changed: 2026-10-31
tier: supporting
relationships:
  - target: "[[entities/benchmarks/artificial-analysis]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/terminal-bench-4-0]]"
    type: uses
  - target: "[[entities/benchmarks/hf/terminal-bench-science]]"
    type: uses
snapshots:
  - "[[_raw/_archived/2026-10-31-artificial-analysis-intelligence-index|2026-10-31-artificial-analysis-intelligence-index]]"
  - "[[_raw/_archived/2026-10-31-artificial-analysis-methodology|2026-10-31-artificial-analysis-methodology]]"
  - "[[_raw/_archived/2026-10-31-artificial-analysis-performance-benchmarking|2026-10-31-artificial-analysis-performance-benchmarking]]"
---

# Artificial Analysis methodology

Artificial Analysis (AA) benchmarks intelligence, quality, performance and price for models, endpoints and systems. Its performance numbers "are intended to represent the real-world performance customers experience across providers," not peak hardware throughput. This page backs the `aa_intelligence` and `aa_coding` units on [[entities/benchmarks/artificial-analysis]].

## Intelligence Index v5.0

A "primarily text-based, English-language evaluation suite." It is a weighted average of four categories at 25% each:

| Category | Evaluation | Size | Weight | Tools | Private |
|---|---|---|---|---|---|
| Knowledge Work | AA-Briefcase v1.1 | 91 tasks, 4 scenarios | 15% | ✓ | ✓ |
| Knowledge Work | AutomationBench-AA | 657 tasks | 5% | ✓ | ✓ |
| Knowledge Work | GDP.pdf | 100 tasks, 10 domains | 5% | ✗ | ✗ |
| Coding | FrontierCode 2.0 | 132 tasks × 3 | 15% | ✓ | ✓ |
| Coding | Terminal-Bench 4.0 | 66 tasks × 3 | 10% | ✓ | ✗ |
| Science | Terminal-Bench-Science 0.1 | 70 tasks × 3 | 15% | ✓ | ✗ |
| Science | CritPt v2 (Hard Subset) | 40 of 70 × 5 | 10% | ✓ | ✓ |
| General | AA-Omniscience v1.1 | 3,000 | 15% (10% accuracy + 5% non-hallucination) | ✗ | ✓ |
| General | HLE-Diamond | 1,000 (500 reasoning, 500 knowledge; 272 image) | 10% | ✗ | ✗ |

Coding-relevant implementation details:

- **Terminal-Bench 4.0**: full 66 tasks with the mini-swe-agent harness, pass@1 over 3 repeats, 500-step cap, no context compaction. A task passes only if every test passes in an isolated verifier container. See [[entities/benchmarks/mg/terminal-bench-4-0]].
- **FrontierCode 2.0** (Cognition): changes to real open-source repositories, graded by held-out tests plus a rubric with a GPT-6 Luna (medium) judge. Any failed blocking check, or a trajectory flagged for looking up the solution, scores 0. Runs in AA's Stirrup harness with a 500-turn cap.
- **Terminal-Bench-Science 0.1**: 70 research-workflow tasks across five sciences, mini-swe-agent, 1,000-step cap, 30-second per-command timeout. See [[entities/benchmarks/hf/terminal-bench-science]].

The capture does not state which evaluations make up the separate Coding Index. The Coding category above (FrontierCode 2.0 + Terminal-Bench 4.0) is the likely basis. ^[inferred]

## Retired and replaced constituents

| Evaluation | Status |
|---|---|
| HLE (2,158 text-only questions) | Removed in v5.0; replaced by HLE-Diamond. Scores on the two "are not directly comparable." |
| SciCode, AA-LCR v1.1 | Removed in v5.0 |
| CritPt | Replaced by CritPt v2 (Hard Subset) in v5.0 |
| Terminal-Bench 2.1 | Superseded by Terminal-Bench 4.0 in v4.3 |
| τ³-Banking | Removed in v4.3; still run as a standalone evaluation |
| GPQA Diamond | Removed in v4.2; still run on new releases as a standalone evaluation |
| τ²-Bench Telecom, Terminal-Bench Hard | Superseded before v4.1 |
| FrontierCode 1.1 | Superseded by 2.0; still used by the separate Coding Agent Index |

AA also reports, outside the Index, a Multilingual Index (Global-MMLU-Lite, 16 languages including Korean), GDPval-AA, Harvey LAB-AA, APEX-Agents-AA, AA-AnalystAgent ([[entities/benchmarks/mg/aa-analyst-agent]]), ITBench-AA, IFBench and MMMU Pro.

## Testing parameters

- Zero-shot, instruction-prompted, identical conditions per model.
- Temperature 0 for non-reasoning models, 0.6 for reasoning models, unless the lab recommends otherwise. Reasoning models get the maximum output tokens the creator discloses.
- pass@1, aggregated across repeats; up to 30 retries on API failure.
- Index cost uses provider-reported token counts. Performance benchmarking instead counts tokens with tiktoken `o200k_base` so the same text costs the same number of tokens across models.
- Agentic evaluations run in e2b sandboxes.

## Performance and price

- Workloads: 1k, 10k (site default since v2.2.0, 2026-03-02) and 100k input tokens, plus a 1-megapixel vision workload. Each run uses a freshly generated prompt, because speculative decoding makes output speed depend on output type.
- Frequency: 1k/10k/vision 8× per day; 10 parallel requests once per day; 100k weekly. Reported as P50 over 72 hours (14 days for 100k).
- Blended price assumes a 7:2:1 ratio of cache-hit, input and output tokens.
- **Cost per Task** and **Time per Task** are weighted by the Intelligence Index weights. Time per Task is derived from tokens ÷ median answer speed, not timed during evaluation. Verbose or heavy-reasoning models therefore cost more per task at identical per-token prices.
- Cache hit rate comes from multi-turn coding-agent sessions per endpoint, measured about every 18 hours and summarised monthly.
- Known limits: tokenizer efficiency differs across models; quantization is not fully disclosed; TTFT includes network latency from a single `us-central1-a` test server.
- Integrity terms forbid providers from detecting AA traffic or serving it on non-public capacity, quantization or batch size. AA cross-checks with anonymous accounts and may delist.

## Open Questions

- The `aa_coding` unit assumes the Coding Index reflects coding ability; which evaluations it averages in v5.0 is not confirmed.
- The Index changed composition between v4.x and v5.0. Whether the adapter records the index version with each score is unchecked, and AA states v5.0 is not comparable with earlier versions for some components. ^[ambiguous]

## Related

- [[entities/benchmarks/artificial-analysis]]
- [[references/sources/openrouter-benchmarks]] — OpenRouter's benchmarks API re-serves AA indexes.
- [[entities/benchmarks/mg/hle]]
- [[entities/benchmarks/mg/gpqa-diamond]]

## Sources

- [[_raw/_archived/2026-10-31-artificial-analysis-intelligence-index]] — intelligence benchmarking methodology (Index v5.0).
- [[_raw/_archived/2026-10-31-artificial-analysis-methodology]] — scope and definitions.
- [[_raw/_archived/2026-10-31-artificial-analysis-performance-benchmarking]] — API performance methodology and integrity terms.
