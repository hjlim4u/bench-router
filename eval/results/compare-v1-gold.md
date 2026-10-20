# 위임 결정 비교 — v1-gold

생성: 2026-10-20T22:52:32+00:00 · 작업 20개 · vendor-guided 3회 반복 · 정답표 = eval/results/v1.jsonl (선택한 프로필의 v1 실행 결과로 채점)

| 정책 | 결정 수 | 결정 성공(성공/전체) | 성공률 | 평균 시간(s) | 선택당 cost proxy | 평균 stage 수 |
|---|---|---|---|---|---|---|
| legacy | 20/20 | 20/20 | 100% | 38.6 | 1.00 | 0.0 |
| vendor-guided | 60/60 | 60/60 | 100% | 38.6 | 1.00 | 2.0 |

- legacy와 같은 프로필을 고른 비율: 60/60
- 반복 간 같은 프로필을 고른 작업: 20/20

## 작업별

| 작업 | legacy | vendor-guided (반복별) | v1 결과(프로필별) |
|---|---|---|---|
| bigfiles | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| checklist | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| csvline | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| email | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| form | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| intervals | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| logs | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:FAIL |
| lru | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| math1 | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| math2 | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| pager | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| release | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| roman | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| rotate | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| sales | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| table | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| timeout | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| translate | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| units | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |
| users | claude-default (default_insufficient_evidence) | claude-default, claude-default, claude-default | claude-default:OK, codex-default:OK |

## 해석 주의

- 정답표가 천장이다(v1: 한 프로필 외 전부 성공). 성공률 차이는 선택이 갈린 작업에서만 생기고, 갈리지 않으면 차이 없음으로 읽어야 한다.
- cost proxy는 tier 값이지 실제 요금이 아니다. 시간은 v1 단일 실행값이다.

프로필 매핑(현재=v1, 같은 모델·effort 가정): claude-default=claude-opus-high, codex-default=codex-sol-high
