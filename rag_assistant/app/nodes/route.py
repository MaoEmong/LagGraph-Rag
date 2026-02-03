from __future__ import annotations

import re
from typing import Dict

from ..config import settings
from ..schemas import State


_KEYWORDS = (
    "문서",
    "설계",
    "프로젝트",
    "코드",
    "API",
    "아키텍처",
)

_FILE_PATTERN = re.compile(r"(\.md|\.txt|\.pdf|\.docx|/|\\\\)")
_DB_KEYWORDS = (
    "db",
    "database",
    "데이터베이스",
    "sql",
    "쿼리",
    "query",
    "테이블",
    "조회",
    "통계",
)


def route(state: State) -> Dict[str, object]:
    question = (state.get("question") or "").strip()

    retrieval_needed = False
    if any(keyword in question for keyword in _KEYWORDS):
        retrieval_needed = True
    if len(question) <= 15:
        retrieval_needed = True
    if _FILE_PATTERN.search(question):
        retrieval_needed = True
    if question and not retrieval_needed:
        # Default to retrieval for most questions to avoid missing relevant docs.
        retrieval_needed = True

    db_needed = False
    if settings.db_enabled and question and any(keyword.lower() in question.lower() for keyword in _DB_KEYWORDS):
        db_needed = True

    return {
        "retrieval_needed": retrieval_needed,
        "retrieval_query": question,
        "db_needed": db_needed,
        "attempt": state.get("attempt", 0),
    }
