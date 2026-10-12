"""Tests for the RAG service."""
from __future__ import annotations

from fastapi.testclient import TestClient

from services.rag_service.app.main import app
from services.rag_service.app.seed import load_corpus
from services.rag_service.app.store import get_store


def test_corpus_loads() -> None:
    n = load_corpus()
    assert n > 0


def test_store_size() -> None:
    load_corpus()
    assert get_store().size() >= 8


def test_search_invoice() -> None:
    load_corpus()
    results = get_store().search("invoice payment rules", top_k=3)
    assert len(results) == 3
    rule_ids = [r.metadata.get("rule_id") for r in results]
    assert "POL-101" in rule_ids


def test_search_gdpr() -> None:
    load_corpus()
    results = get_store().search("GDPR personal data", top_k=3)
    rule_ids = [r.metadata.get("rule_id") for r in results]
    assert any("GDPR" in (rid or "") for rid in rule_ids)


def test_search_scores_sorted() -> None:
    load_corpus()
    results = get_store().search("vendor approval", top_k=5)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_health_endpoint() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "rag_service"


def test_retrieve_endpoint() -> None:
    client = TestClient(app)
    r = client.post("/retrieve", json={"query": "invoice purchase order", "top_k": 2})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2


def test_index_endpoint() -> None:
    client = TestClient(app)
    r = client.post(
        "/index",
        json={"chunks": [{"text": "Test rule for indexing.", "metadata": {"rule_id": "TEST-1"}}]},
    )
    assert r.status_code == 200
    assert r.json()["indexed"] == 1
