# Phase 5 — User Interface (Streamlit): Evaluation

> Evaluation criteria and acceptance tests for Phase 5 of the [Implementation Plan](file:///d:/DRIVE%20F/RAG%20CHATBOT/docs/implementation_plan.md)

---

## Summary

| Attribute      | Value                                    |
|----------------|------------------------------------------|
| **Phase**      | 5 — User Interface (Streamlit)           |
| **Goal**       | Build a minimal, functional chat interface |
| **Duration**   | ~1–2 days                                |
| **Evaluator**  | Developer (manual UI review) + functional testing |

---

## E5.1 — App Layout

| # | Check | Pass Criteria |
|---|-------|---------------|
| E5.1.1 | `src/app.py` exists and is importable | File present in `src/` |
| E5.1.2 | App launches without errors | `streamlit run src/app.py` starts successfully |
| E5.1.3 | Header with title displayed | Page shows application title |
| E5.1.4 | Disclaimer badge visible | Disclaimer badge/banner appears near the header |
| E5.1.5 | Page title set | Browser tab shows descriptive title |

**Verification Command:**
```bash
streamlit run src/app.py --server.headless true &
sleep 5
curl -s http://localhost:8501 | head -50
# Expected: HTML content with app title
```

---

## E5.2 — Welcome Panel

| # | Check | Pass Criteria |
|---|-------|---------------|
| E5.2.1 | Greeting message displayed | Welcome/greeting text visible on first load |
| E5.2.2 | 3 example questions shown | Exactly 3 clickable example questions are displayed |
| E5.2.3 | Example questions are clickable | Clicking an example fills the chat input |
| E5.2.4 | Examples are relevant | Questions relate to HDFC mutual fund facts |

**Manual Test Steps:**
1. Open `http://localhost:8501` in a browser
2. Verify greeting message is visible
3. Verify 3 example questions are displayed
4. Click each example question and verify it populates the chat input

---

## E5.3 — Chat Input & Display

| # | Check | Pass Criteria |
|---|-------|---------------|
| E5.3.1 | `st.chat_input()` present | Text input field visible at bottom of page |
| E5.3.2 | User messages displayed | User messages appear with user icon/avatar |
| E5.3.3 | Bot messages displayed | Bot responses appear with assistant icon/avatar |
| E5.3.4 | Threaded conversation | Messages stack chronologically |
| E5.3.5 | Chat history persists in session | Scrolling up shows previous messages |
| E5.3.6 | Input clears after sending | Chat input field is empty after message is sent |

---

## E5.4 — Pipeline Integration

| # | Test Scenario | Expected Behaviour | Pass Criteria |
|---|---------------|--------------------|---------------|
| E5.4.1 | Type factual query | Response with data, citation, footer | Correctly formatted answer displayed |
| E5.4.2 | Type advisory query | Refusal message displayed | Polite refusal with AMFI/SEBI link |
| E5.4.3 | Type PII-containing query | PII blocked message | Privacy notice displayed |
| E5.4.4 | Type out-of-scope query | "No information" response | Appropriate fallback message |
| E5.4.5 | Submit empty input | No crash or error | Graceful handling (ignored or prompted) |
| E5.4.6 | Rapid successive queries | No crash or race condition | All queries processed sequentially |

**Manual Test Steps:**
1. Type `"What is the expense ratio of HDFC Mid-Cap?"` → verify formatted response
2. Type `"Should I invest in HDFC?"` → verify refusal
3. Type `"My PAN is ABCDE1234F"` → verify PII block
4. Type `"Tell me about SBI funds"` → verify out-of-scope response

---

## E5.5 — Disclaimer Footer

| # | Check | Pass Criteria |
|---|-------|---------------|
| E5.5.1 | Footer visible on all pages | Persistent disclaimer at bottom |
| E5.5.2 | Footer text correct | Contains `"Facts-only. No investment advice."` or equivalent |
| E5.5.3 | Footer does not overlap chat | Footer is separate from chat messages |

---

## E5.6 — Basic Styling

| # | Check | Pass Criteria |
|---|-------|---------------|
| E5.6.1 | Clean layout | No visual clutter, elements properly aligned |
| E5.6.2 | Readable fonts | Text is legible at default zoom |
| E5.6.3 | Proper spacing | Elements have adequate padding/margins |
| E5.6.4 | Responsive | Layout doesn't break on common window sizes |
| E5.6.5 | No visual artifacts | No broken images, cut-off text, or overlapping elements |

---

## E5.7 — Error States

| # | Scenario | Expected Behaviour | Pass Criteria |
|---|----------|--------------------|---------------|
| E5.7.1 | Groq API key missing | User-friendly error displayed | No raw traceback shown |
| E5.7.2 | ChromaDB unavailable | Error message about data load | No crash |
| E5.7.3 | Network timeout | Timeout message displayed | App remains functional |

---

## Overall Phase 5 Exit Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `streamlit run src/app.py` launches a working chat interface | ☐ |
| 2 | Header with title and disclaimer badge is visible | ☐ |
| 3 | Welcome panel shows greeting + 3 clickable example questions | ☐ |
| 4 | Chat input accepts queries and displays threaded responses | ☐ |
| 5 | Pipeline is fully wired: input → classifier → retriever → generator → formatter → display | ☐ |
| 6 | Disclaimer footer is persistent and visible | ☐ |
| 7 | Layout is clean, readable, and properly spaced | ☐ |
| 8 | Error states are handled gracefully without raw tracebacks | ☐ |

> **Phase 5 is PASSED when all boxes above are checked ✅**
