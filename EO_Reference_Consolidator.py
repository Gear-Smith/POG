import json
import re
from typing import Dict, List


class EOReferenceConsolidator:
    """
    Consolidates Executive Orders with related OPM, DA (Army), and DoD memos.
    """

    def __init__(self):
        pass

    def build_relationships(self, po_json_str: str, army_json_str: str, opm_json_str: str) -> str:
        po_data = json.loads(po_json_str)
        army_memos = json.loads(army_json_str)
        opm_memos = json.loads(opm_json_str)

        executive_orders = self._extract_executive_orders(po_data.get("executive_orders", []))
        eo_numbers = {eo["eo_number"] for eo in executive_orders}

        eo_to_opm = self._map_references(opm_memos)
        eo_to_da = self._map_references(army_memos)
        eo_to_dod = self._map_dod_references(po_data.get("memos", []), eo_numbers)

        self._merge_references(executive_orders, eo_to_opm, eo_to_da, eo_to_dod)

        return json.dumps(executive_orders, indent=2, ensure_ascii=False)

    def _extract_executive_orders(self, eo_list: List[Dict]) -> List[Dict]:
        extracted = []
        for eo in eo_list:
            doc_number = eo.get("doc_number", "").strip()
            if doc_number.upper().startswith("EO "):
                eo_number = doc_number[3:].strip()
                extracted.append({
                    "eo_number": eo_number,
                    "eo_title": eo.get("title", ""),
                    "eo_link": eo.get("pdf_link", ""),
                    "opm_docs": [],
                    "dod_docs": [],
                    "da_docs": []
                })
        return extracted

    def _map_references(self, memos: List[Dict]) -> Dict[str, List[Dict]]:
        reference_map = {}
        for memo in memos:
            for ref in memo.get("eo_references", []):
                cleaned_memo = {k: v for k, v in memo.items() if k != "eo_references"}
                reference_map.setdefault(ref.strip(), []).append(cleaned_memo)
        return reference_map

    def _map_dod_references(self, memos: List[Dict], eo_numbers: set) -> Dict[str, List[Dict]]:
        mapping = {eo: [] for eo in eo_numbers}
        for memo in memos:
            doc_number = memo.get("doc_number", "")
            title = memo.get("title", "")
            cleaned = {k: v for k, v in memo.items() if k != "eo_references"}

            for eo in eo_numbers:
                if re.search(rf"\b{re.escape(eo)}\b", doc_number) or re.search(rf"\b{re.escape(eo)}\b", title):
                    mapping[eo].append(cleaned)
        return mapping

    def _merge_references(
        self,
        eo_list: List[Dict],
        opm_map: Dict[str, List[Dict]],
        da_map: Dict[str, List[Dict]],
        dod_map: Dict[str, List[Dict]],
    ) -> None:
        for eo in eo_list:
            number = eo["eo_number"]
            eo["opm_docs"] = opm_map.get(number, [])
            eo["da_docs"] = da_map.get(number, [])
            eo["dod_docs"] = dod_map.get(number, [])
