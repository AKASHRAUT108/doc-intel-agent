"""Verify multi-format document loading."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.cv_service.app.pipeline import process_document

SAMPLES = [
    ("data/samples/invoice.png", "image/png"),
    ("data/samples/invoice.pdf", "application/pdf"),
    ("data/samples/capstone.docx",
     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("data/samples/grades.xlsx",
     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ("data/samples/notes.txt", "text/plain"),
]


def main() -> None:
    for path, mime in SAMPLES:
        p = Path(path)
        if not p.exists():
            print(f"⚠️  skip {path} (missing)")
            continue

        print(f"\n=== {path} ({mime}) ===")
        data = p.read_bytes()
        try:
            result = process_document(data, mime)
            print(f"  pages: {result.page_count}")
            print(f"  words: {len(result.words)}")
            print(f"  chars: {len(result.full_text)}")
            preview = result.full_text[:150].replace("\n", "\\n")
            print(f"  preview: {preview!r}")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")

    print("\n✅ Loader verification complete")


if __name__ == "__main__":
    main()
