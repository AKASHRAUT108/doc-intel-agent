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

from shared.schemas import OCRResult

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
    """Extract text from a digital PDF using pypdf.

    pypdf is ~10x faster than pdfplumber for text-only extraction.
    Trade-off: no word-level bboxes. That's fine — downstream doesn't need
    them for text-only PDFs.
    """
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    page_count = len(reader.pages)

    all_text: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        all_text.append(text)

    return OCRResult(
        page_count=page_count,
        full_text="\n\n".join(all_text),
        words=[],
        regions=[],
    )
