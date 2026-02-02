from pathlib import Path
from typing import Any, Dict, List, Optional

from chromadb import PersistentClient
from chromadb.errors import NotFoundError

from ..config import settings


class VectorDB:
    def __init__(self, collection_name: str = "documents") -> None:
        self._collection_name = collection_name
        self._client = PersistentClient(path=str(settings.chroma_path))
        self._collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        try:
            return self._client.get_collection(name=self._collection_name)
        except NotFoundError:
            return self._client.create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )

    def upsert(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, query_embeddings: List[List[float]], top_k: int = 5):
        return self._collection.query(query_embeddings=query_embeddings, n_results=top_k)

    def delete_by_source_path(self, source_path: str) -> None:
        self._collection.delete(where={"source_path": source_path})


def ensure_chroma_path() -> None:
    Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
