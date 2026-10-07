"""PDF and image loading utilities."""
from __future__ import annotations

import io

from PIL import Image
from pdf2image import convert_from_bytes

DEFAULT_DPI = 200


def pdf_to_images(pdf_bytes: bytes, dpi: int = DEFAULT_DPI) -> list[Image.Image]:
    """Convert a PDF's bytes into a list of PIL images (one per page)."""
    images = convert_from_bytes(pdf_bytes, dpi=dpi, fmt="png")
    return [img.convert("RGB") for img in images]


def load_image(data: bytes) -> Image.Image:
    """Load a single image from bytes and normalize to RGB."""
    return Image.open(io.BytesIO(data)).convert("RGB")