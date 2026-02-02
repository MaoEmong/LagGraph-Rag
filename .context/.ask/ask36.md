# ask36.md — 작업일지 (상세)

- 날짜: 2026-01-30
- 작업 주제: reranker_distance_threshold 기본값 확정 및 문서 반영
- 목표:
  - 스윕 결과(0.60 구간 최적) 기반으로 기본 임계값을 0.60으로 고정

- 변경 사항:
  1) 기본 설정값 업데이트
     - 파일: rag_assistant/app/config.py
     - 변경: reranker_distance_threshold 0.3 → 0.6

  2) 환경 변수 예시 업데이트
     - 파일: rag_assistant/.env
     - 변경: RERANKER_DISTANCE_THRESHOLD=0.3 → 0.6

  3) 문서 반영
     - 파일: README.md
     - 파일: OPERATIONS.md
     - 파일: .context/07UnresolvedItems.md
     - 내용: RERANKER_DISTANCE_THRESHOLD 기본값 0.6 반영

- 근거:
  - reranker 스윕(0.60~0.66) 결과
    - 0.60에서 트리거율 80%로 목표 범위(50~80%)에 적합
    - 0.62 이상부터 급격히 감소

- 다음 작업:
  - E2E 질의 테스트로 품질/지연 영향 확인
  - 필요 시 threshold 미세 조정