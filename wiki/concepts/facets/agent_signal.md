---
title: >-
    facet agent_signal
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/agent-arena-methodology", "url:https://arena.ai/blog/leaderboard-changelog", "url:https://arena.ai/blog/ai-alignment-index"]
summary: >-
    Real-world agent reliability signals. This router always delegates to CLI agents, so most apply to every task. Agent Arena metric is the IPS score (net improvement in percentage points over a rando...
base_confidence: 0.6
lifecycle: reviewed
lifecycle_changed: 2026-10-18
lifecycle_reason: "Reviewed 2026-10-18 at the user's request (assistant review, not independent): structure, rules, LMArena categories vs the HF dataset, key figures vs saved sources, adoption consistency."
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-18T00:00:00Z
---
# facet agent_signal

Real-world agent reliability signals. This router always delegates to CLI agents, so most apply to every task. Agent Arena metric is the IPS score (net improvement in percentage points over a randomized baseline).

`detect`: `rule:*` is decided by the router deterministically (zero tokens); `self` is tagged by the Orchestrator in the task JSON `facets`. `evidence`: official (primary source text) | dataset (dataset card) | name_only (only the name is known).

## Index

```toml
[[facet]]
id = "overall"
desc = "Average of per-signal net improvement, every signal one vote"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "task_outcome"
desc = "The user marks a task as a success or failure in the Arena UI"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "steerability"
desc = "Whether the agent lands an accepted fix after an in-line user correction"
detect = "rule:round>1"
evidence = "official"

[[facet]]
id = "bash_reliability"
desc = "Bash failures per call caused by the model; environment failures excluded"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "tool_hallucination"
desc = "Avoids calling a nonexistent tool (including malformed names and leaked reasoning tokens)"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "praise_complaint"
desc = "Whether explicit praise outnumbers complaints in a task"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "alignment"
desc = "Avoids unauthorized actions, false attribution to the user, and deceptive completion claims"
detect = "rule:always"
evidence = "official"
```

## Other axes

- [[concepts/facets/difficulty|difficulty]]
- [[concepts/facets/domain|domain]]
- [[concepts/facets/lang|lang]]
- [[concepts/facets/shape|shape]]
- [[concepts/facets/task|task]]

## Sources

- [[references/sources/agent-arena-methodology]] — <https://arena.ai/blog/agent-arena-methodology>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
- [[references/sources/arena-alignment-index]] — <https://arena.ai/blog/ai-alignment-index>
