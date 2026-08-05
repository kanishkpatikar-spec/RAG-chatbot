# Phase 2 — Chunking, Embedding & Indexing: Evaluation

> Evaluation criteria and acceptance tests for Phase 2 of the [Implementation Plan](file:///d:/DRIVE%20F/RAG%20CHATBOT/docs/implementation_plan.md)

---

## Summary

| Attribute      | Value                                    |
|----------------|------------------------------------------|
| **Phase**      | 2 — Chunking, Embedding & Indexing       |
| **Goal**       | Split documents into chunks, generate embeddings, store in ChromaDB |
| **Duration**   | ~1–2 days                                |
| **Evaluator**  | Developer (self-check) + automated verification |

---

## E2.1 — Text Chunking

| # | Check | Pass Criteria |
|---|-------|---------------|
| E2.1.1 | Chunker uses `RecursiveCharacterTextSplitter` | Import and usage confirmed in `src/parser.py` |
| E2.1.2 | Chunk size = 500 tokens | Configured as per `config/settings.py` |
| E2.1.3 | Chunk overlap = 50 tokens | Configured as per `config/settings.py` |
| E2.1.4 | All 5 documents chunked | Total chunk count > 0 for each document |
| E2.1.5 | No empty chunks | Every chunk has `len(text.strip()) > 0` |
| E2.1.6 | Chunk boundaries are sensible | Chunks don't break mid-word or mid-sentence when possible |

**Verification Script:**
```python
from src.parser import chunk_documents  # adjust import as needed
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

assert CHUNK_SIZE == 500, f"Chunk size is {CHUNK_SIZE}, expected 500"
assert CHUNK_OVERLAP == 50, f"Chunk overlap is {CHUNK_OVERLAP}, expected 50"

chunks = chunk_documents()  # adjust call as needed
assert len(chunks) > 0, "No chunks generated"
assert all(len(c.page_content.strip()) > 0 for c in chunks), "Empty chunk found"
print(f"PASS — {len(chunks)} chunks generated")
```

---

## E2.2 — Chunk Metadata

| # | Check | Pass Criteria |
|---|-------|---------------|
| E2.2.1 | `scheme_name` attached | Every chunk has `scheme_name` in metadata |
| E2.2.2 | `source_url` attached | Every chunk has `source_url` in metadata |
| E2.2.3 | `category` attached | Every chunk has `category` in metadata |
| E2.2.4 | `scraped_date` attached | Every chunk has `scraped_date` in metadata |
| E2.2.5 | `chunk_index` attached | Every chunk has a sequential `chunk_index` starting from 0 |

**Verification Script:**
```python
required_keys = {"scheme_name", "source_url", "category", "scraped_date", "chunk_index"}

for chunk in chunks:
    missing = required_keys - set(chunk.metadata.keys())
    assert not missing, f"Chunk missing metadata: {missing}"

print("PASS — All metadata keys present")
```

---

## E2.3 — Embedding Generation

| # | Check | Pass Criteria |
|---|-------|---------------|
| E2.3.1 | `src/embedder.py` exists and is importable | `python -c "from src.embedder import *"` succeeds |
| E2.3.2 | Model is `BAAI/bge-small-en-v1.5` | Correct model name used in embedding function |
| E2.3.3 | Embeddings are generated for all chunks | Embedding count == chunk count |
| E2.3.4 | Embedding dimensionality is correct | Each embedding vector has 384 dimensions (bge-small) |
| E2.3.5 | No `NaN` or `Inf` values | All embedding values are finite numbers |

**Verification Script:**
```python
import numpy as np
from src.embedder import get_embeddings  # adjust import

embeddings = get_embeddings(chunks)
assert len(embeddings) == len(chunks), "Embedding count mismatch"
assert all(len(e) == 384 for e in embeddings), "Wrong embedding dimensionality"
assert all(np.isfinite(e).all() for e in embeddings), "NaN/Inf in embeddings"
print("PASS — Embeddings valid")
```

---

## E2.4 — ChromaDB Storage

| # | Check | Pass Criteria |
|---|-------|---------------|
| E2.4.1 | ChromaDB collection created | Collection exists in `vectorstore/` |
| E2.4.2 | Collection is persistent | Data survives process restart |
| E2.4.3 | Document count matches chunk count | `collection.count()` equals total chunks |
| E2.4.4 | Metadata stored with embeddings | Queried results include metadata fields |

**Verification Script:**
```python
import chromadb

client = chromadb.PersistentClient(path="vectorstore/")
collection = client.get_collection("mutual_fund_faq")  # adjust name

assert collection.count() > 0, "Collection is empty"
print(f"PASS — Collection has {collection.count()} documents")
```

---

## E2.5 — Retrieval Verification (Smoke Test)

| # | Test Query | Expected Behaviour |
|---|------------|--------------------|
| E2.5.1 | `"expense ratio HDFC Mid-Cap"` | Returns chunks containing expense ratio information for HDFC Mid-Cap fund |
| E2.5.2 | `"SIP minimum amount"` | Returns chunks mentioning SIP details |
| E2.5.3 | `"exit load"` | Returns chunks discussing exit load policies |

**Verification Script:**
```python
results = collection.query(
    query_texts=["expense ratio HDFC Mid-Cap"],
    n_results=3
)

assert len(results["documents"][0]) == 3, "Expected 3 results"
assert any("expense" in doc.lower() or "ratio" in doc.lower() for doc in results["documents"][0]), \
    "Results don't seem relevant to query"
assert all("scheme_name" in m for m in results["metadatas"][0]), \
    "Metadata missing from results"

print("PASS — Retrieval returns relevant results with metadata")
```

---

## Overall Phase 2 Exit Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All 5 documents chunked with correct size (500) and overlap (50) | ☐ |
| 2 | Every chunk carries required metadata (`scheme_name`, `source_url`, `category`, `scraped_date`, `chunk_index`) | ☐ |
| 3 | Embeddings generated using `BAAI/bge-small-en-v1.5` with 384 dimensions | ☐ |
| 4 | ChromaDB collection populated and persistent in `vectorstore/` | ☐ |
| 5 | Test query `"expense ratio HDFC Mid-Cap"` returns relevant chunks with correct metadata | ☐ |

> **Phase 2 is PASSED when all boxes above are checked ✅**
