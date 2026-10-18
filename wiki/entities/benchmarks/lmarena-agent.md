---
title: >-
    LMArena Agent Arena
category: entities
tags: [benchmark, lmarena, agentic]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/agent-arena-methodology", "url:https://arena.ai/resources/agent-arena-signals", "url:https://arena.ai/blog/leaderboard-changelog"]
summary: >-
    Live agent sessions (bash, file writes, web search) are randomized across models; signals mined from session traces give causal treatment effects (IPS). Not vote-based.
base_confidence: 0.62
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# LMArena Agent Arena

Live agent sessions (bash, file writes, web search) are randomized across models; signals mined from session traces give causal treatment effects (IPS). Not vote-based.

Score columns: Agent configs use `score`, `score_ci_lower`, `score_ci_upper` (IPS); the Bradley-Terry configs elsewhere use `rating`, `rating_lower`, `rating_upper`.

## Index

```toml
[[unit]]
id = "arena:agent/overall"
desc = "Average of per-signal net improvement"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["overall"] }

[[unit]]
id = "arena:agent_task_outcome_explicit/overall"
desc = "User marks the task a success or failure"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["task_outcome"] }

[[unit]]
id = "arena:agent_steerability/overall"
desc = "Average user steering effort (None / Low / High) across all assistant turns (updated 2026-09-30)"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["steerability"] }

[[unit]]
id = "arena:agent_bash_reliability/overall"
desc = "Bash failures per non-exempt call caused by the model (updated 2026-10-12)"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["bash_reliability"], task = ["terminal_ops"] }

[[unit]]
id = "arena:agent_tool_hallucination/overall"
desc = "Avoids calling nonexistent tools"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["tool_hallucination"] }

[[unit]]
id = "arena:agent_praise_complaint/overall"
desc = "Praise versus complaint"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["praise_complaint"] }

[[unit]]
id = "arena:agent_bash_reliability_no_prereq/overall"
desc = "Temporary Bash Reliability export config (2026-10-12..14)"
metric = "ips"
status = "current"
adoption = "archive"
facets = { agent_signal = ["bash_reliability"] }
reason = "Exported only on 2026-10-13..15 (publish date 2026-10-14, 54 rows); on 2026-10-16 Arena backfilled 2026-10-12..14 under agent_bash_reliability and stopped updating this config"
evidence = "name_only"

[[unit]]
id = "arena:agent_bash_recovery_steps/overall"
desc = "Follow-up bash calls until the next non-erroring command (old metric)"
metric = "ips"
status = "current"
adoption = "archive"
facets = { agent_signal = ["bash_reliability"] }
reason = "Replaced by Bash Reliability on 2026-10-12"
```

## Open Questions

- Checked 2026-10-18: `arena.ai/resources/agent-arena-signals` (updated 2026-10-12) defines the 5 active signals (Confirmed Success, Praise vs Complaint, Steerability, Bash Reliability, Tool Hallucinations). HF commit history confirms `agent_bash_reliability_no_prereq` was only committed on 2026-10-13..15 (for 2026-10-12..14) before `agent_bash_reliability` backfilled those dates on 2026-10-16.
- Secondary coverage says Bash Reliability carries half the weight of each other signal in the headline rank ^[ambiguous].

## Facets

- [[concepts/facets/agent_signal|agent_signal]]: bash_reliability, overall, praise_complaint, steerability, task_outcome, tool_hallucination
- [[concepts/facets/task|task]]: terminal_ops

## Related benchmarks

- [[entities/benchmarks/arena-alignment-index]] — Arena Alignment Index
- [[entities/benchmarks/hf/long-horizon-terminal-bench]] — Long-Horizon Terminal-Bench
- [[entities/benchmarks/hf/terminal-bench-2-0]] — Terminal-Bench 2.0
- [[entities/benchmarks/hf/terminal-bench-science]] — Terminal-Bench-Science
- [[entities/benchmarks/lmarena-document]] — LMArena Document (style control)
- [[entities/benchmarks/lmarena-factuality]] — LMArena Factuality (Text and Search)
- [[entities/benchmarks/lmarena-media]] — LMArena generative media
- [[entities/benchmarks/lmarena-search]] — LMArena Search (style control)
- [[entities/benchmarks/lmarena-text]] — LMArena Text (style control)
- [[entities/benchmarks/lmarena-vision]] — LMArena Vision (style control)
- [[entities/benchmarks/lmarena-webdev]] — LMArena WebDev (Code Arena)
- [[entities/benchmarks/mg/terminal-bench-2-1]] — Terminal-Bench 2.1
- [[entities/benchmarks/mg/terminal-bench-4-0]] — Terminal-Bench 4.0
- [[entities/benchmarks/terminal-bench-exact]] — Terminal-Bench 4.0 (exact import)

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/agent-arena-methodology]] — <https://arena.ai/blog/agent-arena-methodology>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
