# 📄 Document AI

**Turn any document into structured insights and ready-to-use LLM prompts.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit)](https://doc-intel-agent-koyfkc2m9qomngy22a2hde.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

---

## 🚀 Try It Live

I built this because I was tired of uploading 20-page PDFs into ChatGPT just to get a generic, half-baked answer. 

**Document AI** acts as the missing layer between your documents and LLMs. Upload a file, and it instantly extracts the content, summarizes it, pulls out key facts, and generates a **custom prompt** that you can copy-paste into ChatGPT, Claude, or Gemini to get the *perfect* answer.

👉 **[Test the Live Demo Here](https://doc-intel-agent-koyfkc2m9qomngy22a2hde.streamlit.app)**

> **Note:** The live demo runs in **Demo Mode** so it works 24/7 without burning through API quotas. The real Gemini API pipeline is fully functional and included in the source code.

---

## 📸 The Interface

![Interface](docs/ui-screenshot.png)

*The UI is custom-built with Streamlit and CSS to look like a modern SaaS product, not a typical data science notebook.*

---

## ✨ What It Actually Does

1. **Reads Anything:** PDFs, Word docs (`.docx`), Excel sheets (`.xlsx`), text files, or images.
2. **Analyzes:** Uses Google Gemini 2.5 Flash to understand the context.
3. **Synthesizes:** Generates a 2-sentence summary, a deeper analysis, and a list of key facts.
4. **Writes Prompts:** Creates a specialized prompt based on what you want to do:
   - 📋 **Summarize:** Get a quick recap.
   - 🔍 **Analyze:** Find gaps and risks.
   - ✅ **Action Plan:** Turn the document into a checklist.
   - 🧠 **Quiz:** Test your understanding of the material.

---

## 🛠 The Architecture (Under the Hood)

This isn't just a single Python script. It's a microservices architecture designed to be scalable and resilient.

```text
┌─────────────────┐        ┌──────────────────┐        ┌───────────────┐
│   Streamlit UI  │───────▶│  FastAPI Gateway │───────▶│   Gemini LLM  │
│   (port 8501)   │        │    (port 8010)   │        │   (2.5 Flash) │
└─────────────────┘        └──────────────────┘        └───────────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │   Document       │
                           │   Extractor      │
                           │  (pypdf + OCR)   │
                           └──────────────────┘

The Gateway: A FastAPI service that handles uploads and orchestrates the pipeline.

The Extractor: Smart routing. If it's a digital PDF, it uses pypdf (takes 2 seconds). If it's a scanned image, it falls back to EasyOCR (takes a few minutes).

The Brain: A robust wrapper around Google Gemini that handles rate limits, retries, and strict JSON formatting.

💻 Run It Locally
Want to run the full pipeline with the real Gemini API?

1. Clone & Install
bash
git clone https://github.com/AKASHRAUT108/doc-intel-agent.git
cd doc-intel-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
2. Add Your API Key
Rename .env.example to .env and add your Google Gemini API key:

env
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash
3. Start the App
Open two terminals:

Terminal 1 (Backend):

bash
uvicorn services.api.app.main:app --port 8010
Terminal 2 (Frontend):

bash
streamlit run services/ui/app/main.py
(Note: If you want to test the UI without an API key, change USE_MOCK = True in services/ui/app/main.py).

🧪 Tests & Quality
I built this with production in mind.

60+ unit tests covering extraction, NLP, and API routing.

Dockerized so you can run the whole stack with docker compose up -d.

Ruff for lightning-fast linting.

bash
# Run the test suite
python -m pytest services/ -v
🧠 Tech Stack
Frontend: Streamlit + Custom CSS

Backend: FastAPI, Pydantic

AI / LLM: Google Gemini 2.5 Flash (via google-generativeai)

Document Parsing: pypdf, python-docx, openpyxl, EasyOCR

Deployment: Streamlit Cloud & Docker

🤝 Let's Connect
If you have questions about how I built the async pipeline, handled the Gemini rate limits, or designed the UI, feel free to reach out!

GitHub: @AKASHRAUT108

LinkedIn: https://www.linkedin.com/in/akash-kumar-76274436a/