# ask31.md — 작업일지 (상세)

- 날짜: 2026-01-30
- 작업 주제: Tesseract 설치 + OCR 인제스트 테스트 완료
- 목표:
  - OCR 실행을 위한 Tesseract 설치 및 PATH 등록
  - 이미지 PDF(ocr_sample.pdf) 인제스트 성공 확인

- 진행 내용:
  1) Tesseract 설치
     - winget으로 UB-Mannheim 패키지 설치
     - 설치 경로 확인: C:\Program Files\Tesseract-OCR
     - 사용자 PATH에 경로 추가
     - 버전 확인: tesseract v5.4.0.20240606

  2) OCR 샘플 PDF 준비
     - 파일: rag_assistant/docs/ocr_sample.pdf (이미지 기반 PDF)

  3) OCR 인제스트 테스트
     - 환경 변수:
       - OCR_ENABLED=true
       - OCR_LANG=eng
       - OCR_DPI=200
       - OCR_MAX_PAGES=0
       - OCR_MIN_TEXT_LEN=10
     - 기존 ingest 기록 삭제(ocr_sample.pdf)
       - docstore 문서/벡터/ingest_files 제거 후 재인제스트
     - 실행 결과:
       - IngestResult(files_processed=1, chunks_created=1, duration_ms=2176)

- 이슈/메모:
  - docs 폴더에 이미 여러 PDF가 존재하며, 과거 인제스트 해시로 인해 기본 실행은 스킵될 수 있음
  - OCR 샘플은 상대 경로(source_path=docs\\ocr_sample.pdf) 기준으로 기록됨

- 다음 작업:
  - 실제 스캔 PDF에 대해 OCR 인제스트 수행
  - 인제스트 완료 후 reranker 스윕 재실행