# ask37.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 평가셋 고정 + 자동 E2E 평가 파이프라인(1번 작업) 구축 및 실행
- 목표:
  - 반복 가능한 고정 평가셋을 도입해 `/chat` 품질/출처/지연을 정량 측정
  - 평가 전용 문서를 인제스트하고 동일 질문 세트로 자동 평가 수행
  - 결과를 JSON 리포트로 저장해 추적 가능하게 구성

---

## 1) 구현 배경 및 설계 결정

- 기존 상태:
  - E2E 테스트는 수동 질의 중심이라 재현성/비교 가능성이 낮았음
  - 실제 docs(PDF) 기반 평가는 문서 변경/추가에 따라 결과 변동이 큼
- 이번 결정:
  - **평가 전용 문서 세트(`evals/docs`)와 고정 질의 세트(JSONL)를 분리 관리**
  - 매 실행 시 `evals/docs`를 먼저 인제스트 후 `/chat` 평가
  - 지표는 success/keyword pass/citation pass/latency를 공통 수집

---

## 2) 추가/변경 파일

1. 평가 전용 문서 3종 추가
   - `rag_assistant/evals/docs/rag_overview.txt`
   - `rag_assistant/evals/docs/ingestion_notes.txt`
   - `rag_assistant/evals/docs/reranker_policy.txt`

2. 고정 평가셋(JSONL) 추가 (12케이스)
   - `rag_assistant/evals/e2e_eval_cases.jsonl`
   - 구조:
     - `id`
     - `question`
     - `expected_keywords` (키워드 정답)
     - `keyword_match` (`all` 또는 `any`)
     - `min_citations` (최소 출처 개수)

3. 자동 평가 스크립트 추가
   - `rag_assistant/scripts/e2e_eval.py`
   - 기능:
     - 케이스 로드(JSONL)
     - (옵션) 사전 인제스트 실행
     - 케이스별 `/chat` 호출
     - 키워드 매칭/출처 개수 평가
     - client 기준 elapsed latency + graph `t_total_ms` 집계
     - JSON 리포트 출력 및 파일 저장

---

## 3) 스크립트 인터페이스

- 기본 실행:
  - `python .\scripts\e2e_eval.py --api-url http://127.0.0.1:8060 --cases .\evals\e2e_eval_cases.jsonl --ingest-path .\evals\docs --thread-prefix eval1 --output .\evals\results\e2e_eval_latest.json`

- 주요 옵션:
  - `--skip-ingest`: 인제스트 단계 생략
  - `--timeout-sec`: HTTP 타임아웃
  - `--thread-prefix`: 평가 실행 구분용 thread prefix
  - `--output`: 결과 JSON 저장 경로

---

## 4) 테스트 수행 내역

### 4.1 실행 환경

- 경로: `D:\ProjectRAG\rag_assistant`
- 파이썬: `.venv\Scripts\python.exe`
- API 서버 포트: `8060`

### 4.2 테스트 절차

1) uvicorn 서버 실행  
2) `GET /health` 확인  
3) `scripts/e2e_eval.py` 실행  
4) 결과 파일 저장 확인: `evals/results/e2e_eval_latest.json`

### 4.3 테스트 결과(요약)

- ingest:
  - `files_processed=3`
  - `chunks_created=3`
  - `duration_ms=5535`

- evaluation summary:
  - `total_cases=12`
  - `success_count=4` (`success_rate=0.3333`)
  - `keyword_pass_count=3` (`keyword_pass_rate=0.25`)
  - `citation_pass_count=4` (`citation_pass_rate=0.3333`)
  - client latency(성공 케이스 기준):
    - min `3266.71ms`
    - p50 `3490.40ms`
    - p90 `4038.83ms`
    - max `4038.83ms`
    - mean `3571.59ms`
  - graph t_total_ms(성공 케이스 기준):
    - min `3134`
    - p50 `3342`
    - p90 `3884`
    - max `3884`
    - mean `3425.5`

### 4.4 관찰 이슈

- case-005 이후 서버 연결이 끊기며 후속 케이스가 실패
  - 대표 오류:
    - `ConnectionResetError(10054)`
    - `Failed to establish a new connection: [WinError 10061]`
- 즉, 이번 실행은 평가 스크립트/포맷 검증에는 성공했으나, 전체 12케이스 안정 완주에는 실패

---

## 5) 결론

- 1번 작업(평가셋 고정 + 자동 E2E 평가) 구현 자체는 완료
- 결과 리포트 생성까지 확인 완료
- 다만 서버 연결 안정성 이슈로 완주율이 낮아, 다음 단계에서 API 서버 안정성 점검이 필요

---

## 6) 다음 작업 제안

1. `/chat` 연속 호출 시 서버 종료/연결 끊김 원인 분석 (uvicorn 실행 방식/예외 로그/프로세스 생존성 점검)
2. `e2e_eval.py`에 재시도(backoff) 옵션 추가해 일시적 네트워크 실패 내성 강화
3. 안정화 후 동일 평가셋 재실행하여 기준 리포트(베이스라인) 확정

