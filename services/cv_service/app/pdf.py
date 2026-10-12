"""PDF and image loading utilities.

Two paths for PDFs:
- Digital PDFs: extract text layer directly (fast, accurate).
- Scanned PDFs: convert to images and run OCR (slow, may have errors).
"""
from __future__ import annotations

import io
import logging

import pdfplumber
from pdf2image import convert_from_bytes
from PIL import Image

from shared.schemas import BBox, OCRResult, OCRWord

logger = logging.getLogger(__name__)

DEFAULT_DPI = 200


# -----------------------------------------------------------------------------
# Image loading
# -----------------------------------------------------------------------------

def load_image(data: bytes) -> Image.Image:
    """Load a single image from bytes and normalize to RGB."""
    return Image.open(io.BytesIO(data)).convert("RGB")


def pdf_to_images(pdf_bytes: bytes, dpi: int = DEFAULT_DPI) -> list[Image.Image]:
    """Convert a PDF's bytes into a list of PIL images (one per page)."""
    images = convert_from_bytes(pdf_bytes, dpi=dpi, fmt="png")
    return [img.convert("RGB") for img in images]


# -----------------------------------------------------------------------------
# Digital PDF text extraction
# -----------------------------------------------------------------------------

def pdf_has_text_layer(pdf_bytes: bytes, sample_pages: int = 3) -> bool:
    """Return True if the PDF contains extractable text (digital, not scanned)."""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages[:sample_pages]:
                text = page.extract_text() or ""
                if len(text.strip()) > 50:
                    return True
    except Exception:
        logger.exception("failed to probe PDF text layer")
    return False


def extract_pdf_text(pdf_bytes: bytes) -> OCRResult:
    """Extract text from a digital PDF (no OCR needed).

    Note: pdfplumber returns text without per-word bounding boxes in
    the simple API, so we approximate bboxes as empty/full-page spans.
    Downstream code that needs bboxes uses OCR path instead.
    """
    all_text: list[str] = []
    all_words: list[OCRWord] = []
    regions: list = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page_count = len(pdf.pages)
        for page_idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            all_text.append(text)

            # Extract word-level bboxes when available
            try:
                for word in page.extract_words():
                    all_words.append(
                        OCRWord(
                            text=word["text"],
                            bbox=BBox(
                                x1=float(word["x0"]),
                                y1=float(word["top"]),
                                x2=float(word["x1"]),
                                y2=float(word["bottom"]),
                            ),
                            confidence=1.0,
                        )
                    )
            except Exception:
                logger.debug("no word boxes on page %d", page_idx)

    return OCRResult(
        page_count=page_count,
        full_text="\n\n".join(all_text),
        words=all_words,
        regions=regions,
    )
