from datetime import date, datetime, timezone
from decimal import Decimal
import pytest

from models.fare_quote import FareQuote


def valid_quote():
    return FareQuote(
        source="airline_a",
        origin="DEL",
        destination="BOM",
        travel_date=date(2026, 9, 20),
        observation_timestamp=datetime(2026, 9, 5, tzinfo=timezone.utc),
        advance_days=15,
        airline="Test Air",
        base_fare=Decimal("4500"),
        taxes=Decimal("500"),
        other_charges=Decimal("100"),
        total_fare=Decimal("5100"),
    )


def test_valid_quote():
    assert valid_quote().total_fare == Decimal("5100")


def test_advance_days_must_match_dates():
    payload = valid_quote().model_dump()
    payload["advance_days"] = 14
    with pytest.raises(ValueError):
        FareQuote(**payload)
