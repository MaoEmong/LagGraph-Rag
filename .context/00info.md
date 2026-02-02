# 00Info.md — 개인용 AI 비서 RAG 시스템 설계서 v1.0

> 목적: LangGraph 기반 RAG 시스템을 개인 AI 비서 용도로 구축하기 위한 **기술 설계서(Technical Specification)**

---

## 1. 개요

### 1.1 목적

* 개인 문서 기반 질의응답 AI 비서 구축
* CLI 우선 개발 → Web 클라이언트 확장 가능 구조
* 단일 사용자, 단일 서버 환경 가정
* 단순성, 유지보수성, 재현성을 최우선 설계 원칙으로 채택

### 1.2 범위

* 질의응답 파이프라인
* 문서 인제스트 파이프라인
* 저장소 구조(Vector DB / Docstore / Checkpoint)
* API 및 CLI 인터페이스

---

## 2. 기술 스택

| 구분               | 기술                  |
| ---------------- | ------------------- |
| Language         | Python 3.11+        |
| API Server       | FastAPI             |
| Orchestration    | LangGraph           |
| LLM Provider     | OpenAI              |
| Vector DB        | Chroma (Persistent) |
| Docstore         | SQLite              |
| State Checkpoint | SQLite              |
| Client (MVP)     | CLI                 |
| Client (Target)  | Web                 |

---

## 3. 시스템 아키텍처

### 3.1 논리 구조

```
[ CLI Client ]
      |
      v
[ FastAPI Server ]
      |
      v
[ LangGraph Runtime ]
   |        |        |
   v        v        v
Retriever  LLM   Checkpoint(SQLite)
   |
   v
Chroma(VectorDB) + Docstore(SQLite)
```

### 3.2 역할 정의

| 컴포넌트       | 책임                   |
| ---------- | -------------------- |
| CLI Client | 사용자 입력/출력            |
| FastAPI    | 요청 라우팅, 인증(옵션), 로깅   |
| LangGraph  | RAG 파이프라인 제어 및 상태 관리 |
| Retriever  | 벡터 검색                |
| LLM        | 응답 생성                |
| Chroma     | 임베딩 벡터 저장 및 검색       |
| Docstore   | 원문 및 메타데이터 저장        |
| Checkpoint | thread 상태 저장         |

---

## 4. LLM 설계

### 4.1 모델 정책

| 용도          | 모델          |
| ----------- | ----------- |
| 기본 질의응답     | gpt-4o-mini |
| 고품질 답변 / 요약 | gpt-4.1     |

### 4.2 비용 절감 전략

* retrieval 미사용 시 context 최소화
* max_tokens 제한 적용
* 대화 히스토리 요약 노드 도입 예정
* temperature: 0.2 ~ 0.5

---

## 5. Vector DB 설계 (Chroma)

### 5.1 저장 방식

* Persistent Directory Mode
* 저장 경로: `./data/chroma`

### 5.2 Collection 정의

| 항목              | 값         |
| --------------- | --------- |
| collection_name | documents |
| distance_metric | cosine    |

### 5.3 Metadata Schema

필수:

* source_path
* file_type
* parent_id
* created_at

선택:

* project
* topic
* tags
* importance

### 5.4 검색 파라미터

* top_k = 5 (기본)
* score_threshold = optional

---

## 6. Chunking 정책

| 항목         | 값                |
| ---------- | ---------------- |
| chunk_size | 500 ~ 800 tokens |
| overlap    | 100 tokens       |
| 분리 기준      | 문단 우선, 코드 블록 별도  |

---

## 7. Docstore 설계 (SQLite)

### 7.1 테이블: documents

| 컬럼          | 타입        |
| ----------- | --------- |
| chunk_id    | TEXT (PK) |
| parent_id   | TEXT      |
| content     | TEXT      |
| source_path | TEXT      |
| file_type   | TEXT      |
| created_at  | DATETIME  |

---

## 8. Checkpoint 설계 (LangGraph)

### 8.1 테이블: checkpoints

| 컬럼          | 타입       |
| ----------- | -------- |
| thread_id   | TEXT     |
| graph_state | JSON     |
| updated_at  | DATETIME |

### 8.2 메모리 전략

* thread_id 기반 상태 저장
* 20턴 초과 시 자동 요약
* 요약 결과는 state에 유지
* 원본 메시지는 checkpoint 보존

---

## 9. LangGraph 그래프 설계 (MVP)

### 9.1 State Schema

| 필드              | 타입   | 설명     |
| --------------- | ---- | ------ |
| question        | str  | 사용자 질문 |
| thread_id       | str  | 세션 ID  |
| retrieval_query | str  | 검색용 쿼리 |
| docs            | list | 검색 결과  |
| answer          | str  | 최종 응답  |
| attempt         | int  | 재시도 횟수 |

### 9.2 Node 목록

| Node     | 기능          |
| -------- | ----------- |
| route    | 검색 필요 여부 판단 |
| retrieve | Chroma 검색   |
| generate | LLM 응답 생성   |
| finalize | 응답 포맷       |

### 9.3 Graph Flow

```
question → route
   ├─ no  → generate → finalize
   └─ yes → retrieve → generate → finalize
```

---

## 10. API 설계

### 10.1 Endpoints

| Method | Path    | 설명      |
| ------ | ------- | ------- |
| POST   | /chat   | 질의 처리   |
| POST   | /ingest | 문서 인제스트 |
| GET    | /health | 상태 체크   |

### 10.2 /chat Request

```json
{
  "thread_id": "default",
  "question": "문서 구조 설명"
}
```

---

## 11. CLI 설계

### 11.1 명령어

| Command                 | 설명        |
| ----------------------- | --------- |
| assistant chat          | 대화 시작     |
| assistant ingest <path> | 문서 추가     |
| assistant threads       | thread 목록 |
| assistant clear         | 상태 초기화    |
| assistant stats         | 시스템 정보    |

---

## 12. 오류 처리 정책

| 상황           | 처리           |
| ------------ | ------------ |
| Vector DB 오류 | fallback 메시지 |
| LLM API 실패   | 최대 2회 재시도    |
| Ingest 실패    | 로그 기록        |
| 문서 파싱 실패     | skip + 로그    |

---

## 13. 환경 변수

```
OPENAI_API_KEY
CHROMA_PATH=./data/chroma
DOCSTORE_PATH=./data/docstore.sqlite
CHECKPOINT_PATH=./data/checkpoints.sqlite
LOG_PATH=./logs
```

---

## 14. 프로젝트 구조

```
rag_assistant/
  app/
    main.py
    graph.py
    nodes/
      route.py
      retrieve.py
      generate.py
      finalize.py
    ingest/
      ingest.py
      loaders.py
      chunking.py
    storage/
      vector_db.py
      docstore.py
      checkpoint.py
    schemas.py
    config.py

  cli/
    assistant.py

  data/
    chroma/
    docstore.sqlite
    checkpoints.sqlite

  logs/
  docker-compose.yml
  00.Info.md
```

---

## 15. 구현 우선순위

1. FastAPI 기본 서버
2. CLI Client
3. LangGraph MVP 그래프
4. Chroma 연동
5. 문서 인제스트 파이프라인
6. Docstore 구현
7. Checkpoint 연동

---

## 16. 결정/잔여 항목

결정 완료:

* [x] embedding 모델: OpenAI `text-embedding-3-small`
* [x] thread 관리: 단일 thread 우선
* [x] chunk size: 500~800 tokens 유지
* [x] reranker: 기본 미도입 (필요 시 on)
* [x] web UI: 단순 SPA

잔여 논의:

* [ ] 토큰 기반 청킹 전환 여부
* [ ] reranker 조건부 활성화 전략

---

작성자: 김해준
작성일: 2026-01-29
버전: v1.1
