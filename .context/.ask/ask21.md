# ask21.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 기능 작업 (청킹 개선)
- 목표:
  - 문자 기반 청킹을 토큰 기반 청킹으로 전환

- 변경 사항:
  - tiktoken 의존성 추가
    - 파일: rag_assistant/requirements.txt
  - 토큰 기반 청킹 구현
    - 파일: rag_assistant/app/ingest/chunking.py
    - encoding_for_model 우선, 실패 시 cl100k_base 폴백
    - overlap >= chunk_size 시 안전 클램프
    - tiktoken 미설치 시 문자 청킹 폴백
  - 청킹 호출부에 모델명 전달
    - 파일: rag_assistant/app/ingest/ingest.py
  - 문서 업데이트
    - 파일: .context/05IngestionSpec.md (토큰 기준 청킹 명시)

- 다음 작업:
  - tiktoken 설치 후 인제스트 재테스트
  - chunk_size/overlap 값 튜닝 여부 검토
