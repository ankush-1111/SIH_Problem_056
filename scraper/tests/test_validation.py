from decimal import Decimal

from core.validation import is_sane_fare
from tests.test_fare_quote import valid_quote


def test_validation_accepts_good_fare():
    assert is_sane_fare(valid_quote()) is True


def test_validation_rejects_sold_out():
    quote = valid_quote().model_copy(update={"availability": "sold_out"})
    assert is_sane_fare(quote) is False
