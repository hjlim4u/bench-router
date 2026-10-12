# bench-router 구현 상태

갱신: 2026-10-12 · 대상 런타임: WSL(Linux) Python 3.11+ · git 저장소 아님(커밋 없음)

## 완료: P0 (오프라인 계약·합성 라우팅)
- `bench_router/routing.py` — task/profiles/categories/snapshot 검증, L0/L1/general 분류, 하드 제약, percentile, coverage/Q/S, near-tie, default/fallback, 소스 stale/max_stale, fingerprint 불일치(stale_config).
- `bench_router/cli.py` — `route --dry-run`, `explain`. live `route`는 exit 2(P2 미구현).
- `bench_router/categories.toml` — 03 문서의 evidence 매핑(P 정책, policy_version 1.0).
- `test_p0.py` — V01–V10 + snapshot stale/fingerprint/변조 검사.

재현:
```bash
python3 -m unittest -v test_p0
python3 -m bench_router.cli --config-dir CFG --cache-dir CACHE route --task task.json --dry-run
```

## 검증 결과
- offline: 11/11 통과. 실행 환경은 Windows Python 3.13.7 (WSL 배포판 미설치로 WSL 실행은 미검증). P0 코드에 OS 의존 부분 없음.
- mutation 확인: near_tie_epsilon/missing_penalty/coverage_threshold 변경 시 테스트 실패함.
- 실제 API·herdr·Agent: 미실행.

## P0에서 정한 것 (문서에 없던 세부)
- snapshot 위치: `$XDG_CACHE_HOME/bench-router/snapshot.json`, 실패 시 `snapshot.last-good.json`. 둘 다 없으면 evidence 없이 constrained default.
- snapshot 형식: `sources.{id}.{last_success_at, ttl_hours, max_stale_hours, published_at?, attribution?}`, `profiles.{id}.{fingerprint, evidence.{evidence_id}.{normalized, raw, scope, cohort_id, metric_version, source_id, source_revision, fetched_at, published_at, evaluated_at}}`. 정규화(percentile)는 refresh 측에서 계산해 넣는다(`routing.percentile_ranks`).
- snapshot_id = `routing.snapshot_hash()` (snapshot_id 제외 canonical JSON SHA-256). P1 writer도 이것을 써야 한다.
- profile fingerprint: kind/executable/args/model_id/harness_id/reasoning_effort/config_revision + cli_version="unknown". P2에서 버전 probe 추가 시 refresh도 같은 입력을 써야 한다.
- fingerprint 불일치 시 해당 프로필 evidence 전체 무시(proxy 포함).
- L1: 한 카테고리에서 서로 다른 규칙 2개 이상, 다른 카테고리 규칙 없음일 때만 채택. 영문 키워드는 단어 경계, 한글은 부분 문자열.
- selection_mode: `benchmark_score` | `default_insufficient_evidence` | `fallback_insufficient_evidence` | `none`.
- coverage < 0.5 후보는 `score=null`(quality는 관측이 있으면 유지).
- kind 지원 목록 검사는 생략 — herdr 설치 schema 확인 후(P2) 추가.

## 미완료
- JSON Schema 파일(task/output): 런타임 validator가 계약을 강제하므로 생략. 외부 소비자가 생기면 작성.
- P1: SQLite, refresh/import/status, AA/Arena adapter, fcntl lock, atomic 게시. ← WSL 필요.
- P2: herdr 연결 전체. herdr 미설치.

## 다음 한 가지 작업
WSL 배포판 설치(`wsl --install Ubuntu`) 후 `python3 -m unittest test_p0` 재실행 → P1 source fixture(AA pagination 2페이지)부터 시작.

## 사용자에게 필요한 정보
- 실제 사용할 프로필(CLI/모델 ID/reasoning/cost tier/context/capability).
- AA API 키 준비 여부(P1 live 확인용, 키 자체는 환경변수로만).
