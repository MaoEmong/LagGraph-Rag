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
