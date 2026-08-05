# Phase 1 — Data Ingestion (Offline Pipeline): Evaluation

> Evaluation criteria and acceptance tests for Phase 1 of the [Implementation Plan](file:///d:/DRIVE%20F/RAG%20CHATBOT/docs/implementation_plan.md)

---

## Summary

| Attribute      | Value                                    |
|----------------|------------------------------------------|
| **Phase**      | 1 — Data Ingestion (Offline Pipeline)    |
| **Goal**       | Scrape 5 Groww URLs, clean HTML, save structured text files |
| **Duration**   | ~2 days                                  |
| **Evaluator**  | Developer (self-check) + manual content review |

---

## Phase 1A — Web Scraper Evaluation

### E1A.1 — Scraper Functionality

| # | Check | Pass Criteria |
|---|-------|---------------|
| E1A.1.1 | `src/scraper.py` exists and is importable | `python -c "from src.scraper import *"` succeeds |
| E1A.1.2 | Scraper fetches all 5 URLs | No HTTP errors (status 200) for all Groww scheme pages |
| E1A.1.3 | Scraper handles network errors | Timeout/connection errors are caught gracefully with informative messages |
| E1A.1.4 | Scraper handles JS-rendered content | If `requests` fails to capture content, fallback mechanism is documented or implemented |

**Verification Command:**
```bash
python -c "from src.scraper import *; print('PASS')"
```

---

### E1A.2 — Content Extraction

| # | Check | Pass Criteria |
|---|-------|---------------|
| E1A.2.1 | Scheme name extracted | Each page yields a non-empty scheme name |
| E1A.2.2 | Expense ratio extracted | Numeric value or "N/A" present |
| E1A.2.3 | Exit load extracted | Text describing exit load conditions present |
| E1A.2.4 | Minimum investment extracted | Numeric value present |
| E1A.2.5 | SIP details extracted | SIP amount and frequency present |
| E1A.2.6 | Risk level extracted | Risk classification (e.g., "Very High", "High") present |
| E1A.2.7 | Benchmark extracted | Benchmark index name present |
| E1A.2.8 | Fund manager extracted | Fund manager name(s) present |
| E1A.2.9 | Category extracted | Fund category label present |

---

### E1A.3 — Raw HTML Storage

| # | Check | Pass Criteria |
|---|-------|---------------|
| E1A.3.1 | Raw HTML files saved to `data/raw/` | 5 `.html` files exist in `data/raw/` |
| E1A.3.2 | Files named correctly | Names follow pattern: `hdfc_mid_cap.html`, `hdfc_flexi_cap.html`, etc. |
| E1A.3.3 | Files are non-empty | Each file is > 1 KB |
| E1A.3.4 | HTML is well-formed | Files contain valid HTML content |

**Verification Command:**
```bash
ls data/raw/*.html | wc -l
# Expected: 5
```

---

## Phase 1B — Document Parser & Cleaner Evaluation

### E1B.1 — HTML Cleaning

| # | Check | Pass Criteria |
|---|-------|---------------|
| E1B.1.1 | `src/parser.py` exists and is importable | `python -c "from src.parser import *"` succeeds |
| E1B.1.2 | HTML tags stripped | Output contains no `<div>`, `<span>`, `<script>`, etc. |
| E1B.1.3 | Navigation bars removed | No menu/nav content in output |
| E1B.1.4 | Footers removed | No site footer content in output |
| E1B.1.5 | Advertisements removed | No ad-related content in output |
| E1B.1.6 | CSS/JS content removed | No `<style>` or `<script>` content remains |

---

### E1B.2 — Text Structuring

| # | Check | Pass Criteria |
|---|-------|---------------|
| E1B.2.1 | Section headers preserved | Key sections (e.g., "Expense Ratio", "Exit Load") are identifiable |
| E1B.2.2 | Readable formatting | Text is human-readable, not garbled |
| E1B.2.3 | No duplicate content | No repeated paragraphs or sections |
| E1B.2.4 | Whitespace normalized | No excessive blank lines or spaces |

---

### E1B.3 — Metadata Extraction

| # | Check | Pass Criteria |
|---|-------|---------------|
| E1B.3.1 | Scheme name in metadata | `scheme_name` field present and correct |
| E1B.3.2 | Source URL in metadata | `source_url` field present and valid |
| E1B.3.3 | Category in metadata | `category` field present |
| E1B.3.4 | Scrape date in metadata | `scraped_date` field present in ISO format |

---

### E1B.4 — Processed File Output

| # | Check | Pass Criteria |
|---|-------|---------------|
| E1B.4.1 | 5 `.txt` files in `data/processed/` | One per scheme |
| E1B.4.2 | 5 `.json` metadata files in `data/processed/` | One per scheme, matching `.txt` files |
| E1B.4.3 | Text files are non-empty | Each `.txt` file is > 500 bytes |
| E1B.4.4 | JSON files are valid | Each `.json` file parses without errors |

**Verification Commands:**
```bash
ls data/processed/*.txt | wc -l
# Expected: 5

ls data/processed/*.json | wc -l
# Expected: 5

python -c "import json; [json.load(open(f)) for f in __import__('glob').glob('data/processed/*.json')]; print('PASS')"
```

---

### E1B.5 — Manual Content Review

| # | Check | Pass Criteria |
|---|-------|---------------|
| E1B.5.1 | No junk/irrelevant content | Manual spot-check confirms clean data |
| E1B.5.2 | Key financial data present | Expense ratio, NAV, exit load, etc. are in the text |
| E1B.5.3 | Data accuracy | Extracted values match the source website |

> [!IMPORTANT]
> Manual review is mandatory. Automated checks cannot validate content accuracy against the live Groww website.

---

## Overall Phase 1 Exit Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | 5 clean `.txt` files exist in `data/processed/` | ☐ |
| 2 | 5 matching `.json` metadata files exist in `data/processed/` | ☐ |
| 3 | Each text file contains accurate, structured scheme information | ☐ |
| 4 | Metadata includes `scheme_name`, `source_url`, `category`, `scraped_date` | ☐ |
| 5 | Manual review confirms no junk content in any file | ☐ |

> **Phase 1 is PASSED when all boxes above are checked ✅**
