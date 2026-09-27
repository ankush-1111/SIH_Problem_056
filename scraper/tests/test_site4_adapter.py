import os
import sys
from pathlib import Path

# Add the parent directory of 'scraper' to sys.path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch
from scraper.sources.site4_adapter import Site4Adapter
from scraper.models.fare_quote import FareQuote

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
  <flight>
    <flightNumber>AW402</flightNumber>
    <cabin>economy</cabin>
    <baseFare>5100</baseFare>
    <taxes>800</taxes>
    <otherCharges>100</otherCharges>
    <totalFare>6000</totalFare>
    <currency>INR</currency>
    <fareFamily>Value</fareFamily>
    <stops>1</stops>
  </flight>
</flightResults>'''


class TestSite4Adapter(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8765"
        self.adapter = Site4Adapter(self.base_url, "TEST_API_KEY_SITE4_789")
        self.travel_date = date(2026, 10, 26)
        self.advance_days = 30

    @patch('requests.get')
    def test_collect_picks_cheapest(self, mock_get):
        """Should return the flight with the lowest total_fare."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_XML
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with patch('scraper.sources.site4_adapter.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 9, 26, tzinfo=timezone.utc)
            quote = self.adapter.collect("DEL", "BOM", self.travel_date, self.advance_days)

        self.assertEqual(quote.source, "site4")
        self.assertEqual(quote.airline, "AirWings")
        self.assertEqual(quote.flight_number, "AW401")
        self.assertEqual(quote.total_fare, Decimal("4949"))
        self.assertEqual(quote.base_fare, Decimal("4200"))
        self.assertEqual(quote.taxes, Decimal("650"))
        self.assertEqual(quote.other_charges, Decimal("99"))
        self.assertEqual(quote.fare_family, "Flexi")
        self.assertEqual(quote.stops, 0)
        print("PASS: Site4Adapter picks cheapest flight")

    @patch('requests.get')
    def test_collect_empty_response(self, mock_get):
        """Should raise Exception when no flights found."""
        mock_response = MagicMock()
        mock_response.text = '<?xml version="1.0"?><flightResults></flightResults>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with patch('scraper.sources.site4_adapter.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 9, 26, tzinfo=timezone.utc)
            with self.assertRaises(Exception):
                self.adapter.collect("DEL", "BOM", self.travel_date, self.advance_days)

        print("PASS: Site4Adapter raises on empty response")

    @patch('requests.get')
    def test_collect_sends_correct_headers(self, mock_get):
        """Should send API key and Accept headers."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_XML
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with patch('scraper.sources.site4_adapter.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 9, 26, tzinfo=timezone.utc)
            self.adapter.collect("DEL", "BOM", self.travel_date, self.advance_days)

        mock_get.assert_called_once_with(
            "http://localhost:8765/site4-api/flights",
            headers={"X-API-Key": "TEST_API_KEY_SITE4_789", "Accept": "application/xml"},
        )
        print("PASS: Site4Adapter sends correct headers")


if __name__ == '__main__':
    unittest.main()
