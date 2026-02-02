# ask18.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 7 (품질/안정화) 후속
- 목표:
  - 중복 인제스트 동작 확인
  - reranker on/off 품질 및 지연 비교
  - 테스트 시 영어 응답 확인(한글 깨짐 회피)

- 테스트 환경:
  - 실행: rag_assistant/.venv 기반 uvicorn
  - 포트: 8030(reranker_off), 8031(reranker_on)
  - 설정: RERANKER_MODEL=embedding, RERANKER_SCORE_THRESHOLD=-1.0
  - 테스트 파일: rag_assistant/tmp_ingest_test.txt (영문 텍스트)
  - 질의: "Answer in English. What are the keywords in the test document?"

- 테스트 결과:
  1) 중복 인제스트
     - 1차 ingest: files_processed=1, chunks_created=1
     - 2차 ingest: files_processed=0, chunks_created=0
     - 동일 내용일 때 스킵 동작 확인

  2) reranker off/on 비교
     - 답변 품질: 동일 (키워드 정확히 반환)
     - citations: 모두 정상 반환
     - 성능: reranker_on이 더 느림
       - off: t_total_ms ~ 3222ms
       - on:  t_total_ms ~ 4567ms

  3) 영어 응답
     - 영어 프롬프트로 응답이 정상적으로 영어로 출력됨
     - 한글 깨짐 문제는 테스트 시 영어 질문으로 우회 가능

- 결론:
  - 중복 인제스트 스킵 로직 정상
  - reranker는 품질 개선이 뚜렷하지 않고 지연 증가
  - 테스트 시 영어 질문을 사용하면 출력 가독성 확보 가능

- 다음 작업 제안:
  - reranker 사용 조건을 품질 저하 케이스에 한정하는 전략 검토
  - 한글 출력 문제는 환경(PS 7/터미널) 기준으로 별도 해결
