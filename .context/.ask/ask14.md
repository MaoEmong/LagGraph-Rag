# ask14.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 7 (품질/안정화) 후속
- 목표:
  - reranker_score_threshold = -1.0 적용 후 재테스트

- 변경 사항:
  - config.py: reranker_score_threshold 기본값을 -1.0으로 변경
  - .env 주석 예시에서 RERANKER_SCORE_THRESHOLD 값을 -1.0으로 변경
  - .env BOM 제거(설정 로딩 오류 해결)

- 테스트 환경:
  - 실행: rag_assistant/.venv 기반 uvicorn
  - 포트: 8014
  - 설정: RERANKER_ON=true, RERANKER_MODEL=embedding, RERANKER_SCORE_THRESHOLD=-1.0
  - 테스트 파일: rag_assistant/tmp_ingest_test.txt
  - 질의: "리랭커 테스트 문서의 키워드는 무엇인가?"

- 테스트 결과:
  - /health: success=true (vector_db/docstore/llm ok)
  - /ingest: files_processed=1, chunks_created=1, duration_ms=1856
  - /chat: success=true, tokens/timing 포함
    - 응답 텍스트가 PowerShell에서 깨져 보임(인코딩 이슈 지속)
    - citations 빈 배열 유지

- 이슈/관찰:
  - .env에 BOM이 포함되어 Settings 로딩 시 ValidationError 발생
    - 에러: \ufeffopenai_api_key 추가 입력으로 인식
    - 조치: .env를 BOM 없는 UTF-8로 재작성
  - reranker_score_threshold=-1.0 적용 후에도 citations가 비어 있음
    - retrieve 결과가 비었거나 generate가 문서를 사용하지 않은 가능성

- 다음 작업 제안:
  - retrieve 단계 결과 확인(Chroma 컬렉션 count/query 디버그)
  - route 조건/검색 질의 확인
  - PowerShell 출력 인코딩 설정 점검
