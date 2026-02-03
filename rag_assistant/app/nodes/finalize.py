from __future__ import annotations

from typing import Dict

from ..schemas import State


def finalize(state: State) -> Dict[str, object]:
    error = state.get("error")

    if error:
        return {
            "response": {
                "success": False,
                "data": None,
                "error": error,
            }
        }

    data = {
        "thread_id": state.get("thread_id"),
        "answer": state.get("answer"),
        "citations": state.get("citations", []),
    }

    db_result = state.get("db_result")
    if db_result:
        data["db_result"] = db_result

    tokens = state.get("tokens") or {}
    if tokens:
        data["tokens"] = tokens

    timing = state.get("timing") or {}
    if timing:
        data["timing"] = timing

    return {
        "response": {
            "success": True,
            "data": data,
            "error": None,
        }
    }
