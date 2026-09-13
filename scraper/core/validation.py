"""Final sanity checks before a fare reaches storage."""

from decimal import Decimal

from models.fare_quote import FareQuote
from core.logger import get_logger

logger = get_logger("validation")

MIN_FARE = Decimal("100.00")
MAX_FARE = Decimal("500000.00")


def is_sane_fare(quote: FareQuote) -> bool:
    checks = [
        (quote.origin != quote.destination, "origin and destination are identical"),
        (quote.total_fare >= quote.base_fare, "total is below base fare"),
        (quote.total_fare >= MIN_FARE, "total fare is suspiciously low"),
        (quote.total_fare <= MAX_FARE, "total fare is suspiciously high"),
        (quote.taxes >= 0, "taxes are negative"),
        (quote.other_charges >= 0, "other charges are negative"),
        (
            abs(quote.total_fare - (quote.base_fare + quote.taxes + quote.other_charges)) <= Decimal("1.00"),
            "fare components do not reconcile",
        ),
        (quote.availability == "available", "fare is not available"),
    ]

    for ok, reason in checks:
        if not ok:
            logger.warning(
                f"Rejected fare {quote.source} {quote.origin}->{quote.destination}: {reason}"
            )
            return False
    return True
