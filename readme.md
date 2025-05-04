# Executive Order Reference Consolidator

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

This Python-based tool scrapes, analyzes, and consolidates Executive Order (EO) references from multiple official U.S. government sources including:

- **Presidential Orders** from the U.S. Department of Defense
- **Army Implementation Guidance Memorandums**
- **Office of Personnel Management (OPM) Memos**

It outputs a structured JSON document that links Executive Orders to memos that reference them, enabling traceability and improved context awareness.

---

## 🚀 Features

- 🔍 **EO Reference Detection**  
  Uses a two-pass system to detect references:
  - Regex for numeric patterns (`Executive Order 14168`, `E.O. 14168`)
  - Keyword and title-based phrase matching (`DOGE Workforce Optimization`, etc.)

- 📰 **Web Scraping**  
  Parses:
  - [DoD Spotlight](https://www.defense.gov/Spotlights/Guidance-for-Federal-Personnel-and-Readiness-Policies/)
  - [Army Executive Order Implementation](https://www.army.mil/executiveorderimplementation)
  - [OPM Memos](https://www.opm.gov/policy-data-oversight/latest-and-other-highlighted-memos/)

- 🧠 **Document Enrichment**  
  Attaches EO metadata to each memo.

- 🧾 **Final Consolidation**  
  Outputs a single JSON file mapping each EO to its related documents.

---

## 📂 Output Structure

The final JSON is saved to:

```
./docs/consolidated_eo_references.json
```

Each object is structured like this:

```json
{
  "eo_number": "14222",
  "eo_title": "Implementing the President's Department of Government Efficiency Cost Efficiency Initiative",
  "eo_link": "https://...",
  "opm_docs": [ ... ],
  "da_docs": [ ... ],
  "dod_docs": [ ... ]
}
```

---

## 🛠 Project Structure

```
.
├── EO_Reference_Consolidator.py
├── OPM_Memo_Scraper.py
├── DA_Memo_Scraper.py
├── PDF_Analyzer.py
├── Presidential_Order_Scraper.py
├── main.py
├── docs/
│   ├── PO_Docs.json
│   ├── OPM_Memos.json
│   ├── DA_Memos.json
│   └── consolidated_eo_references.json
├── LICENSE
└── README.md
```

---

## 📦 Setup Instructions

### 1. Clone this Repository

```bash
git clone https://github.com/GearSmith-Integrations/eo-consolidator.git
cd eo-consolidator
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> Python 3.8+ recommended

---

## 🧪 Run the Application

```bash
python main.py
```

All outputs will be saved in the `./docs/` directory.

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome!

- Fork this repository
- Create a feature branch: `git checkout -b feature/my-feature`
- Commit your changes: `git commit -m "Add my feature"`
- Push to your branch: `git push origin feature/my-feature`
- Open a pull request

---

## 🙏 Acknowledgments

- U.S. Army, OPM, and DoD for publicly accessible documents.
- [`PyPDF2`](https://github.com/py-pdf/pypdf) for PDF parsing.
- [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/) for HTML scraping.
