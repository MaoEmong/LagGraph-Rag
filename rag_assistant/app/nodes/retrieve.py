from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional

from openai import OpenAI

from ..config import settings
from ..schemas import Document, State
from ..storage.docstore import Docstore
from ..storage.vector_db import VectorDB

logger = logging.getLogger(__name__)


_CROSS_ENCODER = None


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
    if model.lower() == "cross-encoder":
        return None
    if model.lower() == "embedding":
        return settings.embedding_model
    return model


def _get_reranker_mode() -> str:
    mode = (getattr(settings, "reranker_mode", "") or "").strip().lower()
    if mode in {"off", "auto", "always"}:
        return mode
    return "always" if settings.reranker_on else "off"


def _use_cross_encoder() -> bool:
    return (settings.reranker_model or "").strip().lower() == "cross-encoder"


def _should_rerank(docs: List[Document]) -> bool:
    if not docs:
        return False
    if len(docs) < settings.top_k:
        return True

    scores = [doc.get("score") for doc in docs if doc.get("score") is not None]
    if scores:
        best_distance = min(scores)
        return best_distance >= settings.reranker_distance_threshold

    sparse_scores = [doc.get("sparse_score") for doc in docs if doc.get("sparse_score") is not None]
    if sparse_scores:
        return True

    return True


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


def _get_cross_encoder():
    global _CROSS_ENCODER
    if _CROSS_ENCODER is not None:
        return _CROSS_ENCODER
    try:
        from sentence_transformers import CrossEncoder
    except Exception as exc:
        raise RuntimeError("sentence-transformers가 설치되어 있지 않습니다.") from exc

    model_name = settings.reranker_cross_encoder_model
    device = settings.reranker_device or "cuda"
    _CROSS_ENCODER = CrossEncoder(model_name, device=device)
    return _CROSS_ENCODER


def _rerank_docs_cross_encoder(query: str, docs: List[Document]) -> List[Document]:
    if not docs:
        return docs

    try:
        model = _get_cross_encoder()
        pairs = [(query, doc.get("content", "")) for doc in docs]
        scores = model.predict(pairs, batch_size=max(1, settings.reranker_batch_size))
    except Exception:
        logger.exception("로컬 리랭커 실행 실패")
        return docs

    reranked: List[Document] = []
    for doc, score in zip(docs, scores):
        doc["rerank_score"] = float(score)
        reranked.append(doc)

    threshold = settings.reranker_score_threshold
    if threshold is not None:
        reranked = [doc for doc in reranked if doc.get("rerank_score", 0.0) >= threshold]

    reranked.sort(key=lambda doc: doc.get("rerank_score", 0.0), reverse=True)
    return reranked


def _dense_retrieve(query: str) -> List[Document]:
    embedding = _embed_query(query)
    vdb = VectorDB()

    initial_top_k = settings.top_k
    mode = _get_reranker_mode()
    reranker_model = _get_reranker_model()
    if mode in {"auto", "always"} and (reranker_model or _use_cross_encoder()):
        initial_top_k = max(settings.top_k, settings.rerank_top_k)

    result = vdb.query([embedding], top_k=initial_top_k)

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
    return docs


def _sparse_retrieve(query: str) -> List[Document]:
    docstore = Docstore()
    rows = docstore.search_fts(query, limit=settings.sparse_top_k)
    docs: List[Document] = []
    for row in rows:
        doc: Document = {
            "chunk_id": row.get("chunk_id", ""),
            "content": row.get("content", ""),
            "metadata": {
                "source_path": row.get("source_path", ""),
                "parent_id": row.get("parent_id", ""),
                "file_type": row.get("file_type", ""),
            },
            "sparse_score": row.get("score"),
        }
        docs.append(doc)
    return docs


def _rank_scores(docs: List[Document], key: str, reverse: bool = False) -> Dict[str, float]:
    scored = []
    for idx, doc in enumerate(docs):
        value = doc.get(key)
        scored.append((idx, value))

    def _sort_key(item):
        _, value = item
        if value is None:
            return float("inf") if not reverse else float("-inf")
        return value

    ordered = sorted(scored, key=_sort_key, reverse=reverse)
    ranks: Dict[str, float] = {}
    for rank, (idx, _) in enumerate(ordered):
        chunk_id = docs[idx].get("chunk_id", "")
        if not chunk_id:
            continue
        ranks[chunk_id] = 1.0 / (rank + 1)
    return ranks


def _merge_docs(dense_docs: List[Document], sparse_docs: List[Document]) -> List[Document]:
    if not dense_docs and not sparse_docs:
        return []

    dense_ranks = _rank_scores(dense_docs, key="score", reverse=False)
    sparse_ranks = _rank_scores(sparse_docs, key="sparse_score", reverse=False)

    merged: Dict[str, Document] = {}
    for doc in dense_docs:
        chunk_id = doc.get("chunk_id", "")
        if not chunk_id:
            continue
        merged[chunk_id] = dict(doc)

    for doc in sparse_docs:
        chunk_id = doc.get("chunk_id", "")
        if not chunk_id:
            continue
        if chunk_id in merged:
            if not merged[chunk_id].get("content") and doc.get("content"):
                merged[chunk_id]["content"] = doc.get("content", "")
            if not merged[chunk_id].get("metadata") and doc.get("metadata"):
                merged[chunk_id]["metadata"] = doc.get("metadata", {})
            merged[chunk_id]["sparse_score"] = doc.get("sparse_score")
        else:
            merged[chunk_id] = dict(doc)

    for chunk_id, doc in merged.items():
        dense_rank = dense_ranks.get(chunk_id, 0.0)
        sparse_rank = sparse_ranks.get(chunk_id, 0.0)
        doc["hybrid_score"] = dense_rank + sparse_rank

    ordered = sorted(merged.values(), key=lambda d: d.get("hybrid_score", 0.0), reverse=True)
    return ordered


def _parent_expand(docs: List[Document]) -> List[Document]:
    if not docs or not settings.parent_expand_enabled:
        return docs

    docstore = Docstore()
    expanded: List[Document] = []
    seen: set[str] = set()

    for doc in docs:
        chunk_id = doc.get("chunk_id", "")
        if chunk_id and chunk_id not in seen:
            expanded.append(doc)
            seen.add(chunk_id)

        meta = doc.get("metadata") or {}
        parent_id = meta.get("parent_id")
        if not parent_id:
            continue

        parent_chunks = docstore.get_chunks_by_parent_id(parent_id, limit=settings.parent_expand_limit)
        for row in parent_chunks:
            pid_chunk_id = row.get("chunk_id", "")
            if not pid_chunk_id or pid_chunk_id in seen:
                continue
            expanded.append(
                {
                    "chunk_id": pid_chunk_id,
                    "content": row.get("content", ""),
                    "metadata": {
                        "source_path": row.get("source_path", ""),
                        "parent_id": row.get("parent_id", ""),
                        "file_type": row.get("file_type", ""),
                        "created_at": row.get("created_at", ""),
                    },
                }
            )
            seen.add(pid_chunk_id)

    return expanded


def retrieve(state: State) -> Dict[str, object]:
    if not state.get("retrieval_needed"):
        return {
            "docs": state.get("docs") or [],
            "error": None,
        }

    if not settings.openai_api_key:
        return {
            "docs": [],
            "error": {
                "code": "EMBEDDING_ERROR",
                "message": "OPENAI_API_KEY가 설정되지 않았습니다.",
            },
        }

    query = state.get("retrieval_query") or state.get("question") or ""

    try:
        dense_docs = _dense_retrieve(query)
    except Exception as exc:
        logger.exception("벡터 검색 실패")
        return {
            "docs": [],
            "error": {
                "code": "VECTOR_DB_ERROR",
                "message": f"벡터 검색 실패: {exc}",
            },
        }

    sparse_docs: List[Document] = []
    if settings.sparse_enabled:
        try:
            sparse_docs = _sparse_retrieve(query)
        except Exception as exc:
            logger.exception("Sparse 검색 실패")
            sparse_docs = []

    docs = _merge_docs(dense_docs, sparse_docs)
    docs = docs[: settings.top_k]

    docs = _parent_expand(docs)

    mode = _get_reranker_mode()

    if mode == "always" or (mode == "auto" and _should_rerank(docs)):
        if _use_cross_encoder():
            docs = _rerank_docs_cross_encoder(query, docs)
        else:
            docs = _rerank_docs(query, docs)
        docs = docs[: settings.top_k]

    return {
        "docs": docs,
        "error": None,
    }
