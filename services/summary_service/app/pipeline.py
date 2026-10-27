"""Summary pipeline: text in → SummaryResult out."""
from __future__ import annotations

import logging

from shared.llm import get_llm
from shared.schemas import KeyFact, SummaryResult

from .prompts import SYSTEM_PROMPT, build_summary_prompt

logger = logging.getLogger(__name__)


def summarize_document(text: str) -> SummaryResult:
    """Summarize a document using the LLM.

    Always returns a SummaryResult. On LLM/parse failure, returns a
    fallback with an error note instead of raising.
    """
    if not text or not text.strip():
        return _empty_summary("Empty document")

    prompt = build_summary_prompt(text)
    llm = get_llm()

    # Try twice with the LLM (some calls succeed on retry)
    last_error = None
    for attempt in range(2):
        try:
            data, llm_result = llm.generate_json(
                prompt=prompt,
                system=SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.2 + (attempt * 0.1),  # slight variation
            )
            return _build_result(data, text, llm_result)
        except Exception as e:
            last_error = e
            logger.warning("LLM attempt %d failed: %s", attempt + 1, e)

    logger.error("LLM failed twice — using fallback")
    return _fallback_summary(text, reason=f"LLM call failed: {last_error}")

def _build_result(data: dict, text: str, llm_result) -> SummaryResult:
    """Convert raw LLM JSON to a validated SummaryResult."""
    try:
        key_facts = [
            KeyFact(label=str(f.get("label", "")), value=str(f.get("value", "")))
            for f in (data.get("key_facts") or [])
            if isinstance(f, dict) and f.get("label") and f.get("value")
        ]

        return SummaryResult(
            summary=str(data.get("summary") or ""),
            document_type=str(data.get("document_type") or "unknown"),
            key_facts=key_facts,
            action_items=[str(a) for a in (data.get("action_items") or []) if a],
            risk_flags=[str(r) for r in (data.get("risk_flags") or []) if r],
            tldr=str(data.get("tldr") or "")[:200],
            word_count=len(text.split()),
            model=llm_result.model,
            latency_ms=llm_result.latency_ms,
            mocked=llm_result.mocked,
        )
    except Exception:
        logger.exception("failed to build result from LLM output")
        return _fallback_summary(text, reason="Invalid LLM output format")


def _empty_summary(reason: str) -> SummaryResult:
    return SummaryResult(
        summary=reason,
        document_type="unknown",
        key_facts=[],
        action_items=[],
        risk_flags=[],
        tldr=reason,
        word_count=0,
    )


def _fallback_summary(text: str, reason: str) -> SummaryResult:
    """Return a minimal summary when LLM fails."""
    preview = text[:200].strip().replace("\n", " ")
    return SummaryResult(
        summary=f"[Fallback] {reason}. Document preview: {preview}...",
        document_type="unknown",
        key_facts=[],
        action_items=[],
        risk_flags=[reason],
        tldr=f"[Fallback] {reason}",
        word_count=len(text.split()),
        model="fallback",
        mocked=True,
    )
