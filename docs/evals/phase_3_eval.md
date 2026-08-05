# Phase 3 — Query Classification & Guardrails: Evaluation

> Evaluation criteria and acceptance tests for Phase 3 of the [Implementation Plan](file:///d:/DRIVE%20F/RAG%20CHATBOT/docs/implementation_plan.md)

---

## Summary

| Attribute      | Value                                    |
|----------------|------------------------------------------|
| **Phase**      | 3 — Query Classification & Guardrails    |
| **Goal**       | Classify queries and detect PII before they enter the RAG pipeline |
| **Duration**   | ~1 day                                   |
| **Evaluator**  | Developer (self-check) + automated unit tests |

---

## E3.1 — Keyword-Based Advisory Detection

| # | Test Input | Expected Classification | Pass Criteria |
|---|------------|------------------------|---------------|
| E3.1.1 | `"Should I invest in HDFC Mid-Cap?"` | Advisory | Classified as advisory |
| E3.1.2 | `"Which fund is better for long term?"` | Advisory | Classified as advisory |
| E3.1.3 | `"Can you recommend a good mutual fund?"` | Advisory | Classified as advisory |
| E3.1.4 | `"What is the best fund for me?"` | Advisory | Classified as advisory |
| E3.1.5 | `"Compare HDFC Mid-Cap and Flexi Cap"` | Advisory | Classified as advisory |
| E3.1.6 | `"Should I invest in SIP or lumpsum?"` | Advisory | Classified as advisory |
| E3.1.7 | `"What is the expense ratio of HDFC Mid-Cap?"` | Factual | **NOT** classified as advisory |
| E3.1.8 | `"What is the NAV of HDFC Flexi Cap?"` | Factual | **NOT** classified as advisory |

**Verification Script:**
```python
from src.classifier import classify_query

advisory_queries = [
    "Should I invest in HDFC Mid-Cap?",
    "Which fund is better for long term?",
    "Can you recommend a good mutual fund?",
    "What is the best fund for me?",
    "Compare HDFC Mid-Cap and Flexi Cap",
    "Should I invest in SIP or lumpsum?",
]

factual_queries = [
    "What is the expense ratio of HDFC Mid-Cap?",
    "What is the NAV of HDFC Flexi Cap?",
]

for q in advisory_queries:
    result = classify_query(q)
    assert result["type"] == "advisory", f"FAIL: '{q}' not classified as advisory"

for q in factual_queries:
    result = classify_query(q)
    assert result["type"] == "factual", f"FAIL: '{q}' wrongly classified as advisory"

print("PASS — Advisory detection works correctly")
```

---

## E3.2 — PII Regex Filters

| # | Test Input | PII Type | Pass Criteria |
|---|------------|----------|---------------|
| E3.2.1 | `"My PAN is ABCDE1234F"` | PAN | PII detected |
| E3.2.2 | `"Aadhaar: 123456789012"` | Aadhaar | PII detected |
| E3.2.3 | `"Call me at 9876543210"` | Phone | PII detected |
| E3.2.4 | `"Email: user@example.com"` | Email | PII detected |
| E3.2.5 | `"My PAN ABCDE1234F, check returns"` | PAN (embedded) | PII detected |
| E3.2.6 | `"What is the expense ratio?"` | None | **No** PII detected |
| E3.2.7 | `"NAV is 12345"` | None (5-digit number) | **No** PII detected (not 10 or 12 digits) |

**Verification Script:**
```python
from src.classifier import detect_pii

pii_inputs = [
    ("My PAN is ABCDE1234F", "PAN"),
    ("Aadhaar: 123456789012", "Aadhaar"),
    ("Call me at 9876543210", "Phone"),
    ("Email: user@example.com", "Email"),
    ("My PAN ABCDE1234F, check returns", "PAN"),
]

clean_inputs = [
    "What is the expense ratio?",
    "NAV is 12345",
]

for text, pii_type in pii_inputs:
    assert detect_pii(text), f"FAIL: PII ({pii_type}) not detected in '{text}'"

for text in clean_inputs:
    assert not detect_pii(text), f"FAIL: False positive PII in '{text}'"

print("PASS — PII detection works correctly")
```

---

## E3.3 — LLM-Based Classification Fallback

| # | Test Input | Expected Behaviour | Pass Criteria |
|---|------------|--------------------|---------------|
| E3.3.1 | `"Tell me about the risk profile"` | Ambiguous → LLM classifies as factual | Returns a classification |
| E3.3.2 | `"Is this a good time to enter the market?"` | Ambiguous → LLM classifies as advisory | Returns a classification |
| E3.3.3 | LLM API unavailable | Graceful fallback | Returns safe default (advisory) or error message |

> [!NOTE]
> LLM-based classification requires a valid `GROQ_API_KEY`. If unavailable during testing, verify that the fallback mechanism handles API errors gracefully.

---

## E3.4 — Refusal Response Generator

| # | Check | Pass Criteria |
|---|-------|---------------|
| E3.4.1 | Advisory refusal is polite | Response is courteous, not dismissive |
| E3.4.2 | Refusal includes educational link | Response contains AMFI or SEBI reference URL |
| E3.4.3 | PII refusal includes privacy notice | Response mentions data privacy and that PII is not processed |
| E3.4.4 | Refusal format is consistent | All refusal responses follow the same template structure |

**Verification Script:**
```python
from src.classifier import get_refusal_response

advisory_refusal = get_refusal_response("advisory")
assert "amfi" in advisory_refusal.lower() or "sebi" in advisory_refusal.lower(), \
    "Missing AMFI/SEBI link in advisory refusal"

pii_refusal = get_refusal_response("pii")
assert "privacy" in pii_refusal.lower() or "personal" in pii_refusal.lower(), \
    "Missing privacy notice in PII refusal"

print("PASS — Refusal responses are well-formed")
```

---

## E3.5 — Unit Tests

| # | Check | Pass Criteria |
|---|-------|---------------|
| E3.5.1 | `tests/test_classifier.py` exists | File present in `tests/` directory |
| E3.5.2 | Tests cover advisory queries | ≥ 5 advisory test cases |
| E3.5.3 | Tests cover factual queries | ≥ 3 factual test cases |
| E3.5.4 | Tests cover PII queries | ≥ 4 PII test cases (PAN, Aadhaar, phone, email) |
| E3.5.5 | Tests cover edge cases | At least 2 edge cases (e.g., empty string, very long input) |
| E3.5.6 | All tests pass | `pytest tests/test_classifier.py` exits with code 0 |

**Verification Command:**
```bash
pytest tests/test_classifier.py -v
# Expected: All tests pass
```

---

## Overall Phase 3 Exit Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All advisory keyword patterns are detected correctly | ☐ |
| 2 | All PII patterns (PAN, Aadhaar, phone, email) are detected correctly | ☐ |
| 3 | No false positives on factual queries | ☐ |
| 4 | LLM fallback classification works (or fails gracefully without API key) | ☐ |
| 5 | Refusal responses are polite and include educational links | ☐ |
| 6 | All unit tests in `tests/test_classifier.py` pass | ☐ |

> **Phase 3 is PASSED when all boxes above are checked ✅**
