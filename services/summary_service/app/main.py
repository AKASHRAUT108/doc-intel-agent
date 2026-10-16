"""FastAPI entry point for the Summary Service."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from shared.logging import get_logger, setup_logging
from shared.schemas import SummaryResult

from .pipeline import summarize_document

setup_logging()
logger = get_logger("summary_service")

app = FastAPI(
    title="Summary Service",
    description="LLM-powered document summarization.",
    version="0.1.0",
)


class SummarizeIn(BaseModel):
    text: str = Field(min_length=1, description="Raw document text")
    job_id: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "summary_service"}


@app.post("/summarize", response_model=SummaryResult)
def summarize(payload: SummarizeIn) -> SummaryResult:
    logger.info("summarize request: %d chars", len(payload.text))
    result = summarize_document(payload.text)
    logger.info(
        "summarized: type=%s facts=%d actions=%d mocked=%s",
        result.document_type,
        len(result.key_facts),
        len(result.action_items),
        result.mocked,
    )
    return result
