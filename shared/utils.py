"""Small utility helpers shared across services."""
from __future__ import annotations

import hashlib
from pathlib import Path


def file_sha256(path: str | Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def bytes_sha256(data: bytes) -> str:
    """Compute SHA-256 hex digest of a byte string."""
    return hashlib.sha256(data).hexdigest()


def truncate(text: str, max_len: int = 200, ellipsis: str = "…") -> str:
    """Truncate text to max_len characters (with ellipsis)."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(ellipsis)] + ellipsis