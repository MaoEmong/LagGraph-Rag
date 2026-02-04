# ask93.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: 재질의 스모크(5케이스) 실행
- 요청: “1번 진행” (진짜 5케이스 스모크)

---

## 1) 1차 시도 실패

- 실패 원인:
  - `/ingest` 호출 시 `WinError 10061` (서버 미기동 상태)
  - 원문 오류: `ConnectionRefusedError` / `HTTPConnectionPool(host='127.0.0.1', port=8000)`
- 조치:
  - 서버를 `run_server.ps1`로 기동 후 재시도

---

## 2) 서버 기동

- 실행:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1 -Action start -Port 8000 -Reload`
- 결과:
  - health 정상 확인(스크립트 내부 체크)

---

## 3) 스모크 테스트 실행

### 3.1 실행 환경
- 작업 디렉터리: `D:\ProjectRAG\rag_assistant`
- 환경 변수:
  - `REQUERY_ENABLED=true`
  - `REQUERY_MAX_ATTEMPTS=1`
  - `REQUERY_MIN_DOCS=2`
  - `REQUERY_MIN_CITATIONS=1`
  - `PYTHONPATH=.`

### 3.2 실행 명령
```
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe .\scripts\e2e_eval.py `
  --api-url http://127.0.0.1:8000 `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --thread-prefix eval-requery-smoke5 `
  --start-index 1 `
  --end-index 5 `
  --max-retries 2 `
  --retry-backoff-sec 1.0 `
  --output .\evals\results\e2e_eval_requery_smoke5.json
```

### 3.3 결과 요약
- output 파일:
  - `rag_assistant\evals\results\e2e_eval_requery_smoke5.json`
- summary:
  - total_cases=5
  - success_count=5 (100%)
  - keyword_pass_count=5 (100%)
  - citation_pass_count=5 (100%)
- ingest 결과:
  - files_processed=0
  - chunks_created=0
  - duration_ms=139

- latency(요약):
  - client p50 ≈ 4862ms, p90 ≈ 10332ms
  - graph p50 ≈ 4773ms, p90 ≈ 10212ms

### 판정 근거
- summary의 success/keyword/citation pass가 모두 1.0
- 결과 JSON 파일 저장 완료
→ 스모크 테스트 **통과 처리**

---

## 4) 서버 종료

- 실행:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1 -Action stop -Port 8000`
- 결과:
  - PID 종료 확인

---

## 5) 비고

- 스모크는 5케이스만 실행되도록 `start/end` 범위를 고정
- 재질의 조건 정교화 후에도 품질 지표 100% 유지

