"""End-to-end CV pipeline: bytes in → OCRResult out.

Routes to the right extractor based on content type:
- PDFs (digital or scanned)
- Images
- DOCX
- XLSX
- TXT/MD/CSV
"""
from __future__ import annotations

import logging

from shared.errors import DocIntelError, DocumentParseError, UnsupportedFormatError
from shared.schemas import OCRResult

from .extractor import extract

logger = logging.getLogger(__name__)


def process_document(data: bytes, content_type: str) -> OCRResult:
    """Extract text + layout from any supported document."""
    if not data:
        raise DocumentParseError("Empty file")

    # Pass through our known domain errors (UnsupportedFormatError, etc.)
    # Only wrap truly unexpected exceptions.
    try:
        result = extract(data, content_type)
    except (UnsupportedFormatError, DocumentParseError):
        raise
    except DocIntelError:
        raise
    except Exception as e:
        logger.exception("failed to process document")
        raise DocumentParseError(f"Could not parse document: {e}") from e

    logger.info(
        "processed %s: %d pages, %d words, %d regions",
        content_type,
        result.page_count,
        len(result.words),
        len(result.regions),
    )
    return result