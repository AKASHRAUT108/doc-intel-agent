"""Tests for the NLP service."""
from __future__ import annotations

from fastapi.testclient import TestClient

from services.nlp_service.app.embed import embed_text
from services.nlp_service.app.main import app
from services.nlp_service.app.ner import extract_entities
from services.nlp_service.app.relations import extract_relations

SAMPLE = (
    "Acme Corp shall pay $45,000 to Beta LLC by Nov 15, 2026. "
    "Invoice ID: INV-2026-0451."
)


def test_extract_amount():
    entities = extract_entities(SAMPLE)
    types = [e.type for e in entities]
    assert "AMOUNT" in types
    assert "$45,000" in [e.text for e in entities]


def test_extract_parties():
    entities = extract_entities(SAMPLE)
    parties = [e.text for e in entities if e.type == "PARTY"]
    assert "Acme Corp" in parties
    assert "Beta LLC" in parties


def test_extract_date():
    entities = extract_entities(SAMPLE)
    dates = [e.text for e in entities if e.type == "DATE"]
    assert "Nov 15, 2026" in dates


def test_extract_invoice_id():
    entities = extract_entities(SAMPLE)
    ids = [e.text for e in entities if e.type == "INVOICE_ID"]
    assert "INV-2026-0451" in ids


def test_relations():
    entities = extract_entities(SAMPLE)
    relations = extract_relations(SAMPLE, entities)
    assert any(r.relation == "OWES" for r in relations)
    assert any(r.relation == "ISSUED" for r in relations)


def test_embedding_dimension():
    vec = embed_text(SAMPLE)
    assert len(vec) == 384


def test_embedding_normalized():
    vec = embed_text(SAMPLE)
    norm = sum(v * v for v in vec) ** 0.5
    assert abs(norm - 1.0) < 0.01  # L2 norm ≈ 1


def test_health_endpoint():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "nlp_service"


def test_extract_endpoint():
    client = TestClient(app)
    r = client.post("/extract", json={"text": SAMPLE})
    assert r.status_code == 200
    body = r.json()
    assert len(body["entities"]) > 0
    assert len(body["embedding"]) == 384