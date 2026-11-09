---
title: >-
  Antigravity CLI /usage report
category: references
tags: [source, quota, antigravity]
sources:
  - "url:https://antigravity.google/docs/cli/commands/usage"
  - "url:https://antigravity.google/changelog"
  - "url:https://github.com/steipete/codexbar/blob/main/docs/antigravity.md"
source_url: "https://antigravity.google/docs/cli/commands/usage"
created: 2026-11-08T15:19:13Z
updated: 2026-11-08T15:19:13Z
as_of: 2026-11-08
summary: >-
  `agy -p /usage --output-format json` returns per-model-group quota buckets (weekly, 5h) as JSON without a model prompt. Verified on agy 1.5.3.
provenance:
  extracted: 0.85
  inferred: 0.1
  ambiguous: 0.05
base_confidence: 0.67
lifecycle: draft
lifecycle_changed: 2026-11-08
---

# Antigravity CLI /usage report

URL: https://antigravity.google/docs/cli/commands/usage

## What it covers

The Antigravity CLI (`agy`) reports the signed-in account's quota. Interactive sessions use `/usage` (alias `/quota`). Since agy 1.1.11, print mode can return the report without a model turn. CodexBar uses this as its `agy` fallback source.

## Key claims

- `agy -p /usage --output-format json` returns `status: SUCCESS`, `num_turns: 0`, zero token usage, and a `command.data` object. Run on agy 1.5.3 on 2026-11-08. ^[extracted]
- `command.data.groups[]` holds quota groups. Each group has a `name`, a `description` that lists its member models, and `buckets[]` with `id`, `window` (`weekly` | `5h`), `remaining_fraction` (0–1), and `reset_time` (ISO 8601). ^[extracted]
- Observed groups on a Pro account: `Gemini Models` (Gemini Flash, Gemini Pro; weekly + 5h), `Claude and GPT models` (Claude Opus, Claude Sonnet, GPT-OSS; bucket ids `3p-weekly`, `3p-5h`), and `Gemini 4 Argon` (weekly only, `gemini-argon-wtu-weekly`). ^[extracted]
- The report's own text: "Within each group, models share a weekly limit and a 5-hour limit. Quota is consumed proportionally to the cost of the tokens." It also says Argon quota is separate on paid Pro plans. ^[extracted]
- The value is *remaining* fraction. CodeBurn and Claude report *used* percent, so an adapter must invert it. ^[inferred]
- CodexBar bounds the call to 90 s and 1 MiB, runs it in a private temp directory, and checks the agy version (1.1.11 or later) first. ^[extracted]

## Limitations

- Group membership comes as prose in `description`, not as model ids. A profile-to-group map still has to parse that text or keep a static table. ^[inferred]
- A community skill describes separate Gemini Pro and Gemini Flash pools. The live report shows them sharing one group. The report is authoritative. ^[ambiguous]
- Google forum threads still ask for an official read-only quota API for third-party apps. This command is the only official machine-readable path found. ^[extracted]

## Related

- [[concepts/quota-scopes]]
- [[synthesis/research-per-model-quota-codeburn-replacement]]
- [[references/sources/codexbar]]
