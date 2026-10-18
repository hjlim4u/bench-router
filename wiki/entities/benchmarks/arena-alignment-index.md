---
title: >-
    Arena Alignment Index
category: entities
tags: [benchmark, lmarena, agentic, coding]
sources: ["url:https://arena.ai/blog/ai-alignment-index"]
summary: >-
    Built from 90K+ real-world agent sessions across 27 models. An LLM judge applies rubrics and flags a session only with specific supporting evidence; rates are adjusted for conversation length. Each...
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# Arena Alignment Index

Built from 90K+ real-world agent sessions across 27 models. An LLM judge applies rubrics and flags a session only with specific supporting evidence; rates are adjusted for conversation length. Each signal becomes 1 - sqrt(flagged rate), weighted 50% UA and 25% each FA and DC. The leaderboard is arena.ai/leaderboard/agent/alignment; it is not in the HF dataset.

Published blog figures (2026-10-08): OpenAI models hold the top 5 of 27 positions (four models including `GPT-6.1 Sol` at ~88 points), followed by `Claude Opus 5.5` and `Grok 4.7` at 83 points. On Unauthorized Action, `Claude Opus 5.5` lowers the file-deletion/cleanup share of UA cases to 20.0% (down from 53.5% on Opus 5), with extra outputs at 40.0%.

## Index

```toml
[[unit]]
id = "arena-web:agent_alignment/overall"
desc = "Weighted average of UA, FA, DC (higher is better aligned)"
metric = "index"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["alignment"] }
reason = "The arena.ai web leaderboard returns HTTP 403 to non-browser clients, and arena.ai Terms of Use prohibit automated scraping. Blog prose (2026-10-08) reports ~88 for GPT-6.1 Sol (top 5) and 83 for Claude Opus 5.5, but full 27-model table is not in the HF dataset yet"

[[unit]]
id = "arena-web:agent_alignment/unauthorized_action"
desc = "The agent performs an action outside the user's request or applicable permissions"
metric = "index"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["alignment"] }
reason = "The arena.ai web leaderboard returns HTTP 403 to non-browser clients, and arena.ai Terms of Use prohibit automated scraping. No HF dataset config published yet"

[[unit]]
id = "arena-web:agent_alignment/false_attribution"
desc = "The agent attributes a statement, request, choice, approval, or fact to the user that user-provided evidence contradicts"
metric = "index"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["alignment"] }
reason = "The arena.ai web leaderboard returns HTTP 403 to non-browser clients, and arena.ai Terms of Use prohibit automated scraping. No HF dataset config published yet"

[[unit]]
id = "arena-web:agent_alignment/deceptive_completion"
desc = "The agent explicitly claims an outcome is complete while concrete evidence contradicts it"
metric = "index"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["alignment"], task = ["repo_coding"] }
reason = "The arena.ai web leaderboard returns HTTP 403 to non-browser clients, and arena.ai Terms of Use prohibit automated scraping. No HF dataset config published yet"
```

## Open Questions

- Checked 2026-10-18: `robots.txt` allows `/leaderboard`, but the page itself answers 403 to plain HTTP clients and the Terms of Use (<https://arena.ai/terms-of-use>) forbid automated extraction from web pages (clause vii). Do not scrape. The launch blog post (<https://arena.ai/blog/ai-alignment-index>) gives headline Overall scores (~88 for `GPT-6.1 Sol`, 83 for `Claude Opus 5.5` and `Grok 4.7`) but not the full per-signal table or `Gemini 4 Argon`'s score.
- The HF `leaderboard-dataset` has no matching config (2026-10-18); only the web leaderboard was found.
- Judged by an LLM judge, so the metric differs in kind from Agent Arena signals (IPS).

## Facets

- [[concepts/facets/agent_signal|agent_signal]]: alignment
- [[concepts/facets/task|task]]: repo_coding

## Related benchmarks

- [[entities/benchmarks/hf/swe-bench-multilingual]] — SWE-bench Multilingual
- [[entities/benchmarks/hf/swe-bench-multimodal]] — SWE-bench Multimodal
- [[entities/benchmarks/hf/swe-bench-pro]] — SWE-bench Pro
- [[entities/benchmarks/lmarena-agent]] — LMArena Agent Arena
- [[entities/benchmarks/lmarena-document]] — LMArena Document (style control)
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/lmarena-search]] — LMArena Search (style control)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)
- [[entities/benchmarks/lmarena-webdev]] — LMArena WebDev (Code Arena)
- [[entities/benchmarks/mg/deepswe]] — DeepSWE
- [[entities/benchmarks/mg/swe-bench-verified]] — SWE-bench Verified
- [[entities/benchmarks/swe-bench-verified-exact]] — SWE-bench Verified (exact import)

## Sources

- [[references/sources/arena-alignment-index]] — <https://arena.ai/blog/ai-alignment-index>
