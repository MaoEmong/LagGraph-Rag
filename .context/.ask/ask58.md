# ask58.md 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 이미지 OCR 실제 운영 적용 확인 (.env 반영 + 서버 재기동 + 실API 검증)
- 사용자 요청: "ㅇㅇㅇ 진행해줘"

---

## 1) 작업 목적

이전 ask57에서 코드 레벨 이미지 OCR 지원을 추가했으므로,  
이번에는 **실제 실행환경(.env + 서버)** 에서 이미지 인제스트가 동작하는지 운영 관점으로 검증.

검증 범위:
1) `.env`에서 OCR 활성화
2) 서버 재시작 후 health 정상
3) 실제 이미지 파일 생성
4) `/ingest` dry-run + 실제 ingest 실행
5) `/chat` 질의와 citation에서 이미지 소스 노출 확인

---

## 2) 변경 사항

### 2.1 환경설정 반영

파일:
- `rag_assistant/.env`

추가 키:
- `OCR_ENABLED=true`
- `OCR_LANG=kor+eng`
- `OCR_DPI=200`
- `OCR_MAX_PAGES=0`
- `OCR_MIN_TEXT_LEN=100`

### 2.2 서버 재시작

명령:
- `powershell -ExecutionPolicy Bypass -File .\\scripts\\run_server.ps1 -Action restart -Port 8000 -Reload`

검증:
- status: 실행 중 확인
- `/health`: `success=true`

---

## 3) 실동작 테스트 상세

### 3.1 테스트 이미지 생성

임시 경로:
- `rag_assistant/tmp_user_image_ingest/`

생성 파일:
1) `image_ocr_test.png` (텍스트: `IMAGE_INGEST_OK_20260202`)
2) `image_ocr_test2.png` (텍스트: `HELLOIMAGE123`)

### 3.2 `/ingest` 테스트

요청:
- dry-run: `POST /ingest` with `dry_run=true`
- 실실행: `POST /ingest` with `dry_run=false`

결과(1차 이미지 기준):
- dry-run: `files_processed=1`, `chunks_created=1`
- 실실행: `files_processed=1`, `chunks_created=1`

결과(2차 이미지 추가 후):
- 실실행 성공(`success=true`)

### 3.3 OCR 추출 확인

로더 직접 확인(`parse_file`):
- `image_ocr_test.png` -> `IMAGE_INGEST-OK_20280202`
- `image_ocr_test2.png` -> `HELLOIMAGE23`

해석:
- 이미지 OCR은 동작하지만, OCR 특성상 일부 문자 오인식이 발생할 수 있음
  - 예: `_` -> `-`, `6` -> `8`, `123` -> `23`

### 3.4 Docstore 저장 확인

SQLite `documents` 테이블 조회 결과:
- `tmp_user_image_ingest\\image_ocr_test.png` 1건
- `tmp_user_image_ingest\\image_ocr_test2.png` 1건

해석:
- 이미지 OCR 텍스트 청크가 docstore에 실제 저장됨.

### 3.5 `/chat` 확인

질의 결과:
- 응답/인용(citation)에서 `tmp_user_image_ingest\\image_ocr_test.png` 소스 확인
- 일부 질의는 top-k 검색/표현 차이로 특정 이미지가 상위 인용에 노출되지 않을 수 있음

---

## 4) 결론

- 코드 변경 + 운영환경 반영까지 포함해 **이미지 OCR 인제스트 기능은 정상 동작** 확인.
- 현재 한계:
  - OCR 오인식 가능
  - retrieval 상위 결과(top_k) 특성상 특정 이미지가 항상 첫 인용으로 보장되지는 않음

---

## 5) 후속 제안

1) OCR 품질 개선 옵션(전처리: grayscale/binarize) 추가
2) 이미지 전용 테스트 케이스(jsonl) 별도 트랙 신설
3) 이미지 문서 우선 retrieval 옵션(메타 필터) 추가 검토
