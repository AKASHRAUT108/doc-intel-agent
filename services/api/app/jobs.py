"""Filesystem-backed job store.

Each job is stored as data/jobs/{job_id}.json.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from shared.config import get_settings
from shared.schemas import JobRecord, JobStatus

logger = logging.getLogger(__name__)


def _jobs_dir() -> Path:
    """Return the jobs directory, creating it if needed."""
    path = Path(get_settings().jobs_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(job_id: str) -> Path:
    return _jobs_dir() / f"{job_id}.json"


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def create_job(filename: str, content_type: str) -> JobRecord:
    """Create a new job with a fresh UUID."""
    job_id = uuid.uuid4().hex[:12]
    now = _now()
    record = JobRecord(
        job_id=job_id,
        filename=filename,
        content_type=content_type,
        status=JobStatus.QUEUED,
        created_at=now,
        updated_at=now,
    )
    save_job(record)
    logger.info("created job %s (%s)", job_id, filename)
    return record


def get_job(job_id: str) -> JobRecord | None:
    """Load a job by ID. Returns None if not found or corrupted."""
    p = _path(job_id)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return JobRecord.model_validate(data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("job %s corrupted (will skip): %s", job_id, e)
        return None
    except Exception:
        logger.exception("failed to load job %s", job_id)
        return None

def save_job(record: JobRecord) -> None:
    """Persist a job record to disk atomically.

    Uses os.replace which is atomic on both POSIX and Windows.
    On Windows, we may get AccessDenied if another process holds the
    file open — retry a few times before giving up.
    """
    import os
    import tempfile
    import time

    record.updated_at = _now()
    final_path = _path(record.job_id)
    data = record.model_dump_json(indent=2)

    fd, tmp_path = tempfile.mkstemp(
        dir=str(final_path.parent), suffix=".json.tmp", prefix="job_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())

        # Retry rename up to 5 times (Windows file lock tolerance)
        last_error: Exception | None = None
        for attempt in range(5):
            try:
                os.replace(tmp_path, final_path)
                return
            except PermissionError as e:
                last_error = e
                time.sleep(0.1 * (attempt + 1))

        # Final attempt — if it still fails, raise
        os.replace(tmp_path, final_path)
        if last_error:
            logger.warning("save_job succeeded after retries: %s", last_error)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise

def mark_processing(job_id: str) -> JobRecord | None:
    rec = get_job(job_id)
    if rec is None:
        return None
    rec.status = JobStatus.PROCESSING
    save_job(rec)
    return rec


def mark_done(job_id: str) -> JobRecord | None:
    rec = get_job(job_id)
    if rec is None:
        return None
    rec.status = JobStatus.DONE
    save_job(rec)
    return rec


def mark_failed(job_id: str, error: str) -> JobRecord | None:
    rec = get_job(job_id)
    if rec is None:
        return None
    rec.status = JobStatus.FAILED
    rec.error = error
    save_job(rec)
    return rec


def list_jobs(limit: int = 20) -> list[JobRecord]:
    """Return the most recent jobs."""
    files = sorted(_jobs_dir().glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    jobs: list[JobRecord] = []
    for f in files[:limit]:
        rec = get_job(f.stem)
        if rec is not None:
            jobs.append(rec)
    return jobs
