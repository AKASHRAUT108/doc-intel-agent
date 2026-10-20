"""Routes incoming files to the correct extractor by MIME type."""
from __future__ import annotations

import logging

from shared.errors import UnsupportedFormatError
from shared.schemas import OCRResult

from .docx_loader import extract_docx
from .pdf import extract_pdf_text, pdf_has_text_layer, pdf_to_images
from .text_loader import extract_text
from .xlsx_loader import extract_xlsx

logger = logging.getLogger(__name__)

# MIME types
PDF_MIMES = {"application/pdf"}
IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/tiff"}
DOCX_MIMES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}
XLSX_MIMES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}
TEXT_MIMES = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "text/x-markdown",
}

SUPPORTED = PDF_MIMES | IMAGE_MIMES | DOCX_MIMES | XLSX_MIMES | TEXT_MIMES


def extract(
    data: bytes,
    content_type: str,
    filename: str | None = None,
) -> OCRResult:
    """Extract text from any supported file type.

    Handles edge cases:
    - application/octet-stream (browsers sometimes send this)
    - application/x-www-form-urlencoded (legacy uploads)
    - No content_type at all
    - Content type with charset suffix (e.g. text/plain; charset=utf-8)

    Falls back to filename-based detection when MIME is unreliable.
    """
    # Normalize content_type (strip charset, whitespace, lowercase)
    if content_type:
        content_type = content_type.split(";")[0].strip().lower()

    # If content type is empty or generic, try filename
    if not content_type or content_type in (
        "application/octet-stream",
        "application/x-www-form-urlencoded",
        "binary/octet-stream",
    ):
        if filename:
            guessed = guess_mime_from_filename(filename)
            if guessed:
                logger.info(
                    "content_type %r generic/empty, guessed %r from %r",
                    content_type, guessed, filename,
                )
                content_type = guessed

    # Still unsupported? Try filename anyway
    if content_type not in SUPPORTED and filename:
        guessed = guess_mime_from_filename(filename)
        if guessed and guessed in SUPPORTED:
            logger.info(
                "content_type %r unsupported, forced %r from %r",
                content_type, guessed, filename,
            )
            content_type = guessed

    if content_type not in SUPPORTED:
        raise UnsupportedFormatError(
            f"Unsupported content type: {content_type} "
            f"(filename: {filename})"
        )

    # Route to correct handler
    if content_type in PDF_MIMES:
        return _handle_pdf(data)
    if content_type in IMAGE_MIMES:
        return _handle_image(data)
    if content_type in DOCX_MIMES:
        return extract_docx(data)
    if content_type in XLSX_MIMES:
        return extract_xlsx(data)
    if content_type in TEXT_MIMES:
        return extract_text(data)

    raise UnsupportedFormatError(f"No handler for: {content_type}")

def _handle_pdf(data: bytes) -> OCRResult:
    """Detect digital vs scanned PDF; route accordingly."""
    if pdf_has_text_layer(data):
        logger.info("PDF has text layer — fast extract")
        return extract_pdf_text(data)

    logger.info("PDF is scanned — falling back to OCR")
    return _ocr_images(pdf_to_images(data))


def _handle_image(data: bytes) -> OCRResult:
    from .pdf import load_image

    return _ocr_images([load_image(data)])


def _ocr_images(images: list) -> OCRResult:
    """Run OCR + layout on a list of images."""
    from .layout import analyze_layout
    from .ocr import run_ocr

    all_words: list = []
    all_regions: list = []
    page_texts: list[str] = []

    for i, img in enumerate(images):
        logger.info("OCR page %d of %d", i + 1, len(images))
        text, words = run_ocr(img)
        regions = analyze_layout(img, page_index=i)
        all_words.extend(words)
        all_regions.extend(regions)
        page_texts.append(text)

    return OCRResult(
        page_count=len(images),
        full_text="\n\n".join(page_texts),
        words=all_words,
        regions=all_regions,
    )
