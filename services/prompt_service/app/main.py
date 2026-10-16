"""FastAPI entry point for the Prompt Generator Service."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from shared.logging import get_logger, setup_logging
from shared.schemas import PromptMode, PromptResult

from .pipeline import generate_prompt

setup_logging()
logger = get_logger("prompt_service")

app = FastAPI(
    title="Prompt Service",
    description="Generate paste-ready prompts for any LLM.",
    version="0.1.0",
)


class KeyFactIn(BaseModel):
    label: str
    value: str


class GenerateIn(BaseModel):
    text: str = Field(min_length=1)
    mode: PromptMode = PromptMode.SUMMARY
    key_facts: list[KeyFactIn] = []
    document_type: str = "unknown"
    summary: str = ""


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "prompt_service"}


@app.post("/generate", response_model=PromptResult)
def generate(payload: GenerateIn) -> PromptResult:
    logger.info(
        "generate: mode=%s doc_type=%s facts=%d",
        payload.mode.value,
        payload.document_type,
        len(payload.key_facts),
    )

    facts = [(f.label, f.value) for f in payload.key_facts]

    result = generate_prompt(
        text=payload.text,
        mode=payload.mode,
        key_facts=facts,
        doc_type=payload.document_type,
        summary=payload.summary,
    )

    logger.info(
        "generated: mode=%s chars=%d followups=%d",
        result.mode.value,
        len(result.prompt),
        len(result.suggested_followups),
    )
    return result
