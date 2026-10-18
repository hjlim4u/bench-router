---
title: >-
    DeepSWE
category: entities
tags: [benchmark, themodelgap, coding]
relationships:
  - target: "[[entities/benchmarks/mg/swe-bench-verified]]"
    type: related_to
  - target: "[[entities/benchmarks/mg/terminal-bench-2-1]]"
    type: related_to
sources: ["url:https://themodelgap.com/data/benchmarks.json", "url:https://arxiv.org/abs/2607.07946", "url:https://huggingface.co/datasets/datacurve/deep-swe"]
summary: >-
    Original, never-before-public software engineering tasks, built so agents can't just recall memorized GitHub fixes.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# DeepSWE

Original, never-before-public software engineering tasks, built so agents can't just recall memorized GitHub fixes.

## Key Ideas

- Category: coding / Long-horizon coding
- Lifecycle: current, trust grade B, meaningful gap 9.5 points, 113 items
- Variants: default
- Task shape: One task drops a coding agent into a shallow git clone of a real, actively maintained open-source repository (one of 91, spanning TypeScript, Go, Python, JavaScript, and Rust) at a fixed base commit. The clone deliberately excludes the repo's later history, so there is no gold-standard fix sitting in .git for the agent to dig up and copy — this is a design choice, not an oversight, made specifically to close a git-history shortcut Datacurve documented on a competing benchmark. The agent receives a written description of a new capability or bug fix to implement (prompts run about half the length of comparable SWE-bench Pro tasks) and must make real, original code changes using its own tools — edits, shell commands, commits — typically touching substantially more code than a comparable SWE-bench Pro fix (the paper reports 5.5x). Success or failure is decided by a hand-written functional verifier built specifically for that task, which checks whether the requested behavior now actually works in an isolated grading container, rather than by diffing the agent's patch against one specific reference implementation.

Related: [[entities/benchmarks/mg/swe-bench-verified]], [[entities/benchmarks/mg/terminal-bench-2-1]]

## Index

```toml
[[unit]]
id = "mg:deepswe/default"
desc = "Original, never-before-public software engineering tasks, built so agents can't just recall memorized GitHub fixes."
metric = "pass_pct"
status = "current"
adoption = "candidate"
facets = { task = ["repo_coding"], shape = ["long_horizon"] }
reason = "Only 1 profile model evaluated so far (gpt-6.1-sol=69.6 via AA Codex harness at max effort; AA xhigh is 73.2); claude-opus-5-5 and gemini-4-argon not yet on deepswe.datacurve.ai or AA"
meaningful_gap = 9.5
trust_grade = "B"
```

## Facets

- [[concepts/facets/shape|shape]]: long_horizon
- [[concepts/facets/task|task]]: repo_coding

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/hf/swe-bench-multilingual]] — SWE-bench Multilingual
- [[entities/benchmarks/hf/swe-bench-multimodal]] — SWE-bench Multimodal
- [[entities/benchmarks/hf/swe-bench-pro]] — SWE-bench Pro
- [[entities/benchmarks/mg/swe-bench-verified]] — SWE-bench Verified
- [[entities/benchmarks/swe-bench-verified-exact]] — SWE-bench Verified (exact import)

## Sources

- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- <https://arxiv.org/abs/2607.07946>
- <https://huggingface.co/datasets/datacurve/deep-swe> — HF official mirror (score rows `verified=false`)
