# ask29.md — 작업일지 (상세)

- 날짜: 2026-01-30
- 작업 주제: 인제스트 OCR 기능 추가
- 목표:
  - 이미지 기반 PDF(스캔본)도 인제스트 가능하도록 OCR 경로 추가
  - OCR은 옵션으로 동작(기본 OFF)하며, 텍스트 추출 실패 시에만 활성화

- 변경 사항 요약:
  1) OCR 설정 추가
     - 파일: rag_assistant/app/config.py
     - 추가 항목:
       - ocr_enabled (default: false)
       - ocr_lang (default: kor+eng)
       - ocr_dpi (default: 200)
       - ocr_max_pages (default: 0=제한 없음)
       - ocr_min_text_len (default: 100)

  2) OCR 모듈 추가
     - 파일: rag_assistant/app/ingest/ocr.py
     - 기능:
       - pytesseract/fitz/Pillow 지연 import
       - Tesseract 실행 파일 존재 여부 확인
       - PyMuPDF로 페이지 렌더링 후 OCR 수행

  3) PDF 파서에 OCR fallback 추가
     - 파일: rag_assistant/app/ingest/loaders.py
     - 로직:
       - pdfplumber 텍스트 결과가 짧으면 OCR 시도
       - OCR 성공 시 OCR 텍스트 반환, 실패 시 원본 텍스트 사용
       - OCR 실패는 warning 로그 기록

  4) 의존성 추가
     - 파일: rag_assistant/requirements.txt
     - 추가: pytesseract, pymupdf, pillow

  5) 문서 업데이트
     - 파일: .context/05IngestionSpec.md
       - OCR 단계 및 조건 명시
     - 파일: OPERATIONS.md
       - OCR 환경 변수 및 필요 구성 요소 안내 추가

- 주의 사항:
  - OCR 동작을 위해 시스템에 Tesseract 설치가 필요
  - OCR은 텍스트 추출 결과가 매우 짧을 때만 실행됨

- 다음 작업:
  - OCR 환경 구성 확인(Tesseract 설치/경로)
  - 이미지 기반 PDF 인제스트 테스트 수행