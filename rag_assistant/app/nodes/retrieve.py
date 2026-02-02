from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional

from openai import OpenAI

from ..config import settings
from ..schemas import Document, State
from ..storage.vector_db import VectorDB

logger = logging.getLogger(__name__)


def _get_client() -> OpenAI:
    if settings.openai_base_url:
        return OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url, timeout=settings.openai_timeout_sec)
    return OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_sec)


def _embed_query(query: str) -> List[float]:
    return _embed_query_with_model(query, settings.embedding_model)


def _embed_query_with_model(query: str, model: str) -> List[float]:
    client = _get_client()
    response = client.embeddings.create(
        model=model,
        input=query,
    )
    return response.data[0].embedding


def _embed_texts(texts: List[str], model: str) -> List[List[float]]:
    client = _get_client()
    embeddings: List[List[float]] = []
    batch_size = max(1, settings.reranker_batch_size)

    for idx in range(0, len(texts), batch_size):
        batch = texts[idx : idx + batch_size]
        response = client.embeddings.create(
            model=model,
            input=batch,
        )
        data = getattr(response, "data", []) or []
        if data and hasattr(data[0], "index"):
            data = sorted(data, key=lambda item: item.index)
        embeddings.extend([item.embedding for item in data])

    return embeddings


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _get_reranker_model() -> Optional[str]:
    model = (settings.reranker_model or "").strip()
    if not model or model.lower() == "none":
        return None
    if model.lower() == "embedding":
        return settings.embedding_model
    return model


def _get_reranker_mode() -> str:
    mode = (getattr(settings, "reranker_mode", "") or "").strip().lower()
    if mode in {"off", "auto", "always"}:
        return mode
    return "always" if settings.reranker_on else "off"


def _should_rerank(docs: List[Document]) -> bool:
    if not docs:
        return False
    if len(docs) < settings.top_k:
        return True

    scores = [doc.get("score") for doc in docs if doc.get("score") is not None]
    if not scores:
        return True

    best_distance = min(scores)
    return best_distance >= settings.reranker_distance_threshold


def _rerank_docs(query: str, docs: List[Document]) -> List[Document]:
    if not docs:
        return docs

    model = _get_reranker_model()
    if not model:
        return docs

    try:
        query_embedding = _embed_query_with_model(query, model)
        texts = [doc.get("content", "") for doc in docs]
        doc_embeddings = _embed_texts(texts, model)
    except Exception as exc:
        logger.exception("리랭커 임베딩 생성 실패")
        return docs

    reranked: List[Document] = []
    for doc, embedding in zip(docs, doc_embeddings):
        score = _cosine_similarity(query_embedding, embedding)
        doc["rerank_score"] = score
        reranked.append(doc)

    threshold = settings.reranker_score_threshold
    if threshold is not None:
        reranked = [doc for doc in reranked if doc.get("rerank_score", 0.0) >= threshold]

    reranked.sort(key=lambda doc: doc.get("rerank_score", 0.0), reverse=True)
    return reranked


def retrieve(state: State) -> Dict[str, object]:
    if not settings.openai_api_key:
        return {
            "docs": [],
            "error": {
                "code": "EMBEDDING_ERROR",
                "message": "OPENAI_API_KEY가 설정되지 않았습니다.",
            },
        }

    query = state.get("retrieval_query") or state.get("question") or ""
    mode = _get_reranker_mode()
    reranker_model = _get_reranker_model()

    try:
        embedding = _embed_query(query)
    except Exception as exc:
        logger.exception("임베딩 생성 실패")
        return {
            "docs": [],
            "error": {
                "code": "EMBEDDING_ERROR",
                "message": f"임베딩 생성 실패: {exc}",
            },
        }

    vdb = VectorDB()

    initial_top_k = settings.top_k
    if mode in {"auto", "always"} and reranker_model:
        initial_top_k = max(settings.top_k, settings.rerank_top_k)

    try:
        result = vdb.query([embedding], top_k=initial_top_k)
    except Exception as exc:
        logger.exception("벡터 검색 실패")
        return {
            "docs": [],
            "error": {
                "code": "VECTOR_DB_ERROR",
                "message": f"벡터 검색 실패: {exc}",
            },
        }

    ids = (result.get("ids") or [[]])[0]
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    docs: List[Document] = []
    for idx, chunk_id in enumerate(ids):
        doc: Document = {
            "chunk_id": chunk_id,
            "content": documents[idx] if idx < len(documents) else "",
            "metadata": metadatas[idx] if idx < len(metadatas) else {},
        }
        if idx < len(distances):
            doc["score"] = distances[idx]
        docs.append(doc)

    if mode == "always" or (mode == "auto" and _should_rerank(docs)):
        docs = _rerank_docs(query, docs)
        docs = docs[: settings.top_k]

    return {
        "docs": docs,
        "error": None,
    }