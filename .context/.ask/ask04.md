# ask04.md — 작업일지

- 날짜: 2026-01-28
- Phase: 2 (Storage Layer)
- 작업 요약:
  - chromadb 설치 완료
  - 스토리지 모듈 스모크 테스트 실행
  - chromadb 예외 클래스 변경에 따른 수정: InvalidCollectionException -> NotFoundError
- 테스트 결과:
  - Docstore 저장 성공 (1건)
  - Checkpoint 저장/조회 성공
  - thread 목록 조회 성공
- 다음 작업:
  - Phase3(LangGraph Core) 착수
