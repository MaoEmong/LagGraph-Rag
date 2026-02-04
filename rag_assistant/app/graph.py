from __future__ import annotations

import logging
import time
from typing import Callable, Dict

from langgraph.graph import END, StateGraph

from .nodes.db_plan import db_plan
from .nodes.db_query import db_query
from .nodes.finalize import finalize
from .nodes.generate import generate
from .nodes.requery import requery
from .nodes.retrieve import retrieve
from .nodes.route import route
from .schemas import State

logger = logging.getLogger(__name__)


def _route_decision(state: State) -> str:
    return "retrieve" if state.get("retrieval_needed") else "db_plan"


def _requery_decision(state: State) -> str:
    return "retrieve" if state.get("requery_needed") else "finalize"


def _timed(name: str, func: Callable[[State], Dict[str, object]]) -> Callable[[State], Dict[str, object]]:
    def wrapper(state: State) -> Dict[str, object]:
        start = time.time()
        result = func(state)
        duration_ms = int((time.time() - start) * 1000)

        timing = {}
        if isinstance(state.get("timing"), dict):
            timing.update(state.get("timing", {}))
        if isinstance(result.get("timing"), dict):
            timing.update(result.get("timing", {}))
        timing[name] = duration_ms

        result["timing"] = timing
        response = result.get("response")
        if isinstance(response, dict) and isinstance(response.get("data"), dict):
            response["data"]["timing"] = timing
        return result

    return wrapper


def build_graph() -> Callable[[State], Dict[str, object]]:
    graph = StateGraph(State)

    graph.add_node("route", _timed("t_route_ms", route))
    graph.add_node("retrieve", _timed("t_retrieve_ms", retrieve))
    graph.add_node("db_plan", _timed("t_db_plan_ms", db_plan))
    graph.add_node("db_query", _timed("t_db_query_ms", db_query))
    graph.add_node("generate", _timed("t_generate_ms", generate))
    graph.add_node("requery", _timed("t_requery_ms", requery))
    graph.add_node("finalize", _timed("t_finalize_ms", finalize))

    graph.set_entry_point("route")
    graph.add_conditional_edges(
        "route",
        _route_decision,
        {
            "retrieve": "retrieve",
            "db_plan": "db_plan",
        },
    )
    graph.add_edge("retrieve", "db_plan")
    graph.add_edge("db_plan", "db_query")
    graph.add_edge("db_query", "generate")
    graph.add_edge("generate", "requery")
    graph.add_conditional_edges(
        "requery",
        _requery_decision,
        {
            "retrieve": "retrieve",
            "finalize": "finalize",
        },
    )
    graph.add_edge("finalize", END)

    return graph.compile()


def run_graph(state: State) -> Dict[str, object]:
    start = time.time()
    graph = build_graph()
    result = graph.invoke(state)
    total_ms = int((time.time() - start) * 1000)

    timing = result.get("timing") or {}
    timing["t_total_ms"] = total_ms
    result["timing"] = timing
    response = result.get("response")
    if isinstance(response, dict) and isinstance(response.get("data"), dict):
        response["data"]["timing"] = timing

    logger.info("graph completed", extra={"timing": timing})
    return result
