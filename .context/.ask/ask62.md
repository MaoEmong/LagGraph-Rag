# ask62.md 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: README에 프로젝트 구조 섹션 추가
- 사용자 요청: "프로젝트 구조도 정리해서 리드미에 넣어줘"

---

## 1) 변경 파일

1. `README.md`

---

## 2) 작업 목적

기존 README는 실행/운영 가이드는 충분했지만,
코드베이스 폴더 역할을 한눈에 파악하기 어려웠음.

따라서 프로젝트 루트부터 `rag_assistant` 내부까지
디렉토리 역할과 주요 파일을 트리 형태로 명시.

---

## 3) 반영 내용

README에 `## 프로젝트 구조` 섹션을 신설하고 아래 항목을 정리:

- 루트 파일:
  - `README.md`, `OPERATIONS.md`
- `.context`:
  - 설계문서(00~07)
  - `.ask` 작업일지
  - `.Mid_inspec` 중간 점검 문서
- `rag_assistant/app`:
  - `main.py`, `graph.py`, `routes/`, `ingest/`, `nodes/`, `storage/`
- `cli/assistant.py`, `scripts/`, `evals/`, `docs/`
- 로컬 전용 디렉토리:
  - `data/`, `logs/` (git ignore)
- 환경 파일:
  - `.env.example` (공유용)
  - `.env` (로컬 비밀키, git ignore)

---

## 4) 기대 효과

- 신규 참여자/미래 본인 기준으로 코드 위치 파악 시간 단축
- 커밋 전 “무엇이 코드고 무엇이 로컬 산출물인지” 경계가 명확해짐
- README 단독으로도 프로젝트 진입이 가능해짐
