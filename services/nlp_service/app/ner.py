"""Entity extraction using regex patterns.

This is a fast, deterministic baseline. Will be augmented with a
fine-tuned BERT NER model in a later stage — same interface.
"""
from __future__ import annotations

import logging
import re

from shared.schemas import Entity

logger = logging.getLogger(__name__)


PATTERNS: dict[str, str] = {
    "AMOUNT": r"\$[\d,]+(?:\.\d{2})?",
    "DATE": (
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]* \d{1,2},? \d{4})\b"
    ),
    "INVOICE_ID": r"\b(?:INV|INVOICE)[- ]?\d{4,}(?:[- ]\d{2,})*\b",
    "EMAIL": r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
    "PARTY": r"\b[A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+){0,3} (?:Corp|LLC|Inc|Ltd|GmbH)\b",
}


def extract_entities(text: str) -> list[Entity]:
    """Extract entities from raw text using regex patterns."""
    entities: list[Entity] = []

    for label, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text):
            entities.append(
                Entity(
                    type=label,
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9,
                )
            )

    # Sort by position in text
    entities.sort(key=lambda e: e.start)
    logger.debug("extracted %d entities", len(entities))
    return entities