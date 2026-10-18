---
title: >-
    LMArena Agent Arena
category: entities
tags: [benchmark, lmarena]
sources: ["url:https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset", "url:https://arena.ai/blog/agent-arena-methodology", "url:https://arena.ai/blog/leaderboard-changelog"]
summary: >-
    실사용 에이전트 세션(bash·파일 쓰기·웹 검색)을 무작위 모델에 배정하고 세션 흔적에서 신호를 추출해 인과 효과(IPS)를 추정. 투표 기반이 아니다.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# LMArena Agent Arena

실사용 에이전트 세션(bash·파일 쓰기·웹 검색)을 무작위 모델에 배정하고 세션 흔적에서 신호를 추출해 인과 효과(IPS)를 추정. 투표 기반이 아니다.

점수 컬럼: Bradley-Terry는 `rating`·`rating_lower`·`rating_upper`, Agent는 `score`·`score_ci_lower`·`score_ci_upper`.

## Index

```toml
[[unit]]
id = "arena:agent/overall"
desc = "신호별 순개선 동일 가중 평균"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["overall"] }

[[unit]]
id = "arena:agent_task_outcome_explicit/overall"
desc = "사용자 명시 성공 판정"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["task_outcome"] }

[[unit]]
id = "arena:agent_steerability/overall"
desc = "교정 후 수정 수용"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["steerability"] }

[[unit]]
id = "arena:agent_bash_reliability/overall"
desc = "호출당 모델 기인 bash 실패율"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["bash_reliability"], task = ["terminal_ops"] }

[[unit]]
id = "arena:agent_tool_hallucination/overall"
desc = "존재하지 않는 도구 호출 회피"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["tool_hallucination"] }

[[unit]]
id = "arena:agent_praise_complaint/overall"
desc = "칭찬 대 불만"
metric = "ips"
status = "current"
adoption = "active"
facets = { agent_signal = ["praise_complaint"] }

[[unit]]
id = "arena:agent_bash_reliability_no_prereq/overall"
desc = "bash 신뢰도 변형 (의미 미공개)"
metric = "ips"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["bash_reliability"] }
reason = "공개 페이지에서 정의를 찾지 못함"
evidence = "name_only"

[[unit]]
id = "arena:agent_bash_recovery_steps/overall"
desc = "오류 후 다음 정상 명령까지 bash 호출 수 (구 지표)"
metric = "ips"
status = "current"
adoption = "archive"
facets = { agent_signal = ["bash_reliability"] }
reason = "2026-10-12 Bash Reliability로 대체"
```

## Open Questions

- `agent_bash_reliability_no_prereq`의 정의를 공개 페이지에서 찾지 못했다(2026-10-17 검색).
- 헤드라인 순위에서 Bash Reliability는 다른 신호의 절반 가중이라는 2차 보도가 있다 ^[ambiguous].

## Sources

- [[references/sources/lmarena-leaderboard-dataset]] — <https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset>
- [[references/sources/agent-arena-methodology]] — <https://arena.ai/blog/agent-arena-methodology>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
