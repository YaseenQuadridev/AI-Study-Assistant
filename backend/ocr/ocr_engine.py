"""ocr/ocr_engine.py — Multi-engine OCR with automatic selection and confidence scoring."""
from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class OCRResult:
    text: str
    confidence: float
    engine: str
    page: int = 1
    needs_review: bool = False


class TesseractEngine:
    def __init__(self, languages: list[str] = None):
        self.languages = languages or ["eng"]

    def process(self, image_data: bytes, page: int = 1) -> OCRResult:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(io.BytesIO(image_data))
            lang = "+".join(self.languages)
            text = pytesseract.image_to_string(img, lang=lang)
            data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data["conf"] if int(c) > 0]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            return OCRResult(text=text, confidence=avg_conf / 100, engine="tesseract", page=page, needs_review=avg_conf < 60)
        except Exception as e:
            return OCRResult(text="", confidence=0, engine="tesseract", page=page, needs_review=True)


class GoogleVisionEngine:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def process(self, image_data: bytes, page: int = 1) -> OCRResult:
        try:
            import requests
            import base64
            b64 = base64.b64encode(image_data).decode()
            r = requests.post(
                f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}",
                json={"requests": [{"image": {"content": b64}, "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]}]},
                timeout=30
            )
            r.raise_for_status()
            text = r.json()["responses"][0].get("fullTextAnnotation", {}).get("text", "")
            return OCRResult(text=text, confidence=0.85, engine="google_vision", page=page, needs_review=False)
        except Exception as e:
            return OCRResult(text="", confidence=0, engine="google_vision", page=page, needs_review=True)


class MathPixEngine:
    def __init__(self, app_id: str, api_key: str):
        self.app_id = app_id
        self.api_key = api_key

    def process(self, image_data: bytes, page: int = 1) -> OCRResult:
        try:
            import requests
            import base64
            b64 = base64.b64encode(image_data).decode()
            r = requests.post(
                "https://api.mathpix.com/v3/text",
                headers={"app_id": self.app_id, "app_key": self.api_key, "Content-Type": "application/json"},
                json={"src": f"data:image/png;base64,{b64}", "formats": ["text", "latex"]},
                timeout=30
            )
            r.raise_for_status()
            data = r.json()
            text = data.get("text", "")
            latex = data.get("latex", "")
            if latex:
                text = f"$$ {latex} $$"
            return OCRResult(text=text, confidence=0.85, engine="mathpix", page=page, needs_review=False)
        except Exception as e:
            return OCRResult(text="", confidence=0, engine="mathpix", page=page, needs_review=True)


class OCREngine:
    def __init__(self, tesseract_langs: list[str] = None, google_api_key: str = None, mathpix_app_id: str = None, mathpix_api_key: str = None):
        self.tesseract = TesseractEngine(tesseract_langs)
        self.google = GoogleVisionEngine(google_api_key) if google_api_key else None
        self.mathpix = MathPixEngine(mathpix_app_id, mathpix_api_key) if mathpix_app_id and mathpix_api_key else None

    def process(self, image_data: bytes, page: int = 1, is_formula: bool = False, is_handwritten: bool = False) -> OCRResult:
        # Strategy selection
        if is_formula and self.mathpix:
            return self.mathpix.process(image_data, page)
        if is_handwritten and self.google:
            return self.google.process(image_data, page)
        # Primary: Tesseract
        result = self.tesseract.process(image_data, page)
        if result.confidence < 0.60 and self.google:
            result = self.google.process(image_data, page)
        return result

    def process_pdf(self, pdf_data: bytes, is_scanned: bool = False) -> list[OCRResult]:
        if not is_scanned:
            return []
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(pdf_data, dpi=200)
            results = []
            for i, img in enumerate(images):
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                results.append(self.process(buf.getvalue(), page=i + 1))
            return results
        except Exception:
            return []
