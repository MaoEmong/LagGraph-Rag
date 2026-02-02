# ask09.md — 작업일지 (상세)

- 날짜: 2026-01-28
- Phase: 6 (CLI Client)
- 목표:
  - CLI 명세(03CliSpec.md) 기반 명령어 구현
  - API 서버와 연동 확인
  - 테스트 수행

- 구현 내역:
  1) CLI 엔트리포인트
     - 파일: `cli/assistant.py`
     - argparse 기반 서브커맨드 구조 구현
     - 전역 옵션: --version, --json, --api-key

  2) 설정 파일 처리
     - 경로: `~/.rag_assistant/config.json`
     - load/save 함수 구현
     - 우선순위: RAG_API_URL env > config.json api_url > 기본값

  3) 명령어 구현
     - chat
       - POST /chat 호출
       - thread 기본값: config.default_thread 또는 "default"
     - ingest
       - POST /ingest 호출
       - 옵션: --recursive / --no-recursive, --dry-run
     - threads
       - GET /threads 호출
     - reset
       - POST /threads/reset 호출
       - --force 미지정 시 확인 프롬프트
     - stats
       - GET /health 호출
     - config
       - show/set/reset 구현

  4) 출력 포맷
     - --json 지정 시 원문 JSON 출력
     - 기본 모드: [AI] 답변, [Sources] 출력
     - 오류 시 [ERROR] + code/message 출력

- 의존성 변경:
  - `requirements.txt`에 requests 추가

- 테스트:
  A) CLI 옵션 위치 확인
     - 전역 옵션(--json)은 서브커맨드 앞에 위치해야 함
     - 잘못된 위치 사용 시 argparse 에러 발생 → 재실행으로 확인

  B) 통합 스모크 테스트 (uvicorn 8004)
     - `assistant --json stats` → /health 정상
     - `assistant --json ingest tmp_ingest_test.txt --no-recursive --dry-run` 정상
     - `assistant --json chat "테스트 문서 요약" --thread cli-test` 정상
     - `assistant --json threads` 목록 조회 정상
     - `assistant --json reset cli-test --force` 초기화 정상

  C) config 명령어
     - `assistant config show` → {} 확인
     - `assistant config set api_url http://localhost:8004` → OK
     - `assistant config show` → api_url 반영 확인
     - `assistant config reset` → OK

- 비고:
  - PowerShell 출력 인코딩으로 한글 응답이 깨져 보일 수 있음

- 다음 작업:
  - Phase7(품질/안정화) 준비 또는 추가 개선 항목 논의
