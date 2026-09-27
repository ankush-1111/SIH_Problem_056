from datetime import date, datetime, timezone
from decimal import Decimal
from models.fare_quote import FareQuote

class MockAirlineCAdapter:
    name = "airline_c"

    def __init__(self, base_url: str, requests_per_minute: int = 12):
        self.base_url = base_url

    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        # Return invalid fare (e.g., negative fare to be rejected)
        return FareQuote(
            source=self.name,
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            observation_timestamp=datetime.now(timezone.utc),
            advance_days=advance_days,
            airline="Mock Air C",
            base_fare=Decimal("-100"),
            taxes=Decimal("0"),
            total_fare=Decimal("-100"),
        )
