# ask25.md — 작업일지 (요약)

- 날짜: 2026-01-29
- 작업 범위:
  - reranker 조건부 활성화(auto) 도입 및 문서 반영
  - 토큰 기반 청킹 전환 + tiktoken 설치/테스트
  - 문서 업데이트 및 운영 가이드/README 추가

- 주요 변경:
  1) reranker auto 모드
     - 설정: RERANKER_MODE=off|auto|always
     - 조건: 결과 수 부족 / score 없음 / best 거리 >= threshold
     - 관련 파일: rag_assistant/app/config.py, rag_assistant/app/nodes/retrieve.py
     - 문서 반영: README.md, OPERATIONS.md, .context/04GraphSpec.md, .context/07UnresolvedItems.md

  2) 토큰 기반 청킹
     - tiktoken 추가 및 토큰 청킹 적용
     - 관련 파일: rag_assistant/app/ingest/chunking.py, rag_assistant/app/ingest/ingest.py, rag_assistant/requirements.txt
     - 문서 반영: .context/05IngestionSpec.md

  3) 문서 정리
     - README.md, OPERATIONS.md 신규 작성
     - 설계/명세 문서 업데이트: .context/00info.md, 02ApiSpec.md, 03CliSpec.md, 04GraphSpec.md, 05IngestionSpec.md, 07UnresolvedItems.md

- 테스트 요약:
  - 토큰 청킹 E2E 테스트 성공 (영어 질문으로 응답 확인)
  - reranker auto 테스트 성공
  - 중복 인제스트 스킵 동작 확인
  - reranker on/off 비교에서 on이 지연 증가, 품질 개선 미미

- 이슈/메모:
  - PowerShell 한글 출력 깨짐 지속 → 테스트는 영어 질문으로 우회
  - .env BOM 문제 재발 → UTF-8 BOM 없는 형식으로 재저장 필요

- 다음 작업:
  - reranker auto 임계값 튜닝
  - Web UI MVP 착수
  - route 기본 retrieval 비용 최적화 여부 검토
