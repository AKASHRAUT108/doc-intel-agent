"""Tests for the Summary Service."""
from __future__ import annotations

from fastapi.testclient import TestClient

from services.summary_service.app.main import app
from services.summary_service.app.pipeline import summarize_document
from services.summary_service.app.prompts import build_summary_prompt

INVOICE_TEXT = (
    "ACME CORP INVOICE\n"
    "Invoice ID: INV-2026-0451\n"
    "Vendor: Acme Corp\n"
    "Total: $45,000.00\n"
    "Due: November 15, 2026"
)


def test_prompt_builder_includes_text() -> None:
    prompt = build_summary_prompt("Hello world")
    assert "Hello world" in prompt
    assert "key_facts" in prompt


def test_prompt_truncation() -> None:
    long_text = "x" * 10000
    prompt = build_summary_prompt(long_text, max_chars=100)
    assert len(prompt) < 2000  # should be truncated
    assert "truncated" in prompt.lower()


def test_summarize_empty() -> None:
    result = summarize_document("")
    assert result.document_type == "unknown"
    assert "Empty" in result.summary or "empty" in result.summary.lower()


def test_summarize_returns_result() -> None:
    """Live test — uses real LLM if key is set, mock otherwise."""
    result = summarize_document(INVOICE_TEXT)
    # Both real and mocked paths must produce a valid result
    assert result.summary
    assert isinstance(result.key_facts, list)
    assert isinstance(result.action_items, list)


def test_health_endpoint() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "summary_service"


def test_summarize_endpoint() -> None:
    client = TestClient(app)
    r = client.post("/summarize", json={"text": INVOICE_TEXT})
    assert r.status_code == 200
    body = r.json()
    assert "summary" in body
    assert "document_type" in body


def test_summarize_endpoint_empty_text() -> None:
    client = TestClient(app)
    r = client.post("/summarize", json={"text": ""})
    assert r.status_code == 422  # Pydantic min_length=1
