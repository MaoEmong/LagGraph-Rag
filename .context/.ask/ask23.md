# ask23.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 기능 작업 (리랭커 조건부 활성화)
- 목표:
  - reranker를 조건부(auto)로 동작하도록 개선

- 변경 사항:
  1) 설정 추가
     - reranker_mode: off | auto | always
     - reranker_distance_threshold: 기본 0.3
     - 파일: rag_assistant/app/config.py

  2) retrieve 로직 개선
     - auto 모드 조건:
       - 결과 수가 top_k 미만
       - 또는 best 거리 >= threshold
       - 또는 score 미제공
     - 파일: rag_assistant/app/nodes/retrieve.py

  3) 문서/환경 반영
     - .env 주석: RERANKER_MODE/RERANKER_DISTANCE_THRESHOLD 추가
     - README.md, OPERATIONS.md, 07UnresolvedItems.md, 04GraphSpec.md 갱신

- 다음 작업:
  - reranker_mode=auto 동작 테스트 (영어 질문 기준)
  - 임계값 튜닝 검토
