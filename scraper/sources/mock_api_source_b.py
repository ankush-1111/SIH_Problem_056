from datetime import date, datetime, timezone
from decimal import Decimal
from models.fare_quote import FareQuote

class MockAirlineBAdapter:
    name = "airline_b"

    def __init__(self, base_url: str, requests_per_minute: int = 12):
        self.base_url = base_url

    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        # Return different fare from airline_a
        return FareQuote(
            source=self.name,
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            observation_timestamp=datetime.now(timezone.utc),
            advance_days=advance_days,
            airline="Mock Air B",
            base_fare=Decimal("6000"),
            taxes=Decimal("600"),
            total_fare=Decimal("6600"),
        )
