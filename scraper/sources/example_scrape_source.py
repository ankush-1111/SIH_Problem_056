"""Template for a permitted JavaScript-rendered fare page.

The adapter intentionally stops on CAPTCHA/challenge/block indicators.
It never attempts CAPTCHA solving, fingerprint evasion, proxy rotation, or
other anti-bot bypasses.
"""

from datetime import date, datetime, timezone

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from sources.base import SourceAdapter
from models.fare_quote import FareQuote
from core.rate_limiter import rate_limiter
from core.retry import with_retry, BlockedError, PermanentSourceError
from core.logger import get_logger

logger = get_logger("airline_b")

BLOCK_INDICATORS = (
    "captcha",
    "verify you are human",
    "access denied",
    "unusual traffic",
    "request blocked",
)


class AirlineBAdapter(SourceAdapter):
    name = "airline_b"

    def __init__(self, base_url: str, page_timeout_ms: int = 20_000, requests_per_minute: int = 12):
        self.base_url = base_url.rstrip("/")
        self.page_timeout_ms = page_timeout_ms
        self.min_interval = 60.0 / max(requests_per_minute, 1)

    @with_retry(max_attempts=2, delay_seconds=3.0)
    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        if "example-airline" in self.base_url:
            raise PermanentSourceError(
                "Placeholder scrape URL configured. Replace airline_b with a verified permitted source."
            )

        rate_limiter.wait_if_needed(self.name, self.min_interval)
        logger.info(f"Opening {self.name} for {origin}->{destination} on {travel_date}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(self.page_timeout_ms)
            try:
                page.goto(self.base_url, wait_until="domcontentloaded")
                self._check_for_block(page)

                # Replace selectors only after confirming the real permitted source.
                page.fill("#origin", origin)
                page.fill("#destination", destination)
                page.fill("#travel-date", travel_date.isoformat())
                page.click("#search-button")
                page.wait_for_selector(".fare-result", timeout=self.page_timeout_ms)
                self._check_for_block(page)

                fare_text = page.locator(".fare-result .price").first.inner_text()
                total_fare = float(fare_text.replace("₹", "").replace(",", "").strip())

                # The real parser must derive these fields from the source.
                base_fare = total_fare
                taxes = 0
                return FareQuote(
                    source=self.name,
                    origin=origin,
                    destination=destination,
                    travel_date=travel_date,
                    observation_timestamp=datetime.now(timezone.utc),
                    advance_days=advance_days,
                    airline=page.locator(".fare-result .airline").first.inner_text(),
                    flight_number=None,
                    fare_class="Economy",
                    cabin="Economy",
                    stops=0,
                    base_fare=base_fare,
                    taxes=taxes,
                    total_fare=total_fare,
                    currency="INR",
                    availability="available",
                )
            except PlaywrightTimeoutError:
                logger.warning(f"[{self.name}] page timed out")
                raise
            finally:
                browser.close()

    def _check_for_block(self, page) -> None:
        content = page.content().lower()
        for indicator in BLOCK_INDICATORS:
            if indicator in content:
                logger.warning(
                    f"[{self.name}] block/CAPTCHA detected ('{indicator}') — stopping this job"
                )
                raise BlockedError(f"{self.name} returned a block/CAPTCHA page")
