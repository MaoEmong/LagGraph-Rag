# ask50.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 리포트 자동 경고 규칙(Threshold Alerts) + fail-on-alert 적용
- 목표:
  - 분석 리포트에서 임계치 미달/초과를 자동 판정
  - 자동화 파이프라인(CI/배치)에서 경고를 실패로 처리 가능한 exit code 제공

---

## 1) 변경 파일

1. `rag_assistant/scripts/e2e_report_analyzer.py`
2. `README.md`
3. `OPERATIONS.md`

---

## 2) analyzer 기능 확장

### 2.1 신규 임계치 옵션

- `--min-success-rate` (default 0.98)
- `--min-keyword-pass-rate` (default 0.98)
- `--min-citation-pass-rate` (default 0.98)
- `--max-p90-graph-ms` (default 4000)
- `--max-soak-drift-pct` (default 10)
- `--fail-on-alert` (경고 존재 시 exit code 2)

### 2.2 출력 확장

- 분석 결과 JSON에 추가:
  - `alerts`: 경고 목록
  - `alert_thresholds`: 적용된 임계치

### 2.3 경고 코드 예시

- `LOW_SUCCESS_RATE`
- `LOW_KEYWORD_PASS_RATE`
- `LOW_CITATION_PASS_RATE`
- `HIGH_GRAPH_P90_LATENCY`
- `HIGH_SOAK_DRIFT`

---

## 3) 테스트 수행

### 3.1 정상 임계치(경고 없음) 테스트

- 입력: `e2e_eval_36cases_batchrunner_v2.json`
- 조건:
  - `min_* = 0.95`, `max_p90_graph_ms = 5000`
- 결과:
  - alerts 없음
  - 정상 종료(code 0)

### 3.2 강제 경고(경고 있음) 테스트

- 입력: 동일
- 조건:
  - `max_p90_graph_ms = 1000` (의도적으로 엄격)
  - `--fail-on-alert`
- 결과:
  - alerts 1건 발생 (`HIGH_GRAPH_P90_LATENCY`)
  - analyzer exit code = `2` 확인

---

## 4) 문서 반영

### 4.1 README.md
- “리포트 분석(고도화)”에 자동 경고/실패 처리 예시 추가

### 4.2 OPERATIONS.md
- `11.3 자동 경고 규칙 + 실패 종료` 섹션 추가
- 임계치 예시, 실행 커맨드, 종료 코드 규칙(0/2) 명시

---

## 5) 결론

- 리포트 분석이 “보기용”에서 “게이트(품질 기준 통과/실패)” 역할까지 확장됨
- 이후 CI/야간 자동 실행에서 결과 기준 미달을 즉시 감지/차단 가능

