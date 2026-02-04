# ask88.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: 재질의(re-query) 노드 추가 + 문서/운영 가이드 반영
- 기준: 품질 최우선 RAG 개선 계획(11QualityRagPlan)

---

## 1) 변경 내용

### 1.1 재질의 노드 추가
- 파일: `rag_assistant/app/nodes/requery.py` (신규)
- 주요 로직:
  - 근거 부족(답변 없음/출처 없음)이고 재시도 횟수 미만이면 재질의 수행
  - LLM으로 검색용 쿼리 생성(1줄, 키워드 중심)
  - `requery_needed`, `retrieval_query`, `attempt` 업데이트

### 1.2 그래프 흐름 확장
- 파일: `rag_assistant/app/graph.py`
- 변경:
  - `generate -> requery -> (retrieve | finalize)` 분기 추가
  - 재질의 필요 시 검색으로 되돌아가는 루프 구조
  - 타이밍 측정 `t_requery_ms` 추가

### 1.3 스키마/설정 확장
- 파일: `rag_assistant/app/schemas.py`
  - `State.requery_needed` 추가
- 파일: `rag_assistant/app/config.py`
  - `requery_enabled` / `requery_max_attempts`
  - `requery_model` / `requery_model_fallbacks`
  - `requery_temperature` / `requery_max_output_tokens`

### 1.4 환경 변수 예시 추가
- 파일: `rag_assistant/.env.example`
  - `REQUERY_*` 옵션 추가

### 1.5 문서 반영
- 파일: `.context/04GraphSpec.md`
  - requery 노드 및 그래프 플로우 반영
  - State 필드 및 node 설명 추가

### 1.6 운영 문서 반영
- 파일: `README.md`
  - 목차에 “검색 전략(하이브리드/부모확장/재질의)” 추가
  - 해당 섹션에 기본 설정 값 명시
- 파일: `OPERATIONS.md`
  - 검색 전략/재질의 운영 항목 추가

---

## 2) 테스트

### 2.1 compileall 테스트
- 실행 명령:
  - `D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall D:\ProjectRAG\rag_assistant\app`
- 확인된 출력(요약):
  - `app/config.py` 컴파일 성공
  - `app/graph.py` 컴파일 성공
  - `app/nodes/requery.py` 컴파일 성공
  - `app/schemas.py` 컴파일 성공
- 판정 근거:
  - SyntaxError/ImportError 없음, 컴파일 완료 로그 확인 → 테스트 통과 처리

---

## 3) 비고

- 재질의는 기본 1회로 제한(`REQUERY_MAX_ATTEMPTS=1`)
- 실제 재질의 품질은 E2E/실질 질문으로 추가 확인 가능

---

## 4) 다음 작업

- 필요 시 재질의 조건(출처 점수/문서 수 기준) 추가 정교화
- 운영 기준 문서에 최신 E2E 결과 반영 여부 검토

