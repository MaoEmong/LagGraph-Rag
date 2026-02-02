# ask22.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 기능 작업 (청킹 개선 검증)
- 목표:
  - tiktoken 설치 및 토큰 기반 청킹 동작 확인

- 수행:
  - tiktoken 설치 완료
  - /ingest + /chat E2E 테스트 수행 (영어 질문)

- 결과:
  - /ingest: files_processed=1, chunks_created=1
  - /chat: 영어 응답 정상, citations 반환
  - timing/토큰 정보 정상 포함

- 비고:
  - 한글 출력 이슈는 영어 질문으로 우회

- 다음 작업:
  - reranker 조건부 활성화 전략 설계/구현
