"""Common adapter contract."""

from abc import ABC, abstractmethod
from datetime import date

from scraper.models.fare_quote import FareQuote


class SourceAdapter(ABC):
    name: str

    @abstractmethod
    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        """Return one representative eligible fare or raise an explicit error."""
        raise NotImplementedError
