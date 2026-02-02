# ask30.md — 작업일지 (상세)

- 날짜: 2026-01-30
- 작업 주제: OCR 인제스트 테스트 준비/시도
- 목표:
  - OCR 의존성 설치 확인 및 테스트용 이미지 PDF 생성
  - OCR 테스트 실행 환경 점검

- 진행 내용:
  1) OCR 파이썬 의존성 확인
     - pytesseract, pymupdf 미설치 상태 확인
  2) 의존성 설치
     - venv에 pytesseract, pymupdf 설치 완료
     - pillow는 이미 설치 상태
  3) Tesseract 설치 확인
     - `tesseract --version` 실패 → 시스템에 Tesseract 미설치
  4) 테스트용 이미지 PDF 생성
     - 경로: rag_assistant/docs/ocr_sample.pdf
     - 내용: 영어 텍스트 삽입된 이미지 기반 PDF

- 결과/이슈:
  - Tesseract 미설치로 OCR 실행이 불가능
  - OCR 테스트는 Tesseract 설치 후 재시도 필요

- 다음 작업:
  - Tesseract 설치(Windows 기준 설치 후 PATH 등록)
  - OCR_ENABLED=true 설정 후 /ingest 실행
  - OCR 결과 기반으로 reranker 스윕 재실행