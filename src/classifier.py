"""
Phase 3 — Query Classification & Guardrails
=============================================

This module sits at the entry of the RAG pipeline and performs three safety checks
before any query reaches the retriever:

1. PII Detection     — Blocks queries containing PAN, Aadhaar, phone, or email.
2. Advisory Detection — Blocks advisory/recommendation-seeking queries.
3. LLM Fallback      — For ambiguous queries, asks the LLM to classify them.

Each check returns a ClassificationResult so the caller can decide whether to
proceed with retrieval or return a refusal response.
"""

import os
import re
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class QueryType(Enum):
    """Possible classifications for an incoming query."""
    FACTUAL = "factual"
    ADVISORY = "advisory"
    PII_DETECTED = "pii_detected"
    AMBIGUOUS = "ambiguous"  # needs LLM fallback


@dataclass
class ClassificationResult:
    """Container for classification output returned to the pipeline."""
    query_type: QueryType
    is_allowed: bool
    refusal_message: Optional[str] = None
    detected_patterns: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Task 3.1 — Advisory keyword patterns (case-insensitive)
ADVISORY_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bshould\s+i\b", re.IGNORECASE),
    re.compile(r"\bwhich\s+(?:\w+\s+)*is\s+better\b", re.IGNORECASE),
    re.compile(r"\bwhich\s+(?:\w+\s+)*better\b", re.IGNORECASE),
    re.compile(r"\brecommend\b", re.IGNORECASE),
    re.compile(r"\bbest\s+fund\b", re.IGNORECASE),
    re.compile(r"\binvest\s+in\b", re.IGNORECASE),
    re.compile(r"\bcompare\b", re.IGNORECASE),
    re.compile(r"\badvice\b", re.IGNORECASE),
    re.compile(r"\bsuggestion\b", re.IGNORECASE),
    re.compile(r"\bsuggest\b", re.IGNORECASE),
    re.compile(r"\bbetter\s+option\b", re.IGNORECASE),
    re.compile(r"\bworth\s+investing\b", re.IGNORECASE),
    re.compile(r"\bgood\s+fund\b", re.IGNORECASE),
    re.compile(r"\bbad\s+fund\b", re.IGNORECASE),
    re.compile(r"\bshould\s+I\s+buy\b", re.IGNORECASE),
    re.compile(r"\bshould\s+I\s+sell\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+should\s+I\b", re.IGNORECASE),
]

# Task 3.2 — PII regex patterns
PII_PATTERNS: dict[str, re.Pattern] = {
    "PAN":    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "Aadhaar": re.compile(r"\b[0-9]{12}\b"),
    "Phone":  re.compile(r"\b[6-9][0-9]{9}\b"),                    # Indian mobile numbers
    "Email":  re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
}

# Task 3.4 — Refusal response templates
ADVISORY_REFUSAL = (
    "I'm designed to share only **factual information** about mutual fund schemes "
    "(e.g., expense ratio, NAV, exit load). I cannot provide personalised investment "
    "advice or fund comparisons.\n\n"
    "For investment guidance, please consult a SEBI-registered financial advisor or "
    "visit:\n"
    "- **AMFI**: https://www.amfiindia.com\n"
    "- **SEBI Investor Education**: https://investor.sebi.gov.in"
)

PII_REFUSAL = (
    "**Warning:** Your query appears to contain **personal or sensitive information** "
    "({pii_types}). For your privacy and security, I cannot process queries "
    "that include personal identifiers.\n\n"
    "Please remove any personal data and try again with a factual question "
    "about mutual fund schemes."
)


# ---------------------------------------------------------------------------
# Task 3.2 — PII Detection
# ---------------------------------------------------------------------------

def detect_pii(query: str) -> list[str]:
    """
    Scan the query for PII patterns.

    Returns:
        A list of PII type names found (e.g., ["PAN", "Email"]).
        Empty list means no PII detected.
    """
    detected: list[str] = []
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(query):
            detected.append(pii_type)
    return detected


# ---------------------------------------------------------------------------
# Task 3.1 — Advisory / Recommendation Detection
# ---------------------------------------------------------------------------

def detect_advisory(query: str) -> bool:
    """
    Check if the query contains advisory-seeking language.

    Returns:
        True if advisory intent is detected.
    """
    for pattern in ADVISORY_PATTERNS:
        if pattern.search(query):
            return True
    return False


# ---------------------------------------------------------------------------
# Task 3.3 — LLM-based Classification Fallback
# ---------------------------------------------------------------------------

def classify_with_llm(query: str) -> QueryType:
    """
    Use the Groq LLM as a fallback classifier for ambiguous queries.

    Sends a short system prompt asking the LLM to classify the query as
    either 'factual' or 'advisory'. Falls back to FACTUAL if the API is
    unavailable (fail-open for non-PII, non-advisory queries).

    Returns:
        QueryType.FACTUAL or QueryType.ADVISORY
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY not configured. Skipping LLM classification — defaulting to FACTUAL.")
        return QueryType.FACTUAL

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import SystemMessage, HumanMessage
        from rate_limiter import groq_limiter, estimate_tokens

        system_prompt = (
            "You are a query classifier for a mutual fund FAQ assistant. "
            "Classify the following user query as either 'factual' or 'advisory'.\n\n"
            "Rules:\n"
            "- 'factual' = the user is asking for objective data about a mutual fund "
            "(e.g., expense ratio, NAV, exit load, fund manager, minimum investment).\n"
            "- 'advisory' = the user is seeking a recommendation, comparison, or "
            "personalised investment advice.\n\n"
            "Respond with EXACTLY one word: factual or advisory."
        )

        # Estimate tokens and respect rate limits
        max_output_tokens = 10
        input_tokens = estimate_tokens(system_prompt + query)
        groq_limiter.wait_if_needed(estimated_tokens=input_tokens + max_output_tokens)

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=max_output_tokens,
            api_key=api_key,
        )

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ])

        answer = response.content.strip().lower()

        # Record actual usage
        actual_tokens = input_tokens + estimate_tokens(answer)
        groq_limiter.record_request(actual_tokens=actual_tokens)
        logger.info(f"LLM classification result: '{answer}' for query: '{query}'")

        if "advisory" in answer:
            return QueryType.ADVISORY
        return QueryType.FACTUAL

    except Exception as e:
        logger.error(f"LLM classification failed: {e}. Defaulting to FACTUAL.")
        return QueryType.FACTUAL


# ---------------------------------------------------------------------------
# Main Classification Pipeline
# ---------------------------------------------------------------------------

def classify_query(query: str, use_llm_fallback: bool = True) -> ClassificationResult:
    """
    Run the full classification pipeline on a user query.

    Order of checks:
        1. PII Detection   → block immediately
        2. Advisory Detection → block with refusal
        3. (Optional) LLM fallback for remaining queries

    Args:
        query: The raw user query string.
        use_llm_fallback: Whether to invoke the LLM for ambiguous queries.

    Returns:
        A ClassificationResult indicating the query type and whether it's allowed.
    """
    query = query.strip()
    if not query:
        return ClassificationResult(
            query_type=QueryType.FACTUAL,
            is_allowed=False,
            refusal_message="Please enter a valid question about mutual fund schemes.",
        )

    # --- Step 1: PII check (highest priority) ---
    pii_types = detect_pii(query)
    if pii_types:
        logger.info(f"PII detected ({', '.join(pii_types)}) in query: '{query[:50]}...'")
        return ClassificationResult(
            query_type=QueryType.PII_DETECTED,
            is_allowed=False,
            refusal_message=PII_REFUSAL.format(pii_types=", ".join(pii_types)),
            detected_patterns=pii_types,
        )

    # --- Step 2: Advisory keyword check ---
    if detect_advisory(query):
        logger.info(f"Advisory intent detected in query: '{query[:50]}...'")
        return ClassificationResult(
            query_type=QueryType.ADVISORY,
            is_allowed=False,
            refusal_message=ADVISORY_REFUSAL,
        )

    # --- Step 3: LLM fallback for borderline queries ---
    if use_llm_fallback:
        llm_result = classify_with_llm(query)
        if llm_result == QueryType.ADVISORY:
            logger.info(f"LLM classified query as advisory: '{query[:50]}...'")
            return ClassificationResult(
                query_type=QueryType.ADVISORY,
                is_allowed=False,
                refusal_message=ADVISORY_REFUSAL,
            )

    # --- Passed all checks → factual ---
    logger.info(f"Query classified as FACTUAL: '{query[:50]}...'")
    return ClassificationResult(
        query_type=QueryType.FACTUAL,
        is_allowed=True,
    )


# ---------------------------------------------------------------------------
# CLI Entry Point (for quick manual testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_queries = [
        # Factual
        "What is the expense ratio of HDFC Mid-Cap Opportunities Fund?",
        "What is the minimum SIP amount for HDFC Flexi Cap Fund?",
        # Advisory
        "Should I invest in HDFC Mid-Cap?",
        "Which fund is better — HDFC or ICICI?",
        "Recommend a good mutual fund for me",
        # PII
        "My PAN is ABCDE1234F, check my returns",
        "My Aadhaar is 123456789012, link my account",
        "Contact me at user@example.com",
        # Ambiguous
        "Tell me about HDFC Mid-Cap fund performance",
    ]

    print("=" * 70)
    print("QUERY CLASSIFIER — MANUAL TEST RUN")
    print("=" * 70)

    for q in test_queries:
        result = classify_query(q, use_llm_fallback=False)  # skip LLM for quick run
        status = "[PASS] ALLOWED" if result.is_allowed else "[FAIL] BLOCKED"
        print(f"\n[{status}] ({result.query_type.value})")
        print(f"  Query: {q}")
        if result.refusal_message:
            # Print first line of refusal only
            print(f"  Refusal: {result.refusal_message.split(chr(10))[0]}")
        if result.detected_patterns:
            print(f"  Detected: {result.detected_patterns}")
