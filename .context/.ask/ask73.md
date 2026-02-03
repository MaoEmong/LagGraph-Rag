# ask73.md 작업일지 (상세)

- 날짜: 2026-02-03
- 작업 주제: DB 스모크 테스트 스크립트 추가 + 문서 반영 + 테스트
- 사용자 요청: 우선순위 1(실제 DB 연결 스모크 테스트) 진행

---

## 1) 목표

1. 실제 DB 연결 확인용 최소 스크립트 제공
2. 문서에 사용법 기록
3. 테스트 수행

---

## 2) 변경 파일 목록

### 2.1 신규 파일

1. `rag_assistant/scripts/db_smoke_test.py`
2. `.context/.ask/ask73.md`

### 2.2 수정 파일

1. `.context/08DbQuerySpec.md`

---

## 3) 구현 상세

### 3.1 스모크 스크립트

- 입력:
  - `--source` (테이블/뷰 이름)
  - `--limit` (행 제한)
  - `--adapter` (mysql/postgres/mock)
- 출력:
  - row_count, rows, schema, warning JSON

---

## 4) 문서 반영

- `08DbQuerySpec.md`에 스모크 테스트 실행 예시 추가

---

## 5) 테스트

```powershell
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall rag_assistant\app rag_assistant\scripts
```

결과: 정상 통과

