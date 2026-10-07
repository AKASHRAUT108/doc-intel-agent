"""End-to-end CV pipeline: bytes in → OCRResult out."""
from __future__ import annotations

import logging

from shared.errors import DocumentParseError, UnsupportedFormatError
from shared.schemas import OCRResult

from .layout import analyze_layout
from .ocr import run_ocr
from .pdf import load_image, pdf_to_images

logger = logging.getLogger(__name__)

SUPPORTED = {"application/pdf", "image/png", "image/jpeg", "image/jpg", "image/tiff"}


def process_document(data: bytes, content_type: str) -> OCRResult:
    if content_type not in SUPPORTED:
        raise UnsupportedFormatError(f"Unsupported content type: {content_type}")

    try:
        if content_type == "application/pdf":
            images = pdf_to_images(data)
        else:
            images = [load_image(data)]
    except Exception as e:
        logger.exception("Failed to load document")
        raise DocumentParseError(f"Could not parse document: {e}") from e

    if not images:
        raise DocumentParseError("Document contains no pages")

    all_words = []
    all_regions = []
    page_texts: list[str] = []

    for i, img in enumerate(images):
        logger.info("processing page %d of %d", i + 1, len(images))
        text, words = run_ocr(img)
        regions = analyze_layout(img, page_index=i)
        all_words.extend(words)
        all_regions.extend(regions)
        page_texts.append(text)

    full_text = "\n\n".join(page_texts)

    return OCRResult(
        page_count=len(images),
        full_text=full_text,
        words=all_words,
        regions=all_regions,
    )