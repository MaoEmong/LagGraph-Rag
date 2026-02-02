# ask53.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: Web UI MVP 확장(`/ingest` 실행 UI 추가)
- 목표:
  - `/web` 화면에서 문서 인제스트를 직접 실행 가능하게 개선
  - API 테스트/운영 흐름(질문+인제스트)을 단일 화면으로 통합

---

## 1) 변경 파일

1. `rag_assistant/app/routes/web.py`

---

## 2) UI 기능 추가 내용

### 2.1 신규 입력/옵션

- `Ingest Path` 입력
- `Recursive` 선택(true/false)
- `Dry Run` 선택(true/false)

### 2.2 신규 버튼

- `Run /ingest`
  - 클릭 시 `POST /ingest` 호출
  - 요청 body:
    - `path`
    - `recursive`
    - `dry_run`

### 2.3 결과 표시

- 상태 메시지(`ingestMsg`)
- 메타 정보(`ingestMeta`)
  - `files_processed`
  - `chunks_created`
  - `duration_ms`

### 2.4 JS 로직

- `runIngest()` 함수 추가
  - 입력값 검증(path 필수)
  - 호출 중 버튼 disable
  - 성공/실패 메시지 분기 처리

---

## 3) 테스트 수행

테스트 서버:
- `uvicorn app.main:app --host 127.0.0.1 --port 8093`

검증 항목:
1) `GET /web` 200
2) HTML에 신규 요소 포함
   - `Run /ingest`
   - `ingestPath`
3) 인제스트 API 연동 확인
   - `POST /ingest` with `dry_run=true`
   - 응답 `success=true` 확인

검증 결과:
- 모두 성공
- 출력:
  - `{'web_status': 200, 'ingest_success': True, 'files_processed': 0, 'chunks_created': 0}`

---

## 4) 결론

- Web UI MVP가 “질문/스레드 관리”에서 “인제스트 실행”까지 확장됨
- 이제 브라우저 기반으로 기본 운영 루프(인제스트 → 질문/응답)가 가능

