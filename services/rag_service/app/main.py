"""FastAPI entry point for the RAG service."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from shared.logging import get_logger, setup_logging
from shared.schemas import RetrievedChunk

from .seed import load_corpus
from .store import get_store

setup_logging()
logger = get_logger("rag_service")

app = FastAPI(
    title="RAG Service",
    description="Retrieve compliance rules and policies.",
    version="0.1.0",
)


class QueryIn(BaseModel):
    query: str
    top_k: int = 5


class IndexIn(BaseModel):
    chunks: list[dict]


@app.on_event("startup")
def _load_default_corpus() -> None:
    """Load compliance corpus at startup."""
    n = load_corpus()
    logger.info("startup: loaded %d rules", n)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "rag_service", "indexed": get_store().size()}


@app.post("/retrieve", response_model=list[RetrievedChunk])
def retrieve(payload: QueryIn) -> list[RetrievedChunk]:
    logger.info("query: %r top_k=%d", payload.query[:60], payload.top_k)
    return get_store().search(payload.query, payload.top_k)


@app.post("/index")
def index(payload: IndexIn) -> dict:
    n = get_store().add_many(payload.chunks)
    return {"indexed": n, "total": get_store().size()}