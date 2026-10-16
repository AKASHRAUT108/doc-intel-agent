"""Verify Gemini LLM client."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.llm import get_llm

llm = get_llm()

print("=== Test 1: text generation ===")
result = llm.generate(
    "In one sentence, what is a document intelligence system?",
    max_tokens=100,
)
print(f"  mocked: {result.mocked}")
print(f"  model: {result.model}")
print(f"  latency: {result.latency_ms} ms")
print(f"  text: {result.text}")

print("\n=== Test 2: JSON generation ===")
prompt = (
    "Return a JSON object with keys 'title' (string) and 'count' (integer). "
    "Set title to 'Sample Doc' and count to 42."
)
data, result2 = llm.generate_json(prompt, max_tokens=200)
print(f"  mocked: {result2.mocked}")
print(f"  parsed: {data}")

print("\n✅ LLM client verified")
