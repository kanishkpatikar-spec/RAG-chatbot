"""
Groq API Rate Limiter
=====================

Thread-safe, sliding-window rate limiter shared by all modules that call
the Groq API (generator.py, classifier.py).

Tracks four limits (from Groq's llama-3.3-70b-versatile tier):
  - Requests per minute  (30)
  - Requests per day     (1,000)
  - Tokens per minute    (12,000)
  - Tokens per day       (100,000)

Usage:
    from rate_limiter import groq_limiter

    groq_limiter.wait_if_needed(estimated_tokens=500)   # blocks until safe
    response = llm.invoke(...)
    groq_limiter.record_request(actual_tokens=250)       # log what was used
"""

import os
import sys
import time
import threading
import logging
from collections import deque

# Ensure project root is on the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    GROQ_REQUESTS_PER_MINUTE,
    GROQ_REQUESTS_PER_DAY,
    GROQ_TOKENS_PER_MINUTE,
    GROQ_TOKENS_PER_DAY,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Token Estimation
# ---------------------------------------------------------------------------

# Rough estimate: 1 token ≈ 4 characters (for English text)
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate the token count for a string (rough heuristic)."""
    return max(1, len(text) // CHARS_PER_TOKEN)


# ---------------------------------------------------------------------------
# Sliding Window Rate Limiter
# ---------------------------------------------------------------------------

class GroqRateLimiter:
    """
    Thread-safe sliding-window rate limiter for Groq API calls.

    Maintains deques of (timestamp, token_count) entries and blocks callers
    when any limit would be exceeded.
    """

    def __init__(
        self,
        requests_per_minute: int = GROQ_REQUESTS_PER_MINUTE,
        requests_per_day: int = GROQ_REQUESTS_PER_DAY,
        tokens_per_minute: int = GROQ_TOKENS_PER_MINUTE,
        tokens_per_day: int = GROQ_TOKENS_PER_DAY,
    ):
        self.rpm = requests_per_minute
        self.rpd = requests_per_day
        self.tpm = tokens_per_minute
        self.tpd = tokens_per_day

        # Deques of (timestamp, token_count)
        self._minute_requests: deque = deque()   # entries within the last 60s
        self._day_requests: deque = deque()       # entries within the last 24h

        self._lock = threading.Lock()

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _prune(self, now: float) -> None:
        """Remove expired entries from both windows."""
        minute_ago = now - 60
        day_ago = now - 86400

        while self._minute_requests and self._minute_requests[0][0] < minute_ago:
            self._minute_requests.popleft()

        while self._day_requests and self._day_requests[0][0] < day_ago:
            self._day_requests.popleft()

    def _minute_request_count(self) -> int:
        return len(self._minute_requests)

    def _day_request_count(self) -> int:
        return len(self._day_requests)

    def _minute_token_count(self) -> int:
        return sum(t for _, t in self._minute_requests)

    def _day_token_count(self) -> int:
        return sum(t for _, t in self._day_requests)

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def wait_if_needed(self, estimated_tokens: int = 0) -> None:
        """
        Block until all rate limits allow the next request.

        Call this BEFORE making an API request. Pass `estimated_tokens`
        (input + max_output) to also respect token-per-minute limits.
        """
        while True:
            with self._lock:
                now = time.time()
                self._prune(now)

                # --- Check requests-per-minute ---
                if self._minute_request_count() >= self.rpm:
                    oldest = self._minute_requests[0][0]
                    wait = 60 - (now - oldest) + 0.5  # +0.5s safety margin
                    logger.warning(
                        f"Rate limit: {self.rpm} requests/min reached. "
                        f"Waiting {wait:.1f}s..."
                    )
                else:
                    wait = 0

                # --- Check tokens-per-minute ---
                if wait == 0 and estimated_tokens > 0:
                    current_tpm = self._minute_token_count()
                    if current_tpm + estimated_tokens > self.tpm:
                        if self._minute_requests:
                            oldest = self._minute_requests[0][0]
                            wait = 60 - (now - oldest) + 0.5
                        else:
                            wait = 1
                        logger.warning(
                            f"Rate limit: ~{current_tpm}+{estimated_tokens} tokens/min "
                            f"would exceed {self.tpm}. Waiting {wait:.1f}s..."
                        )

                # --- Check requests-per-day ---
                if wait == 0 and self._day_request_count() >= self.rpd:
                    oldest = self._day_requests[0][0]
                    wait = 86400 - (now - oldest) + 1
                    logger.error(
                        f"Rate limit: {self.rpd} requests/day reached. "
                        f"Next window in {wait/60:.0f} minutes."
                    )

                # --- Check tokens-per-day ---
                if wait == 0 and estimated_tokens > 0:
                    current_tpd = self._day_token_count()
                    if current_tpd + estimated_tokens > self.tpd:
                        if self._day_requests:
                            oldest = self._day_requests[0][0]
                            wait = 86400 - (now - oldest) + 1
                        else:
                            wait = 1
                        logger.error(
                            f"Rate limit: ~{current_tpd}+{estimated_tokens} tokens/day "
                            f"would exceed {self.tpd}. Next window in {wait/60:.0f} minutes."
                        )

                if wait <= 0:
                    return  # All clear — proceed

            # Release lock while sleeping
            time.sleep(min(wait, 60))  # cap single sleep to 60s, then re-check

    def record_request(self, actual_tokens: int = 0) -> None:
        """
        Record that a request was made. Call this AFTER a successful API call.

        Args:
            actual_tokens: Total tokens used (input + output). If unknown,
                           pass 0 and only request-count limits will be tracked.
        """
        with self._lock:
            now = time.time()
            entry = (now, actual_tokens)
            self._minute_requests.append(entry)
            self._day_requests.append(entry)
            self._prune(now)

    def get_usage(self) -> dict:
        """Return current usage stats for monitoring/logging."""
        with self._lock:
            self._prune(time.time())
            return {
                "requests_this_minute": self._minute_request_count(),
                "requests_this_day": self._day_request_count(),
                "tokens_this_minute": self._minute_token_count(),
                "tokens_this_day": self._day_token_count(),
                "limits": {
                    "rpm": self.rpm,
                    "rpd": self.rpd,
                    "tpm": self.tpm,
                    "tpd": self.tpd,
                },
            }


# ---------------------------------------------------------------------------
# Singleton instance — import this from other modules
# ---------------------------------------------------------------------------

groq_limiter = GroqRateLimiter()
