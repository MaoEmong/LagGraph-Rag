# ask83.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: Parent 확장(부모 청크 합치기) 1차 구현
- 기준: 11QualityRagPlan.md (Phase C)

---

## 1) 변경 내용

### 1.1 설정 추가
- 파일: `rag_assistant/app/config.py`
- 추가:
  - `parent_expand_enabled` (default: true)
  - `parent_expand_limit` (default: 8)

### 1.2 Docstore 조회 추가
- 파일: `rag_assistant/app/storage/docstore.py`
- 추가:
  - `get_chunks_by_parent_id(parent_id, limit)`

### 1.3 retrieve 단계 확장
- 파일: `rag_assistant/app/nodes/retrieve.py`
- 추가:
  - `_parent_expand(docs)` 구현
  - hybrid 결과(top_k) 이후 parent_id 기준 청크 확장
  - 중복 방지(seen set)

### 1.4 문서 반영
- 파일: `.context/04GraphSpec.md`
  - retrieve 파라미터에 parent_expand 설정 추가

---

## 2) 테스트

- 실행:
  - `D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall D:\ProjectRAG\rag_assistant\app`
- 결과: 정상 통과

---

## 3) 다음 작업

- Phase D: 로컬 리랭커(cross-encoder) 도입
- 필요 시 parent_expand 적용 범위/순서 튜닝

