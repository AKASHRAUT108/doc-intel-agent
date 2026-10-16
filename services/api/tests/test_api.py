"""Tests for the API Gateway."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api.app.jobs import create_job, get_job, list_jobs
from services.api.app.main import app

SAMPLE = Path("data/samples/capstone.docx")


def test_create_job():
    rec = create_job("test.pdf", "application/pdf")
    assert rec.job_id
    assert rec.status.value == "queued"
    assert rec.filename == "test.pdf"


def test_get_job_roundtrip():
    rec = create_job("roundtrip.txt", "text/plain")
    loaded = get_job(rec.job_id)
    assert loaded is not None
    assert loaded.job_id == rec.job_id
    assert loaded.filename == "roundtrip.txt"


def test_get_nonexistent_job():
    assert get_job("does-not-exist-xyz") is None


def test_list_jobs():
    create_job("a.txt", "text/plain")
    create_job("b.txt", "text/plain")
    jobs = list_jobs(limit=10)
    assert len(jobs) >= 2


def test_health_endpoint():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "api_gateway"


def test_upload_missing_file():
    client = TestClient(app)
    r = client.post("/upload")
    assert r.status_code == 422


def test_upload_empty_file():
    client = TestClient(app)
    r = client.post(
        "/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert r.status_code == 400


def test_upload_and_status():
    client = TestClient(app)
    r = client.post(
        "/upload",
        files={"file": ("hello.txt", b"Hello world from test.", "text/plain")},
    )
    assert r.status_code == 200
    job = r.json()
    assert job["job_id"]
    assert job["status"] == "queued"

    r2 = client.get(f"/status/{job['job_id']}")
    assert r2.status_code == 200
    assert r2.json()["job_id"] == job["job_id"]


def test_status_not_found():
    client = TestClient(app)
    r = client.get("/status/nonexistent-xyz")
    assert r.status_code == 404


def test_result_not_found():
    client = TestClient(app)
    r = client.get("/result/nonexistent-xyz")
    assert r.status_code == 404


@pytest.mark.skipif(not SAMPLE.exists(), reason="sample file missing")
def test_upload_capstone_docx():
    client = TestClient(app)
    with SAMPLE.open("rb") as f:
        r = client.post(
            "/upload",
            files={"file": (SAMPLE.name, f.read(), "application/octet-stream")},
        )
    assert r.status_code == 200
    job = r.json()
    assert job["job_id"]
