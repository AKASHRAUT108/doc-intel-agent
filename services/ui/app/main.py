"""Streamlit UI for the Document Intelligence Agent."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

# Make project root importable
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from services.ui.app.api_client import APIClient

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Doc Intel Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

client = APIClient()

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------

if "job_id" not in st.session_state:
    st.session_state.job_id = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_filename" not in st.session_state:
    st.session_state.last_filename = None

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    st.header("📄 Doc Intel Agent")
    st.caption("Turn any document into a summary + LLM-ready prompt.")

    health = client.health()
    if health.get("status") == "ok":
        st.success("✅ API Gateway online")
    else:
        st.error("❌ API Gateway unreachable")
        st.code(str(health.get("error", "")), language="text")

    st.divider()
    st.subheader("Recent Jobs")
    recent = client.list_jobs(limit=8)
    if not recent:
        st.caption("No jobs yet.")
    else:
        for job in recent:
            status_icon = {
                "done": "✅",
                "failed": "❌",
                "processing": "⏳",
                "queued": "⏸",
            }.get(job["status"], "•")
            label = f"{status_icon} `{job['job_id'][:6]}` {job['filename'][:22]}"
            if st.button(label, key=f"recent_{job['job_id']}", use_container_width=True):
                st.session_state.job_id = job["job_id"]
                st.session_state.last_filename = job["filename"]
                st.session_state.last_result = None

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------

st.title("Document Intelligence Agent")
st.caption(
    "Upload any document. Get a structured summary and a paste-ready prompt "
    "for ChatGPT, Claude, or Gemini."
)

# -----------------------------------------------------------------------------
# Input section
# -----------------------------------------------------------------------------

col_upload, col_options = st.columns([2, 1])

with col_upload:
    st.subheader("1. Upload a document")
    uploaded = st.file_uploader(
        "PDF, DOCX, XLSX, TXT, PNG, JPG",
        type=["pdf", "docx", "xlsx", "txt", "md", "csv", "png", "jpg", "jpeg"],
        accept_multiple_files=False,
    )

with col_options:
    st.subheader("2. Pick a mode")
    mode = st.radio(
        "What do you want to do?",
        options=["summary", "analyze", "action", "quiz"],
        format_func=lambda m: {
            "summary": "📋 Summary — recap",
            "analyze": "🔍 Analyze — risks & gaps",
            "action": "✅ Action — checklist",
            "quiz": "🧠 Quiz — test understanding",
        }.get(m, m),
        label_visibility="collapsed",
    )

st.divider()

# -----------------------------------------------------------------------------
# Process button
# -----------------------------------------------------------------------------

if uploaded is not None:
    st.info(f"**{uploaded.name}** ({uploaded.size:,} bytes)")

    if st.button("🚀 Process Document", type="primary", use_container_width=True):
        with st.spinner("Uploading..."):
            try:
                content = uploaded.read()
                job = client.upload(uploaded.name, content, mode=mode)
                st.session_state.job_id = job["job_id"]
                st.session_state.last_filename = uploaded.name
                st.session_state.last_result = None
            except Exception as e:
                st.error(f"Upload failed: {e}")
                st.stop()

# -----------------------------------------------------------------------------
# Live status
# -----------------------------------------------------------------------------

if st.session_state.job_id:
    job_id = st.session_state.job_id
    st.divider()
    st.subheader(f"3. Processing — `{job_id}`")

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Poll until done or failed
    max_wait = 600
    start = time.time()
    result = None

    while time.time() - start < max_wait:
        try:
            status = client.status(job_id)
        except Exception as e:
            status_text.error(f"Status error: {e}")
            break

        s = status.get("status", "unknown")
        progress_map = {
            "queued": 0.10,
            "processing": 0.60,
            "done": 1.0,
            "failed": 1.0,
        }
        progress_bar.progress(progress_map.get(s, 0.05))

                # Detailed status with step context.
        # JobRecord only updates AFTER each step completes, so during
        # step 1 (OCR) all result fields are None. Default to step 1
        # while processing and refine as fields appear.
        if s == "queued":
            status_text.info("⏸ **Queued** — waiting to start")
        elif s == "processing":
            ocr_done = status.get("ocr") is not None
            nlp_done = status.get("entities") is not None
            summary_done = status.get("summary") is not None
            prompt_done = status.get("prompt") is not None

            if prompt_done:
                status_text.info("✨ **Finishing up** — almost done")
            elif summary_done:
                status_text.info("✨ **Step 4/4** — Generating prompt")
            elif nlp_done:
                status_text.info("📝 **Step 3/4** — Generating summary")
            elif ocr_done:
                status_text.info("🧠 **Step 2/4** — Extracting entities")
            else:
                status_text.info(
                    "👁 **Step 1/4** — Extracting text "
                    "(fast for digital PDFs, slow for scanned)"
                )
        elif s == "done":
            status_text.success("✅ **Done** — results below")
        elif s == "failed":
            status_text.error(f"❌ **Failed** — {status.get('error', 'unknown')}")
        if s in ("done", "failed"):
            try:
                result = client.result(job_id)
                st.session_state.last_result = result
            except Exception as e:
                st.error(f"Could not fetch result: {e}")
            break

        time.sleep(2)

    if time.time() - start >= max_wait:
        elapsed = int(time.time() - start)
        status_text.warning(
            f"⏱ Still processing after {elapsed}s. "
            "Scanned PDFs can take several minutes. "
            "Check the 'Recent Jobs' sidebar to see the result when done."
        )
# -----------------------------------------------------------------------------
# Result rendering
# -----------------------------------------------------------------------------

result = st.session_state.last_result

if result:
    status = result.get("status")

    if status == "failed":
        st.error(f"❌ Processing failed: {result.get('error', 'unknown error')}")
    elif status == "done":
        st.success("✅ Processing complete")

        summary = result.get("summary")
        prompt = result.get("prompt")
        ocr = result.get("ocr")
        entities = result.get("entities")

        # Top metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Pages", ocr["page_count"] if ocr else "—")
        with m2:
            st.metric("Words", len(ocr["words"]) if ocr else "—")
        with m3:
            st.metric("Entities", len(entities["entities"]) if entities else "—")
        with m4:
            doc_type = summary["document_type"] if summary else "unknown"
            st.metric("Type", doc_type.title())

        st.divider()

        # Summary + Prompt side by side
        col_summary, col_prompt = st.columns(2)

        with col_summary:
            st.subheader("📋 Summary")
            if summary:
                st.markdown(f"**TL;DR:** {summary.get('tldr', '')}")
                st.write(summary.get("summary", ""))

                facts = summary.get("key_facts", [])
                if facts:
                    st.markdown("**Key Facts**")
                    for f in facts:
                        st.markdown(f"- **{f['label']}:** {f['value']}")

                actions = summary.get("action_items", [])
                if actions:
                    st.markdown("**Action Items**")
                    for a in actions:
                        st.markdown(f"- {a}")

                risks = summary.get("risk_flags", [])
                if risks:
                    st.markdown("**⚠️ Risk Flags**")
                    for r in risks:
                        st.markdown(f"- {r}")
            else:
                st.caption("No summary available.")

        with col_prompt:
            st.subheader("✨ Generated Prompt")
            if prompt:
                st.caption(
                    f"Mode: **{prompt['mode']}** — copy the prompt below "
                    "into ChatGPT, Claude, or Gemini."
                )
                st.code(prompt["prompt"], language="markdown")

                followups = prompt.get("suggested_followups", [])
                if followups:
                    st.markdown("**💡 Suggested Follow-ups**")
                    for f in followups:
                        st.markdown(f"- {f}")
            else:
                st.caption("No prompt generated.")

        # Raw OCR (collapsed)
        if ocr and ocr.get("full_text"):
            with st.expander("🔧 Extracted Text (raw OCR)"):
                st.text(ocr["full_text"][:3000])
