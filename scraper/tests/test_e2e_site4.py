import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys
import os

# Setup path to import scraper modules and cleaning-normalization
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(project_root)
sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(project_root) / "cleaning-normalization"))

from scraper.sources.site4_adapter import Site4Adapter
from scraper.db.database import Base
from scraper.db.models import save_fare_quote, FareObservation
from service import process_single_record
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

SAMPLE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<flightResults>
  <flight>
    <flightNumber>AW401</flightNumber>
    <cabin>economy</cabin>
    <baseFare>4200</baseFare>
    <taxes>650</taxes>
    <otherCharges>99</otherCharges>
    <totalFare>4949</totalFare>
    <currency>INR</currency>
    <fareFamily>Flexi</fareFamily>
    <stops>0</stops>
  </flight>
</flightResults>'''


class TestSite4E2EPipeline(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(TEST_DATABASE_URL)
        from scraper.db.models import Airline, Route, FareObservation, JobAudit
        from scraper.db.database import Base as DbBase
        DbBase.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.base_url = "http://localhost:8765"
        self.adapter = Site4Adapter(self.base_url, "TEST_API_KEY_SITE4_789")
        self.travel_date = date(2026, 10, 26)
        self.advance_days = 30

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    @patch('requests.get')
    def test_e2e_pipeline_flow(self, mock_get):
        # Mock XML API response
        mock_response = MagicMock()
        mock_response.text = SAMPLE_XML
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # 1. Collect
        with patch('scraper.sources.site4_adapter.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 9, 26, tzinfo=timezone.utc)
            quote = self.adapter.collect("DEL", "BOM", self.travel_date, self.advance_days)

        self.assertEqual(quote.source, "site4")
        self.assertEqual(quote.airline, "AirWings")
        self.assertEqual(quote.total_fare, Decimal("4949"))
        print("PASS: Site4 Collection")

        # 2. Normalize
        cleaned_data = process_single_record(quote.model_dump())
        quote.origin = cleaned_data['origin']
        quote.destination = cleaned_data['destination']
        quote.airline = cleaned_data['airline']
        quote.total_fare = Decimal(str(cleaned_data['total_fare']))
        print("PASS: Site4 Normalization")

        # 3. Insert into staging (fare_observations)
        inserted = save_fare_quote(self.session, quote)
        self.assertTrue(inserted)

        # 4. Verify in fare_observations
        saved_quote = self.session.query(FareObservation).filter_by(source="site4").first()
        self.assertIsNotNone(saved_quote)
        self.assertEqual(saved_quote.total_fare, Decimal("4949.00"))
        self.assertEqual(saved_quote.airline, "AirWings")
        print("PASS: Site4 Staging")

        print("\nE2E Pipeline Test Passed: Site4 quote collected, cleaned, and saved to staging.")


if __name__ == '__main__':
    unittest.main()
