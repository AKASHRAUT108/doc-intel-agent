"""Simple, synchronous pipeline for fast processing without microservices."""
from __future__ import annotations

import logging
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from services.cv_service.app.extractor import extract
from shared.llm import get_llm
from shared.schemas import PromptMode

logger = logging.getLogger(__name__)
router = APIRouter()


class SimpleResponse(BaseModel):
    text_length: int
    summary: dict
    prompt: dict


@router.post("/simple_process", response_model=SimpleResponse)
async def process_document(file: UploadFile = File(...), mode: str = "summary"):
    logger.info(f"Simple process started for {file.filename}")

    # 1. Extract Text
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")

    try:
        ocr_result = extract(content, file.content_type or "application/pdf", filename=file.filename)
        text = ocr_result.full_text
        if not text.strip():
            raise ValueError("No text could be extracted from this document.")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(400, f"Extraction failed: {str(e)}")

    # 2. Summarize & Analyze via Gemini
    llm = get_llm()

    summary_prompt = f"""
Analyze the following document.
Return ONLY a JSON object with:
- "summary": A 2-sentence overview.
- "key_facts": A list of 3-5 objects with "label" and "value".
- "analysis": A brief paragraph of insights/risks.

Document Text:
{text[:15000]}
"""

    try:
        summary_data, _ = llm.generate_json(prompt=summary_prompt, max_tokens=2048)
    except Exception as e:
        logger.error(f"Summary failed: {e}")
        summary_data = {
            "summary": f"LLM Error: {e}",
            "key_facts": [],
            "analysis": str(e),
        }

    # 3. Generate Prompt via Gemini
    prompt_prompt = f"""
Based on this document, generate a copy-paste prompt that a user can put into ChatGPT.
The goal is to {mode}.
Return ONLY a JSON object with:
- "prompt": The actual prompt text to copy.
- "followups": A list of 3 alternative questions the user could ask.

Document Text:
{text[:15000]}
"""

    try:
        prompt_data, _ = llm.generate_json(prompt=prompt_prompt, max_tokens=2048)
    except Exception as e:
        logger.error(f"Prompt failed: {e}")
        prompt_data = {
            "prompt": f"LLM Error: {e}",
            "followups": [],
        }

    return SimpleResponse(
        text_length=len(text),
        summary=summary_data,
        prompt=prompt_data,
    )