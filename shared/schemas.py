"""Pydantic schemas shared across all microservices.

This module is the single source of truth for data shapes that
cross service boundaries. If you change a model here, every
service that imports it gets the update.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Document / Layout / OCR
# -----------------------------------------------------------------------------

class RegionLabel(str, Enum):
    """Semantic label for a region on a document page."""
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
    """Axis-aligned bounding box in image pixel coordinates."""
    x1: float
    y1: float
    x2: float
    y2: float


class LayoutRegion(BaseModel):
    """A labeled region on a page (e.g., header, table, signature)."""
    label: RegionLabel
    bbox: BBox
    page: int = 0


class OCRWord(BaseModel):
    """A single OCR'd word with location and confidence."""
    text: str
    bbox: BBox
    confidence: float = Field(ge=0.0, le=1.0)


class OCRResult(BaseModel):
    """Output of the CV service."""
    page_count: int
    full_text: str
    words: list[OCRWord] = []
    regions: list[LayoutRegion] = []


# -----------------------------------------------------------------------------
# NLP / Entities / Relations
# -----------------------------------------------------------------------------

class Entity(BaseModel):
    """A named entity extracted from text."""
    type: str
    text: str
    start: int
    end: int
    confidence: float = 1.0
    normalized: dict[str, Any] = {}


class Relation(BaseModel):
    """A relation between two entities."""
    source: str
    relation: str
    target: str
    confidence: float = 1.0


class NERResult(BaseModel):
    """Output of the NLP service."""
    entities: list[Entity]
    relations: list[Relation] = []
    embedding: list[float] | None = None


# -----------------------------------------------------------------------------
# RAG / Retrieval
# -----------------------------------------------------------------------------

class RetrievedChunk(BaseModel):
    """A chunk of retrieved knowledge-base content."""
    id: str
    text: str
    score: float
    metadata: dict[str, Any] = {}


# -----------------------------------------------------------------------------
# Agent / Compliance / Anomalies
# -----------------------------------------------------------------------------

class ComplianceVerdict(BaseModel):
    """Result of checking one rule against a document."""
    rule_id: str
    rule_text: str
    status: Literal["PASS", "FAIL", "UNCERTAIN"]
    reason: str


class Anomaly(BaseModel):
    """An anomaly flagged by the agent."""
    type: str
    severity: Literal["low", "medium", "high"]
    detail: str


class AgentStep(BaseModel):
    """One step in the agent's reasoning trace (for audit)."""
    step: int
    action: str
    payload: dict[str, Any] = {}


class AgentTrace(BaseModel):
    """Full reasoning trace of the agent."""
    steps: list[AgentStep] = []
    decision: Literal["APPROVE", "FLAG", "REJECT"]
    reasons: list[str] = []


# -----------------------------------------------------------------------------
# Final Report
# -----------------------------------------------------------------------------

class FinalReport(BaseModel):
    """The end product returned to the user."""
    job_id: str
    summary: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    entities: list[Entity]
    compliance: list[ComplianceVerdict]
    anomalies: list[Anomaly]
    trace: AgentTrace
    auto_filled: dict[str, Any] = {}