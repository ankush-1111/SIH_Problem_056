import requests
from datetime import datetime, date, timezone
from decimal import Decimal
import xml.etree.ElementTree as ET

from scraper.sources.base import SourceAdapter
from scraper.models.fare_quote import FareQuote


class Site4Adapter(SourceAdapter):
    """XML API adapter for AirWings fare data.

    Unlike Site1/Site2 (JSON APIs) and Site3 (HTML scraping), this adapter
    parses XML responses — a format common in airline GDS/distribution systems.
    """
    name = "site4"

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        """Collect fares from the AirWings XML API."""
        headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/xml",
        }
        response = requests.get(f"{self.base_url}/site4-api/flights", headers=headers)
        response.raise_for_status()

        root = ET.fromstring(response.text)

        quotes = []
        for flight_el in root.findall(".//flight"):
            flight_number = flight_el.findtext("flightNumber", "N/A")
            cabin = flight_el.findtext("cabin", "economy")
            base_fare = Decimal(flight_el.findtext("baseFare", "0"))
            taxes = Decimal(flight_el.findtext("taxes", "0"))
            other_charges = Decimal(flight_el.findtext("otherCharges", "0"))
            total_fare = Decimal(flight_el.findtext("totalFare", "0"))
            currency = flight_el.findtext("currency", "INR")
            fare_family = flight_el.findtext("fareFamily")
            stops_text = flight_el.findtext("stops", "0")
            stops = int(stops_text) if stops_text.isdigit() else 0

            quote = FareQuote(
                source=self.name,
                origin=origin.upper(),
                destination=destination.upper(),
                travel_date=travel_date,
                observation_timestamp=datetime.now(timezone.utc),
                advance_days=advance_days,
                airline="AirWings",
                flight_number=flight_number,
                fare_class="Economy",
                cabin=cabin,
                fare_family=fare_family if fare_family else "N/A",
                stops=stops,
                base_fare=base_fare,
                taxes=taxes,
                other_charges=other_charges,
                total_fare=total_fare,
                currency=currency,
                availability="available",
            )
            quotes.append(quote)

        if not quotes:
            raise Exception("No flights found")

        return min(quotes, key=lambda q: q.total_fare)
