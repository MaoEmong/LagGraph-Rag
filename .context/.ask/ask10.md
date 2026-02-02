# ask10.md — 작업일지 (상세)

- 날짜: 2026-01-28
- Phase: 7 (품질/안정화)
- 목표:
  - 로깅 시스템 추가
  - 타이밍 측정(timing) 기록
  - 토큰 사용량(tokens) 기록
  - 오류 메시지 정제 및 안정성 보완

- 구현 내역:
  1) 로깅 시스템
     - 파일: `app/logging_utils.py`
     - 처리:
       - 로그 디렉토리 생성
       - 파일 로그(`logs/app.log`) + 콘솔 로그 동시 출력
       - 기본 포맷: 시간/레벨/로거/메시지
     - 적용: `app/main.py`에서 setup_logging() 호출

  2) 타이밍 측정
     - 파일: `app/graph.py`
     - 처리:
       - 노드별 실행 시간 측정(t_route_ms, t_retrieve_ms, t_generate_ms, t_finalize_ms)
       - 전체 실행 시간 측정(t_total_ms)
       - response.data.timing에 반영

  3) 토큰 사용량 기록
     - 파일: `app/nodes/generate.py`
     - 처리:
       - OpenAI response.usage에서 prompt/completion/total 추출
       - response.data.tokens에 반영

  4) 오류 로깅 강화
     - 파일: `app/nodes/retrieve.py`, `app/nodes/generate.py`
     - 처리:
       - 임베딩/LLM 호출 실패 시 logger.exception 기록

  5) 인제스트 로그 보강
     - 파일: `app/ingest/ingest.py`
     - 처리:
       - 파싱 실패/빈 문서/청크 없음 로그
       - 인제스트 완료 시 요약 로그

  6) 응답 포맷 확장
     - 파일: `app/nodes/finalize.py`
     - 처리:
       - tokens, timing을 data에 포함

  7) 설정 스키마 확장
     - 파일: `app/schemas.py`
     - 처리:
       - State에 tokens 필드 추가

- 테스트:
  A) /health 확인
     - 결과: success=true

  B) /chat 테스트
     - 결과:
       - 응답 정상
       - tokens 포함 확인
       - timing 포함 확인 (t_total_ms 포함)

- 비고:
  - PowerShell 출력 인코딩으로 한글 응답이 깨져 보일 수 있음

- 다음 작업:
  - 추가 문서 정리 또는 사용자 요청 작업
