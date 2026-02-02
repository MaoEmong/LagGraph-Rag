# ask57.md 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 이미지 파일 인제스트 지원 추가 (OCR 기반)
- 요청: "이미지파일도 가능하게 해줘"

---

## 1) 변경 파일

1. `rag_assistant/app/ingest/discovery.py`
2. `rag_assistant/app/ingest/loaders.py`
3. `rag_assistant/app/ingest/ocr.py`

---

## 2) 구현 상세

### 2.1 파일 탐색 단계에서 이미지 확장자 허용

`SUPPORTED_EXTENSIONS`에 아래 확장자를 추가:
- `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tif`, `.tiff`

효과:
- `/ingest` 경로 탐색 시 이미지 파일도 수집 대상에 포함됨.

### 2.2 로더 단계에 이미지 파서 추가

`loaders.py`에 `_read_image(path)` 추가:
- `OCR_ENABLED=false`면 즉시 `ParseError`로 안내
  - 메시지: `이미지 OCR이 비활성화되어 있습니다. OCR_ENABLED=true로 설정하세요.`
- `OCR_ENABLED=true`면 OCR 경로로 텍스트 추출 시도

`parse_file()` 분기 추가:
- 이미지 확장자면 `_read_image()` 호출

### 2.3 OCR 유틸에 이미지 OCR 함수 추가

`ocr.py`에 `ocr_image(path, lang)` 추가:
- `pytesseract` + `Pillow`로 단일 이미지 OCR 수행
- 결과 텍스트를 `strip()` 후 반환

---

## 3) 테스트 수행 내역

### 3.1 discovery + loader 동작 테스트

테스트 방식:
- 임시 PNG 이미지 생성 후 로컬 함수 호출

확인 결과:
- `discover_files()`가 이미지 파일을 수집함 (`discover_has_image=True`)
- `OCR_ENABLED=false`일 때 이미지 파싱이 기대대로 안내 오류 반환
- `OCR_ENABLED=true`일 때 이미지 텍스트 추출 성공 확인
  - 예: `"ProjectRAG OCRimage test"` 추출

### 3.2 API 경로 테스트 (`/ingest`)

테스트 방식:
- FastAPI `TestClient` 사용
- `OCR_ENABLED=true` 상태에서 `POST /ingest` + `dry_run=true`

결과:
- status: `200`
- success: `True`
- data: `{'files_processed': 1, 'chunks_created': 1, ...}`

해석:
- 이미지 -> OCR -> 청킹 파이프라인이 실제 인제스트 경로에서 정상 동작함.

---

## 4) 운영 가이드 메모

이미지 인제스트를 실제 사용하려면:
1) `.env`에서 `OCR_ENABLED=true`
2) 시스템에 Tesseract 설치 및 PATH 등록
3) 필요 시 OCR 언어 설정
   - `OCR_LANG=kor+eng`

OCR 비활성 상태에서는 이미지 파일이 발견되더라도 파싱 스킵(경고 로그) 처리됨.

---

## 5) 후속 제안

1) 이미지 OCR 전처리(그레이스케일/이진화) 옵션 추가
2) 대용량 이미지 처리 시 해상도 리사이즈 옵션 추가
3) OCR 실패 원인(미설치/언어팩/파일손상) 상세 에러 코드화
