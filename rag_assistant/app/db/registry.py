from __future__ import annotations

from typing import Dict

from .adapter import DbQueryAdapter
from .mock_adapter import MockDbAdapter
from .mysql_adapter import MySqlDbAdapter
from .postgres_adapter import PostgresDbAdapter


_ADAPTERS: Dict[str, DbQueryAdapter] = {
    "mock": MockDbAdapter(),
    "mysql": MySqlDbAdapter(),
    "postgres": PostgresDbAdapter(),
}


def get_adapter(name: str) -> DbQueryAdapter:
    key = (name or "mock").strip().lower()
    if key in _ADAPTERS:
        return _ADAPTERS[key]
    return _ADAPTERS["mock"]
