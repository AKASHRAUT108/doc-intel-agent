"""Simple Streamlit UI - Upload, Summarize, Prompt."""
import sys
from pathlib import Path
import httpx
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

st.set_page_config(page_title="Doc AI", page_icon="📄", layout="wide")

st.title("📄 Document AI Assistant")
st.markdown("Upload a document to get a summary, analysis, and a custom LLM prompt.")

uploaded_file = st.file_uploader("Upload PDF, DOCX, TXT, or Image", type=["pdf", "docx", "txt", "png", "jpg"])

mode = st.radio(
    "What do you want to do?",
    ["Summarize it", "Analyze risks", "Create an action plan", "Generate a quiz"],
    horizontal=True,
)

if st.button("🚀 Process Document", type="primary"):
    if not uploaded_file:
        st.error("Please upload a file first.")
    else:
        with st.spinner("Processing document... This may take a few seconds."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = httpx.post(
                    "http://localhost:8010/simple_process",
                    files=files,
                    params={"mode": mode},
                    timeout=600.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ Processed successfully! ({data['text_length']} characters extracted)")
                    st.divider()

                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("📋 Summary & Analysis")
                        summary = data["summary"]
                        st.info(summary.get("summary", ""))
                        st.write("**Analysis:**")
                        st.write(summary.get("analysis", ""))
                        facts = summary.get("key_facts", [])
                        if facts:
                            st.write("**Key Facts:**")
                            for f in facts:
                                st.markdown(f"- **{f.get('label', '')}:** {f.get('value', '')}")

                    with col2:
                        st.subheader("✨ Copy-Paste Prompt")
                        prompt_data = data["prompt"]
                        st.write("Copy this into ChatGPT, Claude, or Gemini:")
                        st.code(prompt_data.get("prompt", ""), language="markdown")
                        followups = prompt_data.get("followups", [])
                        if followups:
                            st.write("**Try asking:**")
                            for f in followups:
                                st.markdown(f"- {f}")

                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")