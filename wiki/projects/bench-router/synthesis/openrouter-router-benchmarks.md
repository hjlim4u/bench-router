---
title: >-
  OpenRouter model-router benchmarks
category: synthesis
tags: [agentic, coding, benchmark]
sources:
  - "url:https://openrouter.ai/benchmarks/routers"
created: 2026-10-31T00:00:00Z
updated: 2026-10-31T00:00:00Z
as_of: 2026-10-30
summary: >-
  OpenRouter's routing leaderboard: on its index the best router ties the best single model at lower cost. Findings plus a labelled proposal for how bench-router could use it.
provenance:
  extracted: 0.6
  inferred: 0.35
  ambiguous: 0.05
base_confidence: 0.4
lifecycle: draft
lifecycle_changed: 2026-10-31
tier: supporting
relationships:
  - target: "[[references/sources/openrouter-benchmarks]]"
    type: derived_from
  - target: "[[projects/bench-router/synthesis/routing-selection-audit]]"
    type: related_to
---

# OpenRouter model-router benchmarks

OpenRouter scores model routers and single models on six benchmarks: Deep SWE, SWE Atlas QA, Terminal Bench 4.0, Tau3 Banking, MMMU Pro Vision and GPQA Diamond. The extract has per-benchmark 0–10 scores, a combined "Model Routing Index", and cost per task. bench-router is a router too, so this is the closest external comparison for its premise.

## Findings (snapshot 2026-10-30)

| Entry | Routing Index | Cost / task |
|---|---|---|
| Pareto (router) | 9.4 | $0.13 |
| GPT-6.1-Sol (medium) | 9.4 | $0.25 |
| GPT-6.1-Terra (high) | 9.3 | $0.17 |
| GPT-6-Sol (high), GPT-6.1-Sol (high) | 9.1 | $0.28–0.29 |
| Jev Router (Medium tier) | 9.0 | $0.61 |
| Claude Opus 5.5 (high) | 8.9 | $0.45 |
| Gemini 4 Argon (high) | 8.6 | $0.33 |
| Switchyard · Opus 5.5 + Sonnet 5.5 (high) | 8.3 | $2.46 |
| Auto (Medium tier) | 8.2 | $1.02 |
| Fugu Max / Fugu Ultra v2 | 7.3 / 7.8 | $1.04 / $3.01 |

- The best router ties the best single model on the index and costs about half as much. Most other routers score below strong single models and cost more.
- Pareto leads five of six benchmarks; Jev Router (Medium) leads MMMU Pro Vision (9.8).
- Effort is not monotonic. GPT-6.1-Sol scores 9.4 at medium and 9.1 at high; Kimi K3 scores 8.6 at low and 8.3 at high. This matches the vendor advice to keep the lightest setting that meets the bar ([[concepts/model-effort-selection]]). ^[inferred]
- On Deep SWE, Kimi K3.1 Pro leads at 77.9% ($0.84/task); Pareto reaches 74.3% at $0.19/task. One Claude Opus 5.5 row is marked "Failed" at 70.5%, $7.76/task and 51.9 minutes.
- Terminal Bench 4.0 has only six results, so cross-router comparisons there are thin. ^[inferred]

## Implications for bench-router (proposal)

The following is a proposal, not current behaviour. ^[inferred]

- Cost per task belongs next to quality in any decision packet. Routers that ignore cost lose to a single mid-effort model here.
- A "best single model at medium effort" baseline is a fair bar for any routing rule. A routed choice that cannot beat it on this index is not adding value.
- The scale and aggregation of the Routing Index are undocumented in the capture, so treat these numbers as ordering only. ^[ambiguous]

## Open Questions

- How the Routing Index combines the six benchmarks, and whether it is cost-adjusted.
- What Pareto, Jev Router and Switchyard route on; the extract carries names only.
- Whether a manual capture of the routers page methodology exists; only the JSON table extract was saved.

## Related

- [[references/sources/openrouter-benchmarks]]
- [[projects/bench-router/bench-router]]
- [[projects/bench-router/synthesis/routing-selection-audit]]
- [[entities/benchmarks/mg/deepswe]]
- [[entities/benchmarks/mg/terminal-bench-4-0]]

## Sources

- `_raw/web/openrouter-routers.json` — table extract of <https://openrouter.ai/benchmarks/routers>, 2026-10-30T23:14Z.
