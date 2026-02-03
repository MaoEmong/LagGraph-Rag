from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence, Tuple
from urllib.parse import urlparse

import pymysql
from pymysql.cursors import DictCursor

from ..config import settings
from ..schemas import QueryResult, QuerySpec

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_ALLOWED_OPS = {"=", "!=", ">", ">=", "<", "<=", "in", "not_in", "like", "between"}
_ALLOWED_JOIN_TYPES = {"inner", "left", "right"}


class MySqlDbAdapter:
    name = "mysql"

    def run_query(self, query_spec: QuerySpec) -> QueryResult:
        if not settings.db_url:
            raise RuntimeError("DB_URL이 설정되지 않았습니다.")

        sql, params = self._build_sql(query_spec)

        connect_timeout = max(1, int(settings.db_timeout_sec))
        read_timeout = max(1, int(settings.db_timeout_sec))

        conn_info = self._parse_db_url(settings.db_url)
        conn = pymysql.connect(
            host=conn_info["host"],
            user=conn_info["user"],
            password=conn_info["password"],
            database=conn_info["database"],
            port=conn_info["port"],
            cursorclass=DictCursor,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            write_timeout=read_timeout,
            charset="utf8mb4",
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
        finally:
            conn.close()

        return self._build_result(rows, cursor_description=getattr(cursor, "description", None))

    def _build_sql(self, query_spec: QuerySpec) -> Tuple[str, Sequence[Any]]:
        source = (query_spec.get("source") or "").strip()
        if not source or not self._is_valid_identifier(source):
            raise ValueError("QuerySpec.source가 유효하지 않습니다.")
        self._denylist_check(source)

        select_parts: List[str] = []
        params: List[Any] = []

        metrics = list(query_spec.get("metrics") or [])
        group_by = list(query_spec.get("group_by") or [])
        order_by = list(query_spec.get("order_by") or [])
        filters = list(query_spec.get("filters") or [])
        joins = list(query_spec.get("joins") or [])
        having = list(query_spec.get("having") or [])
        select_exprs = list(query_spec.get("select") or [])

        self._enforce_limits(metrics, group_by, order_by, filters, joins, select_exprs)

        if metrics:
            for metric in metrics:
                field = str(metric.get("field") or "").strip()
                agg = str(metric.get("agg") or "").strip().lower()
                if not self._is_valid_identifier(field):
                    raise ValueError(f"metric field가 유효하지 않습니다: {field}")
                self._denylist_check(field)
                if agg not in {"sum", "avg", "min", "max", "count"}:
                    raise ValueError(f"지원하지 않는 집계 함수입니다: {agg}")
                alias = f"{agg}_{field}"
                select_parts.append(f"{agg.upper()}({self._quote_identifier(field)}) AS `{alias}`")
        elif group_by:
            for field in group_by:
                field_name = str(field).strip()
                if not self._is_valid_identifier(field_name):
                    raise ValueError(f"group_by field가 유효하지 않습니다: {field_name}")
                self._denylist_check(field_name)
                select_parts.append(self._quote_identifier(field_name))
        else:
            select_parts.append("*")

        if select_exprs:
            select_parts.extend(self._build_select_exprs(select_exprs))

        selected_fields = set()
        for part in select_parts:
            if part.startswith("`") and part.endswith("`"):
                selected_fields.add(part.strip("`"))

        if metrics and group_by:
            for field in group_by:
                field_name = str(field).strip()
                if not self._is_valid_identifier(field_name):
                    raise ValueError(f"group_by field가 유효하지 않습니다: {field_name}")
                self._denylist_check(field_name)
                if field_name not in selected_fields:
                    select_parts.append(self._quote_identifier(field_name))
                    selected_fields.add(field_name)

        sql = f"SELECT {', '.join(select_parts)} FROM {self._quote_identifier(source)}"
        join_sql = self._build_joins(joins)
        if join_sql:
            sql += f" {join_sql}"

        where_sql, where_params = self._build_filters(filters)
        if where_sql:
            sql += f" WHERE {where_sql}"
            params.extend(where_params)

        if group_by:
            group_fields = [self._quote_identifier(str(field).strip()) for field in group_by]
            sql += f" GROUP BY {', '.join(group_fields)}"

        having_sql, having_params = self._build_filters(having, allow_agg=True)
        if having_sql:
            sql += f" HAVING {having_sql}"
            params.extend(having_params)

        if order_by:
            order_parts: List[str] = []
            for entry in order_by:
                field = str(entry.get("field") or "").strip()
                direction = str(entry.get("direction") or "asc").strip().lower()
                if not self._is_valid_identifier(field):
                    raise ValueError(f"order_by field가 유효하지 않습니다: {field}")
                self._denylist_check(field)
                if direction not in {"asc", "desc"}:
                    raise ValueError(f"order_by 방향이 유효하지 않습니다: {direction}")
                order_parts.append(f"{self._quote_identifier(field)} {direction.upper()}")
            if order_parts:
                sql += f" ORDER BY {', '.join(order_parts)}"

        limit = int(query_spec.get("limit") or settings.db_row_limit or 100)
        limit = max(1, min(limit, 1000))
        sql += " LIMIT %s"
        params.append(limit)

        return sql, params

    def _build_filters(self, filters: List[Dict[str, Any]], allow_agg: bool = False) -> Tuple[str, List[Any]]:
        clauses: List[str] = []
        params: List[Any] = []

        for item in filters:
            field = str(item.get("field") or "").strip()
            op = str(item.get("op") or "").strip().lower()
            value = item.get("value")

            if allow_agg and self._is_agg_alias(field):
                field_expr = f"`{field}`"
            else:
                if not self._is_valid_identifier(field):
                    raise ValueError(f"filter field가 유효하지 않습니다: {field}")
                self._denylist_check(field)
                field_expr = self._quote_identifier(field)
            if op not in _ALLOWED_OPS:
                raise ValueError(f"지원하지 않는 연산자입니다: {op}")

            if op in {"=", "!=", ">", ">=", "<", "<=", "like"}:
                clauses.append(f"{field_expr} {op.upper()} %s")
                params.append(value)
            elif op in {"in", "not_in"}:
                values = value if isinstance(value, list) else []
                if not values:
                    raise ValueError(f"{op} 연산자는 비어있는 목록을 허용하지 않습니다.")
                placeholders = ", ".join(["%s"] * len(values))
                keyword = "IN" if op == "in" else "NOT IN"
                clauses.append(f"{field_expr} {keyword} ({placeholders})")
                params.extend(values)
            elif op == "between":
                if not isinstance(value, list) or len(value) != 2:
                    raise ValueError("between 연산자는 길이 2의 리스트가 필요합니다.")
                clauses.append(f"{field_expr} BETWEEN %s AND %s")
                params.extend(value)

        return " AND ".join(clauses), params

    @staticmethod
    def _is_valid_identifier(value: str) -> bool:
        parts = value.split(".")
        return all(_IDENTIFIER_RE.match(part) for part in parts)

    @staticmethod
    def _quote_identifier(value: str) -> str:
        parts = value.split(".")
        return ".".join([f"`{part}`" for part in parts])

    @staticmethod
    def _build_result(rows: List[Dict[str, Any]], cursor_description=None) -> QueryResult:
        schema: Dict[str, str] = {}
        if cursor_description:
            for col in cursor_description:
                name = col[0]
                type_code = col[1]
                schema[name] = MySqlDbAdapter._map_type(type_code)

        return {
            "rows": rows,
            "schema": schema,
            "row_count": len(rows),
            "warning": None,
        }

    @staticmethod
    def _map_type(type_code: Any) -> str:
        if type_code is None:
            return "unknown"

        try:
            name = type_code.__name__.lower()
        except AttributeError:
            name = str(type_code).lower()

        if "int" in name or "long" in name:
            return "number"
        if "decimal" in name or "numeric" in name or "float" in name or "double" in name:
            return "number"
        if "date" in name or "time" in name or "timestamp" in name:
            return "datetime"
        if "bool" in name:
            return "boolean"
        if "json" in name:
            return "json"
        if "char" in name or "text" in name or "string" in name:
            return "text"
        return "unknown"

    @staticmethod
    def _denylist_check(value: str) -> None:
        denylist = [item.strip().lower() for item in settings.db_denylist_keywords.split(",") if item.strip()]
        lowered = value.lower()
        for keyword in denylist:
            if keyword and keyword in lowered:
                raise ValueError(f"금지 키워드 포함: {keyword}")

    @staticmethod
    def _enforce_limits(
        metrics: List[Dict[str, Any]],
        group_by: List[Any],
        order_by: List[Dict[str, Any]],
        filters: List[Dict[str, Any]],
        joins: List[Dict[str, Any]],
        select_exprs: List[Dict[str, Any]],
    ) -> None:
        if len(filters) > settings.db_max_filters:
            raise ValueError("filters 개수가 제한을 초과했습니다.")
        if len(joins) > settings.db_max_joins:
            raise ValueError("joins 개수가 제한을 초과했습니다.")
        if len(group_by) > settings.db_max_group_by:
            raise ValueError("group_by 개수가 제한을 초과했습니다.")
        if len(metrics) > settings.db_max_metrics:
            raise ValueError("metrics 개수가 제한을 초과했습니다.")
        if len(order_by) > settings.db_max_order_by:
            raise ValueError("order_by 개수가 제한을 초과했습니다.")
        if len(select_exprs) > settings.db_max_select:
            raise ValueError("select 개수가 제한을 초과했습니다.")

    def _build_joins(self, joins: List[Dict[str, Any]]) -> str:
        if not joins:
            return ""
        parts: List[str] = []
        for join in joins:
            join_type = str(join.get("type") or "").strip().lower()
            source = str(join.get("source") or "").strip()
            on_clause = str(join.get("on") or "").strip()

            if join_type not in _ALLOWED_JOIN_TYPES:
                raise ValueError(f"지원하지 않는 join type입니다: {join_type}")
            if not self._is_valid_identifier(source):
                raise ValueError(f"join source가 유효하지 않습니다: {source}")
            self._denylist_check(source)
            if not on_clause or not self._is_safe_on_clause(on_clause):
                raise ValueError("join on 절이 유효하지 않습니다.")

            join_keyword = f"{join_type.upper()} JOIN"
            parts.append(f"{join_keyword} {self._quote_identifier(source)} ON {on_clause}")

        return " ".join(parts)

    @staticmethod
    def _is_safe_on_clause(value: str) -> bool:
        if any(token in value for token in [";", "--", "/*", "*/"]):
            return False
        return bool(re.match(r"^[A-Za-z0-9_\\.\\s=<>!]+$", value))

    @staticmethod
    def _is_agg_alias(value: str) -> bool:
        return bool(re.match(r"^[A-Za-z0-9_]+$", value))

    def _build_select_exprs(self, select_exprs: List[Dict[str, Any]]) -> List[str]:
        parts: List[str] = []
        for item in select_exprs:
            expr = str(item.get("expr") or "").strip()
            alias = str(item.get("alias") or "").strip()
            if not expr or not alias:
                raise ValueError("select expr/alias가 비어있습니다.")
            if not self._is_safe_expr(expr):
                raise ValueError("select expr가 허용되지 않는 형식입니다.")
            if not self._is_valid_identifier(alias):
                raise ValueError("select alias가 유효하지 않습니다.")
            self._denylist_check(alias)
            parts.append(f"{expr} AS `{alias}`")
        return parts

    @staticmethod
    def _is_safe_expr(expr: str) -> bool:
        if any(token in expr for token in [";", "--", "/*", "*/"]):
            return False
        if not re.match(r"^[A-Za-z0-9_\\s\\(\\)\\,\\.%'\\-]+$", expr):
            return False
        return True

    @staticmethod
    def _parse_db_url(db_url: str) -> Dict[str, Any]:
        parsed = urlparse(db_url)
        if parsed.scheme not in {"mysql", "mariadb"}:
            raise ValueError("DB_URL 스킴이 mysql/mariadb가 아닙니다.")

        return {
            "host": parsed.hostname or "localhost",
            "user": parsed.username or "",
            "password": parsed.password or "",
            "database": (parsed.path or "").lstrip("/") or "",
            "port": parsed.port or 3306,
        }
