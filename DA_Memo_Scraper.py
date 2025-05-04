import json
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class ArmyGuidanceScraper:
    """
    Scrapes Army Implementation Guidance Memos and outputs metadata in standardized format.
    """

    DEFAULT_URL = "https://www.army.mil/executiveorderimplementation"
    OUTPUT_PATH = "./docs/DA_Memos.json"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )
    }

    DATE_REGEX = re.compile(r"^(\d{2}/\d{2}/\d{4})\s*—\s*(.*)$")

    def __init__(self, url: str = None):
        self.url = url or self.DEFAULT_URL

    def scrape(self) -> str:
        html = self._fetch_html()
        memos = self._extract_memos(html)
        self._write_to_file(memos)
        return json.dumps(memos, indent=2, ensure_ascii=False)

    def _fetch_html(self) -> str:
        response = requests.get(self.url, headers=self.HEADERS, timeout=10)
        response.raise_for_status()
        return response.text

    def _extract_memos(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        section = self._find_target_section(soup)
        if not section:
            return []

        return [self._parse_list_item(li) for li in section.find_all("li") if li.find("a")]

    def _find_target_section(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        sections = soup.find_all("section", class_="microtext")
        for section in sections:
            header = section.find("h4")
            if header and "ARMY IMPLEMENTATION GUIDANCE MEMORANDUMS" in header.get_text(strip=True):
                return section
        return None

    def _parse_list_item(self, li_tag) -> Dict:
        link_tag = li_tag.find("a")
        title = link_tag.get_text(strip=True)
        pdf_link = link_tag.get("href", "").strip()
        date = self._extract_date(li_tag.get_text(" ", strip=True))

        return {
            "title": title,
            "pdf_link": pdf_link,
            "from": None,
            "date": date,
            "stakeholders": None,
            "combined_text": None,
        }

    def _extract_date(self, text: str) -> Optional[str]:
        match = self.DATE_REGEX.match(text)
        return match.group(1) if match else None

    def _write_to_file(self, memos: List[Dict]) -> None:
        with open(self.OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(memos, f, indent=2, ensure_ascii=False)
