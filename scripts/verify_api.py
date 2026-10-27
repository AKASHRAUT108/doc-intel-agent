"""Verify API Gateway — full end-to-end pipeline test.

Requires all services running:
  uvicorn services.cv_service.app.main:app --port 8001
  uvicorn services.nlp_service.app.main:app --port 8002
  uvicorn services.rag_service.app.main:app --port 8003
  uvicorn services.summary_service.app.main:app --port 8005
  uvicorn services.prompt_service.app.main:app --port 8006
  uvicorn services.api.app.main:app --port 8000
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

API_URL = os.getenv("API_URL", "http://localhost:8010")
SAMPLE = Path("data/samples/capstone.docx")


def wait_for_status(job_id: str, timeout: float = 180.0) -> dict:
    """Poll /status until terminal state or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        r = httpx.get(f"{API_URL}/status/{job_id}", timeout=10)
        r.raise_for_status()
        data = r.json()
        status = data.get("status")
        print(f"  ... status: {status}")
        if status in ("done", "failed"):
            return data
        time.sleep(3)
    raise TimeoutError(f"Job {job_id} did not finish in {timeout}s")


def main() -> None:
    if not SAMPLE.exists():
        print(f"❌ Sample file not found: {SAMPLE}")
        print("   Run a service and check the sample was committed.")
        sys.exit(1)

    print("=== 1. Health check ===")
    r = httpx.get(f"{API_URL}/health", timeout=10)
    print(f"  {r.json()}")

    print(f"\n=== 2. Upload {SAMPLE.name} ===")

    # Detect MIME type from extension
    mime_map = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".txt": "text/plain",
        ".md": "text/markdown",
    }
    mime = mime_map.get(SAMPLE.suffix.lower(), "application/octet-stream")
    print(f"  mime type: {mime}")

    with SAMPLE.open("rb") as f:
        files = {"file": (SAMPLE.name, f.read(), mime)}
    r = httpx.post(f"{API_URL}/upload", files=files, params={"mode": "summary"}, timeout=30)
    r.raise_for_status()
    job = r.json()
    job_id = job["job_id"]
    print(f"  job_id: {job_id}")
    print(f"  status: {job['status']}")

    print("\n=== 3. Poll status ===")
    wait_for_status(job_id)

    print("\n=== 4. Fetch result ===")
    r = httpx.get(f"{API_URL}/result/{job_id}", timeout=30)
    r.raise_for_status()
    result = r.json()

    print(f"  status: {result['status']}")
    if result.get("error"):
        print(f"  error: {result['error']}")

    if result.get("ocr"):
        print(f"  OCR: {result['ocr']['page_count']} pages, {len(result['ocr']['words'])} words")

    if result.get("entities"):
        print(f"  Entities: {len(result['entities']['entities'])} extracted")

    if result.get("summary"):
        s = result["summary"]
        print(f"  Summary type: {s['document_type']}")
        print(f"  TL;DR: {s['tldr']}")
        print(f"  Key facts: {len(s['key_facts'])}")
        for fact in s["key_facts"][:3]:
            print(f"    - {fact['label']}: {fact['value']}")

    if result.get("prompt"):
        p = result["prompt"]
        print(f"  Prompt mode: {p['mode']}")
        print(f"  Prompt chars: {len(p['prompt'])}")
        print(f"  Follow-ups: {len(p['suggested_followups'])}")

    print(f"\n{'=' * 60}")
    print("✅ API Gateway verified")


if __name__ == "__main__":
    main()
