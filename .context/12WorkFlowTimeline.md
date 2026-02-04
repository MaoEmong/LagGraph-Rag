# 12WorkFlowTimeline.md — 작업 진행 흐름 다이어그램 v1.0

> 목적: ProjectRAG의 시작부터 현재까지 진행된 작업 흐름을 다이어그램 형태로 정리한다.
> 기준: .context 문서 및 .ask 작업일지 누적 기록
> 작성일: 2026-02-04

---

## 1. 전체 흐름 다이어그램(요약)

```mermaid
flowchart TD
  A[프로젝트 부트스트랩] --> B[Storage Layer]
  B --> C[LangGraph Core]
  C --> D[API Layer]
  D --> E[Ingestion Pipeline]
  E --> F[CLI Client]
  F --> G[품질/안정화]
  G --> H[평가/운영 자동화]
  H --> I[DB 추상화/확장]
  I --> J[하이브리드 검색 고도화]
  J --> K[재질의/근거 기반 강화]
  K --> L[통합 E2E/분석 게이트]
```

---

## 2. 단계별 주요 작업 흐름(상세)

```mermaid
flowchart LR
  P1_1[Bootstrap FastAPI health]
  P1_2[Bootstrap config env requirements]
  P2_1[Storage Chroma VectorDB]
  P2_2[Storage Docstore SQLite]
  P2_3[Storage Checkpoint SQLite]
  P3_1[Graph State schema]
  P3_2[Graph route retrieve generate finalize]
  P3_3[Graph timing tokens]
  P4_1[API chat endpoint]
  P4_2[API ingest endpoint]
  P4_3[API threads list reset]
  P5_1[Ingest discovery parse clean chunk]
  P5_2[Ingest token chunking]
  P5_3[Ingest OCR support]
  P5_4[Ingest dedupe skip and reingest]
  P6_1[Client CLI commands]
  P6_2[Client Web UI]
  P7_1[Quality reranker auto]
  P7_2[Quality logging metrics]
  P8_1[Eval E2E eval]
  P8_2[Eval batch runner]
  P8_3[Eval soak runner]
  P8_4[Eval analyzer alert gate]
  P9_1[DB QuerySpec QueryResult]
  P9_2[DB db_plan db_query]
  P9_3[DB MySQL adapter]
  P10_1[RAG Hybrid Retrieval]
  P10_2[RAG Parent Expand]
  P10_3[RAG Local Cross Encoder]
  P10_4[RAG Grounded Answer]
  P10_5[RAG Requery]

  P1_1 --> P1_2 --> P2_1 --> P2_2 --> P2_3 --> P3_1 --> P3_2 --> P3_3
  P3_3 --> P4_1 --> P4_2 --> P4_3 --> P5_1 --> P5_2 --> P5_3 --> P5_4
  P5_4 --> P6_1 --> P6_2 --> P7_1 --> P7_2 --> P8_1 --> P8_2 --> P8_3 --> P8_4
  P8_4 --> P9_1 --> P9_2 --> P9_3 --> P10_1 --> P10_2 --> P10_3 --> P10_4 --> P10_5
```

### 2.1 단계별 세부 작업 포인트

- Bootstrap: FastAPI 서버/health, 설정 로딩, requirements 정리
- Storage: Chroma 컬렉션 생성, Docstore/Checkpoint 스키마 구축
- Graph: State 정의, route/retrieve/generate/finalize 구성, timing/tokens 기록
- API: chat/ingest/threads/reset 엔드포인트 구현
- Ingest: 탐색/파싱/클리닝/토큰 청킹, OCR, 중복 스킵 정책
- Client: CLI 명령어 세트, Web UI MVP
- Quality: reranker auto, 로깅/메트릭
- Eval: E2E eval, batch runner, soak runner, analyzer gate
- DB: QuerySpec/QueryResult, db_plan/db_query, MySQL adapter
- RAG+: Hybrid(Chroma+FTS5), Parent Expand, Local Reranker, Grounded Answer, Re-query

### 2.2 Phase별 미세 단계 + 산출물

```mermaid
flowchart TD
  subgraph Phase1[Phase1 Bootstrap]
    P1A[프로젝트 구조 생성]
    P1B[requirements.txt 작성]
    P1C[config/.env 로딩]
    P1D[FastAPI /health 구현]
    P1E[산출물 app main py and app config py]
  end

  subgraph Phase2[Phase2 Storage]
    P2A[Chroma 초기화/collection]
    P2B[Docstore 스키마]
    P2C[Checkpoint 스키마]
    P2D[산출물 storage vector db py docstore py checkpoint py]
  end

  subgraph Phase3[Phase3 LangGraph]
    P3A[State 스키마 정의]
    P3B[route/retrieve/generate/finalize]
    P3C[checkpoint 연동]
    P3D[타이밍/토큰 기록]
    P3E[산출물 app graph py app nodes]
  end

  subgraph Phase4[Phase4 API]
    P4A[chat endpoint]
    P4B[ingest endpoint]
    P4C[threads list reset]
    P4D[공통 응답 포맷]
    P4E[산출물 app routes]
  end

  subgraph Phase5[Phase5 Ingestion]
    P5A[discovery/parse/clean]
    P5B[token chunking]
    P5C[OCR 지원]
    P5D[중복 스킵/재저장]
    P5E[산출물 app ingest]
  end

  subgraph Phase6[Phase6 Client]
    P6A[CLI commands]
    P6B[Web UI /web]
    P6C[산출물 cli assistant py routes web py]
  end

  subgraph Phase7[Phase7 Quality]
    P7A[reranker auto]
    P7B[logging/metrics]
    P7C[산출물 logging utils py nodes]
  end

  subgraph Phase8[Phase8 Eval Ops]
    P8A[E2E eval 스크립트]
    P8B[batch runner]
    P8C[soak runner]
    P8D[analyzer/alerts]
    P8E[산출물 scripts e2e]
  end

  subgraph Phase9[Phase9 DB 확장]
    P9A[QuerySpec/QueryResult]
    P9B[db_plan/db_query]
    P9C[MySQL adapter]
    P9D[산출물 app db]
  end

  subgraph Phase10[Phase10 RAG 고도화]
    P10A[Hybrid Retrieval]
    P10B[Parent Expand]
    P10C[Local Cross-Encoder]
    P10D[Grounded Answer]
    P10E[Re-query]
    P10F[산출물 retrieve requery generate]
  end

  Phase1 --> Phase2 --> Phase3 --> Phase4 --> Phase5 --> Phase6 --> Phase7 --> Phase8 --> Phase9 --> Phase10
```

---

## 3. 최근 품질 고도화 흐름(상세)

```mermaid
flowchart TD
  Q1[Hybrid Retrieval Chroma SQLite FTS5] --> Q2[Parent Expand parent id 청크 확장]
  Q2 --> Q3[Local Reranker Cross Encoder]
  Q3 --> Q4[Grounded Answer 근거 없으면 제한]
  Q4 --> Q5[Requery 근거 부족 시 재검색]
  Q5 --> Q6[통합 E2E 50케이스]
  Q6 --> Q7[Analyzer Gate]
```

---

작성자: 김해준
버전: v1.0
