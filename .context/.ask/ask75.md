# ask75.md 작업일지 (상세)

- 날짜: 2026-02-03
- 작업 주제: SQL 변환 확장(select expr) + QuerySpec 스키마 확장
- 사용자 요청: 우선순위에 따라 SQL 변환 확장 진행

---

## 1) 목표

1. QuerySpec에 select 표현식 지원 추가
2. MySQL 변환 로직에서 안전한 expr/alias 처리
3. 보안 정책과 정합성 유지
4. 테스트 수행

---

## 2) 변경 파일 목록

### 2.1 수정 파일

1. `.context/08DbQuerySpec.md`
2. `rag_assistant/app/schemas.py`
3. `rag_assistant/app/config.py`
4. `rag_assistant/app/nodes/db_plan.py`
5. `rag_assistant/app/db/mysql_adapter.py`
6. `rag_assistant/.env.example`
7. `.context/.ask/ask75.md`

---

## 3) 문서 변경

- QuerySpec에 `select` 필드 추가 및 정의
- 예시 JSON에 select 표현식 추가
- 런타임 정책 표에 `db_max_select` 추가

---

## 4) 코드 변경

### 4.1 스키마/설정 확장

- `QuerySpec.select` 추가
- `db_max_select` 추가

### 4.2 db_plan 확장

- LLM 출력 키에 `select` 추가
- 기본/정규화 로직에 `select` 포함

### 4.3 MySQL 어댑터 확장

- select 표현식 처리(`expr` + `alias`)
- expr 안전성 검사 및 alias 유효성 검증
- select 개수 제한 적용

---

## 5) 테스트

```powershell
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall rag_assistant\app
```

결과: 정상 통과

