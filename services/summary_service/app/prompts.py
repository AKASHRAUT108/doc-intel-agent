"""Prompt templates for the Summary Service."""
from __future__ import annotations

SYSTEM_PROMPT = """You are a document analyst AI. Your job is to read documents and extract structured, accurate information.

Rules:
- Use EXACT values from the document (amounts, dates, names).
- Do not invent facts. If something is unknown, use an empty string "".
- Keep summaries concise: 2-3 sentences max.
- For document_type, choose ONE of: invoice, contract, notes, report, letter, form, id, unknown.
- For key_facts, extract 3-6 most important facts as label/value pairs.
- For action_items, list concrete next steps the reader should take.
- For risk_flags, list anything concerning (missing info, unusual values, red flags).
- Return ONLY valid JSON. No markdown fences, no commentary.
"""


def build_summary_prompt(document_text: str, max_chars: int = 8000) -> str:
    """Build the user prompt for summarization."""
    truncated = document_text[:max_chars]
    was_truncated = len(document_text) > max_chars

    truncation_note = ""
    if was_truncated:
        truncation_note = (
            f"\n\n[Note: Document was truncated from "
            f"{len(document_text)} to {max_chars} characters.]"
        )

    return f"""Analyze this document and return JSON matching this exact schema:

{{
  "summary": "string - 2-3 sentence overview",
  "document_type": "invoice | contract | notes | report | letter | form | id | unknown",
  "key_facts": [
    {{"label": "string", "value": "string"}}
  ],
  "action_items": ["string"],
  "risk_flags": ["string"],
  "tldr": "string - one-line summary under 100 chars"
}}

DOCUMENT:
---
{truncated}{truncation_note}
---

Return ONLY the JSON object. No other text.
"""
