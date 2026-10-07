"""Load compliance rules into the vector store."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .store import get_store

logger = logging.getLogger(__name__)

DEFAULT_CORPUS = Path("data/samples/compliance.json")


def load_corpus(path: Path = DEFAULT_CORPUS) -> int:
    """Load JSON corpus into the store. Returns count added."""
    if not path.exists():
        logger.warning("corpus not found: %s", path)
        return 0

    chunks = json.loads(path.read_text(encoding="utf-8"))
    store = get_store()
    return store.add_many(chunks)