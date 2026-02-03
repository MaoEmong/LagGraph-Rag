# 09DbRoadmap.md — DB 연동 준비/추가 작업 정리 v1.0

> 목적: 추후 DB 연동 시 필요한 작업과 체크리스트를 정리한다.
> 기준 문서: 08DbQuerySpec.md, 02ApiSpec.md, 04GraphSpec.md
> 작성일: 2026-02-03

---

## 1. 현재 준비 상태(요약)

- DB 조회 추상화 구조(QuerySpec/QueryResult) 마련
- LangGraph에 db_plan/db_query 노드 포함
- MySQL 어댑터 구현 완료(SELECT 전용, 안전정책 적용)
- 스모크 테스트/SQL 단위 테스트 스크립트 준비

---

## 2. 실제 DB 연동 전 준비 작업

### 2.1 환경 변수 설정

`.env`에 다음 항목을 설정한다.

```
DB_ENABLED=true
DB_ADAPTER=mysql
DB_URL=mysql://user:pass@host:3306/dbname
DB_ROW_LIMIT=100
DB_TIMEOUT_SEC=5
DB_MAX_FILTERS=10
DB_MAX_JOINS=5
DB_MAX_GROUP_BY=5
DB_MAX_METRICS=5
DB_MAX_ORDER_BY=3
DB_MAX_SELECT=5
DB_DENYLIST_KEYWORDS=drop,delete,update,insert,alter,truncate
```

### 2.2 최소 스모크 테스트

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\db_smoke_test.py --source <table_name> --limit 5 --adapter mysql
```

### 2.3 SQL 변환 단위 테스트

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\db_sql_unit_test.py
```

---

## 3. 스키마/도메인 반영 작업

1. **스키마 힌트 제공**
   - LLM이 QuerySpec을 안정적으로 생성하도록 테이블/컬럼 힌트를 제공
2. **허용 테이블/컬럼 화이트리스트**
   - 도메인별 접근 가능한 테이블 제한
3. **표현식 제한**
   - select expr에 허용 함수 목록 설정(화이트리스트)

---

## 4. 보안/운영 체크리스트

1. 읽기 전용(SELECT only) 유지
2. row limit 강제 확인
3. timeout 설정 확인
4. denylist 키워드 검증
5. 접근 로그(옵션) 기록

---

## 5. 예상 추가 작업(우선순위)

1. 실제 DB 연결 테스트 환경 구축
2. QuerySpec 생성 품질 개선(스키마 힌트, 실패 케이스 보정)
3. 운영 로그/감사 로그 추가
4. DB 결과 캐시(옵션)

---

작성자: 김해준
버전: v1.0
