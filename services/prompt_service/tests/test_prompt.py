"""Tests for the Prompt Service."""
from __future__ import annotations

from fastapi.testclient import TestClient

from services.prompt_service.app.main import app
from services.prompt_service.app.modes import (
    build_prompt,
    get_role,
)
from services.prompt_service.app.pipeline import generate_prompt
from shared.schemas import PromptMode

TEXT = "Sample document content for testing."
FACTS = [("Label1", "Value1"), ("Label2", "Value2")]


def test_role_for_known_type() -> None:
    assert "financial" in get_role("invoice")
    assert "legal" in get_role("contract")
    assert "project" in get_role("notes")


def test_role_for_unknown_type() -> None:
    assert "analyst" in get_role("something_random")


def test_build_summary_prompt() -> None:
    prompt = build_prompt(PromptMode.SUMMARY, TEXT, FACTS, "notes")
    assert "200-word summary" in prompt
    assert "Label1: Value1" in prompt
    assert TEXT in prompt


def test_build_analyze_prompt() -> None:
    prompt = build_prompt(PromptMode.ANALYZE, TEXT, FACTS, "contract")
    assert "risks" in prompt.lower() or "analyze" in prompt.lower()
    assert "legal expert" in prompt


def test_build_action_prompt() -> None:
    prompt = build_prompt(PromptMode.ACTION, TEXT, FACTS, "notes")
    assert "table" in prompt.lower()
    assert "priority" in prompt.lower()


def test_build_quiz_prompt() -> None:
    prompt = build_prompt(PromptMode.QUIZ, TEXT, FACTS, "notes")
    assert "multiple choice" in prompt.lower()
    assert "answer key" in prompt.lower()


def test_generate_full_result() -> None:
    result = generate_prompt(
        text=TEXT,
        mode=PromptMode.SUMMARY,
        key_facts=FACTS,
        doc_type="notes",
        summary="A test document.",
    )
    assert result.mode == PromptMode.SUMMARY
    assert len(result.prompt) > 100
    assert result.document_type == "notes"


def test_generate_empty_text() -> None:
    result = generate_prompt(text="", mode=PromptMode.SUMMARY)
    assert result.prompt == ""
    assert result.mocked is True


def test_health_endpoint() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "prompt_service"


def test_generate_endpoint() -> None:
    client = TestClient(app)
    r = client.post(
        "/generate",
        json={
            "text": TEXT,
            "mode": "action",
            "key_facts": [{"label": "X", "value": "Y"}],
            "document_type": "notes",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "action"
    assert "table" in body["prompt"].lower()


def test_generate_invalid_mode() -> None:
    client = TestClient(app)
    r = client.post(
        "/generate",
        json={"text": TEXT, "mode": "banana"},
    )
    assert r.status_code == 422  # Pydantic enum rejection
