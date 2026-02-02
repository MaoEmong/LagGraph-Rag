# ask33.md — 작업일지 (상세)

- 날짜: 2026-01-30
- 작업 주제: docs 전체 강제 재인제스트 (OCR 적용)
- 목표:
  - 기존 인제스트 해시/문서/벡터를 제거하고 OCR 활성화 상태로 재인제스트
  - 실제 PDF 문서들을 OCR 포함 경로로 재처리

- 수행 내용:
  1) 기존 인제스트 기록 제거
     - 대상: docs 폴더 내 5개 PDF
     - 제거 항목:
       - Docstore 문서(chunks)
       - VectorDB 벡터
       - ingest_files 해시 기록
     - 결과:
       - files=5
       - removed_docs=143
       - removed_hash=5

  2) OCR 활성화 상태로 재인제스트
     - 설정:
       - OCR_ENABLED=true
       - OCR_LANG=kor+eng
       - OCR_DPI=200
       - OCR_MAX_PAGES=0
       - OCR_MIN_TEXT_LEN=10
     - 결과:
       - IngestResult(files_processed=5, chunks_created=143, duration_ms=17015)

- 결론:
  - docs 폴더 내 모든 PDF가 OCR 조건 포함 상태로 재인제스트 완료

- 다음 작업:
  - reranker 스윕 재실행(문서 수 증가 기준)