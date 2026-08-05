"""
Phase 4C — Response Formatter
==============================

Post-processes the raw LLM response to ensure compliance with the
architecture's output format:

  1. Citation link validation — inject source URL if missing
  2. Footer date enforcement — append "Last updated from sources: <date>"
  3. Sentence count enforcement — truncate to <= 3 sentences
"""

import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task 4C.3 — Sentence Splitting & Truncation
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    """
    Split text into sentences. Handles common abbreviations and decimal
    numbers to avoid false splits.
    """
    # Split on sentence-ending punctuation followed by whitespace or end-of-string
    # but avoid splitting on abbreviations like "Rs.", "Mr.", "e.g.", decimal numbers
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'(])', text)

    # Merge very short fragments (< 10 chars) back into the previous sentence
    merged: list[str] = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if merged and len(s) < 10:
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)

    return merged


def _truncate_to_sentences(text: str, max_sentences: int = 3) -> str:
    """Truncate text to at most `max_sentences` sentences."""
    sentences = _split_sentences(text)
    if len(sentences) <= max_sentences:
        return text
    logger.info(f"Truncating response from {len(sentences)} to {max_sentences} sentences.")
    truncated = " ".join(sentences[:max_sentences])
    # Ensure it ends with proper punctuation
    if not truncated.endswith((".", "!", "?")):
        truncated += "."
    return truncated


# ---------------------------------------------------------------------------
# Task 4C.1 — Citation Link Validation
# ---------------------------------------------------------------------------

def _has_source_url(text: str, source_urls: list[str]) -> bool:
    """Check if the response already contains any of the source URLs."""
    for url in source_urls:
        if url in text:
            return True
    # Also check for any groww.in URL
    return bool(re.search(r'https?://groww\.in/\S+', text))


def _inject_citation(text: str, source_urls: list[str]) -> str:
    """Inject a source citation if the response doesn't already contain one."""
    if not source_urls:
        return text
    if _has_source_url(text, source_urls):
        return text

    citation = f"\n\nSource: [{source_urls[0]}]({source_urls[0]})"
    logger.info("Injecting missing citation link into response.")
    return text + citation


# ---------------------------------------------------------------------------
# Task 4C.2 — Footer Date Enforcement
# ---------------------------------------------------------------------------

_FOOTER_PATTERN = re.compile(r"Last updated from sources:", re.IGNORECASE)


def _has_footer(text: str) -> bool:
    """Check if the response already has the date footer."""
    return bool(_FOOTER_PATTERN.search(text))


def _inject_footer(text: str, scraped_dates: list[str]) -> str:
    """Append the date footer if missing."""
    if _has_footer(text):
        return text

    # Use the most recent scraped date, or fall back to today
    if scraped_dates:
        # Parse and use the earliest/most representative date
        try:
            date_str = scraped_dates[0].split("T")[0]  # "2026-08-04T10:26:03" → "2026-08-04"
        except (IndexError, AttributeError):
            date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    footer = f"\n\nLast updated from sources: {date_str}"
    logger.info(f"Injecting missing date footer: {date_str}")
    return text + footer


# ---------------------------------------------------------------------------
# Main Formatter Pipeline
# ---------------------------------------------------------------------------

def format_response(
    raw_response: str,
    source_urls: list[str],
    scraped_dates: list[str],
    max_sentences: int = 3,
) -> str:
    """
    Post-process the raw LLM response to ensure compliance.

    Pipeline:
      1. Truncate to <= max_sentences
      2. Inject citation if missing
      3. Inject date footer if missing

    Args:
        raw_response:  The raw text from the LLM.
        source_urls:   Available source URLs from retrieval metadata.
        scraped_dates: Scrape dates from retrieval metadata.
        max_sentences: Maximum number of sentences allowed.

    Returns:
        The fully formatted, compliant response string.
    """
    if not raw_response or not raw_response.strip():
        return "I don't have this information in my current sources."

    text = raw_response.strip()

    # Step 1: Sentence truncation (on the main answer body only — before footer)
    # First, check if the LLM already included the footer, and separate it
    footer_match = _FOOTER_PATTERN.search(text)
    if footer_match:
        # Split at the footer line
        body = text[:footer_match.start()].strip()
        existing_footer = text[footer_match.start():].strip()
    else:
        body = text
        existing_footer = ""

    # Also check if the LLM included a "Source:" line — separate it
    source_match = re.search(r'\n\s*Source:\s*http', body)
    if source_match:
        citation_part = body[source_match.start():].strip()
        body = body[:source_match.start()].strip()
    else:
        citation_part = ""

    # Truncate the main body
    body = _truncate_to_sentences(body, max_sentences)

    # Reassemble (body only for now — we'll enforce citation and footer below)
    text = body
    if citation_part:
        text += "\n\n" + citation_part

    # Step 2: Ensure citation is present
    text = _inject_citation(text, source_urls)

    # Step 3: Ensure date footer is present
    if existing_footer:
        text += "\n\n" + existing_footer
    else:
        text = _inject_footer(text, scraped_dates)

    return text


# ---------------------------------------------------------------------------
# CLI Entry Point (for quick testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    # Test cases
    test_cases = [
        {
            "name": "Response with everything",
            "raw": "The expense ratio is 0.75%. Source: https://groww.in/mutual-funds/hdfc-mid-cap\nLast updated from sources: 2026-08-04",
            "urls": ["https://groww.in/mutual-funds/hdfc-mid-cap"],
            "dates": ["2026-08-04T10:26:03"],
        },
        {
            "name": "Response missing citation and footer",
            "raw": "The expense ratio of HDFC Mid-Cap Opportunities Fund is 0.75%. The fund is rated Very High risk. Minimum SIP is Rs 100.",
            "urls": ["https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth"],
            "dates": ["2026-08-04T10:26:03"],
        },
        {
            "name": "Response with too many sentences",
            "raw": "The expense ratio is 0.75%. The fund size is large. It has a 5-star rating. The minimum SIP is Rs 100. It was launched in 1999.",
            "urls": ["https://groww.in/mutual-funds/hdfc-mid-cap"],
            "dates": ["2026-08-04T10:26:03"],
        },
        {
            "name": "Empty response",
            "raw": "",
            "urls": [],
            "dates": [],
        },
    ]

    print("=" * 70)
    print("FORMATTER — MANUAL TEST RUN")
    print("=" * 70)

    for tc in test_cases:
        print(f"\n--- {tc['name']} ---")
        result = format_response(tc["raw"], tc["urls"], tc["dates"])
        print(result)
        print()
