"""
Phase 4B — LLM Generator
=========================

Constructs the system prompt and user prompt from the retrieval context,
calls the Groq API via langchain-groq, and returns the raw LLM response.

Uses the 7-rule system prompt from architecture.md and the prompt template:
  Context → Source URLs → User Question
"""

import os
import sys
import logging
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Ensure project root is on the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import TEMPERATURE, MAX_TOKENS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LLM_MODEL = "llama-3.3-70b-versatile"

# Task 4B.1 — System Prompt (7 rules from architecture.md)
SYSTEM_PROMPT = """\
You are a facts-only mutual fund FAQ assistant. You answer questions about mutual fund schemes using ONLY the provided context.

RULES:
1. Answer in a maximum of 3 sentences.
2. Include exactly one source citation link from the context metadata.
3. End every response with: "Last updated from sources: <date>"
4. Do NOT provide investment advice, opinions, or recommendations.
5. Do NOT compare fund performance or calculate returns.
6. If the context does not contain the answer, say: "I don't have this information in my current sources."
7. For performance-related queries, respond only with a link to the official factsheet."""

# Task 4B.2 — User Prompt Template
USER_PROMPT_TEMPLATE = """\
Context:
{context}

Source URLs:
{source_urls}

User Question: {user_query}

Respond following the system rules strictly."""

NO_CONTEXT_RESPONSE = (
    "I don't have this information in my current sources."
)


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

@dataclass
class GenerationResult:
    """Container for the LLM generation output."""
    response: str                      # The raw LLM response text
    source_urls: list[str]             # Source URLs available for citation
    scraped_dates: list[str]           # Scrape dates for footer
    success: bool                      # Whether generation succeeded
    error_message: Optional[str] = None


# ---------------------------------------------------------------------------
# Core Generator
# ---------------------------------------------------------------------------

def generate(
    context: str,
    user_query: str,
    source_urls: list[str],
    scraped_dates: list[str],
) -> GenerationResult:
    """
    Build the prompt from context + query and call the Groq LLM.

    Args:
        context:       Assembled context string from the retriever.
        user_query:    The original user question.
        source_urls:   De-duplicated source URLs from retrieval metadata.
        scraped_dates: De-duplicated scrape dates from retrieval metadata.

    Returns:
        A GenerationResult with the raw LLM response or error info.
    """
    # If retriever returned no context, respond with the fallback
    if not context or not context.strip():
        logger.info("No context provided — returning fallback response.")
        return GenerationResult(
            response=NO_CONTEXT_RESPONSE,
            source_urls=source_urls,
            scraped_dates=scraped_dates,
            success=True,
        )

    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        error_msg = "GROQ_API_KEY is not configured. Please set it in your .env file."
        logger.error(error_msg)
        return GenerationResult(
            response="",
            source_urls=source_urls,
            scraped_dates=scraped_dates,
            success=False,
            error_message=error_msg,
        )

    # Build the user prompt
    source_urls_str = "\n".join(f"- {url}" for url in source_urls) if source_urls else "- (none)"
    user_prompt = USER_PROMPT_TEMPLATE.format(
        context=context,
        source_urls=source_urls_str,
        user_query=user_query,
    )

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import SystemMessage, HumanMessage
        from rate_limiter import groq_limiter, estimate_tokens

        # Estimate total tokens (input + max output)
        input_tokens = estimate_tokens(SYSTEM_PROMPT + user_prompt)
        estimated_total = input_tokens + MAX_TOKENS

        # Wait if rate limits would be exceeded
        groq_limiter.wait_if_needed(estimated_tokens=estimated_total)

        llm = ChatGroq(
            model=LLM_MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            api_key=api_key,
        )

        logger.info(f"Calling Groq LLM ({LLM_MODEL}) for query: '{user_query[:60]}...'")

        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])

        llm_text = response.content.strip()

        # Record actual token usage (estimate from response length)
        actual_tokens = input_tokens + estimate_tokens(llm_text)
        groq_limiter.record_request(actual_tokens=actual_tokens)
        logger.info(f"LLM response received ({len(llm_text)} chars, ~{actual_tokens} tokens)")

        return GenerationResult(
            response=llm_text,
            source_urls=source_urls,
            scraped_dates=scraped_dates,
            success=True,
        )

    except Exception as e:
        error_msg = f"LLM generation failed: {e}"
        logger.error(error_msg)

        # Provide a user-friendly fallback
        return GenerationResult(
            response="",
            source_urls=source_urls,
            scraped_dates=scraped_dates,
            success=False,
            error_message=error_msg,
        )


# ---------------------------------------------------------------------------
# CLI Entry Point (for quick manual testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    # Import retriever for end-to-end test
    from retriever import retrieve

    test_queries = [
        "What is the expense ratio of HDFC Mid-Cap Opportunities Fund?",
        "What is the minimum SIP amount?",
    ]

    print("=" * 70)
    print("GENERATOR — MANUAL TEST RUN")
    print("=" * 70)

    for q in test_queries:
        print(f"\nQuery: {q}")
        retrieval = retrieve(q, top_k=3)

        result = generate(
            context=retrieval.context,
            user_query=q,
            source_urls=retrieval.source_urls,
            scraped_dates=retrieval.scraped_dates,
        )

        if result.success:
            print(f"  Response: {result.response}")
        else:
            print(f"  Error: {result.error_message}")
