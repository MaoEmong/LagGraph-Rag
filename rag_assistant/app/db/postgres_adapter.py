from __future__ import annotations

from typing import Any, Dict, List

from ..config import settings
from ..schemas import QueryResult, QuerySpec


class PostgresDbAdapter:
    name = "postgres"

    def run_query(self, query_spec: QuerySpec) -> QueryResult:
        if not settings.db_url:
            raise RuntimeError("DB_URL이 설정되지 않았습니다.")

        # 스켈레톤 단계에서는 실제 실행을 막는다.
        # 실제 구현 시 QuerySpec → SQL 변환 로직과 psycopg 연결을 추가한다.
        raise NotImplementedError("PostgreSQL 어댑터는 스켈레톤만 제공됩니다.")

    @staticmethod
    def _coerce_rows(rows: List[Dict[str, Any]]) -> QueryResult:
        return {
            "rows": rows,
            "schema": {},
            "row_count": len(rows),
            "warning": None,
        }
