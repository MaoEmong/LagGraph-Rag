# ask13.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 7 (품질/안정화) 후속
- 목표:
  - 리랭커 적용 후 E2E 테스트 수행 (health/ingest/chat)

- 테스트 환경:
  - 실행: rag_assistant/.venv 기반 uvicorn (port 8010)
  - 설정: RERANKER_ON=true, RERANKER_MODEL=embedding
  - 테스트 파일: rag_assistant/tmp_ingest_test.txt
  - 질의: "리랭커 테스트 문서의 키워드는 무엇인가?"

- 테스트 절차:
  1) /health 호출
  2) /ingest 호출 (dry_run=false)
  3) /chat 호출 (thread_id=rerank-test)

- 결과:
  - /health: success=true, vector_db/docstore/llm ok
  - /ingest: files_processed=1, chunks_created=1, duration_ms=832
  - /chat: success=true, tokens/timing 포함
    - 응답 텍스트가 PowerShell에서 깨져 보임(인코딩 이슈 재현)
    - citations가 빈 배열로 반환됨

- 관찰/이슈:
  - 리랭커 사용 시 reranker_score_threshold=0.0으로 인해 모든 문서가 필터링될 가능성 있음
  - 인코딩 문제로 응답 한글 가독성 저하 지속

- 다음 작업:
  - reranker_score_threshold 값을 -1.0 또는 필터링 비활성화로 조정해 재테스트
  - 콘솔/PowerShell 인코딩 설정 점검 및 정리
