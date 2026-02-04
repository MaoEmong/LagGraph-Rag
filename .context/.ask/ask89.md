# ask89.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: 재질의 조건 정교화 (문서/출처 기준 도입)
- 요청: “1번부터 처리” (재질의 조건 정교화)

---

## 1) 변경 내용

### 1.1 설정 추가
- 파일: `rag_assistant/app/config.py`
- 추가:
  - `requery_min_docs` (default: 2)
  - `requery_min_citations` (default: 1)

### 1.2 재질의 조건 개선
- 파일: `rag_assistant/app/nodes/requery.py`
- 변경:
  - 기존: 답변/출처 유무 기반 단순 판단
  - 개선: 아래 기준을 모두 만족할 때만 재질의 수행
    - citations 개수 < `requery_min_citations`
    - docs 개수 < `requery_min_docs`
    - 혹은 answer가 `no_context_message`인 경우
  - 답변이 있고 docs/citations가 기준 이상이면 재질의 차단

### 1.3 환경 변수 예시 추가
- 파일: `rag_assistant/.env.example`
- 추가:
  - `REQUERY_MIN_DOCS`
  - `REQUERY_MIN_CITATIONS`

### 1.4 문서 반영
- 파일: `.context/04GraphSpec.md`
  - requery 조건 설명 추가

---

## 2) 테스트

### 2.1 compileall 테스트
- 실행:
  - `D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall D:\ProjectRAG\rag_assistant\app`
- 확인된 출력(요약):
  - `app/config.py` 컴파일 성공
  - `app/nodes/requery.py` 컴파일 성공
- 판정 근거:
  - SyntaxError/ImportError 없이 종료 → 테스트 통과 처리

---

## 3) 비고

- 재질의 기준을 문서/출처 수로 강화하여 불필요한 재검색을 감소
- 추가로 “문서 수는 많지만 출처가 0”인 케이스는 재질의 대상 유지

---

## 4) 다음 작업

- 재질의 품질 검증(특정 케이스에서 재검색 여부 확인)
- 필요 시 requery 기준값 조정

