import json
import logging
from urllib.parse import urljoin
from pathlib import Path

from EO_Reference_Consolidator import EOReferenceConsolidator
from OPM_Memo_Scraper import OPMMemoScraper
from DA_Memo_Scraper import ArmyGuidanceScraper
from PDF_Analyzer import PDFAnalyzer
from Presidential_Order_Scraper import PresidentialOrderScraper

# Constants
DOCS_DIR = Path("./docs")
OUTPUT_FILE = DOCS_DIR / "consolidated_eo_references.json"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def scrape_and_analyze_memos(scraper, analyzer_base_url: str) -> str:
    """
    Scrapes memos and analyzes PDFs for EO references.

    Returns:
        A JSON string with EO references added to each memo.
    Raises:
        ValueError: If the scraper returns empty data.
    """
    raw_json = scraper.scrape()
    if not raw_json or raw_json.strip() in ["[]", ""]:
        raise ValueError(f"{scraper.__class__.__name__} returned no data.")

    memos = json.loads(raw_json)
    analyzer = PDFAnalyzer(base_url=analyzer_base_url)
    analysis = analyzer.parse_pdfs_for_eo_references(raw_json)

    reference_map = {
        item["pdf_link"]: item.get("eo_references", [])
        for item in analysis
    }

    for memo in memos:
        original_link = memo.get("pdf_link", "")
        absolute_link = urljoin(analyzer.base_url, original_link) if original_link else ""
        memo["eo_references"] = reference_map.get(absolute_link, [])

    return json.dumps(memos, indent=2, ensure_ascii=False)


def write_output_to_file(data: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")
    logging.info(f"✅ Output written to {path}")


def main():
    logging.info("📥 Starting EO Reference Consolidation Pipeline")

    # Step 1: Get Presidential Orders
    po_json = PresidentialOrderScraper().scrape()
    logging.info("✅ Fetched Presidential Orders")

    # Step 2: Army Memos
    try:
        final_army_json = scrape_and_analyze_memos(
            ArmyGuidanceScraper(), "https://api.army.mil"
        )
        logging.info("✅ Army Memos processed")
    except ValueError as e:
        logging.error(f"❌ Army memo error: {e}")
        return

    # Step 3: OPM Memos
    try:
        final_opm_json = scrape_and_analyze_memos(
            OPMMemoScraper(), "https://www.opm.gov"
        )
        logging.info("✅ OPM Memos processed")
    except ValueError as e:
        logging.error(f"❌ OPM memo error: {e}")
        return

    # Step 4: Consolidation
    consolidator = EOReferenceConsolidator()
    consolidated_json = consolidator.build_relationships(
        po_json_str=po_json,
        army_json_str=final_army_json,
        opm_json_str=final_opm_json,
    )
    logging.info("✅ Consolidation complete")

    # Step 5: Output
    write_output_to_file(consolidated_json, OUTPUT_FILE)


if __name__ == "__main__":
    main()
