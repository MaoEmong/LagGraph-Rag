# ask47.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 배치 실패 자동 요약 리포트 추가 + 실패/성공 경로 검증
- 목표:
  - 배치 실행 실패 시 원인 추적 시간을 줄이기 위한 자동 요약 파일 생성
  - preflight 실패와 batch 실행 실패 모두에서 요약 리포트 생성 보장

---

## 1) 변경 파일

1. `rag_assistant/scripts/e2e_eval_batch_runner.py`
2. `README.md`
3. `OPERATIONS.md`

---

## 2) batch runner 기능 추가

### 2.1 신규 옵션

- `--failure-summary-path <json>`
  - 실패 발생 시 요약 리포트 저장 경로
- `--failure-tail-lines <N>`
  - 서버 stderr tail 추출 줄 수 (기본 20)

### 2.2 실패 요약 리포트 구조

- preflight 실패(예: cases 파일 없음):
  - `stage=preflight`
  - `message`, `meta` 포함

- batch 실행 실패:
  - `failed_batch` (실패 배치 메타)
  - `failed_batch_server_stderr_tail`
  - `completed_batches`
  - `meta`

### 2.3 내부 보강

- `_run_single_batch()`가 배치 실행 리포트(dict)를 반환하도록 변경
- eval subprocess 실패 시:
  - return code
  - eval stdout/stderr tail 수집
- preflight 단계 예외도 failure summary 파일로 저장하도록 보강

---

## 3) 테스트 수행

### 3.1 실패 경로 테스트 (preflight)

- 조건:
  - 존재하지 않는 cases 경로 입력
- 결과:
  - `failure_summary_test.json` 생성 확인
  - 내용 확인:
    - `stage=preflight`
    - 오류 메시지 포함

### 3.2 성공 경로 스모크 테스트

- 조건:
  - 3케이스 스모크 파일(`evals/e2e_eval_cases_smoke3.jsonl`) 생성 후 배치 실행
- 결과:
  - `SMOKE_OK 3 3` 확인
  - 병합 결과 정상 생성
  - meta에 `failure_summary_path` 반영 확인

---

## 4) 문서 반영

### 4.1 README.md
- 배치 실행 예시에:
  - `--failure-summary-path`
  - `--failure-tail-lines`
  추가
- 산출물 목록에 실패 요약 리포트 경로 추가

### 4.2 OPERATIONS.md
- 배치 실행 예시에 동일 옵션 추가
- 산출물 목록에 실패 요약 리포트 항목 추가

---

## 5) 결론

- 배치 실패 시 자동 요약 파일이 생성되어 즉시 원인 파악 가능
- preflight/실행 실패 모두 대응 가능
- 서버 로그 저장(`--server-log-dir`)과 결합 시 원인 추적성이 크게 개선됨

