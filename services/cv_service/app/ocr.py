"""OCR wrapper around EasyOCR."""
from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
from PIL import Image

from shared.schemas import BBox, OCRWord

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_reader():
    import easyocr

    logger.info("initializing EasyOCR (first call downloads models)")
    return easyocr.Reader(["en"], gpu=False, verbose=False)


def run_ocr(image: Image.Image) -> tuple[str, list[OCRWord]]:
    """Run OCR on a PIL image, return (full_text, words)."""
    try:
        reader = _get_reader()
    except Exception:
        logger.exception("Failed to initialize EasyOCR reader")
        return "", []

    arr = np.array(image)

    try:
        raw = reader.readtext(arr, detail=1, paragraph=False)
    except Exception:
        logger.exception("OCR failed")
        return "", []

    words: list[OCRWord] = []
    lines: list[str] = []

    for item in raw or []:
        try:
            box, text, conf = item
        except (ValueError, TypeError):
            continue

        xs = [float(p[0]) for p in box]
        ys = [float(p[1]) for p in box]

        words.append(
            OCRWord(
                text=text,
                bbox=BBox(x1=min(xs), y1=min(ys), x2=max(xs), y2=max(ys)),
                confidence=float(conf),
            )
        )
        lines.append(text)

    return "\n".join(lines), words