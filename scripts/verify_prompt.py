"""Verify Prompt Service end-to-end."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.prompt_service.app.pipeline import generate_prompt
from shared.schemas import PromptMode

SAMPLE_TEXT = (
    "Capstone Project Requirements\n\n"
    "Students must submit by November 30, 2026:\n"
    "1. A 15-page report\n"
    "2. A 10-minute presentation\n"
    "3. Source code on GitHub\n\n"
    "Evaluation: innovation 30%, technical depth 40%, presentation 30%."
)

SAMPLE_FACTS = [
    ("Deadline", "November 30, 2026"),
    ("Report Length", "15-page"),
    ("Presentation Duration", "10-minute"),
]

SAMPLE_SUMMARY = (
    "A capstone project brief requiring a report, presentation, "
    "and source code submission by Nov 30, 2026."
)


def main() -> None:
    for mode in PromptMode:
        print(f"\n{'=' * 70}")
        print(f"MODE: {mode.value.upper()}")
        print(f"{'=' * 70}")

        result = generate_prompt(
            text=SAMPLE_TEXT,
            mode=mode,
            key_facts=SAMPLE_FACTS,
            doc_type="notes",
            summary=SAMPLE_SUMMARY,
        )

        print(f"  doc_type: {result.document_type}")
        print(f"  mocked: {result.mocked}")
        print(f"  prompt length: {len(result.prompt)} chars")
        print("\n--- PROMPT ---")
        print(result.prompt[:600] + ("..." if len(result.prompt) > 600 else ""))

        if result.suggested_followups:
            print("\n--- SUGGESTED FOLLOW-UPS ---")
            for f in result.suggested_followups:
                print(f"  • {f}")

    print(f"\n{'=' * 70}")
    print("✅ Prompt pipeline verified")


if __name__ == "__main__":
    main()
