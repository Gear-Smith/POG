import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional


class OPMMemoScraper:
    """
    Scrapes the OPM memos page and extracts metadata including title, link, author,
    date, stakeholders, and combined descriptive text.
    """

    DEFAULT_URL = "https://www.opm.gov/policy-data-oversight/latest-and-other-highlighted-memos/"
    BASE_URL = "https://www.opm.gov"
    OUTPUT_PATH = "./docs/OPM_Memos.json"

    def __init__(self, url: str = None):
        self.url = url or self.DEFAULT_URL

    def scrape(self) -> str:
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()

        memos = self._parse_html(response.text)
        self._write_to_file(memos)
        return json.dumps(memos, indent=2, ensure_ascii=False)

    def _parse_html(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        memo_items = soup.find_all("li", class_="usa-collection__item")
        return [self._parse_memo_item(item) for item in memo_items if self._has_link(item)]

    def _has_link(self, item) -> bool:
        return item.find("a", class_="usa-link") is not None

    def _parse_memo_item(self, item) -> Dict:
        link_tag = item.find("a", class_="usa-link")
        pdf_link = urljoin(self.BASE_URL, link_tag.get("href", "").strip())
        title = link_tag.get_text(strip=True)

        description = item.find("div", class_="usa-collection__description")
        if not description:
            return self._memo_dict(title, pdf_link)

        paragraphs = description.find_all("p")
        fields = {
            "from_": None,
            "date": None,
            "stakeholders": None,
            "combined_text": " ".join(p.get_text(" ", strip=True) for p in paragraphs)
        }

        for p in paragraphs:
            strong_tag = p.find("strong")
            if not strong_tag:
                continue

            label = strong_tag.get_text(strip=True).rstrip(":").lower()
            content = p.get_text(" ", strip=True).replace(strong_tag.get_text(strip=True) + ":", "").strip()

            if label in fields:
                if label == "from":
                    fields["from_"] = content
        return self._memo_dict(title, pdf_link, from_=fields["from_"], date=fields["date"], stakeholders=fields["stakeholders"], combined_text=fields["combined_text"])

    def _memo_dict(
        self,
        title: str,
        pdf_link: str,
        from_: Optional[str] = None,
        date: Optional[str] = None,
        stakeholders: Optional[str] = None,
        combined_text: Optional[str] = None,
    ) -> Dict:
        return {
            "title": title,
            "pdf_link": pdf_link,
            "from": from_,
            "date": date,
            "stakeholders": stakeholders,
            "combined_text": combined_text,
        }

    def _write_to_file(self, data: List[Dict]) -> None:
        with open(self.OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
