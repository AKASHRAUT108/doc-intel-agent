"""FastAPI entry point for the NLP service."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from shared.logging import get_logger, setup_logging
from shared.schemas import NERResult

from .embed import embed_text
from .ner import extract_entities
from .relations import extract_relations

setup_logging()
logger = get_logger("nlp_service")

app = FastAPI(
    title="NLP Service",
    description="Entity, relation, and embedding extraction.",
    version="0.1.0",
)


class TextIn(BaseModel):
    text: str
    include_embedding: bool = True


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "nlp_service"}


@app.post("/extract", response_model=NERResult)
def extract(payload: TextIn) -> NERResult:
    logger.info("extracting from %d chars", len(payload.text))
    entities = extract_entities(payload.text)
    relations = extract_relations(payload.text, entities)
    embedding = embed_text(payload.text) if payload.include_embedding else None
    return NERResult(entities=entities, relations=relations, embedding=embedding)