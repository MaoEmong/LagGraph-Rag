# 08DbQuerySpec.md — DB 조회 확장(추상화) 설계서 v1.0

> 목적: RAG가 외부 DB 조회를 수행할 수 있도록 **DB 종류/스키마에 종속되지 않는 추상 구조**를 정의한다.
> 기준 문서: 00Info.md, 01Architecture.md, 04GraphSpec.md
> 작성일: 2026-02-03

---

## 1. 개요

현재 시스템은 문서 기반 RAG에 최적화되어 있으나,
실제 운영 환경에서는 DB 조회가 필요한 질문이 자주 발생한다.

본 문서는 **실제 DB 미연결 상태**에서도 구조를 먼저 고정할 수 있도록,
다음 목표에 맞춘 **추상 설계**를 제시한다.

### 1.1 목표

1. DB 종류(PostgreSQL/MySQL/SQLite/REST 등)에 종속되지 않는 인터페이스 제공
2. 스키마 미확정 상태에서도 흐름/응답 포맷을 고정
3. 추후 실제 DB 연결 시 어댑터만 교체하도록 설계
4. 안전성 보장(읽기 전용, 제한, 차단 규칙 포함)

---

## 2. 설계 원칙

1. **어댑터 패턴**
   - DB 종류별 구현을 분리하고, 공통 인터페이스만 유지한다.
2. **중립 QuerySpec**
   - 자연어 → SQL 직접 변환 대신, **중립 사양(JSON)**을 거쳐 변환한다.
3. **정책 기반 안전장치**
   - 읽기 전용(SELECT), row limit, timeout, 차단 키워드 등 필수.
4. **확장 가능성**
   - DB가 아닌 REST/CSV/GraphQL도 동일 인터페이스로 연결 가능.

---

## 3. 전체 흐름(추상)

```
question
   ↓
route (db 필요 여부 판단)
   ↓ (필요 시)
db_plan (자연어 → QuerySpec)
   ↓
db_query (Adapter 실행)
   ↓
generate (문서 + DB 결과 컨텍스트)
   ↓
finalize
```

---

## 4. 상태(State) 확장

LangGraph State에 다음 필드를 추가한다.

| 필드          | 타입   | 설명 |
| ------------- | ------ | ---- |
| db_needed     | bool   | DB 조회 필요 여부 |
| db_query_spec | dict   | 중립 QuerySpec(JSON) |
| db_result     | dict   | QueryResult(JSON) |
| db_error      | dict   | DB 관련 오류(옵션) |

---

## 5. QuerySpec (중립 쿼리 사양)

DB 종류에 상관없이 표현 가능한 최소 단위의 쿼리 사양.

```json
{
  "intent": "월별 매출 합계",
  "source": "sales",
  "filters": [
    {"field": "date", "op": ">=", "value": "2025-01-01"}
  ],
  "joins": [
    {"type": "left", "source": "customers", "on": "sales.customer_id = customers.id"}
  ],
  "group_by": ["month"],
  "metrics": [
    {"field": "revenue", "agg": "sum"}
  ],
  "select": [
    {"expr": "DATE_FORMAT(sales.date, '%Y-%m')", "alias": "month"}
  ],
  "having": [
    {"field": "sum_revenue", "op": ">", "value": 1000000}
  ],
  "order_by": [{"field": "month", "direction": "asc"}],
  "limit": 100
}
```

### 5.1 필드 정의

| 필드     | 타입 | 설명 |
| -------- | ---- | ---- |
| intent   | str  | 사용자 의도 요약 |
| source   | str  | 논리적 대상(테이블/뷰/엔드포인트 명칭) |
| filters  | list | 필터 조건 목록 |
| joins    | list | 조인 목록(옵션) |
| group_by | list | 그룹 기준 |
| metrics  | list | 집계 대상 |
| select   | list | 파생/표현식 기반 선택 필드(옵션) |
| having   | list | 집계 필터(옵션) |
| order_by | list | 정렬 기준 |
| limit    | int  | 최대 행 수 |

### 5.2 연산자(op) 허용 목록

```
=, !=, >, >=, <, <=, in, not_in, like, between
```

### 5.3 joins 필드 정의

| 필드   | 타입 | 설명 |
| ------ | ---- | ---- |
| type   | str  | inner/left/right 중 하나 |
| source | str  | 조인 대상 테이블 |
| on     | str  | 조인 조건(간단한 필드 비교 문자열) |

### 5.4 having 필드 정의

filters와 동일한 구조를 사용하되, 집계 결과에 적용된다.

### 5.5 select 필드 정의

| 필드  | 타입 | 설명 |
| ----- | ---- | ---- |
| expr  | str  | SELECT 표현식(제한된 함수/문법) |
| alias | str  | 결과 컬럼 별칭 |

---

## 6. QueryResult (중립 결과 포맷)

모든 어댑터는 아래 포맷으로 결과를 반환한다.

```json
{
  "rows": [
    {"month": "2025-01", "revenue": 1200000}
  ],
  "schema": {
    "month": "text",
    "revenue": "number"
  },
  "row_count": 1,
  "warning": null
}
```

### 6.1 필드 정의

| 필드      | 타입 | 설명 |
| --------- | ---- | ---- |
| rows      | list | 결과 행 목록 |
| schema    | dict | 컬럼 타입 정보 |
| row_count | int  | 반환 행 수 |
| warning   | str  | 경고 메시지(옵션) |

---

## 6.2 스키마 타입 매핑(권장)

DB 드라이버의 컬럼 타입 정보를 가능한 한 보존하여, 응답 `schema`에 반영한다.

권장 매핑(예시):

| DB 타입 | schema 값 |
| --- | --- |
| INT, BIGINT | number |
| DECIMAL, NUMERIC, FLOAT, DOUBLE | number |
| DATE, DATETIME, TIMESTAMP | datetime |
| CHAR, VARCHAR, TEXT | text |
| BOOL, BOOLEAN | boolean |
| JSON | json |

## 7. 어댑터 인터페이스

### 7.1 공통 인터페이스

```
run_query(query_spec: dict) -> QueryResult
```

### 7.2 어댑터 예시

| 어댑터 이름 | 역할 |
| ---------- | ---- |
| mock_adapter | 실제 DB 없이 고정된 샘플 결과 반환 |
| postgres_adapter | QuerySpec → SQL 변환 후 PostgreSQL 실행 |
| mysql_adapter | QuerySpec → SQL 변환 후 MySQL 실행 |
| sqlite_adapter | QuerySpec → SQL 변환 후 SQLite 실행 |
| rest_adapter | QuerySpec → REST 요청 변환 |

---

## 7.3 실제 DB 어댑터 스켈레톤 가이드

### 7.3.1 공통 규칙

1. 환경 변수 또는 설정에서 연결 문자열을 읽는다.
2. 쿼리 실행은 **읽기 전용**으로 제한한다.
3. `limit`을 강제 적용한다(기본 100, 최대 1000).
4. 예외 발생 시 `DB_ERROR`로 래핑한다.

### 7.3.2 PostgreSQL 어댑터(스켈레톤)

- 연결 문자열: `DB_URL`
- 런타임 의존성: `psycopg` 또는 `psycopg2` (추후 결정)
- 현재 단계에서는 **구조만 제공**하고 실제 실행은 향후 구현한다.

### 7.3.3 MySQL 어댑터(구현)

- 연결 문자열: `DB_URL` (예: `mysql://user:pass@host:3306/dbname`)
- 런타임 의존성: `pymysql`
- QuerySpec → SELECT SQL 변환 후 실행
- 필드/연산자 화이트리스트 기반으로 안전성 확보

## 8. 안전 정책(필수)

1. **읽기 전용**
   - SELECT 외 쿼리는 금지
2. **행 수 제한**
   - QuerySpec.limit 기본 100, 최대 1000
3. **타임아웃**
   - 기본 5~10초
4. **금지 키워드**
   - drop, delete, update, insert, alter 등 차단
5. **PII 차단(선택)**
   - 주민번호/전화번호/이메일 등 패턴 필터링

### 8.1 런타임 정책(권장 기본값)

| 항목 | 기본값 | 설명 |
| --- | --- | --- |
| db_max_filters | 10 | 필터 개수 제한 |
| db_max_joins | 5 | 조인 개수 제한 |
| db_max_group_by | 5 | group_by 개수 제한 |
| db_max_metrics | 5 | metrics 개수 제한 |
| db_max_order_by | 3 | order_by 개수 제한 |
| db_max_select | 5 | select 표현식 개수 제한 |
| db_denylist_keywords | drop, delete, update, insert, alter, truncate | 식별자 내 금지 키워드 |

---

## 9. 프롬프트 설계 가이드

LLM이 QuerySpec을 생성할 때 아래 원칙을 적용한다.

1. 스키마가 없으면 `source`를 추정하지 말고 빈 값으로 둔다.
2. 모호하면 `filters`를 비워 두고 질문을 되묻게 한다.
3. 집계 필요 시 `metrics`를 명확히 지정한다.

### 9.1 DB 계획(db_plan) 기본 정책

1. 출력은 **JSON 단일 객체**로 제한한다.
2. `limit`은 기본 100, 최대 1000을 넘지 않는다.
3. 금지 연산(삭제/수정/스키마 변경)은 포함하지 않는다.
4. `source`가 불명확하면 빈 문자열로 둔다.
5. 주 모델 실패 시 fallback 모델로 재시도한다.

### 9.2 계획 실패 시 처리

* LLM 실패/JSON 파싱 실패 시:
  * `QuerySpec.intent`에 질문 원문만 넣고 나머지는 빈 값
  * `db_error.code = PLAN_ERROR` 기록
  * 그래프는 계속 진행(가능한 최소 결과 제공)

---

## 10. 에러 처리 규칙

| 상황 | 처리 |
| ---- | ---- |
| QuerySpec 생성 실패 | db_error.code = PLAN_ERROR |
| 어댑터 실행 실패 | db_error.code = DB_ERROR |
| 결과 없음 | rows 빈 배열로 반환 |
| 제한 초과 | warning에 기록 |

---

## 11. 단계별 구현 가이드 (요약)

1. `QuerySpec`, `QueryResult` 스키마 추가
2. `db_query` 노드 생성
3. `mock_adapter` 기본 구현
4. `generate`에서 db_result를 컨텍스트에 합치기
5. 실 DB 연결 시 어댑터 교체

---

## 12. 향후 확장

* 질의 템플릿 라이브러리 추가
* 사용 패턴 기반 캐시
* DB 스키마 자동 인덱싱
* 감사 로그(누가 어떤 쿼리를 언제 실행했는지)

---

## 13. 스모크 테스트(권장)

실제 DB 연결을 검증하기 위한 최소 스크립트:

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\db_smoke_test.py --source <table_name> --limit 5 --adapter mysql
```

---

## 14. SQL 변환 단위 테스트(권장)

DB 없이 QuerySpec → SQL 변환을 검증하는 최소 스크립트:

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\db_sql_unit_test.py
```

---

작성자: 김해준
버전: v1.0
