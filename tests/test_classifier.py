"""
Phase 3 — Unit Tests for Query Classifier
==========================================

Tests cover three categories:
  1. Advisory queries       → must be BLOCKED
  2. PII-containing queries → must be BLOCKED
  3. Factual queries        → must be ALLOWED

All tests run with use_llm_fallback=False so they execute locally
without requiring a Groq API key.
"""

import sys
import os
import unittest

# Ensure `src/` is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from classifier import (
    classify_query,
    detect_pii,
    detect_advisory,
    QueryType,
    ClassificationResult,
)


class TestPIIDetection(unittest.TestCase):
    """Task 3.2 — PII regex filters."""

    def test_pan_detected(self):
        result = detect_pii("My PAN is ABCDE1234F")
        self.assertIn("PAN", result)

    def test_aadhaar_detected(self):
        result = detect_pii("My Aadhaar number is 123456789012")
        self.assertIn("Aadhaar", result)

    def test_phone_detected(self):
        result = detect_pii("Call me at 9876543210")
        self.assertIn("Phone", result)

    def test_email_detected(self):
        result = detect_pii("Email me at user@example.com")
        self.assertIn("Email", result)

    def test_multiple_pii(self):
        result = detect_pii("PAN: ABCDE1234F, email: a@b.com")
        self.assertIn("PAN", result)
        self.assertIn("Email", result)

    def test_no_pii_in_factual_query(self):
        result = detect_pii("What is the expense ratio of HDFC Mid-Cap?")
        self.assertEqual(result, [])

    def test_pan_like_but_invalid(self):
        # 'abcde1234f' in lowercase should NOT match PAN (requires uppercase)
        result = detect_pii("My code is abcde1234f")
        self.assertNotIn("PAN", result)


class TestAdvisoryDetection(unittest.TestCase):
    """Task 3.1 — Keyword-based advisory detection."""

    def test_should_i(self):
        self.assertTrue(detect_advisory("Should I invest in this fund?"))

    def test_which_is_better(self):
        self.assertTrue(detect_advisory("Which is better HDFC or ICICI?"))

    def test_recommend(self):
        self.assertTrue(detect_advisory("Recommend a good mutual fund"))

    def test_best_fund(self):
        self.assertTrue(detect_advisory("What is the best fund for long term?"))

    def test_invest_in(self):
        self.assertTrue(detect_advisory("Should I invest in HDFC Mid-Cap?"))

    def test_compare(self):
        self.assertTrue(detect_advisory("Compare HDFC and ICICI funds"))

    def test_suggest(self):
        self.assertTrue(detect_advisory("Suggest a mutual fund for me"))

    def test_advice(self):
        self.assertTrue(detect_advisory("Give me investment advice"))

    def test_factual_not_advisory(self):
        self.assertFalse(detect_advisory("What is the expense ratio of HDFC Mid-Cap?"))

    def test_factual_minimum_sip(self):
        self.assertFalse(detect_advisory("What is the minimum SIP amount?"))

    def test_factual_exit_load(self):
        self.assertFalse(detect_advisory("What is the exit load for HDFC Small Cap Fund?"))


class TestClassifyQuery(unittest.TestCase):
    """Full pipeline tests — classify_query()."""

    def _classify(self, query: str) -> ClassificationResult:
        """Helper — classify without LLM fallback for local testing."""
        return classify_query(query, use_llm_fallback=False)

    # --- Factual queries should be ALLOWED ---

    def test_factual_expense_ratio(self):
        result = self._classify("What is the expense ratio of HDFC Mid-Cap Opportunities Fund?")
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.FACTUAL)

    def test_factual_sip_amount(self):
        result = self._classify("What is the minimum SIP amount for HDFC Flexi Cap Fund?")
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.FACTUAL)

    def test_factual_lock_in(self):
        result = self._classify("What is the lock-in period for HDFC ELSS Tax Saver Fund?")
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.FACTUAL)

    def test_factual_fund_manager(self):
        result = self._classify("Who is the fund manager of HDFC Mid-Cap?")
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.FACTUAL)

    def test_factual_nav(self):
        result = self._classify("What is the current NAV of Nippon India Small Cap Fund?")
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.FACTUAL)

    # --- Advisory queries should be BLOCKED ---

    def test_advisory_should_i(self):
        result = self._classify("Should I invest in HDFC Mid-Cap?")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.ADVISORY)
        self.assertIsNotNone(result.refusal_message)

    def test_advisory_which_better(self):
        result = self._classify("Which fund is better?")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.ADVISORY)

    def test_advisory_recommend(self):
        result = self._classify("Recommend a mutual fund for me")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.ADVISORY)

    def test_advisory_compare(self):
        result = self._classify("Compare HDFC and ICICI mutual funds")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.ADVISORY)

    def test_advisory_best_fund(self):
        result = self._classify("Which is the best fund to invest in for 5 years?")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.ADVISORY)

    # --- PII queries should be BLOCKED ---

    def test_pii_pan(self):
        result = self._classify("My PAN is ABCDE1234F, check my returns")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.PII_DETECTED)
        self.assertIn("PAN", result.detected_patterns)

    def test_pii_aadhaar(self):
        result = self._classify("My Aadhaar is 123456789012, link my account")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.PII_DETECTED)
        self.assertIn("Aadhaar", result.detected_patterns)

    def test_pii_email(self):
        result = self._classify("Send details to user@example.com")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.PII_DETECTED)
        self.assertIn("Email", result.detected_patterns)

    def test_pii_phone(self):
        result = self._classify("Call me at 9876543210 for details")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.PII_DETECTED)
        self.assertIn("Phone", result.detected_patterns)

    # --- PII takes priority over advisory ---

    def test_pii_priority_over_advisory(self):
        """PII should be caught even if advisory keywords are also present."""
        result = self._classify("Should I invest? My PAN is ABCDE1234F")
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.query_type, QueryType.PII_DETECTED)

    # --- Edge cases ---

    def test_empty_query(self):
        result = self._classify("")
        self.assertFalse(result.is_allowed)

    def test_whitespace_only_query(self):
        result = self._classify("   ")
        self.assertFalse(result.is_allowed)

    # --- Refusal messages contain expected content ---

    def test_advisory_refusal_contains_amfi_link(self):
        result = self._classify("Should I invest in HDFC Mid-Cap?")
        self.assertIn("amfiindia.com", result.refusal_message)
        self.assertIn("sebi", result.refusal_message.lower())

    def test_pii_refusal_mentions_type(self):
        result = self._classify("My PAN is ABCDE1234F")
        self.assertIn("PAN", result.refusal_message)


if __name__ == "__main__":
    unittest.main()
