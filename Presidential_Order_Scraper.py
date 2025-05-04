import json
import requests
from enum import Enum, auto
from typing import List, Tuple, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class DocumentType(Enum):
    EXECUTIVE_ORDER = auto()
    MEMO = auto()
    PROCLAMATION = auto()


class PresidentialOrderScraper:
    """
    Scrapes the DoD Guidance page and categorizes entries into:
    Executive Orders, Memos, and Proclamations.
    """

    DEFAULT_URL = "https://www.defense.gov/Spotlights/Guidance-for-Federal-Personnel-and-Readiness-Policies/"
    BASE_URL = "https://www.defense.gov"
    OUTPUT_PATH = "./docs/PO_Docs.json"

    def __init__(self, url: str = None, base_url: str = None):
        self.url = url or self.DEFAULT_URL
        self.base_url = base_url or self.BASE_URL
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/135.0.0.0 Mobile Safari/537.36"
            )
        }

    def scrape(self) -> str:
        html = self._fetch_html()
        eo_items, memo_items, proc_items = self._parse_html(html)

        result = {
            "executive_orders": eo_items,
            "memos": memo_items,
            "proclamations": proc_items,
        }

        self._save_json(result)
        return json.dumps(result, indent=2, ensure_ascii=False)

    def _fetch_html(self) -> str:
        response = requests.get(self.url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.text

    def _parse_html(self, html_content: str) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        soup = BeautifulSoup(html_content, "html.parser")
        container = soup.find("div", id="eo-links")
        if not container:
            return [], [], []

        items = {
            DocumentType.EXECUTIVE_ORDER: [],
            DocumentType.MEMO: [],
            DocumentType.PROCLAMATION: [],
        }

        for anchor in container.find_all("a", target="_blank"):
            doc_data = self._extract_document_data(anchor)
            if not doc_data:
                continue

            doc_type = self._categorize(doc_data["doc_number"])
            items[doc_type].append(doc_data)

        return (
            items[DocumentType.EXECUTIVE_ORDER],
            items[DocumentType.MEMO],
            items[DocumentType.PROCLAMATION],
        )

    def _extract_document_data(self, anchor) -> Dict:
        href = anchor.get("href", "").strip()
        pdf_link = urljoin(self.base_url, href)

        item_div = anchor.find("div", class_=["item", "sub-item", "sub-item-first"])
        if not item_div:
            return {}

        doc_number = self._get_text(item_div.find("div", class_="eo"))
        date = self._get_text(item_div.find("div", class_="date"))
        title = self._get_text(item_div.find("div", class_="title"))

        return {
            "doc_number": doc_number,
            "pdf_link": pdf_link,
            "date": date,
            "title": title,
        }

    def _categorize(self, doc_number: str) -> DocumentType:
        if not doc_number:
            return DocumentType.MEMO

        normalized = doc_number.upper()
        if normalized.startswith("EO "):
            return DocumentType.EXECUTIVE_ORDER
        elif normalized.startswith("MEMO"):
            return DocumentType.MEMO
        elif normalized.startswith("PROC."):
            return DocumentType.PROCLAMATION
        else:
            return DocumentType.MEMO

    @staticmethod
    def _get_text(container) -> str:
        if container and container.find("span"):
            return container.find("span").get_text(strip=True)
        return container.get_text(strip=True) if container else ""

    def _save_json(self, data: Dict) -> None:
        with open(self.OUTPUT_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
