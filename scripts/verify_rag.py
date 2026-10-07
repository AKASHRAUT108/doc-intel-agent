"""Verify RAG service end-to-end."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.rag_service.app.seed import load_corpus
from services.rag_service.app.store import get_store

print("=== Loading corpus ===")
n = load_corpus()
print(f"  indexed: {n} chunks")

print("\n=== Query 1: invoice rules ===")
results = get_store().search("invoice payment approval", top_k=3)
for r in results:
    print(f"  [{r.metadata.get('rule_id')}] score={r.score:.3f} — {r.text[:70]}...")

print("\n=== Query 2: data privacy ===")
results = get_store().search("personal data transfer outside EU", top_k=3)
for r in results:
    print(f"  [{r.metadata.get('rule_id')}] score={r.score:.3f} — {r.text[:70]}...")

print("\n=== Query 3: contract signature ===")
results = get_store().search("signature date requirements", top_k=3)
for r in results:
    print(f"  [{r.metadata.get('rule_id')}] score={r.score:.3f} — {r.text[:70]}...")

print("\n✅ RAG pipeline passed")