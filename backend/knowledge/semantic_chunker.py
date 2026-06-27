"""knowledge/semantic_chunker.py — Document-aware semantic chunking."""
from __future__ import annotations

import re
from typing import Any


class SemanticChunker:
    def __init__(self, max_tokens: int = 800, overlap_tokens: int = 80):
        self.max_tokens = max_tokens
        self.overlap = overlap_tokens

    def chunk(self, markdown: str) -> list[dict[str, Any]]:
        """Split markdown into chunks respecting headings and paragraphs."""
        # Split by headings (lines starting with #)
        sections = self._split_by_headings(markdown)
        chunks = []
        for sec in sections:
            heading = sec.get("heading", "")
            body = sec.get("body", "")
            if not body.strip():
                continue
            # Estimate tokens: ~4 chars per token
            max_chars = self.max_tokens * 4
            overlap_chars = self.overlap * 4
            if len(body) <= max_chars:
                chunks.append({"heading": heading, "text": body, "token_count": len(body) // 4})
            else:
                # Split by paragraphs
                paragraphs = [p for p in body.split("\n\n") if p.strip()]
                current = ""
                for para in paragraphs:
                    if len(current) + len(para) + 2 > max_chars and current:
                        chunks.append({"heading": heading, "text": current.strip(), "token_count": len(current) // 4})
                        current = current[-overlap_chars:] if len(current) > overlap_chars else ""
                    current += ("\n\n" if current else "") + para
                if current:
                    chunks.append({"heading": heading, "text": current.strip(), "token_count": len(current) // 4})
        return chunks

    def _split_by_headings(self, markdown: str) -> list[dict[str, str]]:
        lines = markdown.splitlines()
        sections = []
        current_heading = ""
        current_body = ""
        for line in lines:
            if re.match(r"^#{1,6}\s", line):
                if current_body.strip():
                    sections.append({"heading": current_heading, "body": current_body})
                current_heading = line.strip()
                current_body = ""
            else:
                current_body += line + "\n"
        if current_body.strip():
            sections.append({"heading": current_heading, "body": current_body})
        if not sections and markdown.strip():
            sections.append({"heading": "", "body": markdown})
        return sections
