"""Custom exceptions for the document intelligence pipeline."""


class DocIntelError(Exception):
    """Base exception for all domain errors."""
    http_status: int = 500


class DocumentParseError(DocIntelError):
    """Raised when a PDF/image cannot be parsed."""
    http_status = 422


class UnsupportedFormatError(DocIntelError):
    """Raised for unsupported file types."""
    http_status = 415


class OCRError(DocIntelError):
    """Raised when OCR fails."""
    http_status = 500


class LayoutAnalysisError(DocIntelError):
    """Raised when layout analysis fails."""
    http_status = 500


class ComplianceError(DocIntelError):
    """Raised when a compliance rule cannot be evaluated."""
    http_status = 500


class AgentError(DocIntelError):
    """Raised when the agent's reasoning loop fails."""
    http_status = 500


class LLMError(DocIntelError):
    """Raised when the LLM call fails."""
    http_status = 502


class NotFoundError(DocIntelError):
    """Raised when a resource (job, report) is missing."""
    http_status = 404