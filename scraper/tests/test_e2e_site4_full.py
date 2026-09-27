import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timezone
import sys
import os
from sqlalchemy import create_engine
from pathlib import Path

# Setup path
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(project_root)
sys.path.append(str(Path(project_root) / "representative-fare-engine"))
sys.path.append(str(Path(project_root) / "cleaning-normalization"))

from scraper.sources.site4_adapter import Site4Adapter
from scraper.db.models import FareObservation, save_fare_quote
from scraper.db.database import Base as DbBase
import importlib.util

# Unambiguous loads
# 1. Representative Fare Service
fare_spec = importlib.util.spec_from_file_location("fare_service", os.path.join(project_root, "representative-fare-engine", "service.py"))
fare_service = importlib.util.module_from_spec(fare_spec)
fare_spec.loader.exec_module(fare_service)
run_agg = fare_service.run_representative_fare_aggregation

# 2. Cleaning Service
clean_spec = importlib.util.spec_from_file_location("clean_service", os.path.join(project_root, "cleaning-normalization", "service.py"))
clean_service = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(clean_service)

TEST_DATABASE_URL = os.getenv("DATABASE_URL")

SAMPLE_XML_1 = '''<?xml version="1.0" encoding="UTF-8"?>
<flightResults>
  <flight>
    <flightNumber>AW401</flightNumber>
    <cabin>economy</cabin>
    <baseFare>4200</baseFare>
    <taxes>650</taxes>
    <otherCharges>99</otherCharges>
    <totalFare>4949</totalFare>
    <currency>INR</currency>
  </flight>
</flightResults>'''

SAMPLE_XML_2 = '''<?xml version="1.0" encoding="UTF-8"?>
<flightResults>
  <flight>
    <flightNumber>AW402</flightNumber>
    <cabin>economy</cabin>
    <baseFare>4500</baseFare>
    <taxes>800</taxes>
    <otherCharges>100</otherCharges>
    <totalFare>5400</totalFare>
    <currency>INR</currency>
  </flight>
</flightResults>'''

class TestSite4FullIntegration(unittest.TestCase):
    def setUp(self):
        if not TEST_DATABASE_URL:
            self.skipTest("DATABASE_URL not set")

        self.engine = create_engine(TEST_DATABASE_URL)
        DbBase.metadata.create_all(self.engine)
        from sqlalchemy.orm import sessionmaker
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Clean state
        import psycopg2
        if TEST_DATABASE_URL.startswith("postgresql"):
            conn = psycopg2.connect(TEST_DATABASE_URL)
            cur = conn.cursor()
            cur.execute("TRUNCATE TABLE fare_observations, routes, RepresentativeFares RESTART IDENTITY CASCADE;")
            # Seed route for site4 (needs to match what cleaning logic resolves)
            cur.execute("INSERT INTO Routes (origin, destination, weight) VALUES ('DEL', 'BOM', 0.25) ON CONFLICT (origin, destination) DO UPDATE SET weight = 0.25;")
            conn.commit()
            conn.close()

        self.adapter = Site4Adapter("http://localhost:8765", "TEST_API_KEY_SITE4_789")
        self.travel_date = date(2026, 10, 26)

    def tearDown(self):
        self.session.close()

    @patch('requests.get')
    def test_end_to_end_pipeline(self, mock_get):
        # 1. Collection
        def side_effect(url, headers=None, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 200
            if "AW401" in mock_response.text: # Logic based on call order
                mock_response.text = SAMPLE_XML_2
            else:
                mock_response.text = SAMPLE_XML_1
            # Actually, need better mock for side_effect
            return mock_response

        # Simpler approach: call get twice
        mock_get.side_effect = [
            MagicMock(text=SAMPLE_XML_1, status_code=200),
            MagicMock(text=SAMPLE_XML_2, status_code=200)
        ]

        with patch('scraper.sources.site4_adapter.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 9, 26, tzinfo=timezone.utc)
            quote1 = self.adapter.collect("DEL", "BOM", self.travel_date, 30)
            quote2 = self.adapter.collect("DEL", "BOM", self.travel_date, 30)
            quote2.flight_number = "AW402" # differentiate
            quote2.source = "site4-bis" # Differentiate for unique constraint

        # Normalization
        cleaned1 = clean_service.process_single_record(quote1.model_dump())
        cleaned2 = clean_service.process_single_record(quote2.model_dump())

        quote1.total_fare = cleaned1['total_fare']
        quote2.total_fare = cleaned2['total_fare']

        # Staging
        save_fare_quote(self.session, quote1)
        save_fare_quote(self.session, quote2)

        # 2. Aggregation
        run_agg()

        # 3. Validation
        import psycopg2
        conn = psycopg2.connect(TEST_DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT median_fare FROM RepresentativeFares WHERE route_id=1")
        res = cur.fetchone()
        self.assertIsNotNone(res)
        # Median of 4949 and 5400 is 5174.5
        self.assertEqual(float(res[0]), 5174.5)
        conn.close()
        print("PASS: Site4 End-to-End PostgreSQL Validation")

if __name__ == '__main__':
    unittest.main()
