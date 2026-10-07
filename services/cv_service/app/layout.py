"""Layout region analysis (heuristic fallback)."""
from __future__ import annotations

import logging

from PIL import Image

from shared.schemas import BBox, LayoutRegion, RegionLabel

logger = logging.getLogger(__name__)


def analyze_layout(image: Image.Image, page_index: int = 0) -> list[LayoutRegion]:
    """Return a list of layout regions for a single page."""
    w, h = image.size

    return [
        LayoutRegion(
            label=RegionLabel.HEADER,
            bbox=BBox(x1=0, y1=0, x2=float(w), y2=float(h) * 0.15),
            page=page_index,
        ),
        LayoutRegion(
            label=RegionLabel.PARAGRAPH,
            bbox=BBox(x1=0, y1=float(h) * 0.15, x2=float(w), y2=float(h) * 0.85),
            page=page_index,
        ),
        LayoutRegion(
            label=RegionLabel.FOOTER,
            bbox=BBox(x1=0, y1=float(h) * 0.85, x2=float(w), y2=float(h)),
            page=page_index,
        ),
    ]