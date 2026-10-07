"""FastAPI entry point for the CV service."""
from __future__ import annotations

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse

from shared.errors import DocIntelError, UnsupportedFormatError
from shared.logging import get_logger, setup_logging
from shared.schemas import OCRResult

from .pipeline import process_document

setup_logging()
logger = get_logger("cv_service")

app = FastAPI(
    title="CV Service",
    description="Layout analysis and OCR for document intelligence.",
    version="0.1.0",
)


@app.exception_handler(DocIntelError)
async def docintel_exception_handler(request: Request, exc: DocIntelError):
    logger.warning("domain error: %s", exc)
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": exc.__class__.__name__, "detail": str(exc)},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "cv_service"}


@app.post("/extract", response_model=OCRResult)
async def extract(file: UploadFile = File(...)) -> OCRResult:
    if not file.content_type:
        raise UnsupportedFormatError("Missing content type")

    data = await file.read()
    if not data:
        raise UnsupportedFormatError("Empty file")

    logger.info("received file: %s (%d bytes)", file.filename, len(data))
    result = process_document(data, file.content_type)
    logger.info("processed: %d pages, %d words", result.page_count, len(result.words))
    return result