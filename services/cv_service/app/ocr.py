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
    # Disable unnecessary detection steps for speed
    # batch_size and workers optimize CPU usage
    return easyocr.Reader(
        ["en"],
        gpu=False,
        verbose=False,
        model_storage_directory=None,  # use default
        download_enabled=True,
    )

def run_ocr(image: Image.Image) -> tuple[str, list[OCRWord]]:
    """Run OCR on a PIL image, return (full_text, words)."""
    try:
        reader = _get_reader()
    except Exception:
        logger.exception("Failed to initialize EasyOCR reader")
        return "", []

    # Upscale small images for better OCR accuracy
    w, h = image.size
    if w < 500 or h < 500:
        scale = max(500 / w, 500 / h)
        new_size = (int(w * scale), int(h * scale))
        logger.info("upscaling small image from %dx%d to %dx%d", w, h, *new_size)
        image = image.resize(new_size, Image.LANCZOS)

    arr = np.array(image)

    try:
        # Use paragraph=False for speed; combine into lines afterward
        raw = reader.readtext(
            arr,
            detail=1,
            paragraph=False,
            decoder="greedy",  # faster than beam search
            beamWidth=5,
            batch_size=1,
            workers=0,
        )
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
