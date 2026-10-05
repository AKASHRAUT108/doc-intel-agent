# Architecture

## Pipeline

1. Upload (API)
2. CV Service — Layout analysis + OCR
3. NLP Service — NER + relation extraction
4. RAG Service — Compliance retrieval
5. Agent Service — LangGraph reasoning
6. LLM Service — Summaries + reports
7. UI — Human review

## Diagram (to be added)

\`\`\`
Upload → CV → NLP → RAG → Agent → LLM → UI
\`\`\`

## Services

| Service | Port | Role |
|---|---|---|
| api | 8000 | Gateway |
| cv_service | 8001 | Vision |
| nlp_service | 8002 | NLP |
| rag_service | 8003 | Retrieval |
| agent_service | 8004 | Reasoning |
| llm_service | 8005 | Generation |
| ui | 8501 | Review |