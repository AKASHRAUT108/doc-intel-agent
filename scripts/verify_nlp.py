"""Verify NLP service end-to-end."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.nlp_service.app.embed import embed_text
from services.nlp_service.app.ner import extract_entities
from services.nlp_service.app.relations import extract_relations

text = (
    "Acme Corp shall pay $45,000 to Beta LLC by Nov 15, 2026. "
    "Invoice ID: INV-2026-0451. Contact: billing@acme.com."
)

print("=== Input ===")
print(text)

print("\n=== Entities ===")
entities = extract_entities(text)
for e in entities:
    print(f"  [{e.type}] {e.text!r} @ {e.start}-{e.end}")

print("\n=== Relations ===")
relations = extract_relations(text, entities)
for r in relations:
    print(f"  {r.source} --{r.relation}--> {r.target}")

print("\n=== Embedding ===")
vec = embed_text(text)
print(f"  dimension: {len(vec)}")
print(f"  first 5 values: {[round(v, 4) for v in vec[:5]]}")

print("\n✅ NLP pipeline passed")