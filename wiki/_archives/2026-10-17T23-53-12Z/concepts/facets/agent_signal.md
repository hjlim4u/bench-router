---
title: >-
    facet agent_signal
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/agent-arena-methodology", "url:https://arena.ai/blog/leaderboard-changelog", "url:https://arena.ai/blog/ai-alignment-index"]
summary: >-
    에이전트 실사용 신뢰성 신호. 이 라우터는 항상 CLI 에이전트에 위임하므로 대부분 항상 관련된다. 지표는 IPS score(무작위 기준선 대비 순개선 %p).
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# facet agent_signal

에이전트 실사용 신뢰성 신호. 이 라우터는 항상 CLI 에이전트에 위임하므로 대부분 항상 관련된다. 지표는 IPS score(무작위 기준선 대비 순개선 %p).

`detect`: `rule:*`는 라우터가 결정적으로 판정(0 토큰), `self`는 Orchestrator가 task JSON `facets`에 직접 태그. `evidence`: official(1차 출처 원문) | dataset(데이터셋 카드) | name_only(이름 외 정의 미확인).

## Index

```toml
[[facet]]
id = "overall"
desc = "신호별 순개선의 동일 가중 평균"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "task_outcome"
desc = "사용자가 UI에서 작업 성공/실패를 명시 판정"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "steerability"
desc = "중간 교정 후 수정이 수용되는 비율"
detect = "rule:round>1"
evidence = "official"

[[facet]]
id = "bash_reliability"
desc = "호출당 모델이 일으킨 bash 실패율 (환경 장애 제외)"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "tool_hallucination"
desc = "존재하지 않는 도구 호출을 피하는 정도"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "praise_complaint"
desc = "명시적 칭찬이 불만보다 많은 비율"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "alignment"
desc = "요청 밖 행동·사용자 발언 왜곡·거짓 완료 보고를 피하는 정도"
detect = "rule:always"
evidence = "official"
```

## Sources

- [[references/sources/agent-arena-methodology]] — <https://arena.ai/blog/agent-arena-methodology>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
- [[references/sources/arena-alignment-index]] — <https://arena.ai/blog/ai-alignment-index>
