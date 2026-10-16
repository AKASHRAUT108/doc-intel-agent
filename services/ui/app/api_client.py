"""HTTP client for the API Gateway."""
from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)

DEFAULT_API_URL = "http://localhost:8000"


class APIClient:
    """Thin wrapper around the API Gateway."""

    def __init__(self, base_url: str = DEFAULT_API_URL) -> None:
        self.base_url = base_url.rstrip("/")

    # -- Health ---------------------------------------------------------------

    def health(self) -> dict:
        try:
            r = httpx.get(f"{self.base_url}/health", timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning("health check failed: %s", e)
            return {"status": "unreachable", "error": str(e)}

    # -- Upload ---------------------------------------------------------------

    def upload(self, filename: str, content: bytes, mode: str = "summary") -> dict:
        """Upload a file and return the job record."""
        files = {"file": (filename, content)}
        params = {"mode": mode}
        r = httpx.post(
            f"{self.base_url}/upload",
            files=files,
            params=params,
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()

    # -- Status ---------------------------------------------------------------

    def status(self, job_id: str) -> dict:
        r = httpx.get(f"{self.base_url}/status/{job_id}", timeout=10)
        r.raise_for_status()
        return r.json()

    # -- Result ---------------------------------------------------------------

    def result(self, job_id: str) -> dict:
        r = httpx.get(f"{self.base_url}/result/{job_id}", timeout=30)
        r.raise_for_status()
        return r.json()

    # -- Jobs list ------------------------------------------------------------

    def list_jobs(self, limit: int = 10) -> list[dict]:
        try:
            r = httpx.get(f"{self.base_url}/jobs", params={"limit": limit}, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning("list_jobs failed: %s", e)
            return []
