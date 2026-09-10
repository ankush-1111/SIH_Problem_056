from datetime import date, datetime, timezone
from playwright.sync_api import sync_playwright
from sources.base import SourceAdapter
from models.fare_quote import FareQuote
from core.retry import BlockedError

class AirZenAdapter(SourceAdapter):
    name = "airline_e"

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{self.base_url}/normal") # Starting with normal for simplicity

            # Simple block detector
            content = page.content().lower()
            if "verify you are human" in content:
                raise BlockedError("CAPTCHA detected")

            price_text = page.locator(".price").first.inner_text()
            price = float(price_text.replace("₹", "").replace(",", "").strip())

            return FareQuote(
                source=self.name,
                origin=origin,
                destination=destination,
                travel_date=travel_date,
                observation_timestamp=datetime.now(timezone.utc),
                advance_days=advance_days,
                airline="AirZen",
                base_fare=price,
                total_fare=price,
                currency="INR",
                availability="available"
            )
