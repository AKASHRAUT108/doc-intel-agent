"""Document AI — Professional Interface."""
import os
import sys
import time
from pathlib import Path
import httpx
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
API_URL = os.getenv("API_URL", "http://localhost:8010")
USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

# -----------------------------------------------------------------------------
# Page Config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Document AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Custom CSS — Professional Theme
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .stApp {
        background: #f8fafc;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Container */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 4rem;
        max-width: 1200px;
    }
    
    /* Main title */
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }
    
    .main-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 2.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .demo-badge {
        background: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Section headings */
    .section-heading {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
    }
    
    /* Custom buttons */
    .stButton > button[kind="primary"] {
        background: #0f172a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #1e293b;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 1rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #0f172a;
    }
    
    /* Radio buttons */
    [data-testid="stRadio"] > div {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Result cards */
    .result-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .result-card p {
        color: #334155;
        line-height: 1.6;
        margin: 0.5rem 0;
    }
    
    .fact-row {
        display: flex;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .fact-label {
        font-weight: 500;
        color: #64748b;
        width: 180px;
        flex-shrink: 0;
        font-size: 0.875rem;
    }
    
    .fact-value {
        color: #0f172a;
        font-size: 0.875rem;
    }
    
    .followup-item {
        padding: 0.5rem 0;
        color: #334155;
        font-size: 0.875rem;
        border-bottom: 1px solid #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">Document AI</div>', unsafe_allow_html=True)

badge_html = '<span class="demo-badge">DEMO MODE</span>' if USE_MOCK else ''
st.markdown(
    f'<div class="main-subtitle">Upload any document and get a structured summary, analysis, and a ready-to-use prompt for any LLM. {badge_html}</div>',
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Main Layout — Left input, right output
# -----------------------------------------------------------------------------
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown('<div class="section-heading">Upload Document</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "xlsx", "txt", "png", "jpg"],
        label_visibility="collapsed",
    )
    
    st.markdown('<div class="section-heading" style="margin-top: 1.5rem;">Task</div>', unsafe_allow_html=True)
    
    mode = st.radio(
        "Task",
        options=[
            "Summarize the document",
            "Analyze for risks and gaps",
            "Create an action plan",
            "Generate a comprehension quiz",
        ],
        label_visibility="collapsed",
    )
    
    mode_map = {
        "Summarize the document": "summary",
        "Analyze for risks and gaps": "analyze",
        "Create an action plan": "action",
        "Generate a comprehension quiz": "quiz",
    }
    
    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
    
    process_clicked = st.button(
        "Process Document",
        type="primary",
        use_container_width=True,
    )

# -----------------------------------------------------------------------------
# Output Section
# -----------------------------------------------------------------------------
with col_output:
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)
    
    result_placeholder = st.empty()
    
    if process_clicked:
        if not uploaded_file:
            result_placeholder.error("Please upload a document first.")
        else:
            with result_placeholder.container():
                with st.spinner("Processing document..."):
                    try:
                        if USE_MOCK:
                            # --- MOCK MODE ---
                            time.sleep(2)  # Simulate processing delay
                            file_name = uploaded_file.name
                            
                            data = {
                                "text_length": 3812,
                                "summary": {
                                    "summary": f"This document ({file_name}) contains educational content covering key concepts, definitions, and practical examples. It is structured for learning and reference purposes.",
                                    "analysis": "The material is well-organized with clear sections. It covers fundamental topics that are important for understanding the subject. Several concepts build on each other logically.",
                                    "key_facts": [
                                        {"label": "Document Type", "value": "Educational / Reference"},
                                        {"label": "Total Pages", "value": "5"},
                                        {"label": "Complexity Level", "value": "Intermediate"},
                                        {"label": "Key Topics", "value": "Fundamentals, Definitions, Applications"}
                                    ]
                                },
                                "prompt": {
                                    "prompt": f"Context: I am analyzing the document '{file_name}'.\n\nPlease provide a comprehensive summary of this document focusing on:\n1. The main objective of the document\n2. 3-5 key concepts explained\n3. Any action items or important takeaways\n\nFormat as: Executive Summary, Key Concepts, and Next Steps.",
                                    "followups": [
                                        "Can you explain the most complex concept in simpler terms?",
                                        "What are the most important 3 facts I should memorize?",
                                        "Create a 5-question quiz based on this material."
                                    ]
                                }
                            }
                        else:
                            # --- REAL API MODE ---
                            files = {
                                "file": (
                                    uploaded_file.name,
                                    uploaded_file.getvalue(),
                                    uploaded_file.type,
                                )
                            }
                            response = httpx.post(
                                f"{API_URL}/simple_process",
                                files=files,
                                params={"mode": mode_map[mode]},
                                timeout=600.0,
                            )
                            response.raise_for_status()
                            data = response.json()
                        
                        # --- RENDER RESULTS ---
                        st.success(f"Processed successfully — {data['text_length']} characters extracted")
                        st.divider()
                        
                        # SUMMARY
                        summary = data["summary"]
                        st.markdown("### Summary")
                        st.markdown(f'<div class="result-card"><p>{summary.get("summary", "")}</p></div>', unsafe_allow_html=True)
                        
                        # ANALYSIS
                        analysis = summary.get("analysis", "")
                        if analysis:
                            st.markdown("### Analysis")
                            st.markdown(f'<div class="result-card"><p>{analysis}</p></div>', unsafe_allow_html=True)
                        
                        # KEY FACTS
                        facts = summary.get("key_facts", [])
                        if facts:
                            st.markdown("### Key Facts")
                            fact_html = '<div class="result-card">'
                            for f in facts:
                                fact_html += f'<div class="fact-row"><div class="fact-label">{f.get("label", "")}</div><div class="fact-value">{f.get("value", "")}</div></div>'
                            fact_html += '</div>'
                            st.markdown(fact_html, unsafe_allow_html=True)
                        
                        # PROMPT
                        prompt_data = data["prompt"]
                        prompt_text = prompt_data.get("prompt", "")
                        if prompt_text:
                            st.markdown("### Copy-Paste Prompt")
                            st.caption("Click the copy icon in the top right of the box below.")
                            st.code(prompt_text, language="markdown")
                        
                        # FOLLOWUPS
                        followups = prompt_data.get("followups", [])
                        if followups:
                            st.markdown("### Follow-Up Questions")
                            follow_html = '<div class="result-card">'
                            for f in followups:
                                follow_html += f'<div class="followup-item">{f}</div>'
                            follow_html += '</div>'
                            st.markdown(follow_html, unsafe_allow_html=True)
                    
                    except Exception as e:
                        result_placeholder.error(f"Processing failed: {e}")
    else:
        with result_placeholder.container():
            st.markdown(
                '<div class="result-card" style="text-align: center; padding: 3rem 1.5rem;">'
                '<p style="color: #94a3b8;">Upload a document and click Process to see results here.</p>'
                '</div>',
                unsafe_allow_html=True,
            )