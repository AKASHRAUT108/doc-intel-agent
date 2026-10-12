"""In-memory vector store for compliance and knowledge-base retrieval.

Design notes:
- Uses Sentence-BERT embeddings + cosine similarity.
- Interface is designed to be drop-in replaceable with Weaviate / Chroma.
- Embeddings are L2-normalized so dot product == cosine similarity.
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

    def __init__(self, model: SentenceTransformer) -> None:
        self._model = model
        self._texts: list[str] = []
        self._metadata: list[dict] = []
        self._vectors: list[np.ndarray] = []

    def add_many(self, chunks: list[dict]) -> int:
        """Add chunks (each: {text, metadata}) to the store.

        Returns the number of chunks actually added.
        """
        added = 0
        for chunk in chunks:
            text = (chunk.get("text") or "").strip()
            if not text:
                continue

            vec = self._model.encode(text, normalize_embeddings=True)
            self._texts.append(text)
            self._metadata.append(chunk.get("metadata") or {})
            self._vectors.append(np.asarray(vec, dtype=np.float32))
            added += 1

        logger.info("added %d chunks (total now: %d)", added, len(self._texts))
        return added

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return top-k most similar chunks ordered by score (descending)."""
        if not self._vectors:
            return []

        q = self._model.encode(query, normalize_embeddings=True)
        q = np.asarray(q, dtype=np.float32)

        matrix = np.stack(self._vectors)          # shape: (N, 384)
        sims = matrix @ q                          # shape: (N,)
        top_idx = np.argsort(-sims)[:top_k]        # descending

        return [
            RetrievedChunk(
                id=str(int(i)),
                text=self._texts[int(i)],
                score=float(sims[int(i)]),
                metadata=self._metadata[int(i)],
            )
            for i in top_idx
        ]

    def size(self) -> int:
        return len(self._texts)


@lru_cache(maxsize=1)
def get_store() -> VectorStore:
    """Return a singleton store (loads model only once per process)."""
    logger.info("loading Sentence-BERT model: %s", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)
    return VectorStore(model)
