import json
import re
import requests
from io import BytesIO
from urllib.parse import urljoin
from typing import List, Dict, Set, Tuple

try:
    import PyPDF2
except ImportError:
    raise ImportError("Please install PyPDF2 using 'pip install PyPDF2'")


class PDFAnalyzer:
    """Analyzes PDFs for Executive Order references using numeric and keyword-based matching."""

    EO_PATTERN = re.compile(
        r"(Executive Order(?:\s+No\.)?\s*(\d+)(?=\b|\s))|\bE\.O\.\s*(\d+)(?=\b|\s)",
        re.IGNORECASE,
    )

    EO_NAME_KEYWORDS = {
        "14222": ["Implementing the President's Department of Government Efficiency Cost Efficiency Initiative", "DOGE Cost Efficiency Initiative"],
        "14210": ["Implementing the President's Department of Government Efficiency", "DOGE Workforce Optimization Initiative", "Department of Government Efficiency", "DOGE"],
        "14208": ["Ending Procurement and Forced Use of Paper Straws", "Paper Straws"],
        "14202": ["Eradicating Anti-Christian Bias"],
        "14191": ["Expanding Educational Freedom", "Educational Freedom and Opportunity for Families"],
        "14190": ["Ending Radical Indoctrination", "K–12 Schooling"],
        "14188": ["Additional Measures To Combat Anti-Semitism"],
        "14187": ["Protecting Children From Chemical and Surgical Mutilation"],
        "14185": ["Restoring America's Fighting Force"],
        "14184": ["Reinstating Service Members Discharged Under the Military's COVID–19 Vaccination Mandate"],
        "14183": ["Prioritizing Military Excellence and Readiness"],
        "14182": ["Enforcing the Hyde Amendment"],
        "14174": ["Revocation of Certain Executive Orders"],
        "14173": ["Ending Illegal Discrimination and Restoring Merit-Based Opportunity"],
        "14171": ["Restoring Accountability to Policy-Influencing Positions Within the Federal Workforce", "Policy-Influencing Positions"],
        "14168": ["Defending Women From Gender Ideology Extremism", "Restoring Biological Truth to the Federal Government", "Defending Women"],
        "14167": ["Clarifying the Military's Role", "Territorial Integrity of the United States"],
        "14165": ["Securing Our Borders"],
        "14170": ["Reforming the Federal Hiring Process", "Restoring Merit to Government Service"],
        "14151": ["Ending Radical and Wasteful Government DEI Programs", "DEI Programs and Preferencing"],
        "14148": ["Initial Rescissions of Harmful Executive Orders and Actions"],
        "14003": ["Executive Order 14003", "Revocation of Executive Order 14003"],
    }

    def __init__(self, base_url: str = None):
        self.base_url = base_url or "https://www.opm.gov"
        print(f"Initialized PDFAnalyzer with base_url: {self.base_url}")

    def parse_pdfs_for_eo_references(self, json_output: str) -> List[Dict]:
        """Parses memos and extracts EO references from their PDFs."""
        memo_list = json.loads(json_output)
        results = []

        for memo in memo_list:
            pdf_url = urljoin(self.base_url, memo.get("pdf_link", ""))
            if not pdf_url:
                continue

            try:
                eo_refs, pdf_text = self._extract_eo_references_from_pdf(pdf_url)
            except Exception as e:
                print(f"Failed to process {pdf_url}: {e}")
                eo_refs, pdf_text = set(), ""

            results.append({
                "pdf_link": pdf_url,
                "eo_references": list(eo_refs),
                "pdf_text_preview": pdf_text[:200],
            })

        return results

    def _extract_eo_references_from_pdf(self, pdf_url: str) -> Tuple[Set[str], str]:
        """Downloads a PDF and returns EO references and full text."""
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()

        with BytesIO(response.content) as file:
            reader = PyPDF2.PdfReader(file)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

        eo_refs = self._match_eo_numeric(text)
        eo_refs |= self._match_eo_keywords(text)

        return eo_refs, text

    def _match_eo_numeric(self, text: str) -> Set[str]:
        """Finds EO numbers using numeric patterns."""
        matches = self.EO_PATTERN.findall(text)
        return {g2 or g3 for _, g2, g3 in matches if g2 or g3}

    def _match_eo_keywords(self, text: str) -> Set[str]:
        """Finds EO numbers using name/title-based matching."""
        lower_text = text.lower()
        found = set()
        for eo_num, phrases in self.EO_NAME_KEYWORDS.items():
            if any(phrase.lower() in lower_text for phrase in phrases):
                print(f"[Keyword Match] Found EO {eo_num}")
                found.add(eo_num)
        return found
    