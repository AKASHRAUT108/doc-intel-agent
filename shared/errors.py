"""Custom exceptions for the document intelligence pipeline."""


class DocIntelError(Exception):
    http_status: int = 500


class DocumentParseError(DocIntelError):
    http_status = 422


class UnsupportedFormatError(DocIntelError):
    http_status = 415


class OCRError(DocIntelError):
    http_status = 500


class LayoutAnalysisError(DocIntelError):
    http_status = 500


class ComplianceError(DocIntelError):
    http_status = 500


class AgentError(DocIntelError):
    http_status = 500


class LLMError(DocIntelError):
    http_status = 502


class NotFoundError(DocIntelError):
    http_status = 404