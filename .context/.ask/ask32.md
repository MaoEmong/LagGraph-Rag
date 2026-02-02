# ask32.md — 작업일지 (상세)

- 날짜: 2026-01-30
- 작업 주제: OCR 인제스트 재실행 시도
- 목표:
  - docs 폴더 내 실제 PDF에 대해 OCR 인제스트 수행

- 실행 결과:
  - ingest_path('docs') 결과:
    - IngestResult(files_processed=0, chunks_created=0, duration_ms=9426)

- 원인 분석:
  - docs 내 모든 PDF가 이전에 인제스트되어 content_hash가 저장된 상태
  - 현재 파일 내용과 저장된 해시가 동일하여 모두 스킵됨

- 확인 내역:
  - docs 내 파일 목록 및 해시 확인 완료
  - 각 파일에 대해 raw_len/clean_len 정상
  - prev_hash 존재 → 변경 없음 스킵 조건 충족

- 다음 작업 옵션:
  1) 기존 해시/벡터/문서 기록 삭제 후 강제 재인제스트
  2) 신규 PDF 추가 후 인제스트
  3) 특정 파일만 재인제스트 (해당 source_path만 삭제)