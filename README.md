<div align="center">

# Document AI

**Turn any document into structured insights and ready-to-use LLM prompts.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge)](https://doc-intel-agent-koyfkc2m9qomngy22a2hde.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

**[Try the Live Demo](https://doc-intel-agent-koyfkc2m9qomngy22a2hde.streamlit.app)** | **[Quick Start](#quick-start)** | **[Report a Bug](https://github.com/AKASHRAUT108/doc-intel-agent/issues)**

</div>

---

## Screenshot

<div align="center">
  <img src="docs/ui-screenshot.png" alt="Document AI Interface" width="900"/>
</div>

---

## The Problem

You upload a 20-page PDF to ChatGPT. You ask *"Summarize this."* You get a generic answer that misses half the details, or worse — the LLM runs out of context window and forgets the document entirely.

**Document AI fixes this.** It's a preprocessing layer that turns any document into the *perfect* LLM prompt for your specific goal.

---

## How It Works

1. **Reads Anything** — PDFs, Word docs, Excel sheets, images (PNG/JPG)
2. **Extracts Text** — Smart routing: `pypdf` for digital PDFs (5s), `EasyOCR` for scanned docs
3. **Understands** — Google Gemini 2.5 Flash analyzes the content
4. **Generates** — Creates a 2-sentence summary, deep analysis, key facts, and a **specialized prompt**

### 4 Prompt Modes

| Mode | What It Does | Use Case |
|---|---|---|
| **Summarize** | Quick recap | Skim a long report |
| **Analyze** | Find gaps & risks | Due diligence on contracts |
| **Action Plan** | Turn docs into checklists | Extract TODOs from notes |
| **Quiz** | Test your understanding | Study from textbooks |

---

## Architecture

Document AI is built as **7 microservices** with a simple synchronous endpoint for fast, reliable demos:

```text
+-----------------+        +------------------+        +---------------+
|   Streamlit UI  |------->|  FastAPI Gateway |------->|   Gemini LLM  |
|   (port 8501)   |        |    (port 8010)   |        |   (2.5 Flash) |
+-----------------+        +------------------+        +---------------+
                                    |
                                    v
                           +------------------+
                           |   Document       |
                           |   Extractor      |
                           |  (pypdf + OCR)   |
                           +------------------+


                           Key Components
Layer	Purpose	Tech
Frontend	User interface	Streamlit + Custom CSS
API Gateway	Upload handler + orchestrator	FastAPI
Document Extractor	Text extraction with smart routing	pypdf + EasyOCR
LLM Wrapper	Gemini client with retries, JSON mode	google-generativeai
Quick Start
Prerequisites
Python 3.11+

Google Gemini API Key (get one free)

1. Clone & Install
bash
git clone https://github.com/AKASHRAUT108/doc-intel-agent.git
cd doc-intel-agent

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
2. Configure
bash
cp .env.example .env
Edit .env and add your Gemini API key:

env
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash
3. Run Locally
Terminal 1 — Backend:

bash
uvicorn services.api.app.main:app --port 8010
Terminal 2 — Frontend:

bash
streamlit run services/ui/app/main.py
Open http://localhost:8501

No API key? Change USE_MOCK = True in services/ui/app/main.py to test the UI without hitting Gemini.

Testing
bash
# Run all 60+ tests
python -m pytest services/ -v

# Run only the API tests
python -m pytest services/api/tests -v

# Lint the codebase
python -m ruff check services/
Test coverage:

Document extraction (PDF, DOCX, XLSX, TXT, images)

NER and entity extraction

API routing and error handling

LLM wrapper (retries, JSON parsing, rate limits)

Docker Deployment
The entire stack is containerized:

bash
docker compose up -d
Open http://localhost:8501 — the app runs in 2 containers (API + UI).

Project Stats
Metric	Count
Microservices	7
Unit tests	60+
Supported formats	5 (PDF, DOCX, XLSX, TXT, images)
Prompt modes	4
Lines of code	~5,000
Tech Stack
Frontend: Streamlit, custom CSS

Backend: FastAPI, Pydantic

LLM: Google Gemini 2.5 Flash

Document Parsing: pypdf, python-docx, openpyxl, EasyOCR

Testing: pytest

Linting: ruff

Deployment: Streamlit Cloud + Docker

Roadmap
☑ Multi-format document support
☑ Gemini LLM integration
☑ Professional UI
☑ Docker deployment
☑ Live demo on Streamlit Cloud
□ RAG over a compliance knowledge base
□ BERT NER (replace regex)
□ Multi-page PDF chunking for large documents
□ User authentication
Contributing
Contributions are welcome! Please open an issue first to discuss changes.

License
MIT © Akash Kumar

Acknowledgments
Google Gemini — The LLM layer

EasyOCR and pypdf — Document extraction

Streamlit — Rapid UI prototyping

<div align="center">
