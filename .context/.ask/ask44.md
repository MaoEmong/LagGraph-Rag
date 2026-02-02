# ask44.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 포트 충돌 대응 자동화(`--auto-port`) 구현 + 실전 검증
- 목표:
  - 배치 평가 실행 시 포트 충돌로 인한 실패를 자동 회피
  - 문서(README/OPERATIONS)에 대체 규칙 반영
  - 실제 충돌 상황에서 기능이 동작하는지 검증

---

## 1) 변경 파일

1. `rag_assistant/scripts/e2e_eval_batch_runner.py`
2. `README.md`
3. `OPERATIONS.md`

---

## 2) 스크립트 기능 추가

### 2.1 신규 옵션

- `--auto-port`
  - `--api-port`부터 시작해서 사용 가능한 포트를 자동 선택
- `--auto-port-max-tries` (기본 50)
  - 자동 포트 탐색 최대 시도 횟수
- `--port-step` (기본 1)
  - 탐색 시 포트 증가 간격

### 2.2 동작 반영

- 메타 정보 확장:
  - `api_port_requested`
  - `api_port_actual`
  - `auto_port`
  - `auto_port_max_tries`
  - `port_step`

### 2.3 버그 수정(중요)

- 1차 구현에서 점유 포트 판별이 부정확해 `8072` 점유 상황을 회피하지 못하는 문제 발견
- 원인:
  - 기존 `_is_port_available`의 bind 체크 방식이 점유 상태를 확실히 판별하지 못함
- 수정:
  - 먼저 `connect_ex`로 리스닝 여부 확인(성공 시 즉시 사용 불가)
  - 그 다음 bind 가능 여부 확인

---

## 3) 문서 반영

### 3.1 README.md
- 포트 충돌 대응 섹션 추가:
  - 충돌 시 `--auto-port` 사용 예시
  - 권장 포트 규칙(빠른검증 8073 / 전체검증 8074 / 충돌 시 auto-port)

### 3.2 OPERATIONS.md
- `7.4 포트 충돌 대응` 섹션 추가
- 증상 예시 + 자동 포트 선택 커맨드 포함

---

## 4) 테스트 수행

### 4.1 충돌 시뮬레이션

- `http.server`로 `127.0.0.1:8072`를 선점
- 배치러너 실행:
  - 요청 포트: `8072`
  - 옵션: `--auto-port`

### 4.2 결과

- 출력 확인:
  - `REQUESTED_PORT 8072`
  - `ACTUAL_PORT 8073`
  - `AUTO_PORT True`
- 평가 결과:
  - `SUCCESS 36 / 36`
  - `KEYWORD_PASS 36 / 36`
  - `CITATION_PASS 36 / 36`

즉, 실제 포트 충돌 상황에서 자동 회피 + 전체 평가 정상 완료 확인.

---

## 5) 결론

- 배치러너에 포트 충돌 대응 자동화가 적용됨
- 문서와 구현이 일치하며, 실전 충돌 테스트로 기능 검증 완료
- 현재 운영 기준:
  - 포트 충돌이 발생해도 `--auto-port`로 안정적으로 평가 실행 가능

