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


class State(TypedDict, total=False):
    thread_id: str
    question: str
    retrieval_needed: bool
    retrieval_query: str
    docs: List[Document]
    answer: str
    citations: List[Citation]
    attempt: int
    timing: Dict[str, Any]
    tokens: Dict[str, Any]
    error: ErrorInfo
    response: Dict[str, Any]
