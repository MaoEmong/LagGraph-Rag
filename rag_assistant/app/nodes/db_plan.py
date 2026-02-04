from __future__ import annotations

import json
import logging
from typing import Dict, List

from openai import OpenAI

from ..config import settings
from ..schemas import QuerySpec, State

logger = logging.getLogger(__name__)


_SYSTEM_INSTRUCTIONS = """너는 DB 조회 계획을 만드는 도우미다.
사용자 질문을 QuerySpec(JSON)으로 변환하라.
출력은 반드시 JSON 단일 객체만 반환한다.

허용 키:
- intent (str)
- source (str)
- filters (list)
- joins (list)
- group_by (list)
- metrics (list)
- select (list)
- having (list)
- order_by (list)
- limit (int)

규칙:
1) 스키마를 모르면 source는 빈 문자열로 둔다.
2) limit은 1~1000 범위로 설정한다. 기본은 100.
3) 삭제/수정/스키마 변경 관련 연산은 포함하지 않는다.
4) 모호하면 filters를 비워 두고 intent만 명확히 적는다.
"""


def _get_client() -> OpenAI:
    if settings.openai_base_url:
        return OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url, timeout=settings.openai_timeout_sec)
    return OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_sec)


def _basic_spec(question: str) -> QuerySpec:
    limit = max(1, int(settings.db_row_limit))
    return {
        "intent": question,
        "source": "",
        "filters": [],
        "joins": [],
        "group_by": [],
        "metrics": [],
        "select": [],
        "having": [],
        "order_by": [],
        "limit": limit,
    }


def _extract_json(text: str) -> Dict[str, object]:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("JSON 객체를 찾을 수 없습니다.")
    return json.loads(text[start : end + 1])


def _normalize_spec(raw: Dict[str, object], question: str) -> QuerySpec:
    spec: QuerySpec = {
        "intent": str(raw.get("intent") or question),
        "source": str(raw.get("source") or ""),
        "filters": list(raw.get("filters") or []),
        "joins": list(raw.get("joins") or []),
        "group_by": list(raw.get("group_by") or []),
        "metrics": list(raw.get("metrics") or []),
        "select": list(raw.get("select") or []),
        "having": list(raw.get("having") or []),
        "order_by": list(raw.get("order_by") or []),
        "limit": int(raw.get("limit") or settings.db_row_limit),
    }

    limit = max(1, int(spec.get("limit") or settings.db_row_limit))
    limit = min(limit, 1000)
    spec["limit"] = limit

    return spec


def _model_candidates(primary: str, fallbacks: str) -> List[str]:
    candidates = [primary]
    if fallbacks:
        candidates.extend([item.strip() for item in fallbacks.split(",") if item.strip()])
    deduped: List[str] = []
    for model in candidates:
        if model not in deduped:
            deduped.append(model)
    return deduped


def db_plan(state: State) -> Dict[str, object]:
    if not state.get("db_needed"):
        return {
            "db_query_spec": state.get("db_query_spec"),
            "db_error": None,
        }

    question = (state.get("question") or "").strip()
    if not question:
        return {
            "db_query_spec": _basic_spec(""),
            "db_error": {
                "code": "PLAN_ERROR",
                "message": "질문이 비어 있어 QuerySpec을 생성할 수 없습니다.",
            },
        }

    if not settings.openai_api_key:
        return {
            "db_query_spec": _basic_spec(question),
            "db_error": {
                "code": "PLAN_ERROR",
                "message": "OPENAI_API_KEY가 설정되지 않아 기본 QuerySpec으로 대체했습니다.",
            },
        }

    try:
        models = _model_candidates(settings.db_plan_model, settings.db_plan_model_fallbacks)
        last_error = None
        for model in models:
            try:
                client = _get_client()
                response = client.responses.create(
                    model=model,
                    input=question,
                    instructions=_SYSTEM_INSTRUCTIONS,
                    temperature=settings.db_plan_temperature,
                    max_output_tokens=settings.db_plan_max_output_tokens,
                )
                output_text = getattr(response, "output_text", "") or ""
                if not output_text:
                    output_text = ""
                    for item in getattr(response, "output", []) or []:
                        for content in getattr(item, "content", []) or []:
                            text = getattr(content, "text", None)
                            if text:
                                output_text += text
                raw = _extract_json(output_text)
                spec = _normalize_spec(raw, question)
                return {
                    "db_query_spec": spec,
                    "db_error": None,
                }
            except Exception as exc:
                last_error = exc
                logger.exception("QuerySpec 생성 실패: %s", model)
        raise RuntimeError(last_error)
    except Exception as exc:
        logger.exception("QuerySpec 생성 실패")
        return {
            "db_query_spec": _basic_spec(question),
            "db_error": {
                "code": "PLAN_ERROR",
                "message": f"QuerySpec 생성 실패: {exc}",
            },
        }
