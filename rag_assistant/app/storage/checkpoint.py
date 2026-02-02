import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import settings


class CheckpointStore:
    def __init__(self) -> None:
        self._path = Path(settings.checkpoint_path)
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
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT PRIMARY KEY,
                    graph_state TEXT NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )

    def save_state(self, thread_id: str, graph_state: Dict[str, Any]) -> None:
        payload = json.dumps(graph_state, ensure_ascii=False)
        updated_at = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO checkpoints (thread_id, graph_state, updated_at)
                VALUES (?, ?, ?)
                """,
                (thread_id, payload, updated_at),
            )

    def load_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute("SELECT graph_state FROM checkpoints WHERE thread_id = ?", (thread_id,))
            row = cur.fetchone()
        if not row:
            return None
        return json.loads(row["graph_state"])

    def list_threads(self) -> List[str]:
        with self._connect() as conn:
            cur = conn.execute("SELECT thread_id FROM checkpoints ORDER BY updated_at DESC")
            rows = cur.fetchall()
        return [row["thread_id"] for row in rows]

    def reset_thread(self, thread_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        return cur.rowcount > 0
