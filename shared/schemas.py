"""Pydantic schemas shared across all microservices."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class RegionLabel(str, Enum):
    TITLE = "title"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    SIGNATURE = "signature"
    STAMP = "stamp"
    HEADER = "header"
    FOOTER = "footer"
    FIGURE = "figure"
    OTHER = "other"


class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class LayoutRegion(BaseModel):
    label: RegionLabel
    bbox: BBox
    page: int = 0


class OCRWord(BaseModel):
    text: str
    bbox: BBox
    confidence: float = Field(ge=0.0, le=1.0)


class OCRResult(BaseModel):
    page_count: int
    full_text: str
    words: list[OCRWord] = []
    regions: list[LayoutRegion] = []


class Entity(BaseModel):
    type: str
    text: str
    start: int
    end: int
    confidence: float = 1.0
    normalized: dict[str, Any] = {}


class Relation(BaseModel):
    source: str
    relation: str
    target: str
    confidence: float = 1.0


class NERResult(BaseModel):
    entities: list[Entity]
    relations: list[Relation] = []
    embedding: list[float] | None = None


class RetrievedChunk(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict[str, Any] = {}


class ComplianceVerdict(BaseModel):
    rule_id: str
    rule_text: str
    status: Literal["PASS", "FAIL", "UNCERTAIN"]
    reason: str


class Anomaly(BaseModel):
    type: str
    severity: Literal["low", "medium", "high"]
    detail: str


class AgentStep(BaseModel):
    step: int
    action: str
    payload: dict[str, Any] = {}


class AgentTrace(BaseModel):
    steps: list[AgentStep] = []
    decision: Literal["APPROVE", "FLAG", "REJECT"]
    reasons: list[str] = []


class FinalReport(BaseModel):
    job_id: str
    summary: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    entities: list[Entity]
    compliance: list[ComplianceVerdict]
    anomalies: list[Anomaly]
    trace: AgentTrace
    auto_filled: dict[str, Any] = {}


# -----------------------------------------------------------------------------
# Summary Service
# -----------------------------------------------------------------------------

class KeyFact(BaseModel):
    """A key fact extracted from a document (label/value pair)."""
    label: str
    value: str


class SummaryResult(BaseModel):
    """Structured summary produced by the Summary Service."""
    summary: str
    document_type: str = "unknown"
    key_facts: list[KeyFact] = []
    action_items: list[str] = []
    risk_flags: list[str] = []
    tldr: str = ""
    word_count: int = 0
    model: str = ""
    latency_ms: int = 0
    mocked: bool = False

# -----------------------------------------------------------------------------
# Prompt Generator Service
# -----------------------------------------------------------------------------

class PromptMode(str, Enum):
    """User-selectable prompt generation modes."""
    SUMMARY = "summary"
    ANALYZE = "analyze"
    ACTION = "action"
    QUIZ = "quiz"


class PromptResult(BaseModel):
    """Generated prompt ready to paste into an LLM."""
    mode: PromptMode
    prompt: str
    suggested_followups: list[str] = []
    document_type: str = "unknown"
    model: str = ""
    latency_ms: int = 0
    mocked: bool = False

# -----------------------------------------------------------------------------
# API Gateway — Jobs
# -----------------------------------------------------------------------------

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class JobRecord(BaseModel):
    """Represents a processing job."""
    job_id: str
    filename: str
    content_type: str
    status: JobStatus = JobStatus.QUEUED
    created_at: str = ""
    updated_at: str = ""
    error: str | None = None

    # Filled in progressively as the pipeline runs
    ocr: OCRResult | None = None
    entities: NERResult | None = None
    summary: SummaryResult | None = None
    prompt: PromptResult | None = None