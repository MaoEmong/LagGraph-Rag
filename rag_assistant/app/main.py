from fastapi import FastAPI

from .config import settings
from .logging_utils import setup_logging
from .routes.chat import router as chat_router
from .routes.ingest import router as ingest_router
from .routes.threads import router as threads_router
from .routes.web import router as web_router

setup_logging()

app = FastAPI(title="RAG Assistant", version="0.1.0")

app.include_router(chat_router)
app.include_router(ingest_router)
app.include_router(threads_router)
app.include_router(web_router)


@app.get("/health")
def health():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "vector_db": "ok",
            "docstore": "ok",
            "llm": "ok",
        },
        "error": None,
    }


@app.get("/")
def root():
    return {
        "success": True,
        "data": {
            "message": "RAG Assistant API is running.",
            "docs": "/docs",
            "health": "/health",
        },
        "error": None,
    }
