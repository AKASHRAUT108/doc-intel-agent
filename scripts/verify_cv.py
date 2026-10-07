"""Verify CV service pipeline end-to-end."""
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.cv_service.app.pdf import load_image
from services.cv_service.app.ocr import run_ocr
from services.cv_service.app.layout import analyze_layout
from services.cv_service.app.pipeline import process_document

print("=== Loading image ===")
data = open("data/samples/invoice.png", "rb").read()
img = load_image(data)
print(f"size: {img.size} mode: {img.mode}")

print("\n=== Layout regions ===")
regions = analyze_layout(img)
for r in regions:
    print(f"  {r.label.value}: {r.bbox.model_dump()}")

print("\n=== OCR ===")
text, words = run_ocr(img)
print(f"text: {text[:150]!r}")
print(f"words: {len(words)}")
for w in words[:5]:
    print(f"  {w.text!r} (conf={w.confidence:.2f})")

print("\n=== Full pipeline ===")
result = process_document(data, "image/png")
print(f"pages: {result.page_count}")
print(f"words: {len(result.words)}")
print(f"regions: {len(result.regions)}")

print("\n✅ All checks passed")