# ask71.md 작업일지 (상세)

- 날짜: 2026-02-03
- 작업 주제: DB 보안 정책 런타임 강화(denylist/복잡도 제한) + 문서/설정 반영
- 사용자 요청: “우선순위부터 진행”에 따라 1순위(보안 정책 강화) 수행

---

## 1) 목표

1. QuerySpec 실행 전 보안 정책을 런타임에 강제 적용
2. 복잡도 제한(필터/그룹/정렬/집계 개수 제한) 도입
3. 금지 키워드 기반 차단 추가
4. 문서와 설정 템플릿 갱신

---

## 2) 변경 파일 목록

### 2.1 수정 파일

1. `rag_assistant/app/config.py`
2. `rag_assistant/app/db/mysql_adapter.py`
3. `rag_assistant/.env.example`
4. `.context/08DbQuerySpec.md`
5. `.context/.ask/ask71.md`

---

## 3) 구현 상세

### 3.1 설정 추가

- `db_max_filters`
- `db_max_group_by`
- `db_max_metrics`
- `db_max_order_by`
- `db_denylist_keywords`

### 3.2 MySQL 어댑터 보안 강화

- QuerySpec 내 식별자에 금지 키워드 포함 시 차단
- filters/group_by/metrics/order_by 개수 제한 적용
- 모든 필드/테이블 이름은 검증 후 백틱 처리

---

## 4) 문서/설정 반영

- `08DbQuerySpec.md`에 런타임 정책 표 추가
- `.env.example`에 DB 보안 옵션 추가

---

## 5) 테스트

```powershell
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall rag_assistant\app
```

결과: 정상 통과

