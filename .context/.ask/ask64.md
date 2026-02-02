# ask64.md 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: Git 초기화 + 커밋 단위 분리
- 사용자 요청: "좋아 진행하자"

---

## 1) 목적

Git 업로드 전, 저장소를 초기화하고 변경사항을 의미 단위별 커밋으로 분리.

---

## 2) 수행 내용

1) Git 저장소 초기화
- `git init` (프로젝트 루트: `D:\\ProjectRAG`)

2) 커밋 분리 전략 수립
- Commit 1: 핵심 코드/실행 스크립트
- Commit 2: 평가 데이터/샘플 문서
- Commit 3: 문서/설계서/작업일지

3) 실제 커밋 수행

### Commit 1
- 메시지: `feat: add core RAG app, CLI, and ops scripts`
- 포함:
  - `rag_assistant/app/**`
  - `rag_assistant/cli/**`
  - `rag_assistant/scripts/**`
  - `rag_assistant/requirements.txt`
  - `.gitignore`
  - `rag_assistant/.env.example`

### Commit 2
- 메시지: `test: add evaluation datasets and sample source docs`
- 포함:
  - `rag_assistant/evals/**` (results 제외, .gitignore 적용)
  - `rag_assistant/docs/**`
  - `rag_assistant/queries.txt`

### Commit 3
- 메시지: `docs: add project guides, architecture docs, and work logs`
- 포함:
  - `README.md`
  - `OPERATIONS.md`
  - `.context/**`

---

## 3) 검증 결과

- `git status --short` 결과 clean(추가 변경 없음) 확인.
- `.env`, `data`, `logs`, `tmp_*`, `evals/results`는 `.gitignore` 정책으로 추적 제외 유지.

---

## 4) 비고

- 기본 브랜치는 현재 `master`로 생성됨.
- 원격 푸시 전 필요 시 `main`으로 브랜치명 변경 가능:
  - `git branch -M main`
