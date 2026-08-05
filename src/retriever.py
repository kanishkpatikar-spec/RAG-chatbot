"""
Phase 4A — Retriever
====================

Connects to the persistent ChromaDB vectorstore, embeds the user query using
the same BAAI/bge-small-en-v1.5 model, performs semantic search, and assembles
a structured context string for the LLM generator.

Vectorstore profile (from analysis):
  - 38 chunks across 5 schemes, 384-dim embeddings
  - Metadata: scheme_name, source_url, category, scraped_date, chunk_index
  - Relevance scores: scheme-specific queries 0.55–0.71, generic ~0.47–0.49
"""

import os
import sys
import logging
from dataclasses import dataclass, field

# Ensure project root is on the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import TOP_K

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "mutual_fund_faq"
MIN_RELEVANCE_SCORE = 0.35  # Chunks below this score are discarded


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

@dataclass
class RetrievalResult:
    """Container for retrieval output passed to the generator."""
    context: str                           # Assembled context string for the LLM
    source_urls: list[str]                 # De-duplicated source URLs from metadata
    scraped_dates: list[str]               # De-duplicated scrape dates
    num_chunks_retrieved: int              # How many chunks passed the threshold
    scheme_names: list[str] = field(default_factory=list)  # Schemes represented


# ---------------------------------------------------------------------------
# Embedding & Vectorstore Loader
# ---------------------------------------------------------------------------

_embedding_model = None
_vectorstore = None


def _get_embedding_model():
    """Lazy-load the embedding model (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
        _embedding_model = HuggingFaceBgeEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_model


def _get_vectorstore():
    """Lazy-load the persistent ChromaDB vectorstore (singleton)."""
    global _vectorstore
    if _vectorstore is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        persist_directory = os.path.join(base_dir, "vectorstore")
        logger.info(f"Connecting to ChromaDB at: {persist_directory}")
        _vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=_get_embedding_model(),
            collection_name=COLLECTION_NAME,
        )
    return _vectorstore


# ---------------------------------------------------------------------------
# Core Retrieval
# ---------------------------------------------------------------------------

def retrieve(query: str, top_k: int = None) -> RetrievalResult:
    """
    Embed the query, search ChromaDB, filter by relevance score, and assemble
    a structured context string.

    Args:
        query:  The user's factual question.
        top_k:  Number of chunks to retrieve (defaults to config.TOP_K).

    Returns:
        A RetrievalResult with assembled context and metadata.
    """
    if top_k is None:
        top_k = TOP_K

    vectorstore = _get_vectorstore()

    # Semantic search with relevance scores
    raw_results = vectorstore.similarity_search_with_relevance_scores(query, k=top_k)

    # Filter by minimum relevance score
    filtered = [
        (doc, score) for doc, score in raw_results
        if score >= MIN_RELEVANCE_SCORE
    ]

    if not filtered:
        logger.warning(f"No chunks above threshold ({MIN_RELEVANCE_SCORE}) for query: '{query[:60]}'")
        return RetrievalResult(
            context="",
            source_urls=[],
            scraped_dates=[],
            num_chunks_retrieved=0,
        )

    logger.info(
        f"Retrieved {len(filtered)}/{len(raw_results)} chunks above threshold "
        f"(scores: {', '.join(f'{s:.3f}' for _, s in filtered)})"
    )

    # Assemble context — numbered chunks with scheme attribution
    context_parts: list[str] = []
    source_urls_seen: dict[str, None] = {}   # ordered set
    scraped_dates_seen: dict[str, None] = {}
    scheme_names_seen: dict[str, None] = {}

    for i, (doc, score) in enumerate(filtered, start=1):
        meta = doc.metadata
        scheme = meta.get("scheme_name", "Unknown Scheme")
        source_url = meta.get("source_url", "")
        scraped_date = meta.get("scraped_date", "")

        context_parts.append(
            f"[Chunk {i} — {scheme} (relevance: {score:.2f})]\n"
            f"{doc.page_content}"
        )

        if source_url:
            source_urls_seen[source_url] = None
        if scraped_date:
            scraped_dates_seen[scraped_date] = None
        scheme_names_seen[scheme] = None

    context = "\n\n---\n\n".join(context_parts)

    return RetrievalResult(
        context=context,
        source_urls=list(source_urls_seen.keys()),
        scraped_dates=list(scraped_dates_seen.keys()),
        num_chunks_retrieved=len(filtered),
        scheme_names=list(scheme_names_seen.keys()),
    )


# ---------------------------------------------------------------------------
# CLI Entry Point (for quick manual testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys as _sys
    _sys.stdout.reconfigure(encoding="utf-8")

    test_queries = [
        "What is the expense ratio of HDFC Mid-Cap Opportunities Fund?",
        "What is the minimum SIP amount for HDFC Flexi Cap Fund?",
        "exit load HDFC Small Cap",
        "fund manager Nippon India Small Cap",
        "Tell me about SBI mutual funds",  # out-of-scope
    ]

    print("=" * 70)
    print("RETRIEVER — MANUAL TEST RUN")
    print("=" * 70)

    for q in test_queries:
        print(f"\nQuery: {q}")
        result = retrieve(q, top_k=3)
        print(f"  Chunks retrieved: {result.num_chunks_retrieved}")
        print(f"  Schemes: {result.scheme_names}")
        print(f"  Source URLs: {result.source_urls}")
        if result.context:
            preview = result.context[:200].replace("\n", " ")
            print(f"  Context preview: {preview}...")
        else:
            print("  Context: (empty — no relevant chunks)")
