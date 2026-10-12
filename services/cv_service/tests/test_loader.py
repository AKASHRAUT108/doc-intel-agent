"""Tests for multi-format loaders."""
from __future__ import annotations

from pathlib import Path

import pytest

from services.cv_service.app.docx_loader import extract_docx
from services.cv_service.app.extractor import SUPPORTED, extract
from services.cv_service.app.text_loader import extract_text
from services.cv_service.app.xlsx_loader import extract_xlsx

ROOT = Path("data/samples")


def test_supported_types() -> None:
    assert "application/pdf" in SUPPORTED
    assert "image/png" in SUPPORTED
    assert "text/plain" in SUPPORTED


def test_text_loader() -> None:
    result = extract_text(b"Hello world")
    assert result.full_text == "Hello world"
    assert result.page_count == 1


def test_text_loader_utf8_fallback() -> None:
    # Invalid UTF-8 bytes
    result = extract_text(b"\xff\xfehello")
    assert "hello" in result.full_text


def test_docx_loader() -> None:
    p = ROOT / "capstone.docx"
    if not p.exists():
        pytest.skip("sample missing")
    result = extract_docx(p.read_bytes())
    assert "Capstone" in result.full_text or "capstone" in result.full_text.lower()


def test_xlsx_loader() -> None:
    p = ROOT / "grades.xlsx"
    if not p.exists():
        pytest.skip("sample missing")
    result = extract_xlsx(p.read_bytes())
    assert "Sheet" in result.full_text
    assert "Alice" in result.full_text


def test_extract_routes_txt() -> None:
    result = extract(b"plain text here", "text/plain")
    assert result.full_text == "plain text here"


def test_extract_unsupported() -> None:
    from shared.errors import UnsupportedFormatError

    with pytest.raises(UnsupportedFormatError):
        extract(b"x", "application/zip")


def test_extract_docx_via_router() -> None:
    p = ROOT / "capstone.docx"
    if not p.exists():
        pytest.skip("sample missing")
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    result = extract(p.read_bytes(), mime)
    assert len(result.full_text) > 50
