"""Template for a verified official/partner fare API.

No fake data is used: the adapter fails clearly until its real API contract
is configured. This prevents demo data from being mistaken for live data.
"""

from datetime import date, datetime, timezone
import os

import httpx

from sources.base import SourceAdapter
from models.fare_quote import FareQuote
from core.rate_limiter import rate_limiter
from core.retry import with_retry, PermanentSourceError
from core.logger import get_logger

logger = get_logger("airline_a")


class AirlineAAdapter(SourceAdapter):
    name = "airline_a"

    def __init__(self, base_url: str, api_key: str | None = None, requests_per_minute: int = 20):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("AIRLINE_A_API_KEY")
        self.min_interval = 60.0 / max(requests_per_minute, 1)

    @with_retry(max_attempts=3, delay_seconds=2.0)
    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        if "example-airline" in self.base_url:
            raise PermanentSourceError(
                "Placeholder API URL configured. Replace airline_a with a verified real API."
            )
        if not self.api_key:
            raise PermanentSourceError("AIRLINE_A_API_KEY is not configured")

        rate_limiter.wait_if_needed(self.name, self.min_interval)
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {
            "origin": origin,
            "destination": destination,
            "date": travel_date.isoformat(),
            "passengers": 1,
            "cabin": "ECONOMY",
            "trip_type": "ONE_WAY",
        }

        response = httpx.get(
            f"{self.base_url}/v1/fares",
            params=params,
            headers=headers,
            timeout=15.0,
        )
        if response.status_code in (401, 403):
            raise PermanentSourceError(f"API access rejected: HTTP {response.status_code}")
        if response.status_code == 429:
            response.raise_for_status()
        response.raise_for_status()
        data = response.json()

        return FareQuote(
            source=self.name,
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            observation_timestamp=datetime.now(timezone.utc),
            advance_days=advance_days,
            airline=data["airline"],
            flight_number=data.get("flight_number"),
            fare_class=data.get("fare_class", "Economy"),
            cabin=data.get("cabin", "Economy"),
            fare_family=data.get("fare_family"),
            stops=data.get("stops", 0),
            departure_time=data.get("departure_time"),
            arrival_time=data.get("arrival_time"),
            base_fare=data["base_fare"],
            taxes=data.get("taxes", 0),
            other_charges=data.get("other_charges", 0),
            total_fare=data["total_fare"],
            currency=data.get("currency", "INR"),
            availability=data.get("availability", "available"),
        )
