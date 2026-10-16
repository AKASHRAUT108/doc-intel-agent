"""HTTP clients for calling downstream services.

Thin wrappers that hide URLs and error handling from the orchestrator.
"""
from __future__ import annotations

import logging

import httpx

from shared.config import get_settings
from shared.errors import DocIntelError
from shared.schemas import (
    NERResult,
    OCRResult,
    PromptMode,
    PromptResult,
    SummaryResult,
)

logger = logging.getLogger(__name__)

# Timeouts
OCR_TIMEOUT = 120.0       # OCR can take a while on large scans
LLM_TIMEOUT = 90.0        # LLM calls can take 10-30s
DEFAULT_TIMEOUT = 30.0


class ServiceError(DocIntelError):
    """Raised when a downstream service fails."""
    http_status = 502


# -----------------------------------------------------------------------------
# CV Service
# -----------------------------------------------------------------------------

def call_cv_service(file_bytes: bytes, filename: str, content_type: str) -> OCRResult:
    """Send a file to CV Service for OCR / extraction."""
    settings = get_settings()
    url = f"{settings.cv_service_url}/extract"

    files = {"file": (filename, file_bytes, content_type)}
    try:
        r = httpx.post(url, files=files, timeout=OCR_TIMEOUT)
        r.raise_for_status()
        return OCRResult.model_validate(r.json())
    except httpx.HTTPError as e:
        logger.exception("CV service call failed")
        raise ServiceError(f"CV service error: {e}") from e


# -----------------------------------------------------------------------------
# NLP Service
# -----------------------------------------------------------------------------

def call_nlp_service(text: str) -> NERResult:
    """Send text to NLP Service for entity extraction + embeddings."""
    settings = get_settings()
    url = f"{settings.nlp_service_url}/extract"

    try:
        r = httpx.post(url, json={"text": text, "include_embedding": False}, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return NERResult.model_validate(r.json())
    except httpx.HTTPError as e:
        logger.exception("NLP service call failed")
        raise ServiceError(f"NLP service error: {e}") from e


# -----------------------------------------------------------------------------
# Summary Service
# -----------------------------------------------------------------------------

def call_summary_service(text: str) -> SummaryResult:
    """Send text to Summary Service for LLM summarization."""
    settings = get_settings()
    url = f"{settings.summary_service_url}/summarize"

    try:
        r = httpx.post(url, json={"text": text}, timeout=LLM_TIMEOUT)
        r.raise_for_status()
        return SummaryResult.model_validate(r.json())
    except httpx.HTTPError as e:
        logger.exception("Summary service call failed")
        raise ServiceError(f"Summary service error: {e}") from e


# -----------------------------------------------------------------------------
# Prompt Service
# -----------------------------------------------------------------------------

def call_prompt_service(
    text: str,
    mode: PromptMode,
    summary: SummaryResult | None = None,
) -> PromptResult:
    """Generate a prompt for the given mode."""
    settings = get_settings()
    url = f"{settings.prompt_service_url}/generate"

    key_facts = []
    if summary and summary.key_facts:
        key_facts = [{"label": f.label, "value": f.value} for f in summary.key_facts]

    payload = {
        "text": text,
        "mode": mode.value,
        "key_facts": key_facts,
        "document_type": summary.document_type if summary else "unknown",
        "summary": summary.summary if summary else "",
    }

    try:
        r = httpx.post(url, json=payload, timeout=LLM_TIMEOUT)
        r.raise_for_status()
        return PromptResult.model_validate(r.json())
    except httpx.HTTPError as e:
        logger.exception("Prompt service call failed")
        raise ServiceError(f"Prompt service error: {e}") from e
