"""FastAPI entry point for the API Gateway."""
from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile

from shared.logging import get_logger, setup_logging
from shared.schemas import JobRecord, PromptMode

from .jobs import create_job, get_job, list_jobs
from .orchestrator import run_pipeline

setup_logging()
logger = get_logger("api_gateway")

app = FastAPI(
    title="Doc Intel API Gateway",
    description="Upload documents, get summaries and prompts.",
    version="0.1.0",
)


# Max upload size — 25 MB
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "api_gateway"}


@app.post("/upload", response_model=JobRecord)
async def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: PromptMode = PromptMode.SUMMARY,
) -> JobRecord:
    """Accept a file, enqueue it for processing, return the job record."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // 1024 // 1024} MB)",
        )

    content_type = file.content_type or "application/octet-stream"
    logger.info("upload: %s (%d bytes, %s)", file.filename, len(contents), content_type)

    record = create_job(filename=file.filename, content_type=content_type)

    # Launch pipeline in background
    background_tasks.add_task(
        run_pipeline,
        job_id=record.job_id,
        file_bytes=contents,
        filename=file.filename,
        content_type=content_type,
        mode=mode,
    )

    return record


@app.get("/status/{job_id}", response_model=JobRecord)
def status(job_id: str) -> JobRecord:
    """Return the current state of a job."""
    rec = get_job(job_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return rec


@app.get("/result/{job_id}")
def result(job_id: str) -> dict:
    """Return the full result — OCR, entities, summary, prompt."""
    rec = get_job(job_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": rec.job_id,
        "status": rec.status.value,
        "error": rec.error,
        "ocr": rec.ocr.model_dump() if rec.ocr else None,
        "entities": rec.entities.model_dump() if rec.entities else None,
        "summary": rec.summary.model_dump() if rec.summary else None,
        "prompt": rec.prompt.model_dump() if rec.prompt else None,
    }


@app.get("/jobs", response_model=list[JobRecord])
def jobs(limit: int = 20) -> list[JobRecord]:
    """List recent jobs."""
    return list_jobs(limit=limit)
