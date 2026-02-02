# ask60.md 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 데이터 미삭제 정책 반영 (.gitignore 예외/제외 강화)
- 사용자 요청: "데이터를 지우진 말고 .gitignore에서 예외처리"

---

## 1) 작업 목적

실행 산출물(`data/logs/tmp/results`)은 로컬에 유지하되,
Git 커밋 대상에서는 제외하여 저장소를 깔끔하게 유지.

---

## 2) 변경 파일

1. `/.gitignore`

---

## 3) 변경 상세

기존 ignore 규칙을 아래처럼 강화:

- 런타임 데이터/로그
  - `rag_assistant/data/`
  - `rag_assistant/data/**`
  - `rag_assistant/logs/`
  - `rag_assistant/logs/**`
- 임시 파일/폴더
  - `rag_assistant/tmp_*`
  - `rag_assistant/tmp_*/**`
  - `rag_assistant/tmp_user_*/`
  - `rag_assistant/tmp_user_*/**`
- 평가 산출물
  - `rag_assistant/evals/results/`
  - `rag_assistant/evals/results/**`

의도:
- 파일 삭제 없이 로컬 보존
- 신규 생성 파일까지 재귀적으로 커밋 제외

---

## 4) 결론

- 데이터/결과물을 지우지 않고도 Git 추적 제외 정책을 반영 완료.
- 다음 단계에서 바로 커밋 준비(코드/문서 중심) 진행 가능.
