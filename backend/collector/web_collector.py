"""collector/web_collector.py — Auto-discovery of official educational resources."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FoundResource:
    title: str
    url: str
    source_type: str
    confidence: float
    subject: str = ""
    format: str = ""


EXAM_DATABASE = {
    "JEE": {
        "board": "NTA", "country": "India",
        "official_urls": [
            "https://jeemain.nta.nic.in/",
            "https://ncert.nic.in/textbook.php",
        ],
        "subjects": ["Physics", "Chemistry", "Mathematics"]
    },
    "NEET": {
        "board": "NTA", "country": "India",
        "official_urls": [
            "https://neet.nta.nic.in/",
            "https://ncert.nic.in/textbook.php",
        ],
        "subjects": ["Physics", "Chemistry", "Biology"]
    },
    "SAT": {
        "board": "College Board", "country": "USA",
        "official_urls": [
            "https://satsuite.collegeboard.org/sat",
        ],
        "subjects": ["Math", "Evidence-Based Reading", "Writing"]
    },
    "CPA": {
        "board": "AICPA", "country": "USA",
        "official_urls": [
            "https://www.aicpa-cima.com/",
        ],
        "subjects": ["Auditing", "Financial Accounting", "Regulation", "Business Environment"]
    },
}

SOURCE_CONFIDENCE = {
    "official_government": 1.00, "official_exam": 1.00, "official_syllabus": 1.00,
    "ncert": 0.90, "publisher": 0.85, "verified_platform": 0.75,
    "coaching": 0.70, "user_notes": 0.65, "community": 0.40, "unverified": 0.20,
}


class WebResourceCollector:
    def __init__(self, search_api_key: str = None):
        self.search_api_key = search_api_key
        self._last_request_time = 0

    def _rate_limited_get(self, url: str) -> Any:
        elapsed = time.time() - self._last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        try:
            import requests
            r = requests.get(url, headers={"User-Agent": "AdaptiveStudyBot/1.0"}, timeout=10)
            self._last_request_time = time.time()
            return r
        except Exception:
            return None

    def search_exam(self, exam_name: str) -> dict[str, Any]:
        exam = EXAM_DATABASE.get(exam_name.upper())
        if not exam:
            return {"found": False, "exam": exam_name}
        return {"found": True, "exam": exam, "official_urls": exam.get("official_urls", [])}

    def find_resources(self, exam_name: str, subjects: list[str] = None) -> list[FoundResource]:
        exam_info = self.search_exam(exam_name)
        if not exam_info.get("found"):
            return []
        resources = []
        # Official resources
        for url in exam_info.get("official_urls", []):
            resources.append(FoundResource(
                title=f"Official {exam_name} Resource",
                url=url, source_type="official_exam",
                confidence=SOURCE_CONFIDENCE["official_exam"],
                subject="General", format="web"
            ))
        # NCERT for Indian exams
        if exam_info.get("exam", {}).get("country") == "India":
            for subj in (subjects or exam_info.get("exam", {}).get("subjects", [])):
                resources.append(FoundResource(
                    title=f"NCERT {subj} Textbook",
                    url=f"https://ncert.nic.in/textbook.php?subject={subj.lower()}",
                    source_type="ncert", confidence=SOURCE_CONFIDENCE["ncert"],
                    subject=subj, format="pdf"
                ))
        # DuckDuckGo search fallback
        resources.extend(self._search_web(exam_name, subjects))
        # Sort by confidence
        resources.sort(key=lambda r: r.confidence, reverse=True)
        return resources

    def _search_web(self, exam_name: str, subjects: list[str] = None) -> list[FoundResource]:
        resources = []
        try:
            import requests
            query = f"{exam_name} official syllabus PDF previous year questions"
            r = requests.get(
                f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}",
                headers={"User-Agent": "Mozilla/5.0"}, timeout=10
            )
            if r.status_code == 200:
                # Simple regex extraction (production would use proper HTML parsing)
                links = re.findall(r'href="(https?://[^"]+\.pdf)"', r.text)
                for link in links[:5]:
                    resources.append(FoundResource(
                        title=link.split("/")[-1],
                        url=link, source_type="verified_platform",
                        confidence=SOURCE_CONFIDENCE["verified_platform"],
                        format="pdf"
                    ))
        except Exception:
            pass
        return resources

    def approve_resources(self, resource_ids: list[str], approved: list[bool]) -> list[FoundResource]:
        # In production, this would update database status
        return []


import re
