from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI

from ..config import settings
from ..storage.docstore import Docstore
from ..storage.vector_db import VectorDB, ensure_chroma_path
from .chunking import DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP, chunk_text
from .cleaning import clean_text
from .discovery import discover_files
from .loaders import ParseError, parse_file

logger = logging.getLogger(__name__)


@dataclass
class IngestResult:
    files_processed: int
    chunks_created: int
    duration_ms: int


def _get_client() -> OpenAI:
    if settings.openai_base_url:
        return OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=settings.openai_timeout_sec,
        )
    return OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_sec)


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _embed_texts(texts: List[str]) -> List[List[float]]:
    client = _get_client()
    embeddings: List[List[float]] = []

    batch_size = max(1, settings.embedding_batch_size)
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        last_error = None
        for _ in range(2):
            try:
                response = client.embeddings.create(
                    model=settings.embedding_model,
                    input=batch,
                )
                embeddings.extend([item.embedding for item in response.data])
                last_error = None
                break
            except Exception as exc:
                last_error = exc
        if last_error is not None:
            raise last_error

    return embeddings


def _make_chunks(path: Path, text: str) -> List[Dict[str, Any]]:
    parent_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    chunks = []
    for chunk in chunk_text(text, DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP, settings.embedding_model):
        chunk_id = str(uuid.uuid4())
        chunks.append(
            {
                "chunk_id": chunk_id,
                "parent_id": parent_id,
                "content": chunk,
                "source_path": str(path),
                "file_type": path.suffix.lower().lstrip("."),
                "created_at": created_at,
                "hash": _hash_text(chunk),
            }
        )
    return chunks


def ingest_path(path: str, recursive: bool = True, dry_run: bool = False) -> IngestResult:
    start_time = time.time()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

    files = discover_files(path, recursive=recursive)
    if not files:
        return IngestResult(files_processed=0, chunks_created=0, duration_ms=0)

    ensure_chroma_path()
    vector_db = VectorDB()
    docstore = Docstore()

    total_chunks = 0
    processed = 0

    for file_path in files:
        try:
            raw_text = parse_file(file_path)
        except ParseError as exc:
            logger.warning("파싱 실패: %s", exc)
            continue

        cleaned = clean_text(raw_text)
        if not cleaned:
            logger.info("빈 문서 스킵: %s", file_path)
            continue

        content_hash = _hash_text(cleaned)
        previous_hash = docstore.get_file_hash(str(file_path))
        if previous_hash == content_hash:
            logger.info("변경 없음 스킵: %s", file_path)
            continue

        chunks = _make_chunks(file_path, cleaned)
        if not chunks:
            logger.info("청크 없음: %s", file_path)
            continue

        processed += 1
        total_chunks += len(chunks)

        if dry_run:
            continue

        # Remove previous chunks when the file content changed.
        if previous_hash:
            docstore.delete_chunks_by_source_path(str(file_path))
            vector_db.delete_by_source_path(str(file_path))

        embeddings = _embed_texts([chunk["content"] for chunk in chunks])

        vector_db.upsert(
            ids=[chunk["chunk_id"] for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk["content"] for chunk in chunks],
            metadatas=[
                {
                    "source_path": chunk["source_path"],
                    "file_type": chunk["file_type"],
                    "parent_id": chunk["parent_id"],
                    "created_at": chunk["created_at"],
                }
                for chunk in chunks
            ],
        )

        docstore.save_chunks(chunks)
        docstore.upsert_file_hash(str(file_path), content_hash)

    duration_ms = int((time.time() - start_time) * 1000)
    logger.info("ingest completed", extra={"files": processed, "chunks": total_chunks, "duration_ms": duration_ms})
    return IngestResult(files_processed=processed, chunks_created=total_chunks, duration_ms=duration_ms)
