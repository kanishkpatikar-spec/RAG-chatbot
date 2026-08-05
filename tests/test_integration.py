import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure `src/` is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# pyrefly: ignore [missing-import]
from main import app

class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_6_1_factual_expense_ratio(self):
        """6.1 Factual query: What is the expense ratio of HDFC Mid-Cap Opportunities Fund?"""
        response = self.client.post("/api/chat", json={"query": "What is the expense ratio of HDFC Mid-Cap Opportunities Fund?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        text = data["response"].lower()
        self.assertIn("expense ratio", text)
        self.assertIn("last updated from sources", text)
        self.assertIn("http", text)

    def test_6_2_factual_sip_axis(self):
        """6.2 Factual query: What is the minimum SIP amount for Axis Small Cap Fund?"""
        response = self.client.post("/api/chat", json={"query": "What is the minimum SIP amount for Axis Small Cap Fund?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        text = data["response"].lower()
        self.assertTrue("100" in text or "sip" in text or "amount" in text)
        self.assertIn("last updated from sources", text)
        self.assertIn("http", text)

    def test_6_3_factual_manager_nippon(self):
        """6.3 Factual query: Who is the fund manager for Nippon India Small Cap?"""
        response = self.client.post("/api/chat", json={"query": "Who is the fund manager for Nippon India Small Cap?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        text = data["response"].lower()
        self.assertTrue("manager" in text or "samir" in text or "rachart" in text or "kinjal" in text or "tejas" in text or "akshay" in text or "nippon" in text)
        self.assertIn("last updated from sources", text)
        self.assertIn("http", text)

    def test_6_4_advisory(self):
        """6.4 Advisory query: Should I invest in HDFC Mid-Cap?"""
        response = self.client.post("/api/chat", json={"query": "Should I invest in HDFC Mid-Cap?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        text = data["response"].lower()
        self.assertTrue("provide personalized investment advice" in text or "can only provide factual" in text or "amfi" in text)

    def test_6_5_comparison(self):
        """6.5 Comparison query: Which fund is better?"""
        response = self.client.post("/api/chat", json={"query": "Which fund is better?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        text = data["response"].lower()
        self.assertTrue("provide personalized investment advice" in text or "can only provide factual" in text or "amfi" in text)

    def test_6_6_pii(self):
        """6.6 PII query: My PAN is ABCDE1234F, check my returns"""
        response = self.client.post("/api/chat", json={"query": "My PAN is ABCDE1234F, check my returns"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        text = data["response"].lower()
        self.assertTrue("pan" in text or "privacy" in text or "pii" in text)

    def test_6_7_out_of_scope(self):
        """6.7 Out-of-scope query: Tell me about SBI mutual funds"""
        response = self.client.post("/api/chat", json={"query": "Tell me about SBI mutual funds"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        text = data["response"].lower()
        self.assertTrue("don't have" in text or "cannot find" in text or "sources" in text)

    def test_6_8_performance(self):
        """6.8 Performance query: What are the returns of HDFC Flexi Cap?"""
        response = self.client.post("/api/chat", json={"query": "What are the returns of HDFC Flexi Cap?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        text = data["response"].lower()
        # Should link to factsheet or refuse to provide exact past returns
        self.assertTrue("return" in text or "factsheet" in text or "http" in text or "amfi" in text)

if __name__ == "__main__":
    unittest.main()
