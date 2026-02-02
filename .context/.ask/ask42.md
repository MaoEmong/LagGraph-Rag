# ask42.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: README/OPERATIONS 배치 러너 사용법 반영 + 문서 커맨드 검증
- 목표:
  - 사용자가 바로 실행 가능한 운영 문서로 정리
  - 배치 평가 방식(권장 경로)을 문서에 명확히 반영
  - 문서에 적은 핵심 커맨드가 실제로 실행 가능한지 확인

---

## 1) 변경 파일

1. `README.md`
2. `OPERATIONS.md`

---

## 2) README.md 반영 내용

- 신규 섹션 추가: **E2E 평가 (배치 러너 권장)**
- 포함 내용:
  - `scripts/e2e_eval_batch_runner.py` 권장 이유
  - 실제 실행 커맨드 예시(Windows PowerShell)
  - 산출물 위치 안내
    - 배치별 결과: `evals/results/batches/*.json`
    - 병합 결과: `evals/results/e2e_eval_36cases_batchrunner.json`

---

## 3) OPERATIONS.md 정리/갱신

- 기존 문서 인코딩 깨짐(가독성 저하) 이슈가 있어 문서를 UTF-8 기준으로 재작성
- 버전 표기: v1.2
- 주요 구성:
  1) 서버 실행
  2) 헬스 체크
  3) 인제스트
  4) 채팅
  5) 리랭커 설정/스윕
  6) OCR 설정
  7) E2E 평가 실행
     - 단일 실행(`e2e_eval.py`)
     - 배치 실행+자동 병합(`e2e_eval_batch_runner.py`) 권장
  8) Windows 인코딩 운영 메모
  9) 로그 위치

---

## 4) 테스트(문서 반영 검증)

문서에 반영한 커맨드가 실제로 동작하는지 최소 실행 검증:

1) 스크립트 help 실행
- `scripts/e2e_eval_batch_runner.py --help` 성공
- `scripts/e2e_eval.py --help` 성공

2) 최신 병합 리포트 파싱 검증
- 파일: `evals/results/e2e_eval_36cases_batchrunner_v2.json`
- 파싱 결과:
  - `total_cases=36`
  - `success_count=36`
  - `keyword_pass_count=36`
  - `citation_pass_count=36`

검증 출력:
- `REPORT_OK 36 36 36 36`

---

## 5) 결론

- README/OPERATIONS 모두 배치 러너 중심 운영 흐름으로 반영 완료
- 문서 커맨드 실행 가능성(최소 핵심 경로) 검증 완료
- 현재 기준으로 신규 사용자도 문서만 보고 평가를 재현할 수 있는 상태

