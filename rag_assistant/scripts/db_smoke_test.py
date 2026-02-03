from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from app.config import settings
from app.db.registry import get_adapter
from app.schemas import QuerySpec


def _build_spec(source: str, limit: int) -> QuerySpec:
    return {
        "intent": "db_smoke_test",
        "source": source,
        "filters": [],
        "joins": [],
        "group_by": [],
        "metrics": [],
        "having": [],
        "order_by": [],
        "limit": limit,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="DB smoke test")
    parser.add_argument("--source", required=True, help="테이블 또는 뷰 이름")
    parser.add_argument("--limit", type=int, default=5, help="조회 행 수")
    parser.add_argument("--adapter", default="mysql", help="어댑터 이름 (mysql/postgres/mock)")
    args = parser.parse_args()

    settings.db_adapter = args.adapter

    spec = _build_spec(args.source, args.limit)
    adapter = get_adapter(args.adapter)

    try:
        result = adapter.run_query(spec)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    output: Dict[str, Any] = {
        "adapter": adapter.name,
        "source": args.source,
        "row_count": result.get("row_count"),
        "rows": result.get("rows"),
        "schema": result.get("schema"),
        "warning": result.get("warning"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
