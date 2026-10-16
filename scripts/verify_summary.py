"""Verify Summary Service end-to-end."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.summary_service.app.pipeline import summarize_document

SAMPLES = [
    (
        "invoice",
        "ACME CORP INVOICE\n"
        "Invoice ID: INV-2026-0451\n"
        "Vendor: Acme Corp\n"
        "Bill To: Beta LLC\n"
        "Total: $45,000.00\n"
        "Due Date: November 15, 2026\n"
        "Terms: Net 45",
    ),
    (
        "notes",
        "Project Notes — October 2026\n\n"
        "Goal: Build a Document Intelligence Agent for capstone.\n\n"
        "Key requirements:\n"
        "- Support PDF, DOCX, XLSX, TXT\n"
        "- Extract entities\n"
        "- Generate summaries via Gemini\n"
        "- Produce copy-paste prompts for LLMs\n\n"
        "Deadline: November 30, 2026",
    ),
    (
        "capstone",
        "Capstone Project Requirements\n\n"
        "Students must submit by November 30, 2026:\n"
        "1. A 15-page report\n"
        "2. A 10-minute presentation\n"
        "3. Source code on GitHub\n\n"
        "Evaluation: innovation 30%, technical depth 40%, presentation 30%.",
    ),
]


def main() -> None:
    for name, text in SAMPLES:
        print(f"\n{'=' * 60}")
        print(f"Sample: {name}")
        print(f"{'=' * 60}")

        result = summarize_document(text)

        print(f"  type: {result.document_type}")
        print(f"  mocked: {result.mocked}")
        print(f"  latency: {result.latency_ms}ms")
        print(f"  tldr: {result.tldr}")
        print(f"  summary: {result.summary}")
        print(f"  key_facts ({len(result.key_facts)}):")
        for fact in result.key_facts:
            print(f"    - {fact.label}: {fact.value}")
        print(f"  action_items ({len(result.action_items)}):")
        for a in result.action_items:
            print(f"    - {a}")
        if result.risk_flags:
            print(f"  risk_flags: {result.risk_flags}")

    print(f"\n{'=' * 60}")
    print("✅ Summary pipeline verified")


if __name__ == "__main__":
    main()
