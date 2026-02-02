# 02ApiSpec.md — RAG AI 비서 API 명세서 v1.1

> 기준 문서: `00Info.md`, `01Architecture.md`

---

## 1. 개요

본 문서는 개인용 AI 비서 RAG 시스템의 **HTTP API 명세**를 정의한다.

대상:

* CLI Client
* 향후 Web Client

목표:

* API 계약을 고정하여 서버/클라이언트 구현 분리
* Codex CLI 및 자동 코드 생성에 사용 가능한 명확한 스펙 제공

---

## 2. 공통 사항

### 2.1 Base URL

```
http://localhost:8000
```

### 2.2 Content-Type

```
application/json
```

### 2.3 인증 (Optional)

현재 MVP에서는 미사용. 구조만 유지.

```
Authorization: Bearer <API_KEY>
```

### 2.4 공통 응답 포맷

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

### 2.5 공통 에러 포맷

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

---

## 3. API 목록

| Method | Path           | 설명           |
| ------ | -------------- | ------------ |
| POST   | /chat          | 질의응답         |
| POST   | /ingest        | 문서 인제스트      |
| GET    | /health        | 서버 상태 확인     |
| GET    | /threads       | thread 목록 조회 |
| POST   | /threads/reset | thread 초기화   |

---

## 4. POST /chat

### 4.1 설명

사용자 질문을 받아 LangGraph RAG 파이프라인을 실행하고 답변을 반환한다.

### 4.2 Request

```json
{
  "thread_id": "default",
  "question": "이 프로젝트 구조 설명해줘"
}
```

| 필드        | 타입     | 필수 | 설명     |
| --------- | ------ | -- | ------ |
| thread_id | string | O  | 세션 ID  |
| question  | string | O  | 사용자 질문 |

### 4.3 Response (성공)

```json
{
  "success": true,
  "data": {
    "thread_id": "default",
    "answer": "...",
    "citations": [
      {
        "source_path": "/docs/architecture.md",
        "chunk_id": "abc123"
      }
    ],
    "tokens": {
      "prompt": 320,
      "completion": 180,
      "total": 500
    },
    "timing": {
      "t_route_ms": 2,
      "t_retrieve_ms": 95,
      "t_generate_ms": 420,
      "t_finalize_ms": 1,
      "t_total_ms": 520
    }
  },
  "error": null
}
```

추가 필드(옵션):

* tokens: OpenAI 사용량(프롬프트/완료/총합)
* timing: 노드별/전체 처리 시간(ms)

### 4.4 Response (실패)

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "LLM_ERROR",
    "message": "OpenAI API timeout"
  }
}
```

### 4.5 에러 코드

| 코드              | 설명        |
| --------------- | --------- |
| INVALID_REQUEST | 입력 검증 실패  |
| LLM_ERROR       | LLM 호출 실패 |
| VECTOR_DB_ERROR | 벡터 검색 실패  |
| INTERNAL_ERROR  | 내부 서버 오류  |

---

## 5. POST /ingest

### 5.1 설명

로컬 파일 또는 디렉토리를 RAG 데이터 소스로 등록한다.

### 5.2 Request

```json
{
  "path": "./docs",
  "recursive": true,
  "dry_run": false
}
```

| 필드        | 타입      | 필수 | 설명                          |
| --------- | ------- | -- | --------------------------- |
| path      | string  | O  | 인제스트 대상 경로                  |
| recursive | boolean | X  | 하위 폴더 포함 여부 (default: true) |
| dry_run   | boolean | X  | 저장 없이 테스트 실행 (default: false) |

### 5.3 Response

```json
{
  "success": true,
  "data": {
    "files_processed": 12,
    "chunks_created": 248,
    "duration_ms": 5230
  },
  "error": null
}
```

### 5.4 에러 코드

| 코드              | 설명        |
| --------------- | --------- |
| PATH_NOT_FOUND  | 경로 없음     |
| PARSE_ERROR     | 문서 파싱 실패  |
| EMBEDDING_ERROR | 임베딩 생성 실패 |
| STORAGE_ERROR   | 저장 실패     |

---

## 6. GET /health

### 6.1 설명

서버 상태 확인

### 6.2 Response

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "vector_db": "ok",
    "docstore": "ok",
    "llm": "ok"
  },
  "error": null
}
```

---

## 7. GET /threads

### 7.1 설명

존재하는 thread 목록 반환

### 7.2 Response

```json
{
  "success": true,
  "data": {
    "threads": [
      "default",
      "project-a",
      "research"
    ]
  },
  "error": null
}
```

---

## 8. POST /threads/reset

### 8.1 설명

특정 thread의 상태 초기화

### 8.2 Request

```json
{
  "thread_id": "default"
}
```

### 8.3 Response

```json
{
  "success": true,
  "data": {
    "thread_id": "default",
    "reset": true
  },
  "error": null
}
```

---

## 9. HTTP 상태 코드 규칙

| 코드  | 의미     |
| --- | ------ |
| 200 | 성공     |
| 400 | 잘못된 요청 |
| 401 | 인증 실패  |
| 404 | 리소스 없음 |
| 500 | 서버 오류  |

---

## 10. 버전 관리

* API 버전: v1
* 변경 시 URL prefix 또는 header 기반 버전 관리 고려

---

작성자: 김해준
작성일: 2026-01-29
버전: v1.1
