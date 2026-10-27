"""Prompt generation pipeline."""
from __future__ import annotations

import logging

from shared.llm import get_llm
from shared.schemas import PromptMode, PromptResult

from .modes import build_prompt

logger = logging.getLogger(__name__)


MAX_FULLTEXT_CHARS = 6000


FOLLOWUP_SYSTEM = """You are a prompt-engineering assistant.

Given a document summary, suggest 3 follow-up prompts a user might want to try next.
Each should be a single sentence, different angle from the main task, and specific to this document.

Return JSON: {"followups": ["prompt 1", "prompt 2", "prompt 3"]}
"""


def generate_prompt(
    text: str,
    mode: PromptMode,
    key_facts: list[tuple[str, str]] | None = None,
    doc_type: str = "unknown",
    summary: str = "",
) -> PromptResult:
    """Generate a paste-ready prompt for the given mode."""
    if not text or not text.strip():
        return PromptResult(
            mode=mode,
            prompt="",
            suggested_followups=[],
            document_type="unknown",
            model="",
            mocked=True,
        )

    facts = key_facts or []

    # 1. Build main prompt from template (deterministic, free)
    main_prompt = build_prompt(
        mode=mode,
        text=text[:MAX_FULLTEXT_CHARS],
        facts=facts,
        doc_type=doc_type,
    )

    # 2. Ask LLM for follow-up prompt ideas (optional, cheap)
    followups, model, latency_ms, mocked = _suggest_followups(
        mode=mode, summary=summary, doc_type=doc_type
    )

    return PromptResult(
        mode=mode,
        prompt=main_prompt,
        suggested_followups=followups,
        document_type=doc_type,
        model=model,
        latency_ms=latency_ms,
        mocked=mocked,
    )


def _suggest_followups(
    mode: PromptMode, summary: str, doc_type: str
) -> tuple[list[str], str, int, bool]:
    """Ask the LLM for 3 follow-up prompt ideas."""
    if not summary.strip():
        return ([], "", 0, False)

    prompt = (
        f"Document type: {doc_type}\n"
        f"Already generated mode: {mode.value}\n"
        f"Document summary: {summary}\n\n"
        "Suggest 3 follow-up prompts the user might want next."
    )

    try:
        llm = get_llm()
        data, llm_result = llm.generate_json(
            prompt=prompt,
            system=FOLLOWUP_SYSTEM,
            max_tokens=800,
            temperature=0.7,
        )
        followups = [
            str(x) for x in (data.get("followups") or []) if isinstance(x, str)
        ][:3]
        return (followups, llm_result.model, llm_result.latency_ms, llm_result.mocked)
    except Exception:
        logger.exception("follow-up suggestion failed")
        return ([], "fallback", 0, True)
