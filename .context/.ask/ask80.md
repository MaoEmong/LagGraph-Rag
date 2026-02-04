# ask80.md 작업일지 (상세)

- 날짜: 2026-02-03
- 작업 주제: LLM 모델 fallback 적용(응답/DB 계획)
- 사용자 요청: 현재 모델 유지 + 차단 시 대체 모델로 자동 전환

---

## 1) 목표

1. 기본 LLM 실패 시 fallback 모델 순차 시도
2. DB 계획(db_plan)에서도 동일 fallback 적용
3. 환경 변수 템플릿 반영
4. 테스트 수행

---

## 2) 변경 파일 목록

### 2.1 수정 파일

1. `rag_assistant/app/config.py`
2. `rag_assistant/app/nodes/generate.py`
3. `rag_assistant/app/nodes/db_plan.py`
4. `rag_assistant/.env.example`
5. `.context/08DbQuerySpec.md`
6. `.context/.ask/ask80.md`

---

## 3) 구현 상세

### 3.1 설정 추가

- `llm_model_fallbacks`
- `db_plan_model_fallbacks`

### 3.2 generate fallback

- `llm_model` 실패 시 `llm_model_fallbacks` 순차 시도
- 실패 시 마지막 오류를 반환

### 3.3 db_plan fallback

- `db_plan_model` 실패 시 `db_plan_model_fallbacks` 순차 시도
- 실패 시 기본 QuerySpec 폴백 유지

---

## 4) 문서/설정 반영

- `.env.example`에 fallback 옵션 추가
- `08DbQuerySpec.md`에 db_plan fallback 정책 추가

---

## 5) 테스트

```powershell
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall rag_assistant\app
```

결과: 정상 통과

