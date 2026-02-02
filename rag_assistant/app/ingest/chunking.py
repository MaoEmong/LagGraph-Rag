from __future__ import annotations

import logging
from typing import List, Optional

try:
    import tiktoken
except Exception:  # pragma: no cover - optional dependency
    tiktoken = None

logger = logging.getLogger(__name__)


DEFAULT_CHUNK_SIZE = 800
DEFAULT_OVERLAP = 100


def _chunk_by_chars(text: str, chunk_size: int, overlap: int) -> List[str]:
    if not text:
        return []

    if chunk_size <= 0:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= length:
            break
        start = end - overlap
        if start < 0:
            start = 0
        if start >= length:
            break

    return chunks


def _chunk_by_tokens(text: str, chunk_size: int, overlap: int, model_name: Optional[str]) -> List[str]:
    if not tiktoken:
        logger.warning("tiktoken이 없어 문자 기준 청킹으로 폴백합니다.")
        return _chunk_by_chars(text, chunk_size, overlap)

    if not text or chunk_size <= 0:
        return []

    try:
        encoding = tiktoken.encoding_for_model(model_name or "gpt-4o-mini")
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    if not tokens:
        return []

    if overlap < 0:
        overlap = 0
    if overlap >= chunk_size:
        overlap = max(chunk_size - 1, 0)

    chunks = []
    start = 0
    length = len(tokens)

    while start < length:
        end = min(start + chunk_size, length)
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        if end >= length:
            break
        start = end - overlap

    return chunks


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
    model_name: Optional[str] = None,
) -> List[str]:
    if not text:
        return []

    if chunk_size <= 0:
        return []
    return _chunk_by_tokens(text, chunk_size, overlap, model_name)
