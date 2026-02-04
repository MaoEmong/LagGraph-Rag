# 11QualityRagPlan.md — 품질 최우선 RAG 개선 계획 v1.0

> 목적: LangGraph 기반 RAG 시스템을 **품질 최우선**으로 개선하기 위한 작업 계획을 정의한다.
> 전제: LLM/임베딩은 OpenAI 사용, 그 외 구성요소는 **비용 0(로컬/오픈소스)** 로 유지한다.
> 작성일: 2026-02-04

---

## 1. 배경 및 목표

- 질문/문서 유형은 혼합형이며, 속도보다 정확도를 우선한다.
- 기존 Dense 검색(Chroma+OpenAI 임베딩)만으로는 설명형/복합 질의에서 근거 밀도가 부족할 수 있다.
- 목표는 다음이다:
  1) 검색 커버리지 확대 (Dense + Sparse)
  2) 문맥 보강 (Parent 확장)
  3) 정답성 강화 (로컬 리랭커)
  4) 근거 기반 답변 강제 (프롬프트/검증)

---

## 2. 최종 목표 아키텍처(요약)

```
question
  → rewrite (검색용 쿼리 정제)
  → retrieve_dense (Chroma)
  → retrieve_sparse (SQLite FTS5)
  → merge/normalize (중복 제거/스코어 정규화)
  → parent_expand (parent_id 기준 컨텍스트 확장)
  → rerank (로컬 cross-encoder)
  → generate (근거 기반 답변)
  → finalize
```

---

## 3. 설계 결정

1) Sparse 검색: SQLite FTS5
- 의존성 최소, 로컬 비용 0
- 인제스트 시 문서 텍스트를 별도 FTS 테이블에 저장

2) Parent 확장: 청크 합치기 방식
- parent_id 기준으로 동일 문서 청크를 추가 수집
- 추가 테이블 없이 구현 가능

3) 리랭커: 로컬 Cross-Encoder
- GPU(3060) 활용
- 비용 0, 품질 향상 목적

4) OpenAI 사용 범위
- LLM 응답 생성
- Embedding 생성 (Dense 검색)

---

## 4. 작업 범위 및 단계

### Phase A: 설계/스펙 정리
- GraphSpec에 하이브리드 검색/리랭커 노드 반영
- IngestionSpec에 FTS 저장 단계 추가
- API/CLI 영향 여부 검토

### Phase B: Sparse 검색(FTS) 도입
- SQLite FTS5 테이블 신설 (docstore 내 또는 별도 db)
- 인제스트 시 FTS 테이블에 청크 텍스트 저장
- 검색 노드에서 FTS 쿼리 실행

### Phase C: Hybrid Merge + Parent Expand
- Dense + Sparse 결과 병합/중복 제거
- parent_id 기준으로 관련 청크 확장
- top_k/확장 개수 제한 적용

### Phase D: 로컬 리랭커
- cross-encoder 기반 rerank
- 모델/배치 크기/임계값 설정

### Phase E: Answer 품질 강화
- 근거 기반 답변 프롬프트 강화
- 근거 부족 시 명시적으로 모른다고 응답

---

## 5. 테스트 원칙

- 모든 작업 단계마다 테스트 수행
- 테스트 실패 시 다음 단계로 진행하지 않음

### 기본 테스트 세트
1) compileall
2) /health
3) /ingest (dry_run 포함)
4) /chat (retrieval/출처 확인)
5) E2E 배치 평가 (단축 또는 전체)

---

## 6. 산출물

- 문서 업데이트: GraphSpec, IngestionSpec, WorkPlan(필요시)
- 코드 변경: ingest, retrieve, storage, graph
- 테스트 결과: E2E 리포트/분석 결과(필요시)

---

작성자: 김해준
버전: v1.0
