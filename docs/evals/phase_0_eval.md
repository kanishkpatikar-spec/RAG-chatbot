# Phase 0 — Project Setup & Environment: Evaluation

> Evaluation criteria and acceptance tests for Phase 0 of the [Implementation Plan](file:///d:/DRIVE%20F/RAG%20CHATBOT/docs/implementation_plan.md)

---

## Summary

| Attribute      | Value                                    |
|----------------|------------------------------------------|
| **Phase**      | 0 — Project Setup & Environment          |
| **Goal**       | Set up project skeleton, dependencies, and configuration |
| **Duration**   | ~1 day                                   |
| **Evaluator**  | Developer (self-check)                   |

---

## Evaluation Checklist

### E0.1 — Directory Structure

| # | Check | Pass Criteria |
|---|-------|---------------|
| E0.1.1 | `src/` directory exists | Directory is present at project root |
| E0.1.2 | `data/raw/` directory exists | Directory is present and writable |
| E0.1.3 | `data/processed/` directory exists | Directory is present and writable |
| E0.1.4 | `vectorstore/` directory exists | Directory is present and writable |
| E0.1.5 | `config/` directory exists | Directory is present |
| E0.1.6 | `docs/` directory exists | Directory is present |

**Verification Command:**
```bash
# All should return 0 (success)
test -d src && test -d data/raw && test -d data/processed && test -d vectorstore && test -d config && test -d docs && echo "PASS" || echo "FAIL"
```

---

### E0.2 — Virtual Environment

| # | Check | Pass Criteria |
|---|-------|---------------|
| E0.2.1 | `venv/` directory exists | Created via `python -m venv venv` |
| E0.2.2 | Virtual env activates without errors | `venv\Scripts\activate` (Windows) succeeds |
| E0.2.3 | Python version ≥ 3.9 | `python --version` reports 3.9+ |

**Verification Command:**
```bash
python --version
# Expected: Python 3.9.x or higher
```

---

### E0.3 — Dependencies

| # | Check | Pass Criteria |
|---|-------|---------------|
| E0.3.1 | `requirements.txt` exists at project root | File is present and non-empty |
| E0.3.2 | All required packages listed | Contains: `requests`, `beautifulsoup4`, `langchain`, `langchain-community`, `langchain-groq`, `chromadb`, `sentence-transformers`, `streamlit`, `python-dotenv` |
| E0.3.3 | Clean install succeeds | `pip install -r requirements.txt` exits with code 0 |
| E0.3.4 | No version conflicts | No pip dependency resolution warnings |

**Verification Command:**
```bash
pip install -r requirements.txt
echo $?
# Expected: 0
```

---

### E0.4 — Environment Configuration

| # | Check | Pass Criteria |
|---|-------|---------------|
| E0.4.1 | `.env` file exists | File is present at project root |
| E0.4.2 | `GROQ_API_KEY` placeholder present | File contains `GROQ_API_KEY=` (with or without a value) |
| E0.4.3 | `.env` is gitignored | `.gitignore` contains `.env` entry |

**Verification Command:**
```bash
grep "GROQ_API_KEY" .env && echo "PASS" || echo "FAIL"
```

---

### E0.5 — Settings Module

| # | Check | Pass Criteria |
|---|-------|---------------|
| E0.5.1 | `config/settings.py` exists | File is present |
| E0.5.2 | URLs list defined | Contains list of 5 Groww scheme URLs |
| E0.5.3 | Chunk size = 500 | `CHUNK_SIZE` constant equals `500` |
| E0.5.4 | Chunk overlap = 50 | `CHUNK_OVERLAP` constant equals `50` |
| E0.5.5 | Top-K = 3–5 | `TOP_K` constant is between `3` and `5` |
| E0.5.6 | Temperature = 0.1 | `TEMPERATURE` constant equals `0.1` |
| E0.5.7 | Max tokens = 150 | `MAX_TOKENS` constant equals `150` |
| E0.5.8 | Config loads without errors | `python -c "from config.settings import *"` succeeds |

**Verification Command:**
```bash
python -c "from config.settings import *; print('PASS')"
# Expected: PASS
```

---

### E0.6 — Git Ignore

| # | Check | Pass Criteria |
|---|-------|---------------|
| E0.6.1 | `.gitignore` exists | File is present at project root |
| E0.6.2 | `venv/` is excluded | Entry present in `.gitignore` |
| E0.6.3 | `.env` is excluded | Entry present in `.gitignore` |
| E0.6.4 | `vectorstore/` is excluded | Entry present in `.gitignore` |
| E0.6.5 | `data/raw/` is excluded | Entry present in `.gitignore` |
| E0.6.6 | `__pycache__/` is excluded | Entry present in `.gitignore` |

---

## Overall Phase 0 Exit Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `pip install -r requirements.txt` succeeds | ☐ |
| 2 | All directories (`src/`, `data/raw/`, `data/processed/`, `vectorstore/`, `config/`, `docs/`) exist | ☐ |
| 3 | `config/settings.py` loads without import errors | ☐ |
| 4 | `.env` template contains `GROQ_API_KEY` placeholder | ☐ |
| 5 | `.gitignore` excludes all sensitive/generated paths | ☐ |

> **Phase 0 is PASSED when all boxes above are checked ✅**
