# ask48.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 장시간 soak test 자동화 스크립트 추가 + 144요청 실검증
- 목표:
  - 100~200 요청 수준 장시간 안정성 테스트를 반복 가능하게 자동화
  - 배치러너를 여러 사이클로 돌려 누적 안정성 지표를 산출

---

## 1) 변경 파일

1. `rag_assistant/scripts/e2e_soak_runner.py` (신규)
2. `README.md`
3. `OPERATIONS.md`

---

## 2) 신규 스크립트: e2e_soak_runner.py

### 2.1 핵심 기능

- 사이클 기반 반복 실행:
  - `--cycles N`
  - 각 사이클마다 `e2e_eval_batch_runner.py` 호출
- 누적 집계:
  - requests_total / success / keyword_pass / citation_pass
  - client/graph latency 통계(min/p50/p90/max/mean)
- 실패 처리:
  - 사이클 실패 정보(반환코드/stdout/stderr tail/failure summary) 수집
  - `--stop-on-failure` 옵션으로 조기 중단 가능

### 2.2 주요 옵션

- `--cycles`
- `--batch-size`
- `--auto-port`
- `--skip-ingest-after-first`
- `--output-dir`
- `--output`

---

## 3) 테스트 수행 (확실 검증)

### 3.1 실행 조건

- 요청 규모: 144요청
  - 36케이스 × 4사이클
- 실행 옵션:
  - auto-port on
  - retries/backoff on
  - first cycle 이후 ingest skip

### 3.2 실행 결과

- 최종 요약 파일:
  - `rag_assistant/evals/results/e2e_soak_144_v1.json`
- summary:
  - `cycles_ok = 4/4`
  - `requests = 144/144` 성공
  - `keyword_pass = 144/144`
  - `citation_pass = 144/144`
  - `failed_cycles = 0`
  - `graph mean latency ≈ 1686.73ms`

결론:
- 144요청 수준에서 안정성/정답성/출처성 모두 유지됨.

---

## 4) 문서 반영

### 4.1 README.md
- Soak Test 섹션 추가
- 144요청 실행 예시 및 산출물 경로 추가

### 4.2 OPERATIONS.md
- `## 10) Soak Test (장시간 안정성)` 섹션 추가
- 목적/실행 예시/산출물 정리

---

## 5) 결론 및 다음 제안

- 장시간 안정성 테스트가 수동 절차에서 자동 절차로 전환됨
- 다음 확장 제안:
  1. 200요청(예: 36×6사이클) 프리셋 추가
  2. soak 결과의 회차별 latency 드리프트 경고 규칙 추가
  3. CI 야간 잡으로 주기 실행

