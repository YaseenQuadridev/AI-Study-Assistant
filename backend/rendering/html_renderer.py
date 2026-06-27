"""rendering/html_renderer.py"""
from __future__ import annotations

from typing import Any

from .base_renderer import BaseRenderer


class HTMLRenderer(BaseRenderer):
    def render(self, content: dict[str, Any], **kwargs: Any) -> str:
        import markdown
        title = content.get("title", "Study Material")
        body_md = content.get("body", "")
        html_body = markdown.markdown(body_md)
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:700px;margin:40px auto;padding:20px;line-height:1.6}}</style>
</head><body>{html_body}</body></html>"""
