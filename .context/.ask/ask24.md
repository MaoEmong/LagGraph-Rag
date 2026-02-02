# ask24.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 기능 작업 (리랭커 auto 검증)
- 목표:
  - reranker_mode=auto 동작 테스트

- 이슈:
  - .env BOM 재발로 Settings 로딩 실패 발생
  - 조치: .env를 BOM 없는 UTF-8로 재작성

- 테스트 환경:
  - 실행: rag_assistant/.venv 기반 uvicorn
  - 포트: 8053
  - 설정: RERANKER_MODE=auto, RERANKER_MODEL=embedding
  - 질의: 영어 질문 (한글 깨짐 우회)

- 결과:
  - /ingest: files_processed=1, chunks_created=1
  - /chat: 영어 응답 정상, citations 반환
  - tokens/timing 정상 포함

- 결론:
  - reranker_mode=auto 동작 확인
  - .env BOM 재발 방지 필요
