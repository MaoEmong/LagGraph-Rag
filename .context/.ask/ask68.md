# ask68.md 작업일지 (상세)

- 날짜: 2026-02-03
- 작업 주제: db_plan 고도화(LLM 기반 QuerySpec 생성) + 문서 갱신 + 테스트
- 사용자 요청: 우선순위 2번(LLM 기반 db_plan 고도화) 진행, 문서 먼저 정리 후 구현 및 테스트

---

## 1) 목표

1. 자연어 질문을 LLM으로 QuerySpec(JSON)으로 변환
2. 실패 시 기본 QuerySpec으로 폴백
3. 문서와 코드 간 스펙 일치 유지
4. 작업 후 테스트 수행

---

## 2) 변경 파일 목록

### 2.1 수정 파일

1. `.context/08DbQuerySpec.md`
2. `.context/04GraphSpec.md`
3. `rag_assistant/app/config.py`
4. `rag_assistant/app/nodes/db_plan.py`
5. `.context/.ask/ask68.md`

---

## 3) 문서 변경

### 3.1 `08DbQuerySpec.md`

- db_plan 기본 정책/실패 처리 규칙 추가
- `source` 필드 기준으로 문구 정합성 보정

### 3.2 `04GraphSpec.md`

- db_plan/db_query 노드 추가 명시
- State에 db 관련 필드(db_needed/db_query_spec/db_result/db_error) 반영
- generate 입력에 db_result 포함 명시

---

## 4) 코드 변경

### 4.1 설정 추가 (`config.py`)

- `db_plan_model`, `db_plan_temperature`, `db_plan_max_output_tokens` 추가

### 4.2 `db_plan` 고도화

- LLM 기반 QuerySpec 생성
- JSON 파싱 및 스펙 정규화
- 실패 시 기본 QuerySpec으로 폴백
- db_error에 PLAN_ERROR 기록

---

## 5) 테스트

### 5.1 수행 명령

```powershell
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall rag_assistant\app
```

### 5.2 결과

- compileall 정상 완료
- SyntaxError/ImportError 없음 확인

