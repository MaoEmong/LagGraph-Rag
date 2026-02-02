# ask46.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: batch runner 서버 로그 저장 기능 추가 + 실전 검증
- 목표:
  - 배치별 서버 stderr/stdout를 파일로 남겨 원인 분석 추적성 강화
  - 실제 평가 실행에서 로그 파일 생성/내용 검증

---

## 1) 변경 파일

1. `rag_assistant/scripts/e2e_eval_batch_runner.py`
2. `README.md`
3. `OPERATIONS.md`

---

## 2) 스크립트 기능 추가

### 2.1 신규 옵션

- `--server-log-dir <path>`
  - 지정 시 배치별 uvicorn stdout/stderr 로그를 파일로 저장
  - 미지정 시 기존처럼 DEVNULL로 버림

### 2.2 저장 형식

- 배치 출력 파일 stem 기준으로 생성:
  - `<stem>.server.stdout.log`
  - `<stem>.server.stderr.log`
- 예시:
  - `e2e_eval_batch_01_001_012.server.stderr.log`
  - `e2e_eval_batch_01_001_012.server.stdout.log`

### 2.3 구현 상세

- `_run_single_batch(...)`에 `server_log_dir` 인자 추가
- 파일 핸들 line-buffering으로 오픈 후 uvicorn subprocess에 연결
- 종료 시 핸들 안전하게 close
- 병합 결과 `meta`에 `server_log_dir` 기록

---

## 3) 테스트 수행

### 3.1 실행

- 명령:
  - `scripts/e2e_eval_batch_runner.py` 실행
  - 옵션: `--batch-size 12`, `--server-log-dir .\evals\results\server_logs`

### 3.2 결과

- 평가 결과:
  - `SUMMARY 36 36` (36케이스 모두 성공)
- 로그 생성 확인:
  - `LOG_COUNT 6` (3배치 × stdout/stderr)
  - 샘플 파일 head에 uvicorn startup 로그/요청 로그 확인

---

## 4) 문서 반영

### 4.1 README.md
- E2E 배치 실행 예시에 `--server-log-dir` 옵션 추가
- 산출물 목록에 배치별 서버 로그 파일 패턴 추가
- 실행 프리셋(전체 검증)에도 `--server-log-dir` 반영

### 4.2 OPERATIONS.md
- 배치 실행 예시에 `--server-log-dir` 반영
- 산출물 목록에 서버 로그 파일 패턴 추가
- 전체 검증/auto-port 예시에도 `--server-log-dir` 반영

---

## 5) 결론

- 배치 평가 시 서버 로그가 자동 보존되어,
  - 실패 케이스 재현 시 배치 단위 원인 분석이 가능해짐
- 기존 기능(배치 병합/auto-port/e2e 통과)과 충돌 없이 동작 확인

