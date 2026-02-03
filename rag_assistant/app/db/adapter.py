from __future__ import annotations

from typing import Protocol

from ..schemas import QueryResult, QuerySpec


class DbQueryAdapter(Protocol):
    name: str

    def run_query(self, query_spec: QuerySpec) -> QueryResult: ...
