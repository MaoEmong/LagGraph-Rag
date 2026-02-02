# ask03.md — 작업일지

- 날짜: 2026-01-28
- Phase: 2 (Storage Layer)
- 작업 요약:
  - Chroma 래퍼 추가: `app/storage/vector_db.py`
  - Docstore(SQLite) 스키마 및 저장 로직 추가: `app/storage/docstore.py`
  - Checkpoint(SQLite) 스키마 및 저장/조회 로직 추가: `app/storage/checkpoint.py`
  - storage 패키지 초기화: `app/storage/__init__.py`
  - requirements.txt에 chromadb 추가
- 다음 작업:
  - Phase2 모듈 사용 위치 결정(그래프/라우터에서 주입)
  - 필요 시 마이그레이션/초기화 호출 지점 추가
