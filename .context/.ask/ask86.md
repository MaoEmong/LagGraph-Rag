# ask86.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: 하이브리드+로컬 리랭커 통합 E2E(50케이스) 실행
- 기준: 11QualityRagPlan.md (통합 검증 단계)

---

## 1) 사전 준비

### 1.1 로컬 리랭커 의존성 설치
- 실행:
  - `D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m pip install sentence-transformers`
- 결과(요약):
  - `sentence-transformers`, `transformers`, `torch` 등 설치 완료
  - pip exit code 0 확인 → 설치 성공

---

## 2) 1차 실행 실패 기록

### 2.1 실패 원인
- 오류: `ModuleNotFoundError: No module named 'app'`
- 원인: 배치 러너 실행 위치가 `D:\ProjectRAG`로 되어 uvicorn import 경로 불일치
- 생성된 실패 요약:
  - `rag_assistant\evals\results\e2e_eval_50_hybrid_failure_summary.json`

### 2.2 후속 조치
- 실행 위치를 `D:\ProjectRAG\rag_assistant`로 변경
- `PYTHONPATH=.` 설정 후 재실행 계획

---

## 3) 재실행 전 정리

- 이전 실행에서 남은 프로세스 종료:
  - 배치 러너/uvicorn/e2e_eval 프로세스 다수 실행 중 확인
  - PID: 8756, 16172, 21660, 27524, 3844, 21088
  - `Stop-Process -Id ... -Force`로 정리 완료

---

## 4) 통합 E2E 실행(50케이스)

### 4.1 실행 환경
- 작업 디렉터리: `D:\ProjectRAG\rag_assistant`
- 환경 변수:
  - `RERANKER_MODE=always`
  - `RERANKER_MODEL=cross-encoder`
  - `RERANKER_CROSS_ENCODER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2`
  - `RERANKER_DEVICE=cuda`
  - `PYTHONPATH=.`

### 4.2 실행 명령
```
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe .\scripts\e2e_eval_batch_runner.py `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 10 `
  --api-host 127.0.0.1 `
  --api-port 8090 `
  --auto-port `
  --thread-prefix eval50-hybrid `
  --max-retries 2 `
  --retry-backoff-sec 1.0 `
  --health-timeout-sec 60 `
  --batch-output-dir .\evals\results\batches `
  --server-log-dir .\evals\results\server_logs `
  --failure-summary-path .\evals\results\e2e_eval_50_hybrid_failure_summary.json `
  --failure-tail-lines 80 `
  --output .\evals\results\e2e_eval_50_hybrid_batchrunner.json
```

### 4.3 결과 요약
- output 파일:
  - `rag_assistant\evals\results\e2e_eval_50_hybrid_batchrunner.json`
- summary:
  - total_cases=50
  - success_count=50 (100%)
  - keyword_pass_count=50 (100%)
  - citation_pass_count=50 (100%)
- latency(요약):
  - client p50 ≈ 4734ms, p90 ≈ 6831ms
  - graph p50 ≈ 4610ms, p90 ≈ 6710ms

### 4.4 테스트 판정 근거
- 배치 5개 모두 `success=true`
- summary의 success/keyword/citation pass가 모두 1.0
- 결과 JSON 파일 저장 완료
→ 통합 E2E 테스트 **통과 처리**

---

## 5) 비고

- 로컬 리랭커 활성화로 지연이 증가했으나 품질 지표는 100% 유지
- 실패 요약 파일은 기존 실패 기록을 덮어씀(정상 재실행 완료)

---

## 6) 다음 작업

- 분석기(알림 게이트) 실행 여부 결정
- 필요 시 re-query(재질의) 노드 추가 검토

