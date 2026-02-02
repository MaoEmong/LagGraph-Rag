from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..ingest.ingest import ingest_path

router = APIRouter()


class IngestRequest(BaseModel):
    path: str = Field(..., description="인제스트 대상 경로")
    recursive: bool = Field(True, description="하위 폴더 포함 여부")
    dry_run: bool = Field(False, description="저장 없이 테스트 실행 여부")


@router.post("/ingest")
def ingest(request: IngestRequest) -> Dict[str, Any]:
    try:
        result = ingest_path(request.path, recursive=request.recursive, dry_run=request.dry_run)
    except Exception as exc:
        return {
            "success": False,
            "data": None,
            "error": {
                "code": "INGEST_ERROR",
                "message": f"인제스트 실패: {exc}",
            },
        }

    return {
        "success": True,
        "data": {
            "files_processed": result.files_processed,
            "chunks_created": result.chunks_created,
            "duration_ms": result.duration_ms,
        },
        "error": None,
    }
