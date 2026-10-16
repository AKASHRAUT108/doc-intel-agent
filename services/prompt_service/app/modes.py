"""Prompt templates for the 4 generation modes.

Each mode produces a ready-to-paste prompt that includes:
- A role assignment (who the LLM should act as)
- The document content
- Extracted key facts
- A specific task
"""
from __future__ import annotations

from shared.schemas import PromptMode

# Roles assigned to the target LLM per document type
DOC_TYPE_ROLES: dict[str, str] = {
    "invoice": "a financial analyst",
    "contract": "a legal expert",
    "notes": "a project manager",
    "report": "a business analyst",
    "letter": "a communications specialist",
    "form": "a data entry specialist",
    "id": "a verification specialist",
    "unknown": "a document analyst",
}


def get_role(doc_type: str) -> str:
    """Return the appropriate role for the target LLM."""
    return DOC_TYPE_ROLES.get(doc_type, DOC_TYPE_ROLES["unknown"])


def build_summary_prompt(text: str, facts: list[tuple[str, str]], doc_type: str) -> str:
    role = get_role(doc_type)
    facts_block = _format_facts(facts)
    return f"""You are {role}. Below is content from a {doc_type} document.

DOCUMENT CONTENT:
---
{text}
---

KEY FACTS:
{facts_block}

TASK: Provide a clear, structured 200-word summary covering:
1. The document's purpose
2. Key requirements, facts, or figures
3. Who needs to act and by when

Then suggest 3 questions a reader might have about this document.

Format your response with headings. Be concise."""


def build_analyze_prompt(text: str, facts: list[tuple[str, str]], doc_type: str) -> str:
    role = get_role(doc_type)
    facts_block = _format_facts(facts)
    return f"""You are {role} reviewing a {doc_type} document.

DOCUMENT CONTENT:
---
{text}
---

KEY FACTS:
{facts_block}

TASK: Analyze this document thoroughly:
1. Summarize the key claims or commitments
2. Identify potential risks, gaps, or contradictions
3. Surface hidden assumptions
4. List missing information that would matter for decisions

Structure your response with clear headings. Cite specific sections of the document. Flag anything that seems unusual or concerning."""


def build_action_prompt(text: str, facts: list[tuple[str, str]], doc_type: str) -> str:
    role = get_role(doc_type)
    facts_block = _format_facts(facts)
    return f"""You are {role} turning a {doc_type} document into an action plan.

DOCUMENT CONTENT:
---
{text}
---

KEY FACTS:
{facts_block}

TASK: Extract every actionable item and produce a markdown table with columns:
| Task | Deadline | Owner | Priority | Dependencies |

Priority is high/medium/low. If a field is not stated, write "not specified".

After the table, add a "Next 24 hours" section listing the 3 most urgent actions."""


def build_quiz_prompt(text: str, facts: list[tuple[str, str]], doc_type: str) -> str:
    role = get_role(doc_type)
    facts_block = _format_facts(facts)
    return f"""You are {role} creating a quiz from a {doc_type} document.
    ...DOCUMENT CONTENT:
---
{text}
---

KEY FACTS:
{facts_block}

TASK: Generate a comprehension quiz with:
- 5 multiple choice questions (4 options each, mark the correct one)
- 3 short-answer questions
- 2 application or analysis questions

Provide an answer key at the end with brief explanations for each answer.

Number all questions. Use clear formatting."""


def build_prompt(mode: PromptMode, text: str, facts: list[tuple[str, str]], doc_type: str) -> str:
    """Dispatch to the correct template based on mode."""
    if mode == PromptMode.SUMMARY:
        return build_summary_prompt(text, facts, doc_type)
    if mode == PromptMode.ANALYZE:
        return build_analyze_prompt(text, facts, doc_type)
    if mode == PromptMode.ACTION:
        return build_action_prompt(text, facts, doc_type)
    if mode == PromptMode.QUIZ:
        return build_quiz_prompt(text, facts, doc_type)
    raise ValueError(f"Unknown mode: {mode}")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _format_facts(facts: list[tuple[str, str]]) -> str:
    """Format key facts as a bullet list."""
    if not facts:
        return "(no facts extracted)"
    return "\n".join(f"- {label}: {value}" for label, value in facts)
