# ask55.md 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 서버 운영 표준화 1차 (`run_server.ps1`)
- 목표:
  - 수동 `uvicorn` 실행/중지 반복 대신, 단일 스크립트로 운영 절차 통일
  - 포트 점유/프로세스 확인/헬스 체크까지 자동화
  - 문서(README, OPERATIONS)에 동일한 운영 명령 반영

---

## 1) 변경 파일

1. `rag_assistant/scripts/run_server.ps1` (신규)
2. `README.md` (운영 스크립트 사용법 추가)
3. `OPERATIONS.md` (운영 스크립트 섹션 추가)

---

## 2) 구현 상세

### 2.1 run_server.ps1 설계

지원 액션:
- `status`: 포트 기준 실행 상태 확인
- `start`: 서버 시작 + `/health` 확인
- `stop`: 서버 중지
- `restart`: stop -> start

주요 파라미터:
- `-Action`: `start|stop|restart|status`
- `-BindHost`: 기본 `127.0.0.1`
- `-Port`: 기본 `8000`
- `-Reload`: `uvicorn --reload` 옵션

핵심 로직:
- 포트 점유 PID 확인 (`Get-NetTCPConnection`, 실패 시 `netstat` fallback)
- 프로세스 생존 확인
- 시작 시 PID 파일 저장 (`tmp_server_{port}.pid.txt`)
- 시작 후 `/health` 폴링으로 정상 기동 확인(최대 20초)
- 표준 출력/에러 로그 파일 분리
  - `tmp_server_{port}.stdout.log`
  - `tmp_server_{port}.stderr.log`

### 2.2 구현 중 발견/수정한 이슈

1) PowerShell 예약 변수 충돌
- 원인:
  - 파라미터명 `Host`가 PowerShell 내장 변수 `$Host`와 충돌
  - 변수/인자명 `pid/Pid`가 `$PID`와 충돌(대소문자 무시)
- 조치:
  - `Host` -> `BindHost`
  - `Pid` 관련 이름 -> `serverPid`, `ProcessId`로 전면 변경

2) 문서 반영
- `README.md` 빠른 시작 구간에 운영 스크립트 권장 실행 명령 추가
- `README.md` 하단에 "서버 운영 스크립트" 섹션 신설
- `OPERATIONS.md`에 스크립트 기반 상태/시작/중지/재시작 명령 추가

---

## 3) 테스트 수행

실행 위치:
- `D:\\ProjectRAG\\rag_assistant`

실행 명령:
- `powershell -ExecutionPolicy Bypass -File .\\scripts\\run_server.ps1 -Action status -Port 8000`
- `powershell -ExecutionPolicy Bypass -File .\\scripts\\run_server.ps1 -Action start -Port 8000 -Reload`
- `powershell -ExecutionPolicy Bypass -File .\\scripts\\run_server.ps1 -Action restart -Port 8000 -Reload`
- `powershell -ExecutionPolicy Bypass -File .\\scripts\\run_server.ps1 -Action stop -Port 8000`
- `Invoke-RestMethod -Method Get http://127.0.0.1:8000/health`

검증 결과:
- `status`: 중지/실행 상태 각각 정상 판별
- `start`: 서버 기동 후 포트 LISTEN 확인
- `restart`: 포트 재기동 후 PID 변경 확인
- `stop`: 서버 종료 확인
- `/health`: `success=true` 정상 응답 확인

---

## 4) 산출물 요약

- 운영 스크립트 1개로 서버 lifecycle 명령 통일
- 문서에 실행 명령 고정(팀/미래 작업 시 동일 절차 재사용 가능)
- 예약 변수 충돌 이슈를 스크립트 내부에서 예방한 안정 버전 확보

---

## 5) 후속 제안

1) `run_server.ps1`에 `-TailLogs` 옵션 추가(장애 시 즉시 로그 확인)
2) `-HealthTimeoutSec` 파라미터 외부화
3) CI/배치 러너에서도 공통으로 재사용할 수 있게 helper 스크립트화
