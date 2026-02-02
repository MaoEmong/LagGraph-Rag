# ask07.md — 작업일지

- 날짜: 2026-01-28
- Phase: 4 (API Layer)
- 목표:
  - API 명세(02ApiSpec.md) 기반 라우터 구성
  - 그래프 실행 및 체크포인트 저장 연결
  - 스모크 테스트로 동작 확인

- 변경 사항:
  - 라우터 추가
    - /chat: LangGraph 실행 + Checkpoint 저장
    - /ingest: Phase5 전 임시 stub 응답
    - /threads: Checkpoint 기반 목록 조회
    - /threads/reset: 특정 thread 삭제
  - 라우터 등록: FastAPI 앱에 include_router 적용

- 구현 파일:
  - app/routes/chat.py
    - ChatRequest 스키마 정의
    - run_graph 호출 후 response 반환
    - CheckpointStore.save_state 호출
  - app/routes/ingest.py
    - IngestRequest 스키마 정의
    - Stub 응답 포맷 반환
  - app/routes/threads.py
    - ResetRequest 스키마 정의
    - list_threads/reset_thread 구현
  - app/main.py
    - 라우터 3개 등록

- 테스트:
  - 서버 기동: uvicorn app.main:app --port 8001
  - GET /health: success=true 확인
  - POST /chat: success=true, answer 반환 확인
  - GET /threads: threads 목록에 default 포함 확인
  - POST /threads/reset: reset=true 확인

- 이슈:
  - PowerShell 출력에서 한글 응답이 깨져 보임(인코딩 이슈 추정)

- 다음 작업:
  - Phase5(Ingestion Pipeline) 착수
  - 인코딩 이슈가 지속되면 출력 인코딩 설정 점검
