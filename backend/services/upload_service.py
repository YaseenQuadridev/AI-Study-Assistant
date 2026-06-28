"""services/upload_service.py — Upload, validation, chunked upload, duplicate detection."""
from __future__ import annotations

import hashlib
import io
import json
import mimetypes
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".txt", ".epub",
    ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic", ".zip",
}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_BATCH_SIZE = 1024 * 1024 * 1024  # 1 GB
CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB

MAGIC_NUMBERS = {
    b"%PDF": ".pdf",
    b"PK\x03\x04": ".zip",
    b"\x89PNG": ".png",
    b"\xff\xd8\xff": ".jpg",
    b"II*\x00": ".tiff",
    b"MM\x00*": ".tiff",
    b"\x00\x00\x00\x0c\x6a\x50": ".heic",
}


def _detect_extension_from_magic(data: bytes) -> str | None:
    for magic, ext in MAGIC_NUMBERS.items():
        if data.startswith(magic):
            return ext
    if data[:4] == b"PK\x03\x04":
        try:
            import zipfile
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                names = z.namelist()
                if any(n.startswith("word/") for n in names):
                    return ".docx"
                if any(n.startswith("ppt/") for n in names):
                    return ".pptx"
                if any(n.endswith(".opf") or n.startswith("OPS/") or n.startswith("OEBPS/") for n in names):
                    return ".epub"
        except Exception:
            pass
        return ".zip"
    # Plain text heuristic
    try:
        data.decode("utf-8")
        return ".txt"
    except UnicodeDecodeError:
        pass
    return None


@dataclass
class UploadResult:
    upload_id: str
    filename: str
    size: int
    mime_type: str
    status: str
    sha256: str = ""
    phash: str = ""
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class UploadService:
    def __init__(self, storage_path: Path | str = "./uploads"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._uploads: dict[str, UploadResult] = {}

    def validate(self, filename: str, data: bytes) -> tuple[bool, str]:
        if len(data) > MAX_FILE_SIZE:
            return False, f"File exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit"
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"File type '{ext}' not allowed"
        detected = _detect_extension_from_magic(data[:256])
        if detected and detected != ext:
            if not (ext in {".docx", ".pptx", ".epub", ".zip"} and detected in {".zip", ".docx", ".pptx", ".epub"}):
                return False, f"File content does not match extension (detected {detected})"
        return True, ""

    def compute_sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def compute_perceptual_hash(self, data: bytes) -> str:
        ext = Path(data).suffix if hasattr(data, 'suffix') else ''
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(data))
            img = img.convert("L").resize((8, 8), Image.LANCZOS)
            pixels = list(img.getdata())
            avg = sum(pixels) / len(pixels)
            bits = "".join("1" if p > avg else "0" for p in pixels)
            return hex(int(bits, 2))[2:].zfill(16)
        except Exception:
            return self.compute_sha256(data)[:16]

    def check_duplicate(self, sha256: str, phash: str) -> UploadResult | None:
        for up in self._uploads.values():
            if up.sha256 == sha256 or up.phash == phash:
                return up
        return None

    def upload(self, filename: str, data: bytes, user_id: str = "") -> UploadResult:
        valid, error = self.validate(filename, data)
        if not valid:
            return UploadResult(
                upload_id="", filename=filename, size=len(data),
                mime_type="", status="rejected", error=error
            )

        sha256 = self.compute_sha256(data)
        phash = self.compute_perceptual_hash(data)
        dup = self.check_duplicate(sha256, phash)
        if dup:
            return UploadResult(
                upload_id=dup.upload_id, filename=filename, size=len(data),
                mime_type="", status="duplicate", sha256=sha256, phash=phash,
                error=f"Duplicate of {dup.filename}"
            )

        upload_id = hashlib.sha256(f"{filename}:{sha256}:{user_id}".encode()).hexdigest()[:16]
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        user_dir = self.storage_path / user_id / upload_id
        user_dir.mkdir(parents=True, exist_ok=True)
        (user_dir / "original").write_bytes(data)

        result = UploadResult(
            upload_id=upload_id, filename=filename, size=len(data),
            mime_type=mime_type, status="uploaded", sha256=sha256,
            phash=phash, metadata={"user_id": user_id, "path": str(user_dir)}
        )
        self._uploads[upload_id] = result
        return result

    def chunked_upload_init(self, filename: str, total_size: int, user_id: str = "") -> str:
        if total_size > MAX_FILE_SIZE:
            raise ValueError(f"File exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit")
        upload_id = hashlib.sha256(f"{filename}:{total_size}:{user_id}:{os.urandom(16).hex()}".encode()).hexdigest()[:16]
        user_dir = self.storage_path / user_id / upload_id
        user_dir.mkdir(parents=True, exist_ok=True)
        (user_dir / ".chunk_info").write_text(json.dumps({
            "filename": filename, "total_size": total_size, "received": 0, "chunks": []
        }))
        return upload_id

    def chunked_upload(self, upload_id: str, chunk_index: int, chunk_data: bytes, user_id: str = "") -> dict[str, Any]:
        user_dir = self.storage_path / user_id / upload_id
        info_path = user_dir / ".chunk_info"
        if not info_path.exists():
            raise ValueError("Upload session not found")
        info = json.loads(info_path.read_text())
        chunk_path = user_dir / f"chunk_{chunk_index}"
        chunk_path.write_bytes(chunk_data)
        info["received"] += len(chunk_data)
        info["chunks"].append(chunk_index)
        info_path.write_text(json.dumps(info))

        if info["received"] >= info["total_size"]:
            data = b""
            for i in range(max(info["chunks"]) + 1):
                cp = user_dir / f"chunk_{i}"
                if cp.exists():
                    data += cp.read_bytes()
            result = self.upload(info["filename"], data, user_id)
            for f in user_dir.glob("chunk_*"):
                f.unlink()
            info_path.unlink()
            return {"status": "complete", "result": result}
        return {"status": "in_progress", "received": info["received"], "total": info["total_size"]}

    def get_upload(self, upload_id: str) -> UploadResult | None:
        return self._uploads.get(upload_id)

    def list_uploads(self, user_id: str = "") -> list[UploadResult]:
        return [u for u in self._uploads.values() if u.metadata.get("user_id") == user_id]
