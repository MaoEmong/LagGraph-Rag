from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..storage.checkpoint import CheckpointStore

router = APIRouter()


class ResetRequest(BaseModel):
    thread_id: str = Field(..., description="초기화할 thread ID")


@router.get("/threads")
def list_threads() -> Dict[str, Any]:
    checkpoint = CheckpointStore()
    threads = checkpoint.list_threads()
    return {
        "success": True,
        "data": {"threads": threads},
        "error": None,
    }


@router.post("/threads/reset")
def reset_thread(request: ResetRequest) -> Dict[str, Any]:
    checkpoint = CheckpointStore()
    reset = checkpoint.reset_thread(request.thread_id)
    return {
        "success": True,
        "data": {
            "thread_id": request.thread_id,
            "reset": reset,
        },
        "error": None,
    }
