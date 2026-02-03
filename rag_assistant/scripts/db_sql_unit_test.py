from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

from app.db.mysql_adapter import MySqlDbAdapter
from app.schemas import QuerySpec


def _spec_minimal() -> QuerySpec:
    return {
        "intent": "min",
        "source": "sales",
        "filters": [{"field": "region", "op": "=", "value": "KR"}],
        "joins": [],
        "group_by": [],
        "metrics": [],
        "select": [],
        "having": [],
        "order_by": [],
        "limit": 5,
    }


def _spec_join_group() -> QuerySpec:
    return {
        "intent": "join",
        "source": "sales",
        "filters": [{"field": "sales.date", "op": ">=", "value": "2025-01-01"}],
        "joins": [
            {"type": "left", "source": "customers", "on": "sales.customer_id = customers.id"},
        ],
        "group_by": ["sales.region"],
        "metrics": [{"field": "sales.revenue", "agg": "sum"}],
        "select": [],
        "having": [{"field": "sum_sales.revenue", "op": ">", "value": 1000}],
        "order_by": [{"field": "sales.region", "direction": "asc"}],
        "limit": 10,
    }


def _spec_select_expr() -> QuerySpec:
    return {
        "intent": "select",
        "source": "sales",
        "filters": [],
        "joins": [],
        "group_by": [],
        "metrics": [],
        "select": [{"expr": "DATE_FORMAT(sales.date, '%Y-%m')", "alias": "month"}],
        "having": [],
        "order_by": [{"field": "month", "direction": "asc"}],
        "limit": 3,
    }


def _run_case(adapter: MySqlDbAdapter, name: str, spec: QuerySpec) -> Dict[str, Any]:
    sql, params = adapter._build_sql(spec)
    return {"case": name, "sql": sql, "params": params}


def main() -> int:
    adapter = MySqlDbAdapter()
    cases = [
        ("minimal", _spec_minimal()),
        ("join_group", _spec_join_group()),
        ("select_expr", _spec_select_expr()),
    ]

    results: List[Dict[str, Any]] = []
    for name, spec in cases:
        try:
            results.append(_run_case(adapter, name, spec))
        except Exception as exc:
            results.append({"case": name, "error": str(exc)})

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
