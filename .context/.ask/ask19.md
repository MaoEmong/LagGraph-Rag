# ask19.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 문서 업데이트
- 목표:
  - 최근 변경 사항(라우팅 기본 retrieval, 중복 인제스트, 리랭커 기본값, API 응답 확장)을 문서에 반영

- 변경 문서:
  - .context/00info.md
    - 결정/잔여 항목 갱신(embedding, thread, chunk, reranker, web UI)
    - 버전 v1.1, 작성일 2026-01-29

  - .context/02ApiSpec.md
    - /chat 응답에 timing 추가
    - /ingest에 dry_run 추가
    - 버전 v1.1, 작성일 2026-01-29

  - .context/03CliSpec.md
    - Windows PowerShell 한글 출력 이슈 운영 메모 추가
    - 테스트 시 영어 응답 우회 안내 추가
    - 버전 v1.1, 작성일 2026-01-29

  - .context/04GraphSpec.md
    - State에 tokens 필드 추가
    - Document에 rerank_score 추가
    - route 기본 retrieval 동작 반영
    - retrieve 리랭커 동작 설명 추가
    - 버전 v1.1, 작성일 2026-01-29

  - .context/05IngestionSpec.md
    - ingest_files 테이블 및 해시 기반 중복 처리 정책 반영
    - 내용 변경 시 기존 문서/벡터 삭제 후 재저장 명시
    - 버전 v1.1, 작성일 2026-01-29

  - .context/07UnresolvedItems.md
    - 운영 메모/기본 설정/테스트 결과 반영 완료(v1.1)

- 다음 작업:
  - reranker 조건부 활성화 전략 문서화
  - 운영 가이드/README 추가(실행, 테스트, 인코딩 이슈 안내)
