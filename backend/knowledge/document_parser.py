"""knowledge/document_parser.py — Docling-based document parser."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def parse_document(path: str | Path) -> dict[str, Any]:
    """Parse PDF/DOCX into structured markdown using Docling."""
    path = Path(path)
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(path)
        md = result.document.export_to_markdown()
    except Exception:
        # Fallback: read text if docling unavailable
        try:
            md = path.read_text(encoding="utf-8")
        except Exception:
            md = ""
    return {
        "filename": path.name,
        "path": str(path),
        "markdown": md,
        "status": "ready",
    }
