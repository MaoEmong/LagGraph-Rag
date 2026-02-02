# ask12.md — 작업일지

- 날짜: 2026-01-29
- Phase: 7 (품질/안정화) 후속
- 작업 요약:
  - retrieve 단계에 reranker 옵션 연동
  - reranker 설정값 기반으로 후보 확장 후 재정렬
  - Document 스키마에 rerank_score 추가
- 변경 파일:
  - rag_assistant/app/nodes/retrieve.py
  - rag_assistant/app/schemas.py
- 비고:
  - reranker_model=none이면 실제 재정렬 동작 없음
  - reranker_on=true + reranker_model 설정 시 임베딩 기반 재정렬 적용
