from typing import Any, Dict, List, Optional, TypedDict


class Document(TypedDict, total=False):
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    rerank_score: float


class Citation(TypedDict, total=False):
    chunk_id: str
    source_path: str
    parent_id: str


class ErrorInfo(TypedDict, total=False):
    code: str
    message: str


class QuerySpec(TypedDict, total=False):
    intent: str
    source: str
    filters: List[Dict[str, Any]]
    joins: List[Dict[str, Any]]
    group_by: List[str]
    metrics: List[Dict[str, Any]]
    select: List[Dict[str, Any]]
    having: List[Dict[str, Any]]
    order_by: List[Dict[str, Any]]
    limit: int


class QueryResult(TypedDict, total=False):
    rows: List[Dict[str, Any]]
    schema: Dict[str, str]
    row_count: int
    warning: Optional[str]


class DbError(TypedDict, total=False):
    code: str
    message: str


class State(TypedDict, total=False):
    thread_id: str
    question: str
    retrieval_needed: bool
    retrieval_query: str
    docs: List[Document]
    db_needed: bool
    db_query_spec: QuerySpec
    db_result: QueryResult
    db_error: DbError
    answer: str
    citations: List[Citation]
    attempt: int
    timing: Dict[str, Any]
    tokens: Dict[str, Any]
    error: ErrorInfo
    response: Dict[str, Any]
