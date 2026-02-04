# OPERATIONS.md

> 작성일: 2026-02-02
> 목적: 로컬 운영/검증 시 자주 쓰는 명령을 빠르게 참고

## 1) 서버 운영 (Windows)

```powershell
cd D:\ProjectRAG\rag_assistant

# 상태 확인
powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1 -Action status -Port 8000

# 시작
powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1 -Action start -Port 8000 -Reload

# 중지
powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1 -Action stop -Port 8000

# 재시작
powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1 -Action restart -Port 8000 -Reload
```

## 2) 기본 헬스체크

```powershell
curl http://127.0.0.1:8000/health
```

## 3) 웹 UI

- 접속 주소: `http://127.0.0.1:8000/web`
- API 문서: `http://127.0.0.1:8000/docs`

## 4) 주요 API 샘플

### 4.1 Ingest

```powershell
curl -Method Post http://127.0.0.1:8000/ingest `
  -ContentType 'application/json' `
  -Body '{"path":"./evals/docs","recursive":true,"dry_run":false}'
```

### 4.2 Chat

```powershell
curl -Method Post http://127.0.0.1:8000/chat `
  -ContentType 'application/json' `
  -Body '{"thread_id":"default","question":"Answer in English. What is this project?"}'
```

### 4.3 Thread Reset

```powershell
curl -Method Post http://127.0.0.1:8000/threads/reset `
  -ContentType 'application/json' `
  -Body '{"thread_id":"default"}'
```

## 5) OCR 운영 메모

필수 조건:
- `.env`에서 `OCR_ENABLED=true`
- Tesseract 설치 및 PATH 등록

지원 파일:
- 문서: `txt`, `md`, `pdf`, `docx`
- 이미지 OCR: `png`, `jpg`, `jpeg`, `webp`, `bmp`, `tif`, `tiff`

주의:
- 현재는 이미지 "검색"이 아니라 이미지에서 추출한 텍스트를 RAG에 저장해 검색함

## 6) 중복 인제스트 정책

- 동일 `source_path` + 동일 `content_hash`면 스킵
- 내용 변경 시 기존 문서/벡터 삭제 후 재저장

## 6.1) 검색 전략(하이브리드/부모확장/재질의)

운영 기본값(권장):
- Dense 검색: Chroma + OpenAI 임베딩
- Sparse 검색: SQLite FTS5(BM25)
- Parent 확장: 동일 `parent_id` 청크 보강
- 재질의: 근거 부족 시 1회 재검색

관련 환경 변수 예시:
```
SPARSE_ENABLED=true
SPARSE_TOP_K=10
PARENT_EXPAND_ENABLED=true
PARENT_EXPAND_LIMIT=8
REQUERY_ENABLED=true
REQUERY_MAX_ATTEMPTS=1
```

## 6.2) 로컬 리랭커 활성화 예시 (Cross-Encoder)

GPU(예: RTX 3060) 환경에서 품질 최우선 검증 시 사용:

```
RERANKER_MODE=always
RERANKER_MODEL=cross-encoder
RERANKER_CROSS_ENCODER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
RERANKER_DEVICE=cuda
```

## 7) E2E 평가 (배치 러너)

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_eval_batch_runner.py `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 10 `
  --api-host 127.0.0.1 `
  --api-port 8088 `
  --auto-port `
  --thread-prefix eval-main `
  --max-retries 2 `
  --retry-backoff-sec 1.0 `
  --server-log-dir .\evals\results\server_logs `
  --failure-summary-path .\evals\results\e2e_eval_failure_summary.json `
  --failure-tail-lines 20 `
  --output .\evals\results\e2e_eval_merged.json
```

## 8) 리포트 분석 (경고 게이트)

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_report_analyzer.py `
  --input .\evals\results\e2e_eval_50_hybrid_batchrunner.json `
  --min-success-rate 0.98 `
  --min-keyword-pass-rate 0.95 `
  --min-citation-pass-rate 0.98 `
  --max-p90-graph-ms 8000 `
  --fail-on-alert `
  --output .\evals\results\analysis_e2e_50_hybrid_v1.json
```

- 경고 없음: exit code `0`
- 경고 발생: exit code `2`

---

## 9) DB 연동 운영 메모 (MySQL)

### 9.1 기본 설정

`.env`에 다음 항목을 설정한다.

```
DB_ENABLED=true
DB_ADAPTER=mysql
DB_URL=mysql://user:pass@host:3306/dbname
DB_ROW_LIMIT=100
DB_TIMEOUT_SEC=5
```

### 9.2 스모크 테스트

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\db_smoke_test.py --source <table_name> --limit 5 --adapter mysql
```

### 9.3 SQL 변환 단위 테스트

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\db_sql_unit_test.py
```
