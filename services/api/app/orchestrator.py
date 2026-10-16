"""Job orchestrator — runs the full pipeline for a job."""
from __future__ import annotations

import asyncio
import logging

from shared.schemas import PromptMode

from .clients import (
    ServiceError,
    call_cv_service,
    call_nlp_service,
    call_prompt_service,
    call_summary_service,
)
from .jobs import get_job, mark_done, mark_failed, mark_processing, save_job

logger = logging.getLogger(__name__)


async def run_pipeline(
    job_id: str,
    file_bytes: bytes,
    filename: str,
    content_type: str,
    mode: PromptMode = PromptMode.SUMMARY,
) -> None:
    """Execute the full pipeline for a job. Never raises.

    All blocking HTTP calls are wrapped in `asyncio.to_thread` so they
    don't block the event loop.
    """
    logger.info("starting job %s (mode=%s)", job_id, mode.value)

    rec = mark_processing(job_id)
    if rec is None:
        logger.error("job %s disappeared before processing", job_id)
        return

    try:
        # 1. CV — extract text
        logger.info("[%s] step 1/4: CV service", job_id)
        ocr = await asyncio.to_thread(
            call_cv_service, file_bytes, filename, content_type
        )
        rec.ocr = ocr
        save_job(rec)

        text = ocr.full_text or ""
        if not text.strip():
            raise RuntimeError("No text extracted from document")

        # 2. NLP — entities (non-fatal)
        logger.info("[%s] step 2/4: NLP service", job_id)
        try:
            entities = await asyncio.to_thread(call_nlp_service, text)
            rec.entities = entities
            save_job(rec)
        except ServiceError as e:
            logger.warning("[%s] NLP failed (continuing): %s", job_id, e)

        # 3. Summary — LLM (non-fatal)
        logger.info("[%s] step 3/4: Summary service", job_id)
        summary = None
        try:
            summary = await asyncio.to_thread(call_summary_service, text)
            rec.summary = summary
            save_job(rec)
        except ServiceError as e:
            logger.warning("[%s] Summary failed (continuing): %s", job_id, e)

        # 4. Prompt — LLM (non-fatal)
        logger.info("[%s] step 4/4: Prompt service", job_id)
        try:
            prompt = await asyncio.to_thread(
                call_prompt_service, text, mode, summary
            )
            rec.prompt = prompt
            save_job(rec)
        except ServiceError as e:
            logger.warning("[%s] Prompt failed (continuing): %s", job_id, e)

        mark_done(job_id)
        logger.info("job %s completed", job_id)

    except Exception as e:
        logger.exception("job %s failed", job_id)
        mark_failed(job_id, error=str(e))


def _get_job_or_raise(job_id: str):
    rec = get_job(job_id)
    if rec is None:
        raise ValueError(f"Job not found: {job_id}")
    return rec
