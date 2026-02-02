from __future__ import annotations

import logging
from typing import Dict, List

from openai import OpenAI

from ..config import settings
from ..schemas import Citation, Document, State

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTIONS = """너는 개인용 AI 비서다.
반드시 제공된 참고자료(context) 안의 정보만 사용해 답한다.
참고자료에 없는 내용은 추측하지 말고 모른다고 답한다.
질문이 짧은 사실 질의라면, 참고자료의 표현을 우선해 짧고 단정적으로 답한다.
"""


def _get_client() -> OpenAI:
    if settings.openai_base_url:
        return OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url, timeout=settings.openai_timeout_sec)
    return OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_sec)


def _build_context(docs: List[Document]) -> str:
    if not docs:
        return ""
    chunks: List[str] = []
    max_chars = 12000
    current_len = 0

    for doc in docs:
        content = doc.get("content", "")
        if content:
            meta = doc.get("metadata", {})
            source_path = meta.get("source_path", "unknown")
            block = f"[source: {source_path}]\n{content}"
            if current_len + len(block) > max_chars:
                remain = max_chars - current_len
                if remain > 0:
                    chunks.append(block[:remain])
                break
            chunks.append(block)
            current_len += len(block)
    return "\n\n".join(chunks)


def _extract_output_text(response) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    parts: List[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def _extract_tokens(response) -> Dict[str, int]:
    usage = getattr(response, "usage", None)
    if not usage:
        return {}

    prompt = getattr(usage, "input_tokens", None)
    completion = getattr(usage, "output_tokens", None)
    total = getattr(usage, "total_tokens", None)

    tokens = {}
    if prompt is not None:
        tokens["prompt"] = int(prompt)
    if completion is not None:
        tokens["completion"] = int(completion)
    if total is not None:
        tokens["total"] = int(total)

    return tokens


def _build_citations(docs: List[Document]) -> List[Citation]:
    citations: List[Citation] = []
    for doc in docs:
        meta = doc.get("metadata", {})
        citations.append(
            {
                "chunk_id": doc.get("chunk_id", ""),
                "source_path": meta.get("source_path", ""),
                "parent_id": meta.get("parent_id", ""),
            }
        )
    return citations


def generate(state: State) -> Dict[str, object]:
    if not settings.openai_api_key:
        return {
            "answer": "OPENAI_API_KEY가 설정되지 않아 응답을 생성할 수 없습니다.",
            "citations": [],
            "error": {
                "code": "LLM_ERROR",
                "message": "OPENAI_API_KEY가 설정되지 않았습니다.",
            },
        }

    question = state.get("question") or ""
    docs = state.get("docs") or []
    context = _build_context(docs)

    prompt = f"질문: {question}\n\n참고자료:\n{context}" if context else question

    attempt = state.get("attempt", 0)
    last_error = None

    for _ in range(2):
        try:
            client = _get_client()
            response = client.responses.create(
                model=settings.llm_model,
                input=prompt,
                instructions=_SYSTEM_INSTRUCTIONS,
                temperature=settings.temperature,
                max_output_tokens=settings.max_output_tokens,
            )
            answer = _extract_output_text(response)
            tokens = _extract_tokens(response)
            return {
                "answer": answer,
                "citations": _build_citations(docs),
                "tokens": tokens,
                "error": None,
                "attempt": attempt,
            }
        except Exception as exc:
            attempt += 1
            last_error = exc
            logger.exception("LLM 호출 실패")

    return {
        "answer": "",
        "citations": [],
        "error": {
            "code": "LLM_ERROR",
            "message": f"OpenAI 호출 실패: {last_error}",
        },
        "attempt": attempt,
    }
