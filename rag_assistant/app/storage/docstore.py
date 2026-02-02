import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..config import settings


class Docstore:
    def __init__(self) -> None:
        self._path = Path(settings.docstore_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    chunk_id TEXT PRIMARY KEY,
                    parent_id TEXT,
                    content TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    created_at DATETIME NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ingest_files (
                    source_path TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )

    def save_chunks(self, chunks: Iterable[Dict[str, Any]]) -> int:
        now = datetime.utcnow().isoformat()
        rows: List[tuple] = []
        for chunk in chunks:
            rows.append(
                (
                    chunk["chunk_id"],
                    chunk.get("parent_id"),
                    chunk["content"],
                    chunk["source_path"],
                    chunk["file_type"],
                    chunk.get("created_at", now),
                )
            )
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO documents
                (chunk_id, parent_id, content, source_path, file_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def delete_chunks_by_source_path(self, source_path: str) -> int:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM documents WHERE source_path = ?", (source_path,))
            return cur.rowcount

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM documents WHERE chunk_id = ?", (chunk_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def get_file_hash(self, source_path: str) -> Optional[str]:
        with self._connect() as conn:
            cur = conn.execute("SELECT content_hash FROM ingest_files WHERE source_path = ?", (source_path,))
            row = cur.fetchone()
        if not row:
            return None
        return row["content_hash"]

    def upsert_file_hash(self, source_path: str, content_hash: str) -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO ingest_files (source_path, content_hash, updated_at)
                VALUES (?, ?, ?)
                """,
                (source_path, content_hash, now),
            )
