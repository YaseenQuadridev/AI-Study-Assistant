"""validation/document_validator.py — File validation, encoding, language detection."""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any


class DocumentValidator:
    def __init__(self):
        self._virus_scanner = None

    def validate_magic(self, data: bytes, claimed_ext: str) -> tuple[bool, str]:
        magic_map = {
            b"%PDF": ".pdf", b"PK\x03\x04": ".zip", b"\x89PNG": ".png",
            b"\xff\xd8\xff": ".jpg", b"II*\x00": ".tiff", b"MM\x00*": ".tiff",
        }
        detected = None
        for magic, ext in magic_map.items():
            if data.startswith(magic):
                detected = ext
                break
        if data[:4] == b"PK\x03\x04":
            try:
                import zipfile
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    names = z.namelist()
                    if any(n.startswith("word/") for n in names): detected = ".docx"
                    elif any(n.startswith("ppt/") for n in names): detected = ".pptx"
                    elif any(n.endswith(".opf") for n in names): detected = ".epub"
            except Exception:
                pass
        if detected and detected != claimed_ext:
            if not (claimed_ext in {".docx", ".pptx", ".epub", ".zip"} and detected in {".zip", ".docx", ".pptx", ".epub"}):
                return False, f"Magic mismatch: claimed {claimed_ext}, detected {detected}"
        return True, ""

    def detect_encoding(self, data: bytes) -> str:
        try:
            import chardet
            result = chardet.detect(data)
            return result.get("encoding", "utf-8") if result else "utf-8"
        except Exception:
            for enc in ["utf-8", "utf-16", "latin-1", "windows-1252"]:
                try:
                    data.decode(enc)
                    return enc
                except UnicodeDecodeError:
                    continue
            return "utf-8"

    def detect_language(self, text: str) -> str:
        try:
            from langdetect import detect
            return detect(text[:5000])
        except Exception:
            return "en"

    def check_password_protected(self, data: bytes, ext: str) -> bool:
        if ext == ".pdf":
            try:
                import pikepdf
                pikepdf.open(io.BytesIO(data))
                return False
            except pikepdf._core.PasswordError:
                return True
            except Exception:
                return False
        return False

    def check_corrupted(self, data: bytes, ext: str) -> tuple[bool, str]:
        if ext == ".pdf":
            if not data.startswith(b"%PDF"):
                return False, "PDF header missing"
        elif ext == ".png":
            if not data.startswith(b"\x89PNG\r\n\x1a\n"):
                return False, "PNG header missing"
        return True, ""

    def validate(self, filename: str, data: bytes) -> dict[str, Any]:
        ext = Path(filename).suffix.lower()
        result = {"valid": True, "errors": [], "warnings": []}

        ok, msg = self.validate_magic(data, ext)
        if not ok:
            result["valid"] = False
            result["errors"].append(msg)

        ok, msg = self.check_corrupted(data, ext)
        if not ok:
            result["valid"] = False
            result["errors"].append(msg)

        if self.check_password_protected(data, ext):
            result["valid"] = False
            result["errors"].append("Password-protected file")

        result["encoding"] = self.detect_encoding(data)
        result["language"] = self.detect_language(data.decode(result["encoding"], errors="ignore"))
        return result
