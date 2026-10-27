"""Diagnose why Gemini fails on certain file types."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.llm import get_llm
from services.summary_service.app.prompts import SYSTEM_PROMPT, build_summary_prompt

TEXTS = {
    "capstone": (
        "Capstone Project Requirements. Students must submit by November 30, 2026: "
        "1. A 15-page report 2. A 10-minute presentation 3. Source code on GitHub"
    ),
    "grades": (
        "### Sheet: Grades\nStudent | Subject | Score | Grade\n"
        "Alice | Math | 92 | A\nBob | Math | 78 | B\n"
        "### Sheet: Summary\nSubject | Average\nMath | 85.0"
    ),
    "notes": (
        "Project Notes. Goal: Build a Document Intelligence Agent for capstone. "
        "Support PDF, DOCX, XLSX, TXT. Deadline: November 30, 2026"
    ),
    "invoice": (
        "ACME CORP INVOICE\nInvoice ID: INV-2026-0451\n"
        "Total: $45,000.00\nDue: November 15, 2026"
    ),
}


def main() -> None:
    llm = get_llm()
    print(f"LLM mocked: {llm._mock}")
    print(f"LLM model: {llm._model_name}")
    print()

    for name, text in TEXTS.items():
        print(f"{'=' * 60}")
        print(f"Testing: {name} ({len(text)} chars)")
        print(f"{'=' * 60}")

        try:
            data, result = llm.generate_json(
                prompt=build_summary_prompt(text),
                system=SYSTEM_PROMPT,
                max_tokens=1024,
                temperature=0.2,
            )
            print(f"  ✅ Success")
            print(f"  Model: {result.model}")
            print(f"  Latency: {result.latency_ms}ms")
            print(f"  Keys: {list(data.keys())}")
            print(f"  Summary: {data.get('summary', '')[:100]}...")
        except Exception as e:
            print(f"  ❌ Failed: {type(e).__name__}: {e}")
        print()


if __name__ == "__main__":
    main()