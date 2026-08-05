"""
Phase 8 — Scheduler Orchestration Script
==========================================

Sequentially runs the data ingestion pipeline:
  1. scraper.py  — Fetch raw HTML from Groww URLs
  2. parser.py   — Clean HTML and produce structured text + metadata
  3. embedder.py — Chunk, embed, and store in ChromaDB

Designed to be invoked by the GitHub Actions cron workflow,
but can also be run manually:
    python src/scheduler.py
"""

import os
import sys
import time
import logging
from datetime import datetime

# Ensure project root is on the path so config/ and sibling modules resolve
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [scheduler] %(message)s",
)
logger = logging.getLogger(__name__)


def run_step(step_name: str, step_fn):
    """Run a pipeline step, log timing, and return success status."""
    logger.info(f"▶ Starting step: {step_name}")
    start = time.time()
    try:
        step_fn()
        elapsed = time.time() - start
        logger.info(f"✓ Completed step: {step_name} ({elapsed:.1f}s)")
        return True
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"✗ Failed step: {step_name} after {elapsed:.1f}s — {e}", exc_info=True)
        return False


def main():
    logger.info("=" * 60)
    logger.info(f"Scheduler run started at {datetime.utcnow().isoformat()}Z")
    logger.info("=" * 60)

    # Lazy imports so that any import-time errors are caught per-step
    from scraper import main as scrape
    from parser import main as parse
    from embedder import main as embed

    steps = [
        ("1/3 — Scraping (scraper.py)", scrape),
        ("2/3 — Parsing  (parser.py)",  parse),
        ("3/3 — Embedding (embedder.py)", embed),
    ]

    results = {}
    for name, fn in steps:
        ok = run_step(name, fn)
        results[name] = "SUCCESS" if ok else "FAILED"
        if not ok:
            logger.warning(f"Step '{name}' failed — subsequent steps may also fail.")

    # Summary
    logger.info("=" * 60)
    logger.info("Pipeline summary:")
    all_ok = True
    for name, status in results.items():
        logger.info(f"  {status}  {name}")
        if status == "FAILED":
            all_ok = False
    logger.info("=" * 60)

    if not all_ok:
        logger.error("One or more steps failed. Check logs above.")
        sys.exit(1)
    else:
        logger.info("All steps completed successfully.")


if __name__ == "__main__":
    main()
