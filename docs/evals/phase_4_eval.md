# Phase 4 — Retrieval & LLM Response Generation: Evaluation

> Evaluation criteria and acceptance tests for Phase 4 of the [Implementation Plan](file:///d:/DRIVE%20F/RAG%20CHATBOT/docs/implementation_plan.md)

---

## Summary

| Attribute      | Value                                    |
|----------------|------------------------------------------|
| **Phase**      | 4 — Retrieval & LLM Response Generation  |
| **Goal**       | Wire up semantic search → context assembly → LLM generation → response formatting |
| **Duration**   | ~2 days                                  |
| **Evaluator**  | Developer (self-check) + automated + manual |

---

## Phase 4A — Retriever Evaluation

### E4A.1 — Query Embedding

| # | Check | Pass Criteria |
|---|-------|---------------|
| E4A.1.1 | `src/retriever.py` exists and is importable | `python -c "from src.retriever import *"` succeeds |
| E4A.1.2 | Same embedding model used | `BAAI/bge-small-en-v1.5` (same model as indexing) |
| E4A.1.3 | Query embedding dimension = 384 | Output vector has 384 dimensions |
| E4A.1.4 | Embedding is deterministic | Same input produces same output vector |

**Verification Script:**
```python
from src.retriever import embed_query

embedding = embed_query("What is the expense ratio?")
assert len(embedding) == 384, f"Wrong dimension: {len(embedding)}"

# Determinism check
embedding2 = embed_query("What is the expense ratio?")
assert embedding == embedding2, "Embeddings are not deterministic"

print("PASS — Query embedding works correctly")
```

---

### E4A.2 — Semantic Search

| # | Test Query | Expected Behaviour | Pass Criteria |
|---|------------|--------------------|---------------|
| E4A.2.1 | `"expense ratio HDFC Mid-Cap"` | Returns top-K chunks about HDFC Mid-Cap expense ratio | Relevant chunks in results |
| E4A.2.2 | `"minimum SIP amount"` | Returns chunks about SIP details | SIP-related content in top results |
| E4A.2.3 | `"exit load policy"` | Returns chunks about exit load | Exit load content in top results |
| E4A.2.4 | `"fund manager HDFC Flexi Cap"` | Returns chunks about fund manager | Fund manager info in top results |
| E4A.2.5 | Top-K results count | Returns 3–5 results | `len(results) >= 3 and len(results) <= 5` |
| E4A.2.6 | Cosine similarity used | Similarity metric is cosine | Confirmed in ChromaDB query config |

**Verification Script:**
```python
from src.retriever import retrieve

results = retrieve("expense ratio HDFC Mid-Cap")
assert 3 <= len(results) <= 5, f"Expected 3-5 results, got {len(results)}"
assert any("expense" in r["text"].lower() or "ratio" in r["text"].lower() for r in results), \
    "No relevant results for expense ratio query"

print("PASS — Semantic search returns relevant results")
```

---

### E4A.3 — Context Assembly

| # | Check | Pass Criteria |
|---|-------|---------------|
| E4A.3.1 | Chunks combined into single context string | Output is a single string |
| E4A.3.2 | Source URLs included in context | At least one Groww URL present in assembled context |
| E4A.3.3 | Context is well-formatted | Chunks are separated clearly (e.g., numbered or delimited) |
| E4A.3.4 | Context length is reasonable | Combined context doesn't exceed model's context window |

---

## Phase 4B — LLM Generator Evaluation

### E4B.1 — System Prompt

| # | Check | Pass Criteria |
|---|-------|---------------|
| E4B.1.1 | `src/generator.py` exists and is importable | `python -c "from src.generator import *"` succeeds |
| E4B.1.2 | System prompt implements 7 architecture rules | All rules from `architecture.md` are encoded |
| E4B.1.3 | System prompt enforces factual-only responses | Prompt explicitly states "no investment advice" |
| E4B.1.4 | System prompt enforces citation requirement | Prompt requires source URL in response |

---

### E4B.2 — Prompt Template

| # | Check | Pass Criteria |
|---|-------|---------------|
| E4B.2.1 | Template includes context section | `Context:` placeholder present |
| E4B.2.2 | Template includes source URLs | `Source URLs:` placeholder present |
| E4B.2.3 | Template includes user question | `User Question:` placeholder present |
| E4B.2.4 | Template is correctly formatted | No missing or malformed placeholders |

---

### E4B.3 — LLM API Integration

| # | Check | Pass Criteria |
|---|-------|---------------|
| E4B.3.1 | Groq API called successfully | API call returns a valid response |
| E4B.3.2 | Temperature = 0.1 | Low temperature for factual accuracy |
| E4B.3.3 | Max tokens = 150 | Token limit enforced |
| E4B.3.4 | Response is non-empty | LLM returns at least one sentence |

**Verification Script:**
```python
from src.generator import generate_response

response = generate_response(
    context="HDFC Mid-Cap Opportunities Fund has an expense ratio of 1.64%.",
    source_urls=["https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund"],
    question="What is the expense ratio of HDFC Mid-Cap?"
)

assert len(response) > 0, "Empty response from LLM"
print(f"PASS — LLM response: {response[:100]}...")
```

---

### E4B.4 — Error Handling

| # | Scenario | Expected Behaviour | Pass Criteria |
|---|----------|--------------------|---------------|
| E4B.4.1 | Invalid API key | Graceful error message | No unhandled exception |
| E4B.4.2 | API rate limit exceeded | Retry or informative error | Handles `429` status gracefully |
| E4B.4.3 | API timeout | Timeout error caught | Handles timeout without crash |
| E4B.4.4 | Empty context provided | Returns "no information available" response | Doesn't hallucinate |

---

## Phase 4C — Response Formatter Evaluation

### E4C.1 — Citation Link Validation

| # | Check | Pass Criteria |
|---|-------|---------------|
| E4C.1.1 | `src/formatter.py` exists and is importable | `python -c "from src.formatter import *"` succeeds |
| E4C.1.2 | Response with citation passes through | Citation URL preserved |
| E4C.1.3 | Response without citation gets one injected | Source URL appended from metadata |
| E4C.1.4 | Injected URL is valid | URL starts with `https://groww.in/` |

---

### E4C.2 — Footer Date Enforcement

| # | Check | Pass Criteria |
|---|-------|---------------|
| E4C.2.1 | Date footer present | Response ends with `"Last updated from sources: <date>"` |
| E4C.2.2 | Date is from metadata | Date matches `scraped_date` from chunk metadata |
| E4C.2.3 | Footer always appended | Even if LLM already includes a date, footer is standardized |

---

### E4C.3 — Sentence Count Enforcement

| # | Test Input | Expected Behaviour | Pass Criteria |
|---|------------|--------------------|---------------|
| E4C.3.1 | 1-sentence LLM response | Passes through unchanged | 1 sentence in output |
| E4C.3.2 | 3-sentence LLM response | Passes through unchanged | 3 sentences in output |
| E4C.3.3 | 5-sentence LLM response | Truncated to 3 sentences | ≤ 3 sentences in output |
| E4C.3.4 | 10-sentence LLM response | Truncated to 3 sentences | ≤ 3 sentences in output |

**Verification Script:**
```python
from src.formatter import format_response

# Test truncation
long_response = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
formatted = format_response(long_response, source_url="https://groww.in/test", scraped_date="2026-08-04")

# Count sentences (excluding footer)
main_text = formatted.split("Last updated")[0]
sentence_count = len([s for s in main_text.split('.') if s.strip()])
assert sentence_count <= 3, f"Too many sentences: {sentence_count}"

assert "Last updated from sources:" in formatted, "Missing date footer"
print("PASS — Response formatting works correctly")
```

---

## End-to-End Phase 4 Tests

| # | Test Scenario | Input | Expected Output |
|---|--------------|-------|-----------------|
| E4.E2E.1 | Factual query full pipeline | `"What is the expense ratio of HDFC Mid-Cap?"` | ≤ 3 sentences, correct data, citation URL, date footer |
| E4.E2E.2 | Factual query with no context | Query about unknown scheme | `"I don't have this information"` message |
| E4.E2E.3 | Refusal query through pipeline | `"Should I invest in HDFC?"` | Polite refusal (handled before reaching generator) |

---

## Overall Phase 4 Exit Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Query embedding uses the same model as indexing (`BAAI/bge-small-en-v1.5`) | ☐ |
| 2 | Semantic search returns 3–5 relevant chunks with cosine similarity | ☐ |
| 3 | Context assembly produces a well-formatted context string with source URLs | ☐ |
| 4 | LLM generates factual responses with temperature=0.1, max_tokens=150 | ☐ |
| 5 | API errors (invalid key, rate limit, timeout) are handled gracefully | ☐ |
| 6 | Response contains citation link (injected if missing) | ☐ |
| 7 | Response has date footer: `"Last updated from sources: <date>"` | ☐ |
| 8 | Response is ≤ 3 sentences (truncated if needed) | ☐ |
| 9 | E2E test: factual query → correct formatted response with citation and footer | ☐ |

> **Phase 4 is PASSED when all boxes above are checked ✅**
