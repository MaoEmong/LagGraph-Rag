# ask92.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: 재질의 품질 검증(E2E 배치 실행)
- 요청: “2번(재질의 품질 검증)” 진행

---

## 1) 실행 내용

### 1.1 실행 목적
- 재질의 조건 정교화 후 품질 유지 여부 확인
- 의도: 소규모 스모크(5케이스) 실행

### 1.2 실제 실행 파라미터
- 실행 스크립트: `scripts/e2e_eval_batch_runner.py`
- 실행 위치: `D:\ProjectRAG\rag_assistant`
- 환경 변수:
  - `REQUERY_ENABLED=true`
  - `REQUERY_MAX_ATTEMPTS=1`
  - `REQUERY_MIN_DOCS=2`
  - `REQUERY_MIN_CITATIONS=1`
  - `PYTHONPATH=.`
- 배치 설정:
  - `--batch-size 5`
  - 결과적으로 **전체 50케이스**가 5개 단위 배치로 실행됨
  - (start/end 옵션을 지정하지 않아 전체 케이스가 수행됨)

### 1.3 실행 명령
```
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe .\scripts\e2e_eval_batch_runner.py `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 5 `
  --api-host 127.0.0.1 `
  --api-port 8091 `
  --auto-port `
  --thread-prefix eval-requery-smoke `
  --max-retries 2 `
  --retry-backoff-sec 1.0 `
  --health-timeout-sec 60 `
  --batch-output-dir .\evals\results\batches `
  --server-log-dir .\evals\results\server_logs `
  --failure-summary-path .\evals\results\e2e_eval_requery_failure_summary.json `
  --failure-tail-lines 40 `
  --output .\evals\results\e2e_eval_requery_smoke.json
```

---

## 2) 결과 요약

- output 파일:
  - `rag_assistant\evals\results\e2e_eval_requery_smoke.json`
- summary:
  - total_cases=50
  - success_count=50 (100%)
  - keyword_pass_count=50 (100%)
  - citation_pass_count=50 (100%)

- latency(요약):
  - client p50 ≈ 3572ms, p90 ≈ 5983ms
  - graph p50 ≈ 3464ms, p90 ≈ 5870ms

### 판정 근거
- 배치 10개 모두 `success=true`
- summary의 success/keyword/citation pass가 모두 1.0
- 결과 JSON 파일 저장 완료
→ 재질의 조건 변경 후 E2E 품질은 **정상 유지**로 판정

---

## 3) 비고

- 의도는 5케이스 스모크였으나, 배치 러너 특성상 전체 50케이스가 실행됨
- 소규모 스모크가 필요할 경우 `e2e_eval.py --start-index/--end-index` 사용 권장

---

## 4) 다음 작업

- 재질의 트리거 여부를 확인하려면 의도적으로 근거 부족 케이스 추가 필요

