# ask66.md 작업일지 (상세)

- 날짜: 2026-02-03
- 작업 주제: DB 조회 추상화 스켈레톤 추가 + 그래프 통합 + 테스트 수행
- 사용자 요청: DB가 아직 없어도 동작 가능한 추상 구조로 RAG에서 DB 조회 처리 가능하도록 설계/구현

---

## 1) 목표

1. DB 종류/스키마에 종속되지 않는 추상 인터페이스 제공
2. 실제 DB 미연결 상태에서도 그래프 흐름과 응답 포맷을 고정
3. 추후 DB 연결 시 어댑터 교체만으로 확장 가능하게 구성
4. 작업 완료 후 테스트 수행

---

## 2) 변경 파일 목록

### 2.1 신규 파일

1. `rag_assistant/app/db/__init__.py`
2. `rag_assistant/app/db/adapter.py`
3. `rag_assistant/app/db/mock_adapter.py`
4. `rag_assistant/app/db/registry.py`
5. `rag_assistant/app/nodes/db_plan.py`
6. `rag_assistant/app/nodes/db_query.py`
7. `.context/.ask/ask66.md`

### 2.2 수정 파일

1. `rag_assistant/app/config.py`
2. `rag_assistant/app/schemas.py`
3. `rag_assistant/app/nodes/route.py`
4. `rag_assistant/app/nodes/retrieve.py`
5. `rag_assistant/app/nodes/generate.py`
6. `rag_assistant/app/graph.py`
7. `.context/08DbQuerySpec.md`

---

## 3) 구현 상세

### 3.1 DB 추상화 레이어

- `DbQueryAdapter` 프로토콜 정의
  - 입력: `QuerySpec`
  - 출력: `QueryResult`
- 기본 어댑터: `MockDbAdapter`
  - 실제 DB 없이 샘플 데이터 반환
  - 테스트/개발용 기본값
- `registry.py`로 어댑터 선택 구조 제공

### 3.2 스키마 확장

`schemas.py`에 다음 구조 추가:

- `QuerySpec` (중립 쿼리 사양)
  - `intent`, `source`, `filters`, `group_by`, `metrics`, `order_by`, `limit`
- `QueryResult` (중립 결과 포맷)
  - `rows`, `schema`, `row_count`, `warning`
- `DbError`

State 확장 필드:

- `db_needed`
- `db_query_spec`
- `db_result`
- `db_error`

### 3.3 Graph 흐름 변경

기존:

```
route → retrieve → generate → finalize
```

변경:

```
route → retrieve → db_plan → db_query → generate → finalize
```

### 3.4 Route 판단 확장

DB 관련 키워드 감지 시 `db_needed = True` 설정:

- "db", "database", "데이터베이스", "sql", "쿼리", "query", "테이블", "조회", "통계"

또한 `settings.db_enabled`가 `True`일 때만 활성화되도록 제어.

### 3.5 Generate 컨텍스트 확장

- `db_result`가 존재할 경우, LLM 프롬프트에 `DB 결과` 섹션 추가
- 문서 컨텍스트와 병합 시 순서를 명확히 유지

---

## 4) 문서 수정 내용

`08DbQuerySpec.md`의 QuerySpec 예시 필드를 `from` → `source`로 통일하여
코드 스키마와 일치하도록 정리.

---

## 5) 테스트

### 5.1 수행 명령

```powershell
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall rag_assistant\app
```

### 5.2 결과

- compileall 정상 완료
- SyntaxError/ImportError 없음 확인

---

## 6) 후속 작업 후보

1. DB 어댑터 실제 구현(PostgreSQL/MySQL/SQLite 등)
2. QuerySpec 생성기(LLM 기반 db_plan) 고도화
3. DB 결과 응답에 포함 여부(API 스펙 확정)
4. 보안 정책(읽기 전용, row limit, denylist) 런타임 반영

