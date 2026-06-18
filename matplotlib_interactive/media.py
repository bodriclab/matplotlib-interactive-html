"""Media type detection for preview panel routing."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

MediaType = Literal["image", "video", "html", "pdf", "unknown"]

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
_VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg"}
_HTML_EXTENSIONS = {".html", ".htm"}
_PDF_EXTENSIONS = {".pdf"}


def detect_media_type(path: str | Path) -> MediaType:
    """Detect preview media type from a file path extension."""
    suffix = Path(path).suffix.lower()
    if suffix in _IMAGE_EXTENSIONS:
        return "image"
    if suffix in _VIDEO_EXTENSIONS:
        return "video"
    if suffix in _HTML_EXTENSIONS:
        return "html"
    if suffix in _PDF_EXTENSIONS:
        return "pdf"
    return "unknown"
