"""Canonical fare record emitted by every source adapter."""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FareQuote(BaseModel):
    """One representative fare observation.

    Prototype policy: one record represents the lowest available eligible
    one-way economy fare for the standardized search profile.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    source: str = Field(min_length=1)
    origin: str
    destination: str
    travel_date: date
    observation_timestamp: datetime
    advance_days: int = Field(ge=0)

    airline: str = Field(min_length=1)
    flight_number: str | None = None
    fare_class: str = "Economy"
    cabin: str = "Economy"
    fare_family: str | None = None
    stops: int = Field(default=0, ge=0)
    departure_time: str | None = None
    arrival_time: str | None = None

    base_fare: Decimal = Field(gt=0, decimal_places=2)
    taxes: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    other_charges: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    total_fare: Decimal = Field(gt=0, decimal_places=2)
    currency: str = "INR"
    availability: Literal["available", "sold_out", "unknown"] = "available"

    # Makes source-to-source comparisons explicit and reproducible.
    search_profile: str = "one_way_economy_1pax"

    @field_validator("origin", "destination", "currency")
    @classmethod
    def uppercase_codes(cls, value: str) -> str:
        return value.upper()

    @field_validator("origin", "destination")
    @classmethod
    def validate_iata(cls, value: str) -> str:
        if len(value) != 3 or not value.isalpha():
            raise ValueError("Airport code must be a 3-letter IATA code")
        return value

    @field_validator("observation_timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("observation_timestamp must be timezone-aware")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if len(value) != 3 or not value.isalpha():
            raise ValueError("currency must be a 3-letter ISO-style code")
        return value.upper()

    @model_validator(mode="after")
    def validate_fare_math(self) -> "FareQuote":
        expected = self.base_fare + self.taxes + self.other_charges
        if abs(self.total_fare - expected) > Decimal("1.00"):
            raise ValueError("total_fare does not match base_fare + taxes + other_charges")
        observation_date = self.observation_timestamp.astimezone(ZoneInfo("Asia/Kolkata")).date()
        if self.travel_date < observation_date:
            raise ValueError("travel_date cannot be before the observation date")
        actual_advance = (self.travel_date - observation_date).days
        if actual_advance != self.advance_days:
            raise ValueError("advance_days does not match travel_date and observation date")
        return self
