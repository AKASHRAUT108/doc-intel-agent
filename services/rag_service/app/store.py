"""In-memory vector store for compliance rules.

Uses Sentence-BERT embeddings + cosine similarity.
Interface is designed to be swapped for Weaviate later.
"""
from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from shared.schemas import RetrievedChunk

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


class VectorStore:
    """Simple in-memory vector store with cosine similarity search."""

    def __init__(self, model: SentenceTransformer):
        self._model = model
        self._texts: list[str] = []
        self._metadata: list[dict] = []
        self._vectors: list[np.ndarray] = []

    def add_many(self, chunks: list[dict]) -> int:
        """Add chunks (each: {text, metadata}) to the store."""
        added = 0
        for chunk in chunks:
            text = chunk.get("text", "").strip()
            if not text:
                continue
            vec = self._model.encode(text, normalize_embeddings=True)
            self._texts.append(text)
            self._metadata.append(chunk.get("metadata", {}))
            self._vectors.append(np.array(vec))
            added += 1
        logger.info("added %d chunks (total: %d)", added, len(self._texts))
        return added

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return top-k most similar chunks."""
        if not self._vectors:
            return []

        q = self._model.encode(query, normalize_embeddings=True)
        sims = np.dot(np.stack(self._vectors), q)
        top_idx = np.argsort(-sims)[:top_k]

        return [
            RetrievedChunk(
                id=str(i),
                text=self._texts[i],
                score=float(sims[i]),
                metadata=self._metadata[i],
            )
            for i in top_idx
        ]

    def size(self) -> int:
        return len(self._texts)


@lru_cache(maxsize=1)
def get_store() -> VectorStore:
    """Singleton store (loads model once)."""
    logger.info("loading model: %s", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)
    return VectorStore(model)