---
title: >-
    Arena Alignment Index
category: entities
tags: [benchmark, lmarena]
sources: ["url:https://arena.ai/blog/ai-alignment-index"]
summary: >-
    27개 모델, 9만+ 실사용 에이전트 세션에서 LLM judge가 루브릭으로 실패를 표시하고 대화 길이로 보정. 신호별 1−√(표시율)을 UA 50%, FA·DC 각 25%로 가중 평균. 순위표는 arena.ai/leaderboard/agent/alignment이며 HF 데이터셋에는 없다.
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# Arena Alignment Index

27개 모델, 9만+ 실사용 에이전트 세션에서 LLM judge가 루브릭으로 실패를 표시하고 대화 길이로 보정. 신호별 1−√(표시율)을 UA 50%, FA·DC 각 25%로 가중 평균. 순위표는 arena.ai/leaderboard/agent/alignment이며 HF 데이터셋에는 없다.

점수 컬럼: Bradley-Terry는 `rating`·`rating_lower`·`rating_upper`, Agent는 `score`·`score_ci_lower`·`score_ci_upper`.

## Index

```toml
[[unit]]
id = "arena-web:agent_alignment/overall"
desc = "UA·FA·DC 가중 평균 (높을수록 정렬됨)"
metric = "index"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["alignment"] }
reason = "HF 데이터셋에 없음. 웹 순위표 수집 경로와 이용 조건 확인 필요"

[[unit]]
id = "arena-web:agent_alignment/unauthorized_action"
desc = "요청·권한 범위를 벗어난 행동"
metric = "index"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["alignment"] }
reason = "HF 데이터셋에 없음"

[[unit]]
id = "arena-web:agent_alignment/false_attribution"
desc = "사용자 증거와 모순되는 발언·승인·사실을 사용자에게 귀속"
metric = "index"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["alignment"] }
reason = "HF 데이터셋에 없음"

[[unit]]
id = "arena-web:agent_alignment/deceptive_completion"
desc = "증거와 모순되는데 작업 완료를 명시 주장"
metric = "index"
status = "current"
adoption = "candidate"
facets = { agent_signal = ["alignment"], task = ["repo_coding"] }
reason = "HF 데이터셋에 없음. 코드 디버깅 세션에서 48%로 가장 빈번"
```

## Open Questions

- HF `leaderboard-dataset`에 해당 config가 없다(2026-10-17). 웹 순위표만 확인했다.
- 판정이 LLM judge 기반이라 Agent Arena 신호(IPS)와 지표 성격이 다르다.

## Sources

- [[references/sources/arena-alignment-index]] — <https://arena.ai/blog/ai-alignment-index>
