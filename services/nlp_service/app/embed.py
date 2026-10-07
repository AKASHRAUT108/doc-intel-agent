"""Sentence-BERT embeddings."""
from __future__ import annotations

import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    logger.info("loading Sentence-BERT model: %s", MODEL_NAME)
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    """Return a normalized 384-dim embedding."""
    if not text.strip():
        return []
    model = _get_model()
    vec = model.encode(text[:512], normalize_embeddings=True)
    return vec.tolist()