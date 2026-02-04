# ask82.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: 하이브리드 검색(FTS5) 도입 1차 + 스펙 반영
- 기준: 11QualityRagPlan.md (Phase B)

---

## 1) 변경 내용

### 1.1 Docstore FTS5 저장/검색 추가
- 파일: `rag_assistant/app/storage/docstore.py`
- 변경:
  - `documents_fts`(FTS5) 테이블 생성
  - `save_chunks()`에서 FTS 인덱스 저장 추가
  - `delete_chunks_by_source_path()`에서 FTS 삭제 연동
  - `search_fts(query, limit)` 추가

### 1.2 하이브리드 검색 로직 추가
- 파일: `rag_assistant/app/nodes/retrieve.py`
- 변경:
  - Dense 검색: 기존 Chroma 유지
  - Sparse 검색: FTS5 기반 `Docstore.search_fts`
  - 결과 병합: rank-based score 합산으로 `hybrid_score` 산정
  - `sparse_score`/`hybrid_score` 메타 포함

### 1.3 스키마/설정 확장
- 파일: `rag_assistant/app/schemas.py`
  - Document에 `sparse_score`, `hybrid_score` 추가
- 파일: `rag_assistant/app/config.py`
  - `sparse_enabled`, `sparse_top_k` 추가

### 1.4 문서 반영
- 파일: `.context/05IngestionSpec.md`
  - FTS5 저장 단계(4.9) 추가
- 파일: `.context/04GraphSpec.md`
  - retrieve 단계 하이브리드 검색 반영

---

## 2) 테스트

- 실행:
  - `D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall D:\ProjectRAG\rag_assistant\app`
- 결과: 정상 통과

---

## 3) 다음 작업

- Phase C: Hybrid 결과 기반 Parent 확장 설계/구현
- 필요 시 FTS 쿼리 전처리(특수문자 처리) 보강

