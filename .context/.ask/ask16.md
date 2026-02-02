# ask16.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 7 (품질/안정화) 후속
- 목표:
  - retrieval이 확실히 동작하는 질문으로 재테스트

- 테스트 환경:
  - 실행: rag_assistant/.venv 기반 uvicorn
  - 포트: 8017
  - 설정: RERANKER_ON=true, RERANKER_MODEL=embedding, RERANKER_SCORE_THRESHOLD=-1.0
  - 질의: "문서 키워드는 무엇인가?"

- 결과:
  - /chat: success=true
  - citations: 4건 반환 (tmp_ingest_test.txt 관련 chunk_id 포함)
  - timing: t_retrieve_ms 포함 확인
  - 응답 텍스트는 PowerShell에서 여전히 깨짐

- 결론:
  - retrieval 경로는 정상 동작
  - 이전 테스트에서 citations가 비었던 원인은 route 조건을 타지 않은 질문 때문으로 판단
