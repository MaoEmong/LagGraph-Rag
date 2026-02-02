from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..graph import run_graph
from ..schemas import State
from ..storage.checkpoint import CheckpointStore

router = APIRouter()


class ChatRequest(BaseModel):
    thread_id: str = Field(..., description="세션 ID")
    question: str = Field(..., description="사용자 질문")


@router.post("/chat")
def chat(request: ChatRequest) -> Dict[str, Any]:
    state: State = {
        "thread_id": request.thread_id,
        "question": request.question,
    }

    result = run_graph(state)

    # 체크포인트 저장
    checkpoint = CheckpointStore()
    checkpoint.save_state(request.thread_id, result)

    response = result.get("response")
    if response:
        return response

    # 예외적 상황에 대한 기본 응답
    return {
        "success": False,
        "data": None,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "응답 포맷 구성 실패",
        },
    }
