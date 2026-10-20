"""Test pipeline with multiple file types."""
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

API_URL = "http://localhost:8010"

SAMPLES = [
    ("data/samples/capstone.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("data/samples/grades.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ("data/samples/notes.txt", "text/plain"),
    ("data/samples/invoice.png", "image/png"),
]


def process_file(path: str, mime: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"File: {path}")
    print(f"{'=' * 60}")

    if not Path(path).exists():
        print("⚠️  SKIP — file missing")
        return

    start = time.time()

    # Upload
    with open(path, "rb") as f:
        files = {"file": (Path(path).name, f.read(), mime)}
    r = httpx.post(f"{API_URL}/upload", files=files, params={"mode": "summary"}, timeout=30)

    if r.status_code != 200:
        print(f"❌ Upload failed: {r.status_code} — {r.text[:200]}")
        return

    job = r.json()
    job_id = job["job_id"]
    print(f"  Job: {job_id}")

    # Poll
    for _ in range(60):
        r = httpx.get(f"{API_URL}/status/{job_id}", timeout=10)
        status = r.json()
        s = status.get("status")
        if s in ("done", "failed"):
            break
        time.sleep(2)

    elapsed = time.time() - start

    # Result
    r = httpx.get(f"{API_URL}/result/{job_id}", timeout=30)
    result = r.json()

    print(f"  Status: {result['status']}")
    print(f"  Time: {elapsed:.1f}s")
    if result.get("error"):
        print(f"  Error: {result['error'][:150]}")
        return

    if result.get("ocr"):
        print(f"  OCR: {result['ocr']['page_count']} pages, {len(result['ocr']['full_text'])} chars")
    if result.get("summary"):
        print(f"  Summary type: {result['summary']['document_type']}")
        print(f"  TL;DR: {result['summary']['tldr'][:100]}")
    if result.get("prompt"):
        print(f"  Prompt: {len(result['prompt']['prompt'])} chars")


def main() -> None:
    for path, mime in SAMPLES:
        process_file(path, mime)


if __name__ == "__main__":
    main()
