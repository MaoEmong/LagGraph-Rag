# ask87.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: E2E 50케이스 분석기 실행(알림 게이트)
- 기준: 통합 E2E 결과 분석 및 경고 규칙 적용

---

## 1) 실행 내용

- 입력 리포트:
  - `rag_assistant\evals\results\e2e_eval_50_hybrid_batchrunner.json`
- 출력 리포트:
  - `rag_assistant\evals\results\analysis_e2e_50_hybrid_v1.json`

- 실행 명령:
```
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe D:\ProjectRAG\rag_assistant\scripts\e2e_report_analyzer.py `
  --input D:\ProjectRAG\rag_assistant\evals\results\e2e_eval_50_hybrid_batchrunner.json `
  --min-success-rate 0.98 `
  --min-keyword-pass-rate 0.95 `
  --min-citation-pass-rate 0.98 `
  --max-p90-graph-ms 8000 `
  --max-soak-drift-pct 10 `
  --fail-on-alert `
  --output D:\ProjectRAG\rag_assistant\evals\results\analysis_e2e_50_hybrid_v1.json
```

---

## 2) 결과 요약

- success_rate: 1.0
- keyword_pass_rate: 1.0
- citation_pass_rate: 1.0
- graph p90: 6710ms (threshold 8000ms 이하)
- alerts: 없음
- exit code: 0 (알림 게이트 통과)

### 판정 근거
- 경고 목록이 비어 있음(`alerts=[]`)
- 임계치 초과 항목 없음 → 분석기 통과 처리

---

## 3) 비고

- citation source 분포에 로컬 docs 파일이 다수 포함됨
- hybrid + cross-encoder 구성에서도 품질/근거 지표는 100% 유지

---

## 4) 다음 작업

- 필요 시 재질의(re-query) 노드 추가 검토
- 운영 기준 문서(README/OPERATIONS)에 최신 E2E 결과 반영 여부 결정

