# 위임 결정 비교 — oneshot-vs-staged

생성: 2026-10-21T01:27:00+00:00 · 작업 20개 · one-shot/staged 각 3회 반복 · 정답표 = eval/results/v1.jsonl (선택한 프로필의 v1 실행 결과로 채점), oracle = 성공 프로필 중 최저 tier→최단 시간

| 정책 | 결정 수 | 성공 | oracle 일치 | 평균 시간(s) | cost proxy | 호출/결정 | input tok | output tok | 지연(ms) | oracle 1건당 tok | legacy 일치 | 반복 안정 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| legacy | 20/20 | 20/20 | 20/20 | 38.6 | 1.00 | 0.00 | 0 | 0 | 0 | 0 | 20/20 | 0/0 |
| one-shot | 13/60 | 13/60 | 3/60 | 60.6 | 0.22 | 2.00 | 3566 | 814 | 412 | 87594 | 3/13 | 3/20 |
| staged | 60/60 | 60/60 | 60/60 | 38.6 | 1.00 | 2.00 | 3926 | 1033 | 451 | 4960 | 60/60 | 20/20 |

## 작업별

| 작업 | oracle | legacy | one-shot (반복별) | staged (반복별) | v1 결과(프로필별) |
|---|---|---|---|---|---|
| bigfiles | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| checklist | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| csvline | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| email | claude-default | claude-default | claude-default, claude-default, claude-default | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| form | claude-default | claude-default | codex-default, codex-default, codex-default | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| intervals | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| logs | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:FAIL |
| lru | claude-default | claude-default | codex-default, codex-default, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| math1 | claude-default | claude-default | codex-default, abstained, codex-default | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| math2 | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| pager | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| release | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| roman | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| rotate | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| sales | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| table | claude-default | claude-default | codex-default, codex-default, codex-default | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| timeout | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| translate | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| units | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| users | claude-default | claude-default | abstained, abstained, abstained | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |

## 해석 주의

- 정답표가 천장이다(v1: 한 프로필 외 전부 성공). 성공률 차이는 선택이 갈린 작업에서만 생기고, 갈리지 않으면 차이 없음으로 읽어야 한다.
- oracle은 tier 동률이면 v1 단일 실행 시간으로 정한다. 시간 차가 작으면 우연에 가깝다.
- one-shot은 1bd5ea1 이전 decision.md 절차의 재현이지 구 코드 그대로가 아니다.
- cost proxy는 tier 값이지 실제 요금이 아니다. 토큰은 Jev usage 합계(결정 1회 기준 평균)다.

프로필 매핑(현재=v1, 같은 모델·effort 가정): claude-default=claude-opus-high, codex-default=codex-sol-high
