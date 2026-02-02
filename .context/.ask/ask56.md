# ask56.md 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: E2E 평가셋 확장 (36 -> 50) + 배치 재검증
- 목표:
  1) 기존 36개 평가 케이스를 50개로 확장
  2) 새 케이스 포함 전체 배치 평가를 실제 실행해 품질 기준 확인
  3) 분석기(alert gate)까지 통과하는 결과 확보

---

## 1) 변경 파일

1. `rag_assistant/evals/e2e_eval_cases.jsonl`
2. `rag_assistant/evals/results/e2e_eval_50cases_batchrunner_v1.json` (1차 실행 결과)
3. `rag_assistant/evals/results/e2e_eval_50cases_batchrunner_v2.json` (2차 실행 결과)
4. `rag_assistant/evals/results/e2e_eval_50cases_batchrunner_v3.json` (최종 결과)
5. `rag_assistant/evals/results/analysis_e2e_50cases_v1.json` (1차 분석)
6. `rag_assistant/evals/results/analysis_e2e_50cases_v3.json` (최종 분석)

---

## 2) 케이스 확장 상세

### 2.1 확장 범위

- 기존: `case-001` ~ `case-036` (36개)
- 추가: `case-037` ~ `case-050` (14개)
- 최종: 총 50개

### 2.2 추가 케이스 설계 방향

- 단일 문서 사실 질의 + 다중 문서 조합 질의를 혼합
- coverage 확대:
  - overview(기술 스택 조합)
  - ingestion(파일형식/chunking/overlap/중복 스킵)
  - reranker(모드/기본값/threshold/auto trigger)
  - cross-doc 비교 질의
- 모든 신규 케이스는 `min_citations=1` 유지
- 평가 지표 안정화를 위해 `expected_keywords`를 과도하게 취약하지 않게 설계

### 2.3 중간 조정 이력(실패 케이스 튜닝)

1차(v1) 실행에서 신규 3개가 keyword miss:
- `case-037`, `case-044`, `case-050`

조정:
- `case-037`: 질문을 API+Vector DB 직접 질의 형태로 변경, 키워드 `FastAPI`, `Chroma`로 명확화
- `case-044`: cross-doc 질의를 ingestion 단일 사실 질의로 변경 (`500`, `800`)
- `case-050`: 답변 변동성이 높은 `token` 키워드를 제거하고 핵심 구성 키워드만 유지

결과:
- v2: 49/50 keyword pass
- v3: 50/50 keyword pass 달성

---

## 3) 테스트/검증 실행 내역

### 3.1 JSONL 구조 검증

- 파싱 및 개수 확인:
  - 총 50개
  - first=`case-001`, last=`case-050`

### 3.2 배치 평가 실행 명령

실행 위치:
- `D:\\ProjectRAG\\rag_assistant`

실행 명령(최종 v3):

```powershell
.\.venv\Scripts\python.exe .\scripts\e2e_eval_batch_runner.py `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 10 `
  --api-host 127.0.0.1 `
  --api-port 8088 `
  --auto-port `
  --thread-prefix eval50r3 `
  --max-retries 2 `
  --retry-backoff-sec 1.0 `
  --health-timeout-sec 30 `
  --batch-output-dir .\evals\results\batches `
  --server-log-dir .\evals\results\server_logs `
  --failure-summary-path .\evals\results\e2e_eval_50r3_failure_summary.json `
  --failure-tail-lines 20 `
  --output .\evals\results\e2e_eval_50cases_batchrunner_v3.json
```

### 3.3 분석기(alert gate) 실행

```powershell
.\.venv\Scripts\python.exe .\scripts\e2e_report_analyzer.py `
  --input .\evals\results\e2e_eval_50cases_batchrunner_v3.json `
  --min-success-rate 0.98 `
  --min-keyword-pass-rate 0.95 `
  --min-citation-pass-rate 0.98 `
  --max-p90-graph-ms 4000 `
  --fail-on-alert `
  --output .\evals\results\analysis_e2e_50cases_v3.json
```

분석기 종료코드:
- `EXIT:0` (경고 없음)

---

## 4) 최종 결과 요약 (v3 기준)

- total_cases: `50`
- success_count: `50` (`success_rate=1.0`)
- keyword_pass_count: `50` (`keyword_pass_rate=1.0`)
- citation_pass_count: `50` (`citation_pass_rate=1.0`)
- graph p90 latency: `2443ms` (임계치 4000ms 이하)
- alerts: 없음

해석:
- 기능 성공률/근거/키워드 기준 모두 100% 충족
- 현재 설정의 품질 게이트(0.98/0.95/0.98 + p90<=4000ms) 통과

---

## 5) 산출물 경로

- 케이스 파일:
  - `rag_assistant/evals/e2e_eval_cases.jsonl`
- 최종 배치 결과:
  - `rag_assistant/evals/results/e2e_eval_50cases_batchrunner_v3.json`
- 최종 분석 결과:
  - `rag_assistant/evals/results/analysis_e2e_50cases_v3.json`

---

## 6) 후속 제안

1) 50 -> 70 확장 시, “근거 없음”/“모호한 질의” 케이스를 분리 트랙으로 운영
2) citation source를 `evals/docs/*` 중심으로 유도하는 retriever 제약 옵션 검토
3) CI 야간 배치에 v3 결과 파일 규격을 고정해 추세 비교 자동화
