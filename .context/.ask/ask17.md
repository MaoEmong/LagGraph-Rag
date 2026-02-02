# ask17.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 7 (품질/안정화) 후속
- 목표:
  - route 규칙 완화(기본 retrieval on)
  - reranker on/off 비교 테스트
  - 인제스트 중복 관리 추가

- 변경 사항:
  1) route 완화
     - 질문이 비어있지 않다면 기본적으로 retrieval을 타도록 수정
     - 파일: rag_assistant/app/nodes/route.py

  2) 인제스트 중복 관리
     - ingest_files 테이블 추가 (source_path, content_hash, updated_at)
     - 동일 파일 내용 해시가 같으면 인제스트 스킵
     - 변경된 경우 기존 문서/벡터 삭제 후 재저장
     - 파일: rag_assistant/app/storage/docstore.py
     - 파일: rag_assistant/app/storage/vector_db.py
     - 파일: rag_assistant/app/ingest/ingest.py

  3) reranker 비교 테스트
     - 질문: "문서 키워드는 무엇인가?"
     - reranker_off/ON 모두 citations 4건 반환
     - reranker_on은 t_retrieve_ms/t_total_ms 증가

- 테스트 결과 요약:
  - reranker_off: t_total_ms ~ 2905ms
  - reranker_on: t_total_ms ~ 4715ms
  - 응답 텍스트는 PowerShell에서 여전히 깨짐

- 다음 작업 제안:
  - 중복 관리 동작 확인(동일 파일 재인제스트 시 files_processed=0 확인)
  - reranker 사용 시 비용/지연 대비 품질 개선 여부 추가 평가
