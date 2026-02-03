from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from ..schemas import QueryResult, QuerySpec


class MockDbAdapter:
    name = "mock"

    def run_query(self, query_spec: QuerySpec) -> QueryResult:
        intent = query_spec.get("intent") or "mock"
        now = datetime.utcnow().strftime("%Y-%m-%d")

        rows: List[Dict[str, Any]] = [
            {"label": "sample", "value": 123, "as_of": now},
            {"label": "intent", "value": intent, "as_of": now},
        ]

        return {
            "rows": rows,
            "schema": {
                "label": "text",
                "value": "text",
                "as_of": "text",
            },
            "row_count": len(rows),
            "warning": "mock data",
        }
