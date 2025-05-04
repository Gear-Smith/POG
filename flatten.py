import json

with open("./docs/consolidated_eo_references.json", "r", encoding="utf-8") as f:
    eo_data = json.load(f)

flat_docs = []

for eo in eo_data:
    base = {
        "eo_number": eo["eo_number"],
        "eo_title": eo["eo_title"],
        "eo_link": eo["eo_link"]
    }

    for source, docs in [("opm", eo["opm_docs"]), ("dod", eo["dod_docs"]), ("da", eo["da_docs"])]:
        for doc in docs:
            flat_docs.append({
                **base,
                "source": source,
                "doc_title": doc.get("title") or doc.get("doc_number"),
                "doc_link": doc.get("pdf_link"),
                "date": doc.get("date"),
                "from": doc.get("from"),
                "stakeholders": doc.get("stakeholders"),
            })

with open("./docs/eo_docs_flat.json", "w", encoding="utf-8") as f:
    json.dump(flat_docs, f, indent=2, ensure_ascii=False)
