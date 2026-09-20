"""
Automated Test Suite for Japanese Ski Resort Accommodation Scraper & API
Verifies exact dates (Dec 29, 2026 - Jan 2, 2027) for 5 adult guests
"""

import unittest
import os
import csv
from scraper_engine import SkiResortScraper, get_stay_dates
from fastapi.testclient import TestClient
from server import app

class TestSkiScraper(unittest.TestCase):
    def setUp(self):
        self.checkin = "2026-12-29"
        self.checkout = "2027-01-02"
        self.adults = 5
        self.rooms = 1
        self.scraper = SkiResortScraper(
            checkin=self.checkin,
            checkout=self.checkout,
            adults=self.adults,
            rooms=self.rooms
        )

    def test_stay_dates_calculation(self):
        """Verify the 4-night stay date array generation."""
        dates = get_stay_dates(self.checkin, self.checkout)
        expected = ["2026-12-29", "2026-12-30", "2026-12-31", "2027-01-01"]
        self.assertEqual(dates, expected, f"Dates calculated must match the 4 stay nights: {expected}")
        self.assertEqual(len(dates), 4)

    def test_nozawa_scraper_execution(self):
        """Verify Nozawa Onsen tourism bureau scraper returns valid lodges."""
        lodges = self.scraper.scrape_nozawa_onsen()
        self.assertGreaterEqual(len(lodges), 15, "Should discover at least 15 Nozawa lodges")
        
        # Check required fields
        sample = lodges[0]
        for field in ["id", "resort", "name", "status", "status_code", "direct_link"]:
            self.assertIn(field, sample)
            self.assertTrue(sample[field], f"Field {field} should not be empty")

        # Verify Nozawa Tourism Concierge Desk exists
        concierge = next((l for l in lodges if l["id"] == "nozawa_concierge"), None)
        self.assertIsNotNone(concierge, "Nozawa Tourism Bureau Concierge service should be included")
        self.assertEqual(concierge["status_code"], "INQUIRY")

    def test_hakuba_scraper_and_unlock_rule(self):
        """Verify Hakuba Valley scraper and detection of Hotel Goryukan 5-night/Oct 1 unlock rule."""
        lodges = self.scraper.scrape_hakuba_valley()
        self.assertGreaterEqual(len(lodges), 15, "Should discover at least 15 Hakuba lodges")
        
        # Find Hotel Goryukan (CID 1847)
        goryukan = next((l for l in lodges if l["cid"] == "1847"), None)
        self.assertIsNotNone(goryukan, "Hotel Goryukan should be present in Hakuba results")
        self.assertEqual(goryukan["status_code"], "UNLOCKING_OCT_1")
        self.assertIn("October 1", goryukan["notes"], "Notes must mention October 1 unlock")

    def test_csv_export(self):
        """Verify that export_to_csv creates a valid, readable CSV file."""
        test_csv_path = "test_output.csv"
        lodges = self.scraper.run_all()
        self.scraper.export_to_csv(lodges, test_csv_path)

        self.assertTrue(os.path.exists(test_csv_path), "CSV output file must exist")
        with open(test_csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertGreaterEqual(len(rows), 40, "CSV must contain at least 40 lodge records")
            self.assertIn("resort", rows[0])
            self.assertIn("name", rows[0])
            self.assertIn("direct_link", rows[0])

        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)

class TestServerAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_lodges_endpoint(self):
        """Verify GET /api/lodges endpoint."""
        res = self.client.get("/api/lodges")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["total"], 40)
        self.assertEqual(data["checkin"], "2026-12-29")
        self.assertEqual(data["checkout"], "2027-01-02")
        self.assertEqual(data["adults"], 5)

    def test_get_lodges_filtering(self):
        """Verify resort filtering on /api/lodges."""
        res = self.client.get("/api/lodges?resort=Nozawa")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for lodge in data["data"]:
            self.assertEqual(lodge["resort"], "Nozawa Onsen")

    def test_get_stats_endpoint(self):
        """Verify GET /api/stats endpoint."""
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.json()
        self.assertIn("total_monitored", stats)
        self.assertIn("available_now", stats)
        self.assertIn("unlocking_oct_1", stats)
        self.assertGreaterEqual(stats["total_monitored"], 40)

    def test_export_csv_endpoint(self):
        """Verify GET /api/export endpoint returns CSV file."""
        res = self.client.get("/api/export")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "text/csv; charset=utf-8")
        self.assertIn("resort,name", res.text)

if __name__ == "__main__":
    unittest.main()
