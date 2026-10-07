"""Tests for the CV service."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from services.cv_service.app.layout import analyze_layout
from services.cv_service.app.main import app
from services.cv_service.app.pdf import load_image
from services.cv_service.app.pipeline import process_document

SAMPLE = Path("data/samples/invoice.png")


@pytest.fixture(scope="module")
def sample_bytes() -> bytes:
    if not SAMPLE.exists():
        pytest.skip(f"Missing sample: {SAMPLE}")
    return SAMPLE.read_bytes()


@pytest.fixture(scope="module")
def sample_image(sample_bytes: bytes) -> Image.Image:
    return load_image(sample_bytes)


def test_load_image(sample_image: Image.Image) -> None:
    assert sample_image.mode == "RGB"
    assert sample_image.size[0] > 0


def test_layout_regions(sample_image: Image.Image) -> None:
    regions = analyze_layout(sample_image)
    assert len(regions) == 3
    labels = [r.label.value for r in regions]
    assert "header" in labels
    assert "footer" in labels


def test_pipeline_runs(sample_bytes: bytes) -> None:
    result = process_document(sample_bytes, "image/png")
    assert result.page_count == 1
    assert len(result.words) > 0
    assert "ACME" in result.full_text.upper()


def test_pipeline_rejects_unsupported() -> None:
    from shared.errors import UnsupportedFormatError

    with pytest.raises(UnsupportedFormatError):
        process_document(b"x", "application/zip")


def test_health_endpoint() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "cv_service"


def test_extract_endpoint(sample_bytes: bytes) -> None:
    client = TestClient(app)
    r = client.post(
        "/extract",
        files={"file": ("invoice.png", sample_bytes, "image/png")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["page_count"] == 1
    assert len(body["words"]) > 0