"""Plain-text loader for .txt, .md, .csv files."""
from __future__ import annotations

import logging

from shared.schemas import OCRResult

logger = logging.getLogger(__name__)


def extract_text(data: bytes) -> OCRResult:
    """Decode bytes into text. Tries UTF-8, falls back to latin-1."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning("utf-8 decode failed, falling back to latin-1")
        text = data.decode("latin-1", errors="replace")

    return OCRResult(
        page_count=1,
        full_text=text,
        words=[],
        regions=[],
    )
