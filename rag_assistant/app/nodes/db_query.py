from __future__ import annotations

import logging
from typing import Dict

from ..config import settings
from ..db.registry import get_adapter
from ..schemas import QueryResult, State

logger = logging.getLogger(__name__)


def db_query(state: State) -> Dict[str, object]:
    if not state.get("db_needed"):
        return {
            "db_result": state.get("db_result"),
            "db_error": None,
        }

    query_spec = state.get("db_query_spec") or {}
    adapter = get_adapter(settings.db_adapter)

    try:
        result: QueryResult = adapter.run_query(query_spec)
        return {
            "db_result": result,
            "db_error": None,
        }
    except Exception as exc:
        logger.exception("DB 조회 실패")
        return {
            "db_result": None,
            "db_error": {
                "code": "DB_ERROR",
                "message": f"DB 조회 실패: {exc}",
            },
            "error": {
                "code": "DB_ERROR",
                "message": f"DB 조회 실패: {exc}",
            },
        }
