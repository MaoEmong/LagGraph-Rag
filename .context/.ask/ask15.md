# ask15.md — 작업일지 (상세)

- 날짜: 2026-01-29
- Phase: 7 (품질/안정화) 후속
- 목표:
  - PowerShell 한글 출력 인코딩 문제 해결

- 변경 사항:
  - UTF-8 설정 스크립트 추가: rag_assistant/scripts/set-utf8.ps1

- 시도 및 결과:
  1) 스크립트 직접 실행
     - 실패: ExecutionPolicy로 인해 스크립트 로드 불가
  2) 인라인 UTF-8 설정 후 /chat 호출
     - 설정: chcp 65001, OutputEncoding/Console.OutputEncoding UTF-8, PYTHONUTF8=1
     - 결과: 응답 한글 여전히 깨짐

- 관찰:
  - FastAPI/JSON 응답은 UTF-8인데 콘솔 출력에서만 깨지는 것으로 보임
  - Windows PowerShell 5.1 환경일 경우 UTF-8 출력 문제가 지속될 수 있음

- 다음 작업 제안:
  - PowerShell 7(pwsh)에서 동일 스크립트/테스트 실행
  - 실행 정책 허용 후 스크립트 사용:
    - powershell -ExecutionPolicy Bypass -File .\scripts\set-utf8.ps1
    - 또는 Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  - Windows Terminal에서 UTF-8 코드 페이지/폰트 확인
