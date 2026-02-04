from __future__ import annotations

import logging
from typing import Dict, List

from openai import OpenAI

from ..config import settings
from ..schemas import State

logger = logging.getLogger(__name__)


_SYSTEM_INSTRUCTIONS = """너는 검색용 재질의 생성기다.
사용자 질문을 검색에 적합한 짧은 쿼리로 변환하라.
반드시 1줄의 간결한 키워드 중심 문장으로 출력하라.
불필요한 조사/수식어를 제거하고 핵심 명사 위주로 구성한다.
"""


def _get_client() -> OpenAI:
    if settings.openai_base_url:
        return OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url, timeout=settings.openai_timeout_sec)
    return OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_sec)


def _model_candidates(primary: str, fallbacks: str) -> List[str]:
    candidates = [primary]
    if fallbacks:
        candidates.extend([item.strip() for item in fallbacks.split(",") if item.strip()])
    deduped: List[str] = []
    for model in candidates:
        if model not in deduped:
            deduped.append(model)
    return deduped


def _extract_output_text(response) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text.strip()

    parts: List[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def _needs_requery(state: State) -> bool:
    if not settings.requery_enabled:
        return False
    if not state.get("retrieval_needed"):
        return False
    if state.get("attempt", 0) >= settings.requery_max_attempts:
        return False

    answer = (state.get("answer") or "").strip()
    citations = state.get("citations") or []
    docs = state.get("docs") or []

    if answer and answer != settings.no_context_message:
        # 답변이 있고, 출처/문서가 충분하면 재질의하지 않는다.
        if len(citations) >= settings.requery_min_citations and len(docs) >= settings.requery_min_docs:
            return False

    if len(citations) >= settings.requery_min_citations and len(docs) >= settings.requery_min_docs:
        return False

    return True


def _rewrite_query(question: str) -> str:
    if not settings.openai_api_key:
        return question

    models = _model_candidates(settings.requery_model, settings.requery_model_fallbacks)
    last_error = None
    for model in models:
        try:
            client = _get_client()
            response = client.responses.create(
                model=model,
                input=question,
                instructions=_SYSTEM_INSTRUCTIONS,
                temperature=settings.requery_temperature,
                max_output_tokens=settings.requery_max_output_tokens,
            )
            output = _extract_output_text(response)
            return output or question
        except Exception as exc:
            last_error = exc
            logger.exception("재질의 생성 실패: %s", model)

    logger.warning("재질의 생성 실패, 원문 유지: %s", last_error)
    return question


def requery(state: State) -> Dict[str, object]:
    if not _needs_requery(state):
        return {"requery_needed": False}

    question = (state.get("question") or "").strip()
    if not question:
        return {"requery_needed": False}

    rewritten = _rewrite_query(question)
    attempt = state.get("attempt", 0) + 1

    return {
        "requery_needed": True,
        "retrieval_query": rewritten,
        "attempt": attempt,
    }
