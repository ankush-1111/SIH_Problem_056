from datetime import date, datetime, timezone
from decimal import Decimal
from models.fare_quote import FareQuote

class MockAirlineAAdapter:
    name = "airline_a"

    def __init__(self, base_url: str, requests_per_minute: int = 20):
        self.base_url = base_url

    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        return FareQuote(
            source=self.name,
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            observation_timestamp=datetime.now(timezone.utc),
            advance_days=advance_days,
            airline="Mock Air",
            base_fare=Decimal("5000"),
            taxes=Decimal("500"),
            total_fare=Decimal("5500"),
        )
