# ask51.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: Web UI MVP 1차 구현(`/web`)
- 목표:
  - 기존 API 위에 즉시 사용 가능한 최소 웹 인터페이스 제공
  - 질문 입력/응답 확인/출처 확인/스레드 조회를 한 화면에서 수행

---

## 1) 변경 파일

1. `rag_assistant/app/routes/web.py` (신규)
2. `rag_assistant/app/main.py` (라우터 등록)

---

## 2) 구현 내용

### 2.1 라우트 추가
- `GET /web`
- 응답: `HTMLResponse`
- 용도: 브라우저에서 바로 사용할 수 있는 단일 페이지 UI 제공

### 2.2 UI 기능 범위(MVP)
- Thread ID 입력
- 저장된 threads 조회(`GET /threads`) + 선택 반영
- 질문 입력
- `/chat` 호출(`POST /chat`)
- 답변 표시
- citations 표시(source_path + chunk_id)
- 토큰/타이밍 일부 메타 표시(`tokens.total`, `timing.t_total_ms`)
- health 상태 텍스트 표시(`GET /health`)

### 2.3 UI 디자인 방향
- 단일 카드/2컬럼(반응형) 구조
- 배경 그라디언트 + 강조 색상 사용
- 가독성 우선의 폼/결과 영역 분리
- 모바일/데스크톱 모두 동작하도록 CSS 미디어쿼리 적용

### 2.4 서버 연결
- `app/main.py`에 `web_router` include 추가
- 기존 `/`, `/health`, `/chat`, `/ingest`, `/threads`와 충돌 없이 공존

---

## 3) 테스트 수행

테스트 서버:
- `uvicorn app.main:app --host 127.0.0.1 --port 8091`

검증 항목:
1) `GET /` 성공
2) `GET /health` 성공
3) `GET /web` 200 응답
4) `/web` HTML에 핵심 텍스트/호출 경로 포함 여부 확인
   - `"RAG Assistant Web MVP"` 포함
   - `"/chat"` 포함

검증 결과:
- 모든 항목 성공

---

## 4) 결론

- Web UI MVP 1차(단일 페이지) 구현 완료
- 기존 API를 그대로 활용하며, 브라우저에서 즉시 질의/응답/출처 확인 가능
- 다음 단계로는 UI 고도화(에러 상세, 스레드 생성/리셋 버튼, 응답 스트리밍) 확장이 가능

