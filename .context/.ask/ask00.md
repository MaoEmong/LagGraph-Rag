# ask00.md — 작업일지

- 날짜: 2026-01-28
- Phase: 1 (Project Bootstrap)
- 작업 요약:
  - 문서(00~06) 확인 완료
  - 프로젝트 기본 구조 생성: rag_assistant/app
  - FastAPI /health 엔드포인트 구현
  - 환경설정 파일 생성: app/config.py, .env
  - requirements.txt 생성
- 이슈:
  - Python 미설치로 venv 생성 실패 ("Python was not found")
- 다음 작업:
  - Python 3.11+ 설치 후 `python -m venv .venv` 재시도
  - 서버 실행 확인 (uvicorn)
