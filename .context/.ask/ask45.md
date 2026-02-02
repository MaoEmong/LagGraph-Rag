# ask45.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 서버 끊김 이슈(장시간 `/chat` 연속 호출) 원인 분석
- 목표:
  - 기존에 간헐적으로 발생하던 `ConnectionResetError(10054)` / `WinError 10061`의 원인 범위를 축소
  - 앱 코드 문제인지, 실행 하네스(프로세스 실행 방식) 문제인지 구분

---

## 1) 사전 로그 점검

- 대상:
  - `rag_assistant/logs/app.log`
  - `rag_assistant/tmp_uvicorn_stdout.txt`
  - `rag_assistant/tmp_uvicorn_stderr.txt`

- 관찰:
  - 실패 구간 전후로 Python traceback/CRITICAL 로그 없음
  - `app.graph - graph completed` 로그가 정상적으로 지속되는 구간 다수 확인
  - 즉, 앱 레벨 예외로 즉시 종료된 패턴은 로그상 뚜렷하지 않음

---

## 2) 리소스 누수 가설 검증

- 방법:
  - uvicorn 단일 서버 실행
  - `/chat` 40회 연속 호출
  - 요청마다 프로세스 상태(생존/핸들/메모리) 수집

- 결과:
  - 40/40 성공
  - 프로세스 생존 지속
  - 핸들/메모리 수치 급증 패턴 없음(누수 징후 미관측)

- 결론:
  - 단기 연속 부하에서 명확한 리소스 누수로 인한 크래시는 재현되지 않음

---

## 3) 실행 하네스 비교 검증

### 3.1 재현이 잘 되던 방식
- PowerShell에서 ad-hoc `Start-Process`로 서버 띄우고 같은 블록에서 평가 실행
- 이 방식에서 간헐적으로 중간 끊김 발생

### 3.2 통제된 방식
- `scripts/e2e_eval_batch_runner.py`로 서버 프로세스 lifecycle을 Python에서 관리
- 동일 36케이스를 **단일 배치(batch-size=36)**로 실행해 검증

- 결과:
  - `success_count=36/36`
  - `keyword_pass=36/36`
  - `citation_pass=36/36`
  - 실패 0건

---

## 4) 분석 결론

- 현재까지의 증거 기준:
  - **애플리케이션 로직(노드/그래프/스토리지) 자체가 직접 크래시를 유발한다는 근거는 부족**
  - 끊김 이슈는 **실행 하네스/프로세스 관리 방식(PowerShell ad-hoc Start-Process 흐름)**에서 발생했을 가능성이 높음

- 실무 대응:
  - 장시간 평가는 `e2e_eval_batch_runner.py`를 표준 실행 경로로 사용
  - 필요 시 `--auto-port`로 포트 충돌까지 자동 회피

---

## 5) 다음 액션 제안

1. 끊김이 재발하는 특정 실행 명령을 고정해 최소 재현 스크립트 확보
2. batch runner에 서버 stderr 파일 분리 저장 옵션 추가(배치별 원인 추적 강화)
3. 원하면 로컬 장시간 soak test(예: 100~200 케이스)를 nightly 성격으로 자동화

